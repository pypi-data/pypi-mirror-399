"""CUDA-Enabled Shared Memory Ring Buffer for GPU Zero-Copy Frame Access.

This module implements a lock-free ring buffer using CUDA pinned (page-locked) memory
for zero-copy frame sharing between producer (streaming gateway) and GPU consumers
(inference servers, Triton, TensorRT).

Key Features:
- CUDA pinned memory for DMA transfers to GPU without CPU copies
- Same ring buffer semantics as ShmRingBuffer
- DLPack support for framework-agnostic tensor exchange
- Zero-copy path to Triton/TensorRT inference

Architecture:
- Producer creates pinned memory buffer and writes frames
- GPU consumers can DMA frames directly without memcpy
- Supports CuPy, PyTorch, and raw CUDA tensor interfaces
- Falls back to CPU SHM if CUDA is unavailable

Memory Hierarchy:
┌─────────────────────────────────────────────────────────────────┐
│ CUDA Pinned Host Memory (cudaHostAlloc / cudaMallocHost)        │
│ ┌────────────────────┐                                          │
│ │ Header (64 bytes)  │  write_idx, width, height, format, etc.  │
│ ├────────────────────┤                                          │
│ │ Per-slot metadata  │  frame_idx, seq_start, seq_end per slot  │
│ ├────────────────────┤                                          │
│ │ Frame slot 0       │  ← DMA to GPU via cudaMemcpyAsync        │
│ ├────────────────────┤                                          │
│ │ Frame slot 1       │  ← Zero-copy: GPU reads directly         │
│ ├────────────────────┤                                          │
│ │ ...                │                                          │
│ └────────────────────┘                                          │
└─────────────────────────────────────────────────────────────────┘
              ↕ PCIe DMA (no CPU memcpy)
┌─────────────────────────────────────────────────────────────────┐
│ GPU Memory (CUDA Device)                                        │
│ ┌────────────────────┐                                          │
│ │ Inference Tensor   │  ← Direct access or async copy           │
│ └────────────────────┘                                          │
└─────────────────────────────────────────────────────────────────┘

Performance Notes:
- Pinned memory enables ~12 GB/s PCIe transfers (vs ~6 GB/s pageable)
- Zero-copy mode maps pinned memory directly into GPU address space
- Best for small/medium frames where transfer < kernel execution time
- For large frames, async copy + double buffering is recommended

Requirements:
- CUDA Toolkit (nvcc) installed
- CuPy or PyTorch with CUDA support
- NVIDIA GPU with compute capability >= 3.5
"""

import logging
import struct
import time
from typing import TYPE_CHECKING, Any, Optional, Tuple, Union

import numpy as np

# Lazy imports for CUDA libraries (may not be available)
if TYPE_CHECKING:
    import cupy as cp
    import torch


class CudaRingBufferError(Exception):
    """Base exception for CUDA ring buffer errors."""
    pass


class CudaNotAvailableError(CudaRingBufferError):
    """Raised when CUDA is not available."""
    pass


class CudaShmRingBuffer:
    """CUDA-enabled shared memory ring buffer for GPU zero-copy frame access.

    This buffer uses CUDA pinned (page-locked) memory to enable:
    1. Zero-copy GPU access via cudaHostGetDevicePointer
    2. Fast async DMA transfers via cudaMemcpyAsync
    3. DLPack tensor exchange with Triton/TensorRT

    Example (Producer):
        buffer = CudaShmRingBuffer(
            camera_id="cam_001",
            width=1920,
            height=1080,
            frame_format=CudaShmRingBuffer.FORMAT_BGR,
            slot_count=60,  # ~2 seconds at 30 FPS
            create=True
        )
        frame_idx, slot = buffer.write_frame(bgr_frame)

    Example (GPU Consumer with CuPy):
        buffer = CudaShmRingBuffer(
            camera_id="cam_001",
            width=1920,
            height=1080,
            frame_format=CudaShmRingBuffer.FORMAT_BGR,
            slot_count=60,
            create=False
        )
        # Get GPU tensor directly (zero-copy)
        gpu_tensor = buffer.get_frame_gpu_tensor(frame_idx)
        # Or get as DLPack capsule for Triton
        dlpack = buffer.get_frame_dlpack(frame_idx)

    Example (GPU Consumer with PyTorch):
        buffer = CudaShmRingBuffer(...)
        # Get as PyTorch CUDA tensor
        torch_tensor = buffer.get_frame_torch_tensor(frame_idx, device='cuda:0')
    """

    # Header and metadata layout (same as ShmRingBuffer for compatibility)
    HEADER_FORMAT = '<QIIIIQ'
    HEADER_SIZE = 64
    SLOT_METADATA_SIZE = 16
    PAGE_SIZE = 4096

    # Frame format constants (same as ShmRingBuffer)
    FORMAT_NV12 = 0
    FORMAT_RGB = 1
    FORMAT_BGR = 2

    FORMAT_NAMES = {
        FORMAT_NV12: "NV12",
        FORMAT_RGB: "RGB",
        FORMAT_BGR: "BGR",
    }

    # CUDA memory allocation flags
    CUDA_HOST_ALLOC_DEFAULT = 0x00
    CUDA_HOST_ALLOC_PORTABLE = 0x01  # Memory accessible from any CUDA context
    CUDA_HOST_ALLOC_MAPPED = 0x02    # Map into device address space (zero-copy)
    CUDA_HOST_ALLOC_WRITECOMBINED = 0x04  # Optimized for CPU writes, GPU reads

    def __init__(
        self,
        camera_id: str,
        width: int,
        height: int,
        frame_format: int = FORMAT_BGR,
        slot_count: int = 60,
        create: bool = True,
        use_zero_copy: bool = True,
        cuda_device: int = 0,
        fallback_to_cpu: bool = True,
    ):
        """Initialize CUDA ring buffer with pinned memory.

        Args:
            camera_id: Unique camera identifier
            width: Frame width in pixels
            height: Frame height in pixels
            frame_format: One of FORMAT_NV12, FORMAT_RGB, FORMAT_BGR
            slot_count: Number of frame slots (default: 60 = ~2s at 30fps)
            create: True for producer (creates buffer), False for consumer
            use_zero_copy: Enable GPU zero-copy access (CUDA_HOST_ALLOC_MAPPED)
            cuda_device: CUDA device ID to use (default: 0)
            fallback_to_cpu: If True, fall back to CPU SHM when CUDA unavailable

        Raises:
            CudaNotAvailableError: If CUDA not available and fallback_to_cpu=False
            ValueError: If parameters are invalid
        """
        self.logger = logging.getLogger(f"{__name__}.CudaShmRingBuffer")

        # Validate inputs
        if frame_format not in self.FORMAT_NAMES:
            raise ValueError(f"Invalid frame_format: {frame_format}")
        if width <= 0 or height <= 0:
            raise ValueError(f"Invalid dimensions: {width}x{height}")
        if slot_count < 2:
            raise ValueError(f"slot_count must be >= 2, got {slot_count}")

        self.camera_id = camera_id
        self.width = width
        self.height = height
        self.frame_format = frame_format
        self.slot_count = slot_count
        self._is_producer = create
        self._use_zero_copy = use_zero_copy
        self._cuda_device = cuda_device
        self._fallback_to_cpu = fallback_to_cpu

        # Calculate sizes
        self.frame_size = self._calculate_frame_size(width, height, frame_format)
        self._aligned_slot_size = self._calculate_aligned_slot_size(self.frame_size)
        self._slot_metadata_size = self.SLOT_METADATA_SIZE * slot_count
        self._total_size = self._calculate_total_size()

        # OPTIMIZATION: Producer-side cached counters
        self._cached_write_idx: int = 0
        self._cached_slot_seq: list = [0] * slot_count

        # CUDA state
        self._cuda_available = False
        self._cupy_available = False
        self._torch_available = False
        self._pinned_buffer: Optional[np.ndarray] = None
        self._device_ptr: Optional[int] = None  # GPU-mapped pointer for zero-copy
        self._cp = None  # CuPy module reference
        self._torch = None  # PyTorch module reference

        # Initialize CUDA or fall back to CPU
        self._init_cuda_backend()

        self.logger.info(
            f"CudaShmRingBuffer {'created' if create else 'attached'}: "
            f"camera={camera_id}, size={self._total_size:,} bytes, "
            f"{width}x{height} {self.FORMAT_NAMES[frame_format]}, "
            f"{slot_count} slots, cuda={self._cuda_available}, "
            f"zero_copy={use_zero_copy and self._cuda_available}"
        )

    def _calculate_frame_size(self, width: int, height: int, frame_format: int) -> int:
        """Calculate frame size in bytes based on format."""
        if frame_format == self.FORMAT_NV12:
            return int(width * height * 1.5)
        elif frame_format in (self.FORMAT_RGB, self.FORMAT_BGR):
            return width * height * 3
        else:
            raise ValueError(f"Unknown frame format: {frame_format}")

    def _calculate_aligned_slot_size(self, frame_size: int) -> int:
        """Calculate page-aligned slot size for hardware efficiency."""
        return ((frame_size + self.PAGE_SIZE - 1) // self.PAGE_SIZE) * self.PAGE_SIZE

    def _calculate_total_size(self) -> int:
        """Calculate total buffer size."""
        return self.HEADER_SIZE + self._slot_metadata_size + (self._aligned_slot_size * self.slot_count)

    def _init_cuda_backend(self) -> None:
        """Initialize CUDA backend with pinned memory.

        Tries CuPy first (most flexible), then PyTorch, then raw CUDA.
        Falls back to CPU numpy if CUDA unavailable.
        """
        # Try CuPy first (best for general CUDA operations)
        try:
            import cupy as cp
            self._cp = cp
            self._cupy_available = True
            self._cuda_available = True

            # Set device
            with cp.cuda.Device(self._cuda_device):
                # Allocate pinned memory using CuPy
                self._pinned_buffer = cp.cuda.alloc_pinned_memory(self._total_size)
                # Create numpy array view of pinned memory
                self._buffer_array = np.frombuffer(self._pinned_buffer, dtype=np.uint8)

                if self._use_zero_copy:
                    # Get device pointer for zero-copy access
                    # This maps the pinned host memory into GPU address space
                    self._device_ptr = cp.cuda.runtime.hostGetDevicePointer(
                        self._pinned_buffer.ptr, 0
                    )

            self.logger.info(f"CUDA backend initialized with CuPy (device {self._cuda_device})")

        except ImportError:
            self.logger.debug("CuPy not available, trying PyTorch")

        except Exception as e:
            self.logger.warning(f"CuPy CUDA init failed: {e}, trying PyTorch")

        # Try PyTorch if CuPy failed
        if not self._cuda_available:
            try:
                import torch
                if torch.cuda.is_available():
                    self._torch = torch
                    self._torch_available = True
                    self._cuda_available = True

                    # Allocate pinned memory using PyTorch
                    # pin_memory() creates page-locked memory
                    self._pinned_tensor = torch.empty(
                        self._total_size,
                        dtype=torch.uint8,
                        pin_memory=True
                    )
                    self._buffer_array = self._pinned_tensor.numpy()

                    self.logger.info(f"CUDA backend initialized with PyTorch")
                else:
                    self.logger.debug("PyTorch CUDA not available")

            except ImportError:
                self.logger.debug("PyTorch not available")

            except Exception as e:
                self.logger.warning(f"PyTorch CUDA init failed: {e}")

        # Fall back to CPU numpy if CUDA unavailable
        if not self._cuda_available:
            if self._fallback_to_cpu:
                self.logger.warning(
                    "CUDA not available, falling back to CPU numpy buffer. "
                    "GPU zero-copy will not be available."
                )
                self._buffer_array = np.zeros(self._total_size, dtype=np.uint8)
            else:
                raise CudaNotAvailableError(
                    "CUDA not available and fallback_to_cpu=False. "
                    "Install CuPy or PyTorch with CUDA support."
                )

        # Initialize header if producer
        if self._is_producer:
            self._write_header(
                write_idx=0,
                width=self.width,
                height=self.height,
                frame_format=self.frame_format,
                slot_count=self.slot_count,
                last_ts_ns=int(time.time() * 1e9)
            )
            # Initialize slot metadata
            for slot in range(self.slot_count):
                self._write_slot_frame_idx(slot, 0)
                self._write_slot_seq_start(slot, 0)
                self._write_slot_seq_end(slot, 0)

    # =========================================================================
    # Header and Metadata Operations (same as ShmRingBuffer)
    # =========================================================================

    def _write_header(
        self,
        write_idx: int,
        width: int,
        height: int,
        frame_format: int,
        slot_count: int,
        last_ts_ns: int
    ) -> None:
        """Write header to buffer."""
        header_bytes = struct.pack(
            self.HEADER_FORMAT,
            write_idx, width, height, frame_format, slot_count, last_ts_ns
        )
        header_bytes = header_bytes.ljust(self.HEADER_SIZE, b'\x00')
        self._buffer_array[:self.HEADER_SIZE] = np.frombuffer(header_bytes, dtype=np.uint8)

    def _read_header(self) -> dict:
        """Read header from buffer."""
        header_bytes = bytes(self._buffer_array[:struct.calcsize(self.HEADER_FORMAT)])
        write_idx, width, height, fmt, slot_count, last_ts_ns = struct.unpack(
            self.HEADER_FORMAT, header_bytes
        )
        return {
            'write_idx': write_idx,
            'width': width,
            'height': height,
            'format': fmt,
            'slot_count': slot_count,
            'last_ts_ns': last_ts_ns,
        }

    def _update_write_idx(self, new_idx: int) -> None:
        """Update write_idx in header."""
        self._buffer_array[:8] = np.frombuffer(struct.pack('<Q', new_idx), dtype=np.uint8)

    def _update_last_ts_ns(self, ts_ns: int) -> None:
        """Update heartbeat timestamp in header."""
        offset = 8 + 4 + 4 + 4 + 4  # After write_idx, width, height, format, slot_count
        self._buffer_array[offset:offset+8] = np.frombuffer(struct.pack('<Q', ts_ns), dtype=np.uint8)

    def _get_slot_metadata_offset(self, slot: int) -> int:
        """Get offset for slot's metadata."""
        return self.HEADER_SIZE + (slot * self.SLOT_METADATA_SIZE)

    def _write_slot_frame_idx(self, slot: int, frame_idx: int) -> None:
        """Write frame_idx to slot metadata."""
        offset = self._get_slot_metadata_offset(slot)
        self._buffer_array[offset:offset+8] = np.frombuffer(struct.pack('<Q', frame_idx), dtype=np.uint8)

    def _read_slot_frame_idx(self, slot: int) -> int:
        """Read frame_idx from slot metadata."""
        offset = self._get_slot_metadata_offset(slot)
        return struct.unpack('<Q', bytes(self._buffer_array[offset:offset+8]))[0]

    def _write_slot_seq_start(self, slot: int, seq: int) -> None:
        """Write seq_start counter for slot."""
        offset = self._get_slot_metadata_offset(slot) + 8
        self._buffer_array[offset:offset+4] = np.frombuffer(struct.pack('<I', seq & 0xFFFFFFFF), dtype=np.uint8)

    def _read_slot_seq_start(self, slot: int) -> int:
        """Read seq_start counter for slot."""
        offset = self._get_slot_metadata_offset(slot) + 8
        return struct.unpack('<I', bytes(self._buffer_array[offset:offset+4]))[0]

    def _write_slot_seq_end(self, slot: int, seq: int) -> None:
        """Write seq_end counter for slot."""
        offset = self._get_slot_metadata_offset(slot) + 12
        self._buffer_array[offset:offset+4] = np.frombuffer(struct.pack('<I', seq & 0xFFFFFFFF), dtype=np.uint8)

    def _read_slot_seq_end(self, slot: int) -> int:
        """Read seq_end counter for slot."""
        offset = self._get_slot_metadata_offset(slot) + 12
        return struct.unpack('<I', bytes(self._buffer_array[offset:offset+4]))[0]

    def _get_frame_offset(self, slot: int) -> int:
        """Get byte offset for frame data in given slot."""
        return self.HEADER_SIZE + self._slot_metadata_size + (slot * self._aligned_slot_size)

    # =========================================================================
    # Producer Operations
    # =========================================================================

    def write_frame(self, raw_bytes: Union[bytes, memoryview, np.ndarray]) -> Tuple[int, int]:
        """Write frame to next slot (producer only).

        OPTIMIZED: Uses cached counters and memoryview for minimal overhead.
        Uses odd/even sequence semantics for torn frame and crash detection.

        Args:
            raw_bytes: Raw frame data (NV12, RGB, or BGR bytes)

        Returns:
            Tuple of (frame_idx, slot_idx)

        Raises:
            RuntimeError: If called on consumer instance
            ValueError: If raw_bytes size doesn't match expected frame_size
        """
        if not self._is_producer:
            raise RuntimeError("write_frame() can only be called on producer instance")

        # Handle input types efficiently
        if isinstance(raw_bytes, np.ndarray):
            if raw_bytes.flags['C_CONTIGUOUS']:
                raw_data = raw_bytes.ravel().view(np.uint8)
            else:
                raw_data = np.ascontiguousarray(raw_bytes).ravel().view(np.uint8)
        elif isinstance(raw_bytes, memoryview):
            raw_data = np.frombuffer(raw_bytes, dtype=np.uint8)
        else:
            raw_data = np.frombuffer(raw_bytes, dtype=np.uint8)

        if len(raw_data) != self.frame_size:
            raise ValueError(
                f"Frame size mismatch: expected {self.frame_size} bytes, "
                f"got {len(raw_data)} bytes"
            )

        # OPTIMIZATION: Use cached write_idx
        self._cached_write_idx += 1
        frame_idx = self._cached_write_idx
        slot = frame_idx % self.slot_count

        # Odd/even sequence semantics for torn frame detection
        self._cached_slot_seq[slot] += 1  # Now ODD → writing
        seq_writing = self._cached_slot_seq[slot]
        self._write_slot_seq_start(slot, seq_writing)

        # Write frame data to slot
        frame_offset = self._get_frame_offset(slot)
        self._buffer_array[frame_offset:frame_offset + self.frame_size] = raw_data

        # Update slot metadata
        self._write_slot_frame_idx(slot, frame_idx)

        # Complete write (even sequence)
        self._cached_slot_seq[slot] += 1  # Now EVEN → committed
        seq_committed = self._cached_slot_seq[slot]
        self._write_slot_seq_end(slot, seq_committed)

        # Update header
        ts_ns = int(time.time() * 1e9)
        self._update_write_idx(frame_idx)
        self._update_last_ts_ns(ts_ns)

        return frame_idx, slot

    # =========================================================================
    # Consumer Operations - CPU
    # =========================================================================

    def read_frame(self, frame_idx: int) -> Optional[np.ndarray]:
        """Read frame as numpy array (zero-copy view into pinned memory).

        WARNING: The returned array is a VIEW into pinned memory and may be
        overwritten by the producer. Use read_frame_copy() for safe copies.

        Args:
            frame_idx: Frame index to read

        Returns:
            Numpy array view of frame data, or None if frame invalid/torn
        """
        if not self.is_frame_valid(frame_idx):
            return None

        slot = frame_idx % self.slot_count
        frame_offset = self._get_frame_offset(slot)

        # Return view into pinned memory (zero-copy)
        return self._buffer_array[frame_offset:frame_offset + self.frame_size]

    def read_frame_copy(self, frame_idx: int) -> Optional[bytes]:
        """Read frame and return a safe copy with torn frame detection.

        Args:
            frame_idx: Frame index to read

        Returns:
            Bytes copy of frame data, or None if frame invalid/torn
        """
        if not self.is_frame_valid(frame_idx):
            return None

        slot = frame_idx % self.slot_count

        # Check for crash (odd seq_start)
        seq_start = self._read_slot_seq_start(slot)
        if seq_start & 1:
            self.logger.debug(f"Crashed frame at frame_idx={frame_idx}, slot={slot}")
            return None

        # Read frame data
        frame_offset = self._get_frame_offset(slot)
        frame_data = bytes(self._buffer_array[frame_offset:frame_offset + self.frame_size])

        # Verify no torn frame
        seq_end = self._read_slot_seq_end(slot)
        if seq_start != seq_end:
            self.logger.debug(f"Torn frame at frame_idx={frame_idx}, slot={slot}")
            return None

        # Verify frame_idx didn't change
        stored_frame_idx = self._read_slot_frame_idx(slot)
        if stored_frame_idx != frame_idx:
            self.logger.debug(f"Frame overwritten: expected {frame_idx}, got {stored_frame_idx}")
            return None

        return frame_data

    # =========================================================================
    # Consumer Operations - GPU (Zero-Copy & DMA)
    # =========================================================================

    def get_frame_gpu_tensor(
        self,
        frame_idx: int,
        copy: bool = False,
        stream: Optional[Any] = None
    ) -> Optional[Any]:
        """Get frame as GPU tensor (CuPy ndarray).

        Zero-copy mode (copy=False):
            Returns a CuPy array that directly accesses pinned host memory
            via the GPU's PCIe interface. No data copy occurs.
            Best for: Small frames, single-use inference.

        Copy mode (copy=True):
            Copies frame to GPU device memory via DMA (cudaMemcpyAsync).
            Best for: Large frames, repeated access, batch processing.

        Args:
            frame_idx: Frame index to read
            copy: If True, copy to device memory. If False, use zero-copy.
            stream: CUDA stream for async copy (optional, copy mode only)

        Returns:
            CuPy ndarray on GPU, or None if frame invalid/torn or CUDA unavailable
        """
        if not self._cupy_available:
            self.logger.warning("CuPy not available for GPU tensor access")
            return None

        if not self.is_frame_valid(frame_idx):
            return None

        slot = frame_idx % self.slot_count

        # Torn frame check
        seq_start = self._read_slot_seq_start(slot)
        if seq_start & 1:
            return None

        frame_offset = self._get_frame_offset(slot)

        cp = self._cp
        with cp.cuda.Device(self._cuda_device):
            if copy:
                # DMA copy to device memory (async if stream provided)
                host_array = self._buffer_array[frame_offset:frame_offset + self.frame_size]
                if stream is not None:
                    gpu_array = cp.empty(self.frame_size, dtype=cp.uint8)
                    gpu_array.set(host_array, stream=stream)
                else:
                    gpu_array = cp.asarray(host_array)
            else:
                # Zero-copy: Create GPU array that maps pinned host memory
                if self._device_ptr is None:
                    self.logger.warning("Zero-copy not available (device pointer not mapped)")
                    return None

                # Create memory pointer at the frame offset
                mem_ptr = cp.cuda.MemoryPointer(
                    cp.cuda.UnownedMemory(
                        self._device_ptr + frame_offset,
                        self.frame_size,
                        owner=self
                    ),
                    0
                )
                gpu_array = cp.ndarray(
                    shape=(self.frame_size,),
                    dtype=cp.uint8,
                    memptr=mem_ptr
                )

        # Verify no torn frame after read
        seq_end = self._read_slot_seq_end(slot)
        if seq_start != seq_end:
            return None

        return gpu_array

    def get_frame_torch_tensor(
        self,
        frame_idx: int,
        device: str = 'cuda:0',
        non_blocking: bool = True
    ) -> Optional["torch.Tensor"]:
        """Get frame as PyTorch CUDA tensor.

        Uses non-blocking transfer from pinned memory for optimal performance.

        Args:
            frame_idx: Frame index to read
            device: Target CUDA device (e.g., 'cuda:0')
            non_blocking: Use async transfer (recommended for pinned memory)

        Returns:
            PyTorch tensor on GPU, or None if frame invalid/torn or PyTorch unavailable
        """
        if not self._torch_available:
            self.logger.warning("PyTorch not available for tensor access")
            return None

        if not self.is_frame_valid(frame_idx):
            return None

        slot = frame_idx % self.slot_count

        # Torn frame check
        seq_start = self._read_slot_seq_start(slot)
        if seq_start & 1:
            return None

        frame_offset = self._get_frame_offset(slot)

        torch = self._torch

        # Create tensor from pinned memory slice
        host_array = self._buffer_array[frame_offset:frame_offset + self.frame_size]
        host_tensor = torch.from_numpy(host_array)

        # Transfer to GPU (fast because source is pinned)
        gpu_tensor = host_tensor.to(device, non_blocking=non_blocking)

        # Verify no torn frame after read
        seq_end = self._read_slot_seq_end(slot)
        if seq_start != seq_end:
            return None

        return gpu_tensor

    def get_frame_dlpack(self, frame_idx: int, copy: bool = True) -> Optional[Any]:
        """Get frame as DLPack capsule for framework-agnostic exchange.

        DLPack is the standard for zero-copy tensor exchange between:
        - PyTorch
        - TensorFlow
        - CuPy
        - Triton Inference Server
        - TensorRT

        Args:
            frame_idx: Frame index to read
            copy: If True, copy to device memory first (recommended for Triton)

        Returns:
            DLPack capsule, or None if frame invalid/torn or CUDA unavailable

        Example (Triton Python backend):
            dlpack = buffer.get_frame_dlpack(frame_idx)
            tensor = torch.utils.dlpack.from_dlpack(dlpack)
        """
        if self._cupy_available:
            gpu_array = self.get_frame_gpu_tensor(frame_idx, copy=copy)
            if gpu_array is None:
                return None
            return gpu_array.toDlpack()

        elif self._torch_available:
            gpu_tensor = self.get_frame_torch_tensor(frame_idx)
            if gpu_tensor is None:
                return None
            return self._torch.utils.dlpack.to_dlpack(gpu_tensor)

        else:
            self.logger.warning("No CUDA backend available for DLPack")
            return None

    def get_frame_shaped(
        self,
        frame_idx: int,
        as_gpu: bool = False
    ) -> Optional[np.ndarray]:
        """Get frame reshaped to (H, W, C) for image processing.

        Args:
            frame_idx: Frame index to read
            as_gpu: If True, return CuPy array on GPU

        Returns:
            Numpy or CuPy array shaped as (height, width, channels), or None
        """
        if as_gpu and self._cupy_available:
            flat_array = self.get_frame_gpu_tensor(frame_idx, copy=True)
            if flat_array is None:
                return None
            cp = self._cp
        else:
            flat_array = self.read_frame(frame_idx)
            if flat_array is None:
                return None

        # Reshape based on format
        if self.frame_format == self.FORMAT_NV12:
            # NV12 is special - return as-is or convert
            return flat_array
        elif self.frame_format in (self.FORMAT_RGB, self.FORMAT_BGR):
            if as_gpu and self._cupy_available:
                return flat_array.reshape((self.height, self.width, 3))
            else:
                return np.asarray(flat_array).reshape((self.height, self.width, 3))
        else:
            return flat_array

    # =========================================================================
    # Frame Validation and Status
    # =========================================================================

    def is_frame_valid(self, frame_idx: int, max_wait_ms: float = 5.0) -> bool:
        """Check if frame_idx is still available (not overwritten)."""
        if frame_idx <= 0:
            return False

        header = self._read_header()
        current_write_idx = header['write_idx']

        # Frame too old
        if current_write_idx - frame_idx >= self.slot_count:
            return False

        # Frame in future - wait briefly for visibility
        if frame_idx > current_write_idx:
            start_time = time.time()
            max_wait_sec = max_wait_ms / 1000.0

            while time.time() - start_time < max_wait_sec:
                header = self._read_header()
                current_write_idx = header['write_idx']
                if frame_idx <= current_write_idx:
                    break
                time.sleep(0.0001)

            if frame_idx > current_write_idx:
                return False

        # Verify slot metadata
        slot = frame_idx % self.slot_count
        stored_frame_idx = self._read_slot_frame_idx(slot)
        return stored_frame_idx == frame_idx

    def is_frame_torn(self, frame_idx: int) -> bool:
        """Check if frame is torn or corrupted."""
        slot = frame_idx % self.slot_count
        seq_start = self._read_slot_seq_start(slot)
        seq_end = self._read_slot_seq_end(slot)
        return seq_start != seq_end or (seq_start & 1) == 1

    def get_current_frame_idx(self) -> int:
        """Get latest written frame index."""
        header = self._read_header()
        return header['write_idx']

    def get_last_heartbeat_ns(self) -> int:
        """Get last heartbeat timestamp in nanoseconds."""
        header = self._read_header()
        return header['last_ts_ns']

    def is_producer_alive(self, timeout_ns: int = 2_000_000_000) -> bool:
        """Check if producer is still alive (heartbeat watchdog)."""
        now_ns = time.time_ns()
        last_heartbeat = self.get_last_heartbeat_ns()
        return (now_ns - last_heartbeat) < timeout_ns

    def get_producer_age_ms(self) -> float:
        """Get time since last producer write in milliseconds."""
        now_ns = time.time_ns()
        last_heartbeat = self.get_last_heartbeat_ns()
        return (now_ns - last_heartbeat) / 1_000_000

    def get_header(self) -> dict:
        """Get full header information."""
        return self._read_header()

    # =========================================================================
    # CUDA-Specific Utilities
    # =========================================================================

    @property
    def is_cuda_available(self) -> bool:
        """Check if CUDA backend is available."""
        return self._cuda_available

    @property
    def is_zero_copy_enabled(self) -> bool:
        """Check if zero-copy GPU access is enabled."""
        return self._use_zero_copy and self._device_ptr is not None

    @property
    def cuda_device(self) -> int:
        """Get the CUDA device ID being used."""
        return self._cuda_device

    def synchronize(self) -> None:
        """Synchronize CUDA device (wait for all async operations)."""
        if self._cupy_available:
            self._cp.cuda.Device(self._cuda_device).synchronize()
        elif self._torch_available:
            self._torch.cuda.synchronize(self._cuda_device)

    def get_buffer_ptr(self) -> Optional[int]:
        """Get raw pointer to pinned buffer (for advanced CUDA interop)."""
        if self._cupy_available and hasattr(self._pinned_buffer, 'ptr'):
            return self._pinned_buffer.ptr
        return None

    def get_device_ptr(self) -> Optional[int]:
        """Get GPU-mapped device pointer (for zero-copy access)."""
        return self._device_ptr

    # =========================================================================
    # Cleanup
    # =========================================================================

    def close(self) -> None:
        """Close and free CUDA resources."""
        if self._pinned_buffer is not None:
            if self._cupy_available:
                # CuPy manages deallocation
                self._pinned_buffer = None
            self._buffer_array = None
            self._device_ptr = None

        if hasattr(self, '_pinned_tensor') and self._pinned_tensor is not None:
            self._pinned_tensor = None

        self.logger.debug(f"CudaShmRingBuffer closed: {self.camera_id}")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"CudaShmRingBuffer(camera={self.camera_id}, "
            f"{self.width}x{self.height} {self.FORMAT_NAMES.get(self.frame_format, 'unknown')}, "
            f"slots={self.slot_count}, cuda={self._cuda_available}, "
            f"zero_copy={self.is_zero_copy_enabled})"
        )


# =============================================================================
# Factory Function for Automatic Backend Selection
# =============================================================================

def create_ring_buffer(
    camera_id: str,
    width: int,
    height: int,
    frame_format: int = CudaShmRingBuffer.FORMAT_BGR,
    slot_count: int = 60,
    create: bool = True,
    prefer_cuda: bool = True,
    **kwargs
) -> Union["ShmRingBuffer", CudaShmRingBuffer]:
    """Factory function to create the best available ring buffer.

    Automatically selects CUDA or CPU backend based on availability
    and user preference.

    Args:
        camera_id: Unique camera identifier
        width: Frame width in pixels
        height: Frame height in pixels
        frame_format: Frame format constant
        slot_count: Number of frame slots
        create: True for producer, False for consumer
        prefer_cuda: If True, prefer CUDA backend when available
        **kwargs: Additional arguments passed to buffer constructor

    Returns:
        CudaShmRingBuffer if CUDA available and preferred, else ShmRingBuffer

    Example:
        # Automatically uses CUDA if available
        buffer = create_ring_buffer("cam_001", 1920, 1080, create=True)

        # Force CPU backend
        buffer = create_ring_buffer("cam_001", 1920, 1080, create=True, prefer_cuda=False)
    """
    if prefer_cuda:
        try:
            return CudaShmRingBuffer(
                camera_id=camera_id,
                width=width,
                height=height,
                frame_format=frame_format,
                slot_count=slot_count,
                create=create,
                fallback_to_cpu=False,
                **kwargs
            )
        except CudaNotAvailableError:
            pass  # Fall through to CPU backend
        except Exception as e:
            logging.getLogger(__name__).warning(f"CUDA buffer creation failed: {e}")

    # Import and use CPU ShmRingBuffer
    from .shm_ring_buffer import ShmRingBuffer
    return ShmRingBuffer(
        camera_id=camera_id,
        width=width,
        height=height,
        frame_format=frame_format,
        slot_count=slot_count,
        create=create,
        **kwargs
    )

