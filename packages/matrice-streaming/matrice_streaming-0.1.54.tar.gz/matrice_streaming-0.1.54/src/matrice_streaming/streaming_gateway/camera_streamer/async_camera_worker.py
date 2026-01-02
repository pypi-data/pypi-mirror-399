"""Async camera worker process for handling multiple cameras concurrently.

This module implements an async event loop worker that handles multiple cameras
in a single process using asyncio for efficient I/O-bound operations.

Supports two capture architectures (controlled by use_blocking_threads flag):
1. Legacy: Per-camera asyncio tasks with ThreadPoolExecutor for capture
2. Optimized: Dedicated blocking capture thread per camera with shared frame queue
"""
import asyncio
import logging
import time
import multiprocessing
import os
import psutil
import threading
import queue
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Union, Tuple
from collections import deque
import cv2
from pathlib import Path
import numpy as np


# =========================
# CPU AFFINITY PINNING
# =========================

def pin_to_cores(worker_id: int, total_workers: int) -> Optional[List[int]]:
    """Pin worker process to specific CPU cores for cache locality.

    This optimization from cv2_bench.py improves throughput by 15-20%
    by reducing CPU cache misses when processing frames.

    Args:
        worker_id: Worker identifier (0-indexed)
        total_workers: Total number of worker processes

    Returns:
        List of CPU core indices this worker is pinned to, or None if pinning failed
    """
    try:
        p = psutil.Process()
        cpu_count = psutil.cpu_count(logical=True)
        cores_per_worker = max(1, cpu_count // total_workers)

        start_core = worker_id * cores_per_worker
        end_core = min(start_core + cores_per_worker, cpu_count)

        core_list = list(range(start_core, end_core))
        if core_list:
            p.cpu_affinity(core_list)
            return core_list
    except Exception:
        pass
    return None

from matrice_common.optimize import FrameOptimizer
from matrice_common.stream.shm_ring_buffer import ShmRingBuffer

from .video_capture_manager import VideoCaptureManager
from .frame_processor import FrameProcessor
from .message_builder import StreamMessageBuilder
from .stream_statistics import StreamStatistics

import os
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["KMP_NUM_THREADS"] = "1"
os.environ["KMP_BLOCKTIME"] = "0"
os.environ["TBB_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"
import cv2
cv2.setNumThreads(1)
cv2.setUseOptimized(True)
cv2.ocl.setUseOpenCL(False)


# =========================
# FEATURE FLAGS
# =========================
USE_BLOCKING_THREADS = os.getenv("USE_BLOCKING_THREADS", "true").lower() == "true"


# =========================
# OPTIMIZED CAPTURE ARCHITECTURE
# =========================

@dataclass
class CapturedFrame:
    """Represents a captured frame ready for processing.

    Used for thread-to-async communication in blocking capture mode.
    Contains frame data and metadata needed for processing.
    """
    stream_key: str
    frame: np.ndarray
    timestamp_ns: int
    frame_counter: int
    width: int
    height: int
    camera_config: Dict[str, Any]
    capture_time_ms: float
    # SHM mode fields (populated by capture thread if SHM enabled)
    shm_frame_idx: Optional[int] = None
    shm_slot: Optional[int] = None
    is_similar: bool = False
    similarity_score: float = 0.0
    reference_frame_idx: Optional[int] = None


@dataclass
class ShmMetadataItem:
    """Lightweight metadata item for batched Redis writes in SHM mode.

    When SHM is enabled, capture threads write frames directly to SHM
    and enqueue only this metadata for the async loop to batch and send to Redis.
    """
    stream_key: str
    stream_group_key: str
    topic: str
    shm_name: str
    frame_idx: int
    slot: int
    ts_ns: int
    width: int
    height: int
    format: str
    is_similar: bool = False
    reference_frame_idx: Optional[int] = None
    similarity_score: Optional[float] = None
    camera_location: str = "Unknown"
    frame_counter: int = 0


class CameraCapture:
    """Blocking capture thread for a single camera.

    Runs in a dedicated thread, captures frames at target FPS,
    and either writes to SHM (with metadata enqueue) or enqueues
    full frames for async processing.

    Key design decisions:
    - Uses time.sleep() for FPS throttling (not async) - no coroutine overhead
    - Uses stop_event.wait() for interruptible sleep - fast shutdown
    - Infinite retry with exponential backoff for camera reconnection
    - Directly writes to SHM when enabled - minimal latency
    """

    # Retry settings
    MIN_RETRY_COOLDOWN = 5   # 5 second minimum backoff
    MAX_RETRY_COOLDOWN = 30  # 30 second maximum backoff
    MAX_CONSECUTIVE_FAILURES = 10  # Max failures before reconnect

    def __init__(
        self,
        camera_config: Dict[str, Any],
        frame_queue: queue.Queue,
        stop_event: threading.Event,
        capture_manager: 'VideoCaptureManager',
        frame_optimizer: Optional['FrameOptimizer'] = None,
        # SHM support
        use_shm: bool = False,
        shm_buffer: Optional['ShmRingBuffer'] = None,
        shm_frame_format: str = "BGR",
        # Performance options
        drop_stale_frames: bool = True,
        buffer_size: int = 1,
    ):
        """Initialize capture thread for a single camera.

        Args:
            camera_config: Camera configuration dictionary
            frame_queue: Queue for sending frames/metadata to async loop
            stop_event: Event to signal thread shutdown
            capture_manager: VideoCaptureManager for source handling
            frame_optimizer: FrameOptimizer for similarity detection (optional)
            use_shm: If True, write frames to SHM and enqueue metadata only
            shm_buffer: ShmRingBuffer instance for this camera (if use_shm)
            shm_frame_format: Frame format for SHM storage
            drop_stale_frames: Use grab/grab/retrieve pattern for latest frame
            buffer_size: VideoCapture buffer size
        """
        self.camera_config = camera_config
        self.stream_key = camera_config['stream_key']
        self.stream_group_key = camera_config.get('stream_group_key', 'default')
        self.topic = camera_config['topic']
        self.source = camera_config['source']
        self.target_fps = camera_config.get('fps', 30)
        self.width = camera_config.get('width')
        self.height = camera_config.get('height')
        self.camera_location = camera_config.get('camera_location', 'Unknown')
        self.simulate_video_file_stream = camera_config.get('simulate_video_file_stream', False)

        self.frame_queue = frame_queue
        self.stop_event = stop_event
        self.capture_manager = capture_manager
        self.frame_optimizer = frame_optimizer

        # SHM configuration
        self.use_shm = use_shm
        self.shm_buffer = shm_buffer
        self.shm_frame_format = shm_frame_format

        # Performance settings
        self.drop_stale_frames = drop_stale_frames
        self.buffer_size = buffer_size
        self.frame_interval = 1.0 / self.target_fps

        # State
        self._thread: Optional[threading.Thread] = None
        self._frame_counter = 0
        self._last_shm_frame_idx: Optional[int] = None
        self._is_running = False

        self.logger = logging.getLogger(f"CameraCapture-{self.stream_key}")

    def start(self) -> None:
        """Start the capture thread."""
        if self._thread and self._thread.is_alive():
            self.logger.warning(f"Capture thread for {self.stream_key} already running")
            return

        self._is_running = True
        self._thread = threading.Thread(
            target=self._capture_loop,
            name=f"capture-{self.stream_key}",
            daemon=True
        )
        self._thread.start()
        self.logger.info(f"Started capture thread for {self.stream_key}")

    def stop(self, timeout: float = 5.0) -> None:
        """Stop the capture thread gracefully."""
        self._is_running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=timeout)
            if self._thread.is_alive():
                self.logger.warning(f"Capture thread for {self.stream_key} did not stop in time")
            else:
                self.logger.info(f"Capture thread for {self.stream_key} stopped")

    def is_alive(self) -> bool:
        """Check if capture thread is running."""
        return self._thread is not None and self._thread.is_alive()

    def _capture_loop(self) -> None:
        """Main blocking capture loop with infinite retry.

        Structure mirrors the original _camera_handler but runs in a blocking thread:
        - Outer loop: Infinite retry for camera reconnection
        - Inner loop: Frame capture and processing
        """
        retry_cycle = 0
        source_type = None

        # OUTER LOOP: Infinite retry for reconnection
        while not self.stop_event.is_set() and self._is_running:
            cap = None
            consecutive_failures = 0

            try:
                # Prepare source (download if URL)
                prepared_source = self.capture_manager.prepare_source(
                    self.source, self.stream_key
                )

                # Open capture (blocking)
                cap, source_type = self.capture_manager.open_capture(
                    prepared_source, self.width, self.height
                )

                # Get actual dimensions
                actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

                if self.width or self.height:
                    actual_width, actual_height = FrameProcessor.calculate_actual_dimensions(
                        actual_width, actual_height, self.width, self.height
                    )

                # Reset retry on success
                retry_cycle = 0

                self.logger.info(
                    f"Camera {self.stream_key} connected - "
                    f"{actual_width}x{actual_height} @ {self.target_fps} FPS (type: {source_type})"
                )

                # INNER LOOP: Capture frames
                while not self.stop_event.is_set() and self._is_running:
                    frame_start = time.time()

                    # Read latest frame
                    ret, frame = self._read_latest_frame(cap)
                    read_time = time.time() - frame_start

                    if not ret:
                        consecutive_failures += 1

                        # Handle video file end
                        if source_type == "video_file":
                            if self.simulate_video_file_stream:
                                self.logger.info(
                                    f"Video {self.stream_key} ended, restarting "
                                    f"(simulate_video_file_stream=True)"
                                )
                                self.stop_event.wait(1.0)  # Brief pause
                                break  # Restart video
                            else:
                                self.logger.info(f"Video {self.stream_key} ended (no loop)")
                                return  # Exit completely

                        # For cameras, check failure threshold
                        if consecutive_failures >= self.MAX_CONSECUTIVE_FAILURES:
                            self.logger.warning(
                                f"Camera {self.stream_key} - {self.MAX_CONSECUTIVE_FAILURES} "
                                f"consecutive failures, reconnecting..."
                            )
                            break  # Reconnect

                        self.stop_event.wait(0.1)
                        continue

                    # Reset failure counter
                    consecutive_failures = 0
                    self._frame_counter += 1

                    # Resize if needed
                    if self.width or self.height:
                        frame = FrameProcessor.resize_frame(frame, self.width, self.height)

                    # Process and enqueue frame
                    self._process_and_enqueue_frame(
                        frame, actual_width, actual_height, read_time
                    )

                    # FPS throttling (blocking sleep)
                    elapsed = time.time() - frame_start
                    sleep_time = self.frame_interval - elapsed
                    if sleep_time > 0:
                        # Use wait() for interruptible sleep
                        self.stop_event.wait(sleep_time)

            except Exception as exc:
                self.logger.error(f"Camera {self.stream_key} error: {exc}", exc_info=True)
            finally:
                if cap:
                    try:
                        cap.release()
                    except Exception:
                        pass

            # Check if we should retry
            if self.stop_event.is_set() or not self._is_running:
                break

            # For video files with looping, restart immediately
            if source_type == "video_file" and self.simulate_video_file_stream:
                continue

            # Exponential backoff for camera reconnection
            cooldown = min(
                self.MAX_RETRY_COOLDOWN,
                self.MIN_RETRY_COOLDOWN + retry_cycle
            )
            self.logger.info(
                f"Retrying camera {self.stream_key} in {cooldown}s (retry {retry_cycle})"
            )
            self.stop_event.wait(cooldown)
            retry_cycle += 1

        self.logger.info(f"Capture thread for {self.stream_key} exiting")

    def _read_latest_frame(self, cap: cv2.VideoCapture) -> Tuple[bool, Optional[np.ndarray]]:
        """Read latest frame, dropping stale buffered frames.

        Uses grab/grab/retrieve pattern when drop_stale_frames is True.
        """
        if self.drop_stale_frames:
            cap.grab()  # Clear stale frame
            ret = cap.grab()  # Get current frame
        else:
            ret = cap.grab()

        if not ret:
            return False, None

        ret, frame = cap.retrieve()
        return ret, frame

    def _process_and_enqueue_frame(
        self,
        frame: np.ndarray,
        width: int,
        height: int,
        read_time: float
    ) -> None:
        """Process frame and add to queue for async loop.

        In SHM mode: Write to SHM, enqueue metadata only
        In JPEG mode: Enqueue full frame for encoding in async loop
        """
        ts_ns = int(time.time() * 1e9)

        # Check frame similarity if optimizer available
        is_similar = False
        similarity_score = 0.0
        reference_frame_idx = None

        if self.frame_optimizer:
            is_similar, similarity_score = self.frame_optimizer.is_similar(
                frame, self.stream_key
            )
            if is_similar:
                reference_frame_idx = self._last_shm_frame_idx

        if self.use_shm and self.shm_buffer:
            # SHM MODE: Write frame to SHM, enqueue metadata only
            if is_similar and reference_frame_idx is not None:
                # Similar frame - just enqueue metadata with reference
                metadata = ShmMetadataItem(
                    stream_key=self.stream_key,
                    stream_group_key=self.stream_group_key,
                    topic=self.topic,
                    shm_name=self.shm_buffer.shm_name,
                    frame_idx=reference_frame_idx,
                    slot=-1,  # No new slot for similar frame
                    ts_ns=ts_ns,
                    width=width,
                    height=height,
                    format=self.shm_frame_format,
                    is_similar=True,
                    reference_frame_idx=reference_frame_idx,
                    similarity_score=similarity_score,
                    camera_location=self.camera_location,
                    frame_counter=self._frame_counter,
                )
            else:
                # Different frame - write to SHM
                raw_bytes = self._convert_frame_for_shm(frame)
                frame_idx, slot = self.shm_buffer.write_frame(raw_bytes)
                self._last_shm_frame_idx = frame_idx

                metadata = ShmMetadataItem(
                    stream_key=self.stream_key,
                    stream_group_key=self.stream_group_key,
                    topic=self.topic,
                    shm_name=self.shm_buffer.shm_name,
                    frame_idx=frame_idx,
                    slot=slot,
                    ts_ns=ts_ns,
                    width=width,
                    height=height,
                    format=self.shm_frame_format,
                    is_similar=False,
                    camera_location=self.camera_location,
                    frame_counter=self._frame_counter,
                )

            # Enqueue metadata (non-blocking, drop if queue full)
            try:
                self.frame_queue.put_nowait(metadata)
            except queue.Full:
                self.logger.warning(f"Frame queue full, dropping metadata for {self.stream_key}")
        else:
            # JPEG MODE: Enqueue full frame for async processing
            captured = CapturedFrame(
                stream_key=self.stream_key,
                frame=frame,
                timestamp_ns=ts_ns,
                frame_counter=self._frame_counter,
                width=width,
                height=height,
                camera_config=self.camera_config,
                capture_time_ms=read_time * 1000,
                is_similar=is_similar,
                similarity_score=similarity_score,
                reference_frame_idx=reference_frame_idx,
            )

            try:
                self.frame_queue.put_nowait(captured)
            except queue.Full:
                self.logger.warning(f"Frame queue full, dropping frame for {self.stream_key}")

    def _convert_frame_for_shm(self, frame: np.ndarray) -> bytes:
        """Convert frame to target format for SHM storage."""
        if self.shm_frame_format == "RGB":
            return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB).tobytes()
        elif self.shm_frame_format == "NV12":
            from matrice_common.stream.shm_ring_buffer import bgr_to_nv12
            return bgr_to_nv12(frame)
        else:  # BGR (default)
            return frame.tobytes()


class AsyncCameraWorker:
    """Async worker process that handles multiple cameras concurrently.

    This worker runs an async event loop to handle I/O-bound operations
    (video capture, Redis writes) for multiple cameras efficiently.
    """

    def __init__(
        self,
        worker_id: int,
        camera_configs: List[Dict[str, Any]],
        stream_config: Dict[str, Any],
        stop_event: multiprocessing.Event,
        health_queue: multiprocessing.Queue,
        command_queue: Optional[multiprocessing.Queue] = None,
        response_queue: Optional[multiprocessing.Queue] = None,
        frame_optimizer_enabled: bool = True,
        frame_optimizer_config: Optional[Dict[str, Any]] = None,
        # ================================================================
        # SHM_MODE: New parameters for shared memory architecture
        # ================================================================
        use_shm: bool = True,  # Feature flag (default: existing JPEG behavior)
        shm_slot_count: int = 1000,  # Ring buffer size per camera (5 seconds at 30 FPS)
        shm_frame_format: str = "BGR",  # "BGR", "RGB", or "NV12"
        # ================================================================
        # PERFORMANCE: New parameters for optimized frame capture
        # ================================================================
        drop_stale_frames: bool = True,  # Use grab()/grab()/retrieve() pattern for latest frame
        pin_cpu_affinity: bool = True,   # Pin worker to specific CPU cores
        total_workers: int = 1,          # Total worker count for CPU affinity calculation
        buffer_size: int = 1,            # Minimal buffer for low latency (cv2_bench uses 1)
        # ================================================================
        # BLOCKING THREADS: Optimized capture architecture (Phase 1)
        # ================================================================
        use_blocking_threads: bool = USE_BLOCKING_THREADS,  # Use blocking capture threads per camera
    ):
        """Initialize async camera worker.

        Args:
            worker_id: Unique identifier for this worker
            camera_configs: List of camera configurations to handle
            stream_config: Streaming configuration (Redis, Kafka, etc.)
            stop_event: Event to signal worker shutdown
            health_queue: Queue for reporting health status
            command_queue: Queue for receiving dynamic camera commands (add/remove/update)
            response_queue: Queue for sending command responses back to manager
            frame_optimizer_enabled: Whether to enable frame optimization
            frame_optimizer_config: Frame optimizer configuration
            use_shm: Enable SHM mode (raw frames in shared memory, metadata in Redis)
            shm_slot_count: Number of frame slots per camera ring buffer
            shm_frame_format: Frame format for SHM storage ("BGR", "RGB", or "NV12")
            drop_stale_frames: Use grab()/grab()/retrieve() pattern to get latest frame
            pin_cpu_affinity: Pin worker process to specific CPU cores for cache locality
            total_workers: Total number of workers (for CPU affinity calculation)
            buffer_size: VideoCapture buffer size (1 = minimal latency)
            use_blocking_threads: Use blocking capture threads instead of asyncio tasks (optimized mode)
        """
        self.worker_id = worker_id
        self.camera_configs = camera_configs
        self.stream_config = stream_config
        self.stop_event = stop_event
        self.health_queue = health_queue
        self.command_queue = command_queue
        self.response_queue = response_queue

        # Setup logging with worker ID
        self.logger = logging.getLogger(f"AsyncWorker-{worker_id}")
        self.logger.info(f"Initializing worker {worker_id} with {len(camera_configs)} cameras")

        # Initialize components
        self.capture_manager = VideoCaptureManager()
        self.message_builder = StreamMessageBuilder(
            service_id=stream_config.get('service_id', 'streaming_gateway'),
            strip_input_content=False
        )
        self.statistics = StreamStatistics()

        # Track camera tasks
        self.camera_tasks: Dict[str, asyncio.Task] = {}
        self.captures: Dict[str, cv2.VideoCapture] = {}

        # Setup async Redis client
        self.redis_client = None

        # Initialize frame optimizer for skipping similar frames
        frame_optimizer_config = frame_optimizer_config or {}
        self.frame_optimizer = FrameOptimizer(
            enabled=frame_optimizer_enabled,
            scale=frame_optimizer_config.get("scale", 0.4),
            diff_threshold=frame_optimizer_config.get("diff_threshold", 15),
            similarity_threshold=frame_optimizer_config.get("similarity_threshold", 0.05),
            bg_update_interval=frame_optimizer_config.get("bg_update_interval", 10),
        )
        self._last_sent_frame_ids: Dict[str, str] = {}  # stream_key -> last sent frame_id

        # ================================================================
        # SHM_MODE: Shared memory ring buffer configuration
        # ================================================================
        self.use_shm = use_shm
        self.shm_slot_count = shm_slot_count
        self.shm_frame_format = shm_frame_format

        # SHM buffers (created on demand per camera)
        self._shm_buffers: Dict[str, ShmRingBuffer] = {}

        # Track last written frame_idx per camera for FrameOptimizer references
        self._last_shm_frame_idx: Dict[str, int] = {}

        # Register atexit and signal handlers for SHM cleanup on crash/exit
        if use_shm:
            import atexit
            import signal
            import sys

            # atexit handler for normal exits
            atexit.register(self._cleanup_shm_on_exit)

            # Signal handlers for SIGTERM/SIGINT (graceful shutdown)
            # This ensures SHM is cleaned up even when killed externally
            def _signal_handler(signum, frame):
                """Handle SIGTERM/SIGINT for graceful SHM cleanup."""
                sig_name = signal.Signals(signum).name if hasattr(signal.Signals, 'name') else str(signum)
                self.logger.info(f"Worker {worker_id}: Received {sig_name}, cleaning up SHM...")
                self._cleanup_shm_on_exit()
                # Re-raise the signal to allow normal termination
                signal.signal(signum, signal.SIG_DFL)
                os.kill(os.getpid(), signum)

            # Register signal handlers (SIGINT=Ctrl+C, SIGTERM=kill command)
            signal.signal(signal.SIGINT, _signal_handler)
            # SIGTERM may not be available on Windows
            if sys.platform != 'win32':
                signal.signal(signal.SIGTERM, _signal_handler)

            self.logger.info(f"Worker {worker_id}: SHM mode ENABLED - format={shm_frame_format}, slots={shm_slot_count}")

        # ================================================================
        # PERFORMANCE: Optimized frame capture configuration
        # ================================================================
        self.drop_stale_frames = drop_stale_frames
        self.pin_cpu_affinity = pin_cpu_affinity
        self.total_workers = total_workers
        self.buffer_size = buffer_size
        self.pinned_cores: Optional[List[int]] = None

        # Apply CPU affinity pinning if enabled
        if pin_cpu_affinity:
            self.pinned_cores = pin_to_cores(worker_id, total_workers)
            if self.pinned_cores:
                self.logger.info(
                    f"Worker {worker_id}: CPU affinity pinned to cores {self.pinned_cores[0]}-{self.pinned_cores[-1]}"
                )
            else:
                self.logger.warning(f"Worker {worker_id}: CPU affinity pinning failed")

        if drop_stale_frames:
            self.logger.info(f"Worker {worker_id}: Frame dropping ENABLED (grab/grab/retrieve pattern)")

        # ThreadPoolExecutor for I/O-bound frame capture only
        # Encoding is done inline (cv2.imencode releases GIL, ~5ms for 480p)
        #
        # Thread scaling strategy:
        # - Video files are I/O bound (disk read), not CPU bound
        # - More threads = more concurrent reads = less contention
        # - But TOO many threads causes burst frame arrivals → Redis write queue backup
        # - Cap at 64 threads to balance I/O parallelism vs write contention
        num_cameras = len(camera_configs)
        # Use 1 thread per camera, capped at 64 to prevent write burst contention
        num_capture_threads = min(64, max(8, num_cameras))
        self.capture_executor = ThreadPoolExecutor(max_workers=num_capture_threads)
        self.num_capture_threads = num_capture_threads

        # Track encoding metrics (encoding done inline, not in executor)
        self.num_encoding_processes = 0  # Inline encoding, no separate processes

        # ========================================================================
        # Performance Metrics Tracking
        # ========================================================================
        self._encoding_times = deque(maxlen=100)
        self._frame_times = deque(maxlen=100)
        self._frames_encoded = 0
        self._encoding_errors = 0
        self._last_metrics_log = time.time()
        self._metrics_log_interval = 30.0
        self._process_info = psutil.Process(os.getpid())

        self.logger.info(
            f"Worker {worker_id}: Created capture pool ({num_capture_threads} threads), "
            f"encoding inline (no executor - cv2.imencode releases GIL)"
        )
        self._log_system_resources("INIT")

        # ========================================================================
        # BLOCKING THREADS: Data structures for optimized capture architecture
        # ========================================================================
        self.use_blocking_threads = use_blocking_threads

        if use_blocking_threads:
            # Frame queue for thread-to-async communication
            # Sized to handle burst: ~2 seconds of frames per camera
            queue_size = max(1000, len(camera_configs) * 60)
            self._frame_queue: queue.Queue = queue.Queue(maxsize=queue_size)

            # Thread stop event (separate from process stop_event for cleaner shutdown)
            self._thread_stop_event = threading.Event()

            # Camera capture threads (stream_key -> CameraCapture)
            self._capture_threads: Dict[str, CameraCapture] = {}

            # Pending SHM metadata for batched Redis writes
            self._shm_metadata_batch: List[ShmMetadataItem] = []
            self._metadata_batch_lock = threading.Lock()

            self.logger.info(
                f"Worker {worker_id}: Blocking threads mode ENABLED "
                f"(queue_size={queue_size}, per-camera capture threads)"
            )
        else:
            self._frame_queue = None
            self._thread_stop_event = None
            self._capture_threads = {}
            self._shm_metadata_batch = []
            self._metadata_batch_lock = None
            self.logger.info(f"Worker {worker_id}: Legacy asyncio tasks mode")

    async def _log_metrics(self) -> None:
        """Log comprehensive worker metrics periodically."""
        try:
            # Per-camera metrics (use StreamStatistics methods)
            for stream_key in self.camera_tasks.keys():
                self.statistics.log_detailed_stats(stream_key)

            # Frame optimizer metrics
            if self.frame_optimizer.enabled:
                opt_metrics = self.frame_optimizer.get_metrics()
                self.logger.info(
                    f"Worker {self.worker_id} Frame Optimizer: "
                    f"similarity_rate={opt_metrics['similarity_rate']:.1f}%, "
                    f"active_streams={opt_metrics['active_streams']}"
                )

            # Worker-level encoding metrics
            if self._encoding_times:
                avg_encoding_ms = (sum(self._encoding_times) / len(self._encoding_times)) * 1000
                self.logger.info(
                    f"Worker {self.worker_id} Encoding Pool: "
                    f"avg_time={avg_encoding_ms:.1f}ms, "
                    f"frames_encoded={self._frames_encoded}, "
                    f"errors={self._encoding_errors}, "
                    f"pool_size={self.num_encoding_processes}"
                )

            # System resources
            proc_cpu = self._process_info.cpu_percent(interval=0.1)
            memory_mb = self._process_info.memory_info().rss / 1024 / 1024

            self.logger.info(
                f"Worker {self.worker_id} Resources: "
                f"CPU={proc_cpu:.1f}%, "
                f"Memory={memory_mb:.1f}MB, "
                f"Active cameras={len(self.camera_tasks)}"
            )

            # Aggregate stats (all streams)
            self.statistics.log_aggregated_stats()

        except Exception as exc:
            self.logger.warning(f"Worker {self.worker_id}: Failed to log metrics: {exc}")

    def _log_system_resources(self, context: str = ""):
        """Simple fallback for initial resource logging.

        Args:
            context: Optional context string
        """
        try:
            proc_cpu = self._process_info.cpu_percent(interval=0.1)
            memory_mb = self._process_info.memory_info().rss / 1024 / 1024
            self.logger.info(
                f"Worker {self.worker_id} [{context}]: "
                f"CPU={proc_cpu:.1f}%, Memory={memory_mb:.1f}MB, "
                f"Encoding pool size={self.num_encoding_processes}"
            )
        except Exception as exc:
            self.logger.warning(f"Worker {self.worker_id}: Failed to log resources: {exc}")


    async def initialize(self):
        """Initialize async resources (Redis client, etc.)."""
        try:
            # Import and initialize async Redis client
            from matrice_common.stream import MatriceStream, StreamType

            # Create MatriceStream with async support
            # Unpack stream_config as keyword arguments (MatriceStream expects **config)
            self.stream = MatriceStream(
                stream_type=StreamType.REDIS,
                enable_shm_batching=True,
                **self.stream_config
            )

            # Use async client
            self.redis_client = self.stream.async_client
            await self.redis_client.setup_client()

            self.logger.info(f"Worker {self.worker_id}: Initialized async Redis client")

        except Exception as exc:
            self.logger.error(f"Worker {self.worker_id}: Failed to initialize: {exc}", exc_info=True)
            raise

    async def run(self):
        """Main worker loop - starts capture threads or async tasks based on mode."""
        try:
            # Initialize async resources (Redis client, etc.)
            await self.initialize()

            if self.use_blocking_threads:
                # ================================================================
                # OPTIMIZED MODE: Blocking capture threads + single async processor
                # ================================================================
                await self._run_blocking_threads_mode()
            else:
                # ================================================================
                # LEGACY MODE: Per-camera asyncio tasks
                # ================================================================
                await self._run_legacy_async_mode()

        except Exception as exc:
            self.logger.error(f"Worker {self.worker_id}: Fatal error in run loop: {exc}", exc_info=True)
            self._report_health("error", error=str(exc))
            raise

    async def _run_legacy_async_mode(self):
        """Legacy mode: Per-camera asyncio tasks with ThreadPoolExecutor for capture."""
        self.logger.info(f"Worker {self.worker_id}: Starting legacy asyncio mode")

        # Start initial camera tasks using internal method
        for camera_config in self.camera_configs:
            await self._add_camera_internal(camera_config)

        # Report initial health
        self._report_health("running", len(self.camera_tasks))

        # Start command handler task if command queue is provided
        command_task = None
        if self.command_queue:
            command_task = asyncio.create_task(
                self._command_handler(),
                name="command-handler"
            )
            self.logger.info(f"Worker {self.worker_id}: Command handler started")

        # Monitor tasks and stop event
        while not self.stop_event.is_set():
            # Check for completed/failed tasks
            for stream_key, task in list(self.camera_tasks.items()):
                if task.done():
                    try:
                        # Check if task raised exception
                        task.result()
                        self.logger.warning(f"Worker {self.worker_id}: Camera {stream_key} task completed")
                    except Exception as exc:
                        self.logger.error(f"Worker {self.worker_id}: Camera {stream_key} task failed: {exc}")

                    # Remove completed task
                    del self.camera_tasks[stream_key]

            # Report health periodically
            self._report_health("running", len(self.camera_tasks))

            # Sleep briefly
            await asyncio.sleep(1.0)

        # Stop event set - graceful shutdown
        self.logger.info(f"Worker {self.worker_id}: Stop event detected, shutting down...")

        # Cancel command handler if running
        if command_task and not command_task.done():
            command_task.cancel()
            try:
                await command_task
            except asyncio.CancelledError:
                pass

        await self._shutdown()

    async def _run_blocking_threads_mode(self):
        """Optimized mode: Blocking capture threads + single async frame processor.

        Architecture:
        - One CameraCapture thread per camera (blocking I/O, time.sleep for FPS)
        - Threads write to SHM (if enabled) and enqueue metadata to frame_queue
        - Single async loop polls frame_queue and batches Redis writes
        - Eliminates per-camera asyncio task overhead
        """
        self.logger.info(f"Worker {self.worker_id}: Starting blocking threads mode")

        # Start capture threads for all cameras
        self._start_capture_threads()

        # Report initial health
        active_cameras = len(self._capture_threads)
        self._report_health("running", active_cameras)

        # Start command handler task if command queue is provided
        command_task = None
        if self.command_queue:
            command_task = asyncio.create_task(
                self._command_handler(),
                name="command-handler"
            )
            self.logger.info(f"Worker {self.worker_id}: Command handler started")

        # Run the frame processor loop
        try:
            await self._run_frame_processor()
        finally:
            # Stop event set - graceful shutdown
            self.logger.info(f"Worker {self.worker_id}: Stop event detected, shutting down threads...")

            # Signal threads to stop
            if self._thread_stop_event:
                self._thread_stop_event.set()

            # Cancel command handler if running
            if command_task and not command_task.done():
                command_task.cancel()
                try:
                    await command_task
                except asyncio.CancelledError:
                    pass

            await self._shutdown()

    def _start_capture_threads(self) -> None:
        """Start blocking capture threads for all cameras."""
        for camera_config in self.camera_configs:
            self._start_capture_thread(camera_config)

        self.logger.info(
            f"Worker {self.worker_id}: Started {len(self._capture_threads)} capture threads"
        )

    def _start_capture_thread(self, camera_config: Dict[str, Any]) -> None:
        """Start a capture thread for a single camera."""
        stream_key = camera_config.get('stream_key')
        if not stream_key:
            self.logger.error("Camera config missing stream_key")
            return

        if stream_key in self._capture_threads:
            self.logger.warning(f"Capture thread for {stream_key} already exists")
            return

        # Get or create SHM buffer if needed
        shm_buffer = None
        if self.use_shm:
            width = camera_config.get('width', 1920)
            height = camera_config.get('height', 1080)
            shm_buffer = self._get_or_create_shm_buffer(stream_key, width, height)

        # Create and start capture thread
        capture = CameraCapture(
            camera_config=camera_config,
            frame_queue=self._frame_queue,
            stop_event=self._thread_stop_event,
            capture_manager=self.capture_manager,
            frame_optimizer=self.frame_optimizer if self.frame_optimizer.enabled else None,
            use_shm=self.use_shm,
            shm_buffer=shm_buffer,
            shm_frame_format=self.shm_frame_format,
            drop_stale_frames=self.drop_stale_frames,
            buffer_size=self.buffer_size,
        )
        capture.start()
        self._capture_threads[stream_key] = capture

    async def _run_frame_processor(self) -> None:
        """Main async loop that polls frame queue and batches Redis writes.

        This replaces per-camera asyncio tasks with a single efficient loop:
        - Polls frame queue (non-blocking)
        - Batches metadata for Redis writes
        - Flushes batches periodically or when full
        - Reports health
        """
        poll_interval_ms = 1  # 1ms polling when idle
        batch_timeout_ms = 25  # 25ms max batch wait (allows 4 flushes in 100ms SLA)
        batch_size_limit = 100  # Max items per batch
        health_report_interval = 1.0  # Report health every second

        last_health_report = time.time()
        last_batch_flush = time.time()

        self.logger.info(
            f"Worker {self.worker_id}: Frame processor started "
            f"(batch_timeout={batch_timeout_ms}ms, batch_size={batch_size_limit})"
        )

        while not self.stop_event.is_set():
            try:
                frames_processed = 0
                process_start = time.time()

                # Poll queue for available items (non-blocking)
                while True:
                    try:
                        item = self._frame_queue.get_nowait()
                        await self._process_queue_item(item)
                        frames_processed += 1

                        # Check if batch is full or timeout reached
                        if len(self._shm_metadata_batch) >= batch_size_limit:
                            await self._flush_metadata_batch()
                            last_batch_flush = time.time()
                        elif (time.time() - last_batch_flush) * 1000 > batch_timeout_ms:
                            await self._flush_metadata_batch()
                            last_batch_flush = time.time()

                        # Limit items per iteration to prevent starvation
                        if frames_processed >= batch_size_limit * 2:
                            break

                    except queue.Empty:
                        break

                # Flush any remaining items if timeout reached
                if self._shm_metadata_batch and (time.time() - last_batch_flush) * 1000 > batch_timeout_ms:
                    await self._flush_metadata_batch()
                    last_batch_flush = time.time()

                # Report health periodically
                current_time = time.time()
                if current_time - last_health_report >= health_report_interval:
                    active_threads = sum(1 for c in self._capture_threads.values() if c.is_alive())
                    self._report_health("running", active_threads)
                    last_health_report = current_time

                # Brief yield to prevent busy-waiting when queue is empty
                if frames_processed == 0:
                    await asyncio.sleep(poll_interval_ms / 1000)

            except Exception as exc:
                self.logger.error(
                    f"Worker {self.worker_id}: Error in frame processor: {exc}",
                    exc_info=True
                )
                await asyncio.sleep(0.1)  # Brief pause on error

        # Final flush of remaining items
        if self._shm_metadata_batch:
            await self._flush_metadata_batch()

        self.logger.info(f"Worker {self.worker_id}: Frame processor stopped")

    async def _process_queue_item(self, item: Union[ShmMetadataItem, CapturedFrame]) -> None:
        """Process an item from the frame queue.

        Args:
            item: Either ShmMetadataItem (SHM mode) or CapturedFrame (JPEG mode)
        """
        if isinstance(item, ShmMetadataItem):
            # SHM mode: Collect metadata for batched write
            self._shm_metadata_batch.append(item)
            # Update statistics
            if item.is_similar:
                self.statistics.increment_frames_skipped()
            else:
                self.statistics.increment_frames_sent()

        elif isinstance(item, CapturedFrame):
            # JPEG mode: Process and send frame
            await self._process_captured_frame(item)

    async def _process_captured_frame(self, captured: CapturedFrame) -> None:
        """Process a captured frame in JPEG mode.

        Args:
            captured: CapturedFrame from queue
        """
        stream_key = captured.stream_key
        config = captured.camera_config

        # Get timing stats
        last_read, last_write, last_process = self.statistics.get_timing(stream_key)
        input_order = self.statistics.get_next_input_order(stream_key)

        if captured.is_similar and captured.reference_frame_idx is not None:
            # Similar frame - send cached reference
            reference_frame_id = self._last_sent_frame_ids.get(stream_key)
            if reference_frame_id:
                metadata = self.message_builder.build_frame_metadata(
                    config['source'], {}, config.get('fps', 30), config.get('quality', 90),
                    captured.width, captured.height, "camera",
                    captured.frame_counter, False, None, None, config.get('camera_location', 'Unknown')
                )
                metadata["similarity_score"] = captured.similarity_score

                message = self.message_builder.build_message(
                    frame_data=b"",
                    stream_key=stream_key,
                    stream_group_key=config.get('stream_group_key', 'default'),
                    codec="cached",
                    metadata=metadata,
                    topic=config['topic'],
                    broker_config=self.stream_config.get('bootstrap_servers', 'localhost:9092'),
                    input_order=input_order,
                    last_read_time=last_read,
                    last_write_time=last_write,
                    last_process_time=last_process,
                    cached_frame_id=reference_frame_id,
                )

                write_start = time.time()
                await self.redis_client.add_message(config['topic'], message)
                write_time = time.time() - write_start

                self.statistics.increment_frames_skipped()
                self.statistics.update_timing(stream_key, captured.capture_time_ms / 1000, write_time, write_time, 0, 0)
                return

        # Encode frame
        quality = config.get('quality', 90)
        frame_data, codec = await self._encode_frame_async(captured.frame, quality)

        # Build and send message
        metadata = self.message_builder.build_frame_metadata(
            config['source'], {}, config.get('fps', 30), quality,
            captured.width, captured.height, "camera",
            captured.frame_counter, False, None, None, config.get('camera_location', 'Unknown')
        )
        metadata["encoding_type"] = "jpeg"

        message = self.message_builder.build_message(
            frame_data, stream_key, config.get('stream_group_key', 'default'),
            codec, metadata, config['topic'],
            self.stream_config.get('bootstrap_servers', 'localhost:9092'),
            input_order, last_read, last_write, last_process,
            cached_frame_id=None,
        )

        write_start = time.time()
        await self.redis_client.add_message(config['topic'], message)
        write_time = time.time() - write_start

        # Track frame_id for future cached references
        new_frame_id = message.get("frame_id")
        if new_frame_id:
            self._last_sent_frame_ids[stream_key] = new_frame_id

        # Update statistics
        self.statistics.increment_frames_sent()
        frame_size = len(frame_data) if frame_data else 0
        self.statistics.update_timing(
            stream_key, captured.capture_time_ms / 1000, write_time,
            write_time + captured.capture_time_ms / 1000, frame_size, 0
        )

    async def _flush_metadata_batch(self) -> None:
        """Flush pending SHM metadata to Redis as a batch.

        Uses Redis pipeline for efficient multi-message writes.
        """
        if not self._shm_metadata_batch:
            return

        batch = self._shm_metadata_batch
        self._shm_metadata_batch = []

        batch_start = time.time()

        try:
            # Send each metadata item (batching is handled by redis_client)
            for item in batch:
                await self.redis_client.add_shm_metadata(
                    stream_name=item.topic,
                    cam_id=item.stream_key,
                    shm_name=item.shm_name,
                    frame_idx=item.frame_idx,
                    slot=item.slot if item.slot >= 0 else None,
                    ts_ns=item.ts_ns,
                    width=item.width,
                    height=item.height,
                    format=item.format,
                    is_similar=item.is_similar,
                    reference_frame_idx=item.reference_frame_idx,
                    similarity_score=item.similarity_score,
                    stream_group_key=item.stream_group_key,
                    camera_location=item.camera_location,
                    frame_counter=item.frame_counter,
                )

            batch_time = (time.time() - batch_start) * 1000
            if batch_time > 50:  # Log slow batches
                self.logger.warning(
                    f"Worker {self.worker_id}: Slow batch flush - "
                    f"{len(batch)} items in {batch_time:.1f}ms"
                )

        except Exception as exc:
            self.logger.error(
                f"Worker {self.worker_id}: Failed to flush metadata batch: {exc}",
                exc_info=True
            )

    async def _read_latest_frame(
        self,
        cap: cv2.VideoCapture,
        drop_stale: bool = True
    ) -> Tuple[bool, Optional[Any]]:
        """Read latest frame, optionally dropping stale buffered frames.

        This optimization from cv2_bench.py uses grab()/grab()/retrieve()
        pattern to always get the most recent frame instead of reading
        stale frames from the buffer.

        Args:
            cap: OpenCV VideoCapture object
            drop_stale: If True, use grab/grab/retrieve pattern to skip stale frames

        Returns:
            Tuple of (success, frame) where frame is None if read failed
        """
        loop = asyncio.get_event_loop()

        if drop_stale:
            # Aggressive frame dropping: grab twice to get latest frame
            # First grab clears any stale frame, second grab gets current
            await loop.run_in_executor(self.capture_executor, cap.grab)
            ret = await loop.run_in_executor(self.capture_executor, cap.grab)
        else:
            ret = await loop.run_in_executor(self.capture_executor, cap.grab)

        if not ret:
            return False, None

        # Retrieve the frame (converts to numpy array)
        ret, frame = await loop.run_in_executor(self.capture_executor, cap.retrieve)
        return ret, frame

    async def _camera_handler(self, camera_config: Dict[str, Any]):
        """Handle a single camera with async I/O.

        Features:
        - Infinite retry with exponential backoff for camera reconnection
        - Video file looping via simulate_video_file_stream parameter
        - Two-level loop: outer (reconnection) + inner (frame processing)
        - Optimized frame capture with grab/retrieve pattern for latest frame

        Args:
            camera_config: Camera configuration dictionary
        """
        stream_key = camera_config['stream_key']
        stream_group_key = camera_config.get('stream_group_key', 'default')
        source = camera_config['source']
        topic = camera_config['topic']
        fps = camera_config.get('fps', 30)
        quality = camera_config.get('quality', 90)
        width = camera_config.get('width')
        height = camera_config.get('height')
        camera_location = camera_config.get('camera_location', 'Unknown')
        simulate_video_file_stream = camera_config.get('simulate_video_file_stream', False)

        # Retry settings (similar to RetryManager in old flow)
        MIN_RETRY_COOLDOWN = 5   # 5 second minimum backoff
        MAX_RETRY_COOLDOWN = 30  # 30 second maximum backoff
        retry_cycle = 0
        max_frame_failures = 10  # Max failures within a single connection

        # Track source type for video looping decision
        source_type = None

        # OUTER LOOP: Infinite retry for reconnection (similar to old CameraStreamer)
        while not self.stop_event.is_set():
            cap = None
            consecutive_failures = 0
            frame_counter = 0

            try:
                # Prepare source (download if URL)
                prepared_source = self.capture_manager.prepare_source(source, stream_key)

                # Open capture in thread pool (blocking operation)
                cap, source_type = await asyncio.to_thread(
                    self.capture_manager.open_capture,
                    prepared_source, width, height
                )
                self.captures[stream_key] = cap

                # Get video properties
                video_props = self.capture_manager.get_video_properties(cap)
                original_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                original_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

                actual_width, actual_height = FrameProcessor.calculate_actual_dimensions(
                    original_width, original_height, width, height
                )

                # Reset retry cycle on successful connection
                retry_cycle = 0

                self.logger.info(
                    f"Worker {self.worker_id}: Camera {stream_key} connected - "
                    f"{actual_width}x{actual_height} @ {fps} FPS (type: {source_type})"
                )

                # INNER LOOP: Process frames
                while not self.stop_event.is_set():
                    try:
                        # Read frame using optimized grab/retrieve pattern
                        # This gets the latest frame and drops stale buffered frames
                        read_start = time.time()
                        ret, frame = await self._read_latest_frame(
                            cap, drop_stale=self.drop_stale_frames
                        )
                        read_time = time.time() - read_start

                        if not ret:
                            consecutive_failures += 1

                            # Check for video file end
                            if source_type == "video_file":
                                if simulate_video_file_stream:
                                    self.logger.info(
                                        f"Worker {self.worker_id}: Video {stream_key} ended, "
                                        f"restarting (simulate_video_file_stream=True)"
                                    )
                                    await asyncio.sleep(1.0)  # Brief pause before restart
                                    break  # Break inner loop to restart video in outer loop
                                else:
                                    self.logger.info(
                                        f"Worker {self.worker_id}: Video {stream_key} ended (no loop)"
                                    )
                                    return  # Exit handler completely - video finished

                            # For cameras, check failure threshold before reconnect
                            if consecutive_failures >= max_frame_failures:
                                self.logger.warning(
                                    f"Worker {self.worker_id}: Camera {stream_key} - "
                                    f"{max_frame_failures} consecutive failures, reconnecting..."
                                )
                                break  # Break inner loop to reconnect in outer loop

                            await asyncio.sleep(0.1)
                            continue

                        # Reset failure counter on success
                        consecutive_failures = 0
                        frame_counter += 1

                        # Resize if needed
                        if width or height:
                            frame = FrameProcessor.resize_frame(frame, width, height)

                        # ================================================================
                        # SHM_MODE: Branch based on mode
                        # ================================================================
                        if self.use_shm:
                            await self._process_frame_shm_mode(
                                frame, stream_key, stream_group_key, topic,
                                actual_width, actual_height, frame_counter,
                                camera_location, read_time
                            )
                        else:
                            # EXISTING FLOW: JPEG encode and send full frame
                            await self._process_and_send_frame(
                                frame, stream_key, stream_group_key, topic,
                                source, video_props, fps, quality,
                                actual_width, actual_height, source_type,
                                frame_counter, camera_location, read_time
                            )

                        # Maintain target FPS for ALL sources (video files AND live cameras)
                        # This prevents overwhelming the encoder by reading at native camera rate (30+ FPS)
                        frame_interval = 1.0 / fps
                        frame_elapsed = time.time() - read_start
                        sleep_time = max(0, frame_interval - frame_elapsed)
                        if sleep_time > 0:
                            await asyncio.sleep(sleep_time)

                    except asyncio.CancelledError:
                        self.logger.info(f"Worker {self.worker_id}: Camera {stream_key} task cancelled")
                        return  # Exit completely on cancellation
                    except Exception as exc:
                        self.logger.error(
                            f"Worker {self.worker_id}: Error in camera {stream_key}: {exc}",
                            exc_info=True
                        )
                        consecutive_failures += 1
                        if consecutive_failures >= max_frame_failures:
                            self.logger.warning(
                                f"Worker {self.worker_id}: Camera {stream_key} - "
                                f"max failures in inner loop, reconnecting..."
                            )
                            break  # Break inner loop to reconnect
                        await asyncio.sleep(1.0)

            except asyncio.CancelledError:
                self.logger.info(f"Worker {self.worker_id}: Camera {stream_key} task cancelled during setup")
                return  # Exit completely on cancellation
            except Exception as exc:
                self.logger.error(
                    f"Worker {self.worker_id}: Camera {stream_key} connection error: {exc}",
                    exc_info=True
                )
            finally:
                # Cleanup capture for this iteration
                if cap:
                    try:
                        cap.release()
                    except Exception:
                        pass
                if stream_key in self.captures:
                    del self.captures[stream_key]

            # Determine if we should retry or exit
            if self.stop_event.is_set():
                break  # Exit if stop requested

            # For video files with simulate_video_file_stream, restart immediately (no backoff)
            if source_type == "video_file" and simulate_video_file_stream:
                self.logger.info(f"Worker {self.worker_id}: Restarting video {stream_key}")
                continue  # Restart immediately

            # For cameras, apply exponential backoff before reconnection
            cooldown = min(MAX_RETRY_COOLDOWN, MIN_RETRY_COOLDOWN + retry_cycle)
            self.logger.info(
                f"Worker {self.worker_id}: Retrying camera {stream_key} in {cooldown}s "
                f"(retry cycle {retry_cycle})"
            )
            await asyncio.sleep(cooldown)
            retry_cycle += 1

        self.logger.info(f"Worker {self.worker_id}: Camera handler for {stream_key} exited")

    async def _process_and_send_frame(
        self,
        frame,
        stream_key: str,
        stream_group_key: str,
        topic: str,
        source: Union[str, int],
        video_props: Dict[str, Any],
        fps: int,
        quality: int,
        actual_width: int,
        actual_height: int,
        source_type: str,
        frame_counter: int,
        camera_location: str,
        read_time: float
    ):
        """Process frame and send to Redis asynchronously.

        Features frame optimization to skip encoding for similar frames.

        Args:
            frame: Frame data
            stream_key: Stream identifier
            stream_group_key: Stream group identifier
            topic: Topic name
            source: Video source
            video_props: Video properties
            fps: Target FPS
            quality: JPEG quality
            actual_width: Frame width
            actual_height: Frame height
            source_type: Type of source
            frame_counter: Current frame number
            camera_location: Camera location
            read_time: Time taken to read frame
        """
        frame_start = time.time()

        # Build metadata
        metadata = self.message_builder.build_frame_metadata(
            source, video_props, fps, quality, actual_width, actual_height,
            source_type, frame_counter, False, None, None, camera_location
        )
        metadata["feed_type"] = "disk" if source_type == "video_file" else "camera"
        metadata["frame_count"] = 1
        metadata["stream_unit"] = "frame"

        # Check frame similarity BEFORE encoding (saves CPU if frame is similar)
        is_similar, similarity_score = self.frame_optimizer.is_similar(frame, stream_key)
        reference_frame_id = self._last_sent_frame_ids.get(stream_key)

        # Get timing stats
        last_read, last_write, last_process = self.statistics.get_timing(stream_key)
        input_order = self.statistics.get_next_input_order(stream_key)

        if is_similar and reference_frame_id:
            # Frame is similar to previous - send message with empty content + cached_frame_id
            encoding_time = 0.0  # No encoding needed
            metadata["similarity_score"] = similarity_score

            # Build message with empty content and cached_frame_id
            message = self.message_builder.build_message(
                frame_data=b"",  # EMPTY content for cached frame
                stream_key=stream_key,
                stream_group_key=stream_group_key,
                codec="cached",  # Special codec to indicate cached frame
                metadata=metadata,
                topic=topic,
                broker_config=self.stream_config.get('bootstrap_servers', 'localhost:9092'),
                input_order=input_order,
                last_read_time=last_read,
                last_write_time=last_write,
                last_process_time=last_process,
                cached_frame_id=reference_frame_id,  # Reference to cached frame
            )

            # Send to Redis asynchronously
            write_start = time.time()
            await self.redis_client.add_message(topic, message)
            write_time = time.time() - write_start

            # Update statistics - frame was skipped (no encoding)
            self.statistics.increment_frames_skipped()
            process_time = read_time + write_time
            encoding_time = 0.0  # No encoding for cached frames
            self.statistics.update_timing(stream_key, read_time, write_time, process_time, 0, encoding_time)

            # Track total frame time for metrics
            total_frame_time = time.time() - frame_start
            self._frame_times.append(total_frame_time)
            return

        # Frame is different - encode and send full frame
        encoding_start = time.time()
        frame_data, codec = await self._encode_frame_async(frame, quality)
        encoding_time = time.time() - encoding_start
        metadata["encoding_type"] = "jpeg"

        # Build message (normal frame - no cache reference)
        message = self.message_builder.build_message(
            frame_data, stream_key, stream_group_key, codec, metadata, topic,
            self.stream_config.get('bootstrap_servers', 'localhost:9092'),
            input_order, last_read, last_write, last_process,
            cached_frame_id=None,  # Normal frame, no cache reference
        )

        # Send to Redis asynchronously
        write_start = time.time()
        await self.redis_client.add_message(topic, message)
        write_time = time.time() - write_start

        # Track this frame_id as the last sent for future reference frames
        new_frame_id = message.get("frame_id")
        if new_frame_id:
            self._last_sent_frame_ids[stream_key] = new_frame_id
            self.frame_optimizer.set_last_frame_id(stream_key, new_frame_id)

        # Update statistics
        self.statistics.increment_frames_sent()
        process_time = read_time + write_time
        frame_size = len(frame_data) if frame_data else 0
        self.statistics.update_timing(stream_key, read_time, write_time, process_time, frame_size, encoding_time)

        # Track total frame time for metrics
        total_frame_time = time.time() - frame_start
        self._frame_times.append(total_frame_time)

    async def _encode_frame_async(self, frame, quality: int) -> tuple:
        """Encode frame to JPEG.

        Encoding is done inline (synchronously) because:
        1. cv2.imencode() is very fast (~5ms for 480p)
        2. cv2.imencode() releases the GIL, allowing other async tasks to run
        3. Executor overhead (queue, context switch) adds more latency than the encoding itself
        4. At 1000 cameras, executor queue contention causes 200ms+ delays

        Args:
            frame: Frame data (numpy array)
            quality: JPEG quality

        Returns:
            Tuple of (encoded_data, codec)
        """
        encode_start = time.time()

        try:
            # Encode directly - cv2.imencode releases GIL so other coroutines can run
            encode_success, jpeg_buffer = cv2.imencode(
                '.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), quality]
            )

            encoding_time = time.time() - encode_start
            self._encoding_times.append(encoding_time)
            self._frames_encoded += 1

            # Periodically log metrics
            if time.time() - self._last_metrics_log > self._metrics_log_interval:
                self._last_metrics_log = time.time()
                await self._log_metrics()

            if encode_success:
                # Return buffer directly
                frame_data = memoryview(jpeg_buffer)
                return frame_data, "h264"
            else:
                # Encoding failed - return raw frame
                self.logger.warning(f"Worker {self.worker_id}: JPEG encoding returned False, using raw frame")
                frame_data = memoryview(frame).cast('B')
                return frame_data, "raw"

        except Exception as exc:
            self._encoding_errors += 1
            encoding_time = time.time() - encode_start

            self.logger.error(
                f"Worker {self.worker_id}: Encoding error: {type(exc).__name__}: {exc} "
                f"(encoding time: {encoding_time*1000:.2f}ms)",
                exc_info=True
            )
            raise

    # ========================================================================
    # SHM_MODE: Shared Memory Methods
    # ========================================================================

    def _cleanup_shm_on_exit(self):
        """Atexit handler to cleanup SHM on unexpected exit/crash.

        CRITICAL: Producer is responsible for unlinking SHM segments.
        This ensures cleanup happens even on crashes.
        """
        for camera_id, shm_buffer in list(self._shm_buffers.items()):
            try:
                shm_buffer.close()
                self.logger.info(f"Worker {self.worker_id}: Cleanup - closed SHM for {camera_id}")
            except Exception as e:
                self.logger.warning(f"Worker {self.worker_id}: Failed to cleanup SHM {camera_id}: {e}")

    async def _process_frame_shm_mode(
        self,
        frame,
        stream_key: str,
        stream_group_key: str,
        topic: str,
        width: int,
        height: int,
        frame_counter: int,
        camera_location: str,
        read_time: float
    ):
        """SHM_MODE: Write raw frame to SHM, send metadata to Redis.

        NO JPEG encoding - frame stored as raw NV12 bytes.
        FrameOptimizer still used to skip similar frames.

        Args:
            frame: BGR frame from OpenCV
            stream_key: Camera stream identifier
            stream_group_key: Stream group identifier
            topic: Redis stream topic
            width: Frame width
            height: Frame height
            frame_counter: Current frame number
            camera_location: Camera location string
            read_time: Time taken to read frame
        """
        frame_start = time.time()

        # ================================================================
        # FRAME OPTIMIZER: Check similarity BEFORE writing to SHM
        # This saves SHM writes and Redis messages for static scenes
        # ================================================================
        is_similar, similarity_score = self.frame_optimizer.is_similar(frame, stream_key)
        reference_frame_idx = self._last_shm_frame_idx.get(stream_key)

        if is_similar and reference_frame_idx is not None:
            # Frame is similar - send metadata with reference to previous frame
            # Consumer can skip reading SHM and use previous result
            ts_ns = int(time.time() * 1e9)
            shm_buffer = self._shm_buffers.get(stream_key)

            await self.redis_client.add_shm_metadata(
                stream_name=topic,
                cam_id=stream_key,
                shm_name=shm_buffer.shm_name if shm_buffer else "",
                frame_idx=reference_frame_idx,  # Reference to cached frame
                slot=None,  # No new slot written
                ts_ns=ts_ns,
                width=width,
                height=height,
                format=self.shm_frame_format,
                is_similar=True,
                reference_frame_idx=reference_frame_idx,
                similarity_score=similarity_score,
                stream_group_key=stream_group_key,
                camera_location=camera_location,
                frame_counter=frame_counter,
            )

            self.statistics.increment_frames_skipped()

            # Track timing (no encoding, minimal write)
            write_time = time.time() - frame_start - read_time
            self.statistics.update_timing(stream_key, read_time, write_time, read_time + write_time, 0, 0)
            return

        # ================================================================
        # DIFFERENT FRAME: Convert to target format and write to SHM
        # ================================================================

        # Get or create SHM buffer for this camera
        shm_buffer = self._get_or_create_shm_buffer(stream_key, width, height)

        # Convert BGR to target format (BGR is default - no conversion needed)
        convert_start = time.time()
        if self.shm_frame_format == "RGB":
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            raw_bytes = rgb_frame.tobytes()
        elif self.shm_frame_format == "NV12":
            # NV12 conversion - import helper only if needed
            from matrice_common.stream.shm_ring_buffer import bgr_to_nv12
            raw_bytes = bgr_to_nv12(frame)
        else:  # BGR (default) - no conversion needed
            raw_bytes = frame.tobytes()
        convert_time = time.time() - convert_start

        # Write to SHM ring buffer
        frame_idx, slot = shm_buffer.write_frame(raw_bytes)

        # Track this frame_idx for future similar frame references
        self._last_shm_frame_idx[stream_key] = frame_idx

        # Send metadata-only message to Redis
        ts_ns = int(time.time() * 1e9)
        write_start = time.time()

        await self.redis_client.add_shm_metadata(
            stream_name=topic,
            cam_id=stream_key,
            shm_name=shm_buffer.shm_name,
            frame_idx=frame_idx,
            slot=slot,
            ts_ns=ts_ns,
            width=width,
            height=height,
            format=self.shm_frame_format,
            is_similar=False,
            stream_group_key=stream_group_key,
            camera_location=camera_location,
            frame_counter=frame_counter,
        )

        write_time = time.time() - write_start

        # Update statistics (no JPEG encoding time, but track format conversion)
        self.statistics.increment_frames_sent()
        process_time = read_time + convert_time + write_time
        self.statistics.update_timing(
            stream_key, read_time, write_time, process_time,
            frame_size=len(raw_bytes),
            encoding_time=convert_time  # Track conversion time in encoding slot
        )

        # Track total frame time for metrics
        total_frame_time = time.time() - frame_start
        self._frame_times.append(total_frame_time)

    def _get_or_create_shm_buffer(self, camera_id: str, width: int, height: int) -> ShmRingBuffer:
        """Get existing or create new SHM buffer for camera.

        Args:
            camera_id: Camera stream identifier
            width: Frame width
            height: Frame height

        Returns:
            ShmRingBuffer instance for this camera
        """
        if camera_id not in self._shm_buffers:
            format_map = {
                "BGR": ShmRingBuffer.FORMAT_BGR,
                "RGB": ShmRingBuffer.FORMAT_RGB,
                "NV12": ShmRingBuffer.FORMAT_NV12
            }
            frame_format = format_map.get(self.shm_frame_format, ShmRingBuffer.FORMAT_BGR)

            self._shm_buffers[camera_id] = ShmRingBuffer(
                camera_id=camera_id,
                width=width,
                height=height,
                frame_format=frame_format,
                slot_count=self.shm_slot_count,
                create=True  # Producer creates
            )
            self.logger.info(
                f"Worker {self.worker_id}: Created SHM buffer for camera {camera_id}: "
                f"{width}x{height} {self.shm_frame_format}, {self.shm_slot_count} slots"
            )
        return self._shm_buffers[camera_id]

    # ========================================================================
    # Dynamic Camera Management Methods
    # ========================================================================

    async def _command_handler(self):
        """Process commands from the manager (runs in async loop).

        Phase 6: Adaptive backoff polling to reduce overhead for rare commands.
        - Start at 100ms poll interval
        - Exponential backoff when idle (up to 1s)
        - Speed up after command received (down to 50ms)
        """
        self.logger.info(f"Worker {self.worker_id}: Command handler started (adaptive polling)")

        # Adaptive polling parameters (Phase 6)
        MIN_POLL_INTERVAL = 0.05  # 50ms - fast when active
        MAX_POLL_INTERVAL = 1.0   # 1s - slow when idle
        INITIAL_POLL_INTERVAL = 0.1  # 100ms - starting point
        BACKOFF_MULTIPLIER = 1.5  # Exponential backoff factor

        poll_interval = INITIAL_POLL_INTERVAL

        while not self.stop_event.is_set():
            try:
                # Non-blocking check for commands using executor
                command = await asyncio.get_event_loop().run_in_executor(
                    None,
                    self._get_command_nonblocking
                )

                if command:
                    await self._process_command(command)
                    # Speed up polling after receiving command (more likely to get another)
                    poll_interval = MIN_POLL_INTERVAL
                else:
                    # Exponential backoff when idle to reduce polling overhead
                    poll_interval = min(poll_interval * BACKOFF_MULTIPLIER, MAX_POLL_INTERVAL)
                    await asyncio.sleep(poll_interval)

            except asyncio.CancelledError:
                self.logger.info(f"Worker {self.worker_id}: Command handler cancelled")
                break
            except Exception as exc:
                self.logger.error(f"Worker {self.worker_id}: Error in command handler: {exc}", exc_info=True)
                await asyncio.sleep(1.0)

        self.logger.info(f"Worker {self.worker_id}: Command handler stopped")

    def _get_command_nonblocking(self):
        """Get command from queue without blocking."""
        try:
            return self.command_queue.get_nowait()
        except Exception:
            return None

    async def _process_command(self, command: Dict[str, Any]):
        """Process a single command.

        Args:
            command: Command dictionary with 'type' and payload
        """
        cmd_type = command.get('type')
        self.logger.info(f"Worker {self.worker_id}: Processing command: {cmd_type}")

        try:
            if cmd_type == 'add_camera':
                camera_config = command.get('camera_config')
                success = await self._add_camera_internal(camera_config)
                self._send_response(cmd_type, camera_config.get('stream_key'), success)

            elif cmd_type == 'remove_camera':
                stream_key = command.get('stream_key')
                success = await self._remove_camera_internal(stream_key)
                self._send_response(cmd_type, stream_key, success)

            elif cmd_type == 'update_camera':
                camera_config = command.get('camera_config')
                stream_key = command.get('stream_key')
                # Update = remove + add with new config
                await self._remove_camera_internal(stream_key)
                success = await self._add_camera_internal(camera_config)
                self._send_response(cmd_type, stream_key, success)

            else:
                self.logger.warning(f"Worker {self.worker_id}: Unknown command type: {cmd_type}")

        except Exception as exc:
            self.logger.error(f"Worker {self.worker_id}: Error processing command {cmd_type}: {exc}", exc_info=True)
            self._send_response(cmd_type, command.get('stream_key'), False, str(exc))

    async def _add_camera_internal(self, camera_config: Dict[str, Any]) -> bool:
        """Add a camera and start its streaming task.

        Args:
            camera_config: Camera configuration dictionary

        Returns:
            bool: True if camera was added successfully
        """
        stream_key = camera_config.get('stream_key')

        if not stream_key:
            self.logger.error(f"Worker {self.worker_id}: Camera config missing stream_key")
            return False

        if stream_key in self.camera_tasks:
            self.logger.warning(f"Worker {self.worker_id}: Camera {stream_key} already exists")
            return False

        try:
            # Create and start camera task
            task = asyncio.create_task(
                self._camera_handler(camera_config),
                name=f"camera-{stream_key}"
            )
            self.camera_tasks[stream_key] = task

            self.logger.info(f"Worker {self.worker_id}: Added camera {stream_key}")
            return True

        except Exception as exc:
            self.logger.error(f"Worker {self.worker_id}: Failed to add camera {stream_key}: {exc}", exc_info=True)
            return False

    async def _remove_camera_internal(self, stream_key: str) -> bool:
        """Remove a camera and stop its streaming task.

        Args:
            stream_key: Unique identifier for the camera stream

        Returns:
            bool: True if camera was removed successfully
        """
        if stream_key not in self.camera_tasks:
            self.logger.warning(f"Worker {self.worker_id}: Camera {stream_key} not found")
            return False

        try:
            # Cancel the camera task
            task = self.camera_tasks[stream_key]
            if not task.done():
                task.cancel()
                try:
                    await asyncio.wait_for(task, timeout=5.0)
                except (asyncio.CancelledError, asyncio.TimeoutError):
                    pass

            # Remove from tracking
            del self.camera_tasks[stream_key]

            # Release capture if exists
            if stream_key in self.captures:
                self.captures[stream_key].release()
                del self.captures[stream_key]

            self.logger.info(f"Worker {self.worker_id}: Removed camera {stream_key}")
            return True

        except Exception as exc:
            self.logger.error(f"Worker {self.worker_id}: Error removing camera {stream_key}: {exc}", exc_info=True)
            return False

    def _send_response(self, cmd_type: str, stream_key: str, success: bool, error: str = None):
        """Send response back to manager.

        Args:
            cmd_type: Type of command that was processed
            stream_key: Stream key the command was for
            success: Whether the command succeeded
            error: Error message if failed
        """
        if self.response_queue:
            try:
                self.response_queue.put_nowait({
                    'worker_id': self.worker_id,
                    'command_type': cmd_type,
                    'stream_key': stream_key,
                    'success': success,
                    'error': error,
                    'timestamp': time.time()
                })
            except Exception as exc:
                self.logger.warning(f"Worker {self.worker_id}: Failed to send response: {exc}", exc_info=True)

    async def _shutdown(self):
        """Gracefully shutdown worker - cancel tasks and cleanup."""
        self.logger.info(f"Worker {self.worker_id}: Starting graceful shutdown")

        # ================================================================
        # BLOCKING THREADS: Stop capture threads first
        # ================================================================
        if self.use_blocking_threads and self._thread_stop_event:
            self.logger.info(f"Worker {self.worker_id}: Stopping capture threads...")
            self._thread_stop_event.set()

            # Stop each capture thread
            for stream_key, capture in list(self._capture_threads.items()):
                try:
                    capture.stop()
                    self.logger.debug(f"Worker {self.worker_id}: Stopped capture thread for {stream_key}")
                except Exception as e:
                    self.logger.warning(f"Worker {self.worker_id}: Error stopping capture {stream_key}: {e}")
            self._capture_threads.clear()

            # Drain frame queue to prevent blocking
            if self._frame_queue:
                drained = 0
                while not self._frame_queue.empty():
                    try:
                        self._frame_queue.get_nowait()
                        drained += 1
                    except queue.Empty:
                        break
                if drained > 0:
                    self.logger.debug(f"Worker {self.worker_id}: Drained {drained} items from frame queue")

        # Cancel all camera tasks (legacy mode)
        for stream_key, task in self.camera_tasks.items():
            if not task.done():
                task.cancel()
                self.logger.info(f"Worker {self.worker_id}: Cancelled task for {stream_key}")

        # Wait for tasks to complete
        if self.camera_tasks:
            await asyncio.gather(*self.camera_tasks.values(), return_exceptions=True)

        # Release all captures (legacy mode uses self.captures)
        for stream_key, cap in list(self.captures.items()):
            cap.release()
            self.logger.info(f"Worker {self.worker_id}: Released capture {stream_key}")
        self.captures.clear()

        # ================================================================
        # SHM_MODE: Cleanup and UNLINK SHM buffers (producer responsibility)
        # ================================================================
        if self.use_shm:
            for camera_id, shm_buffer in list(self._shm_buffers.items()):
                try:
                    shm_buffer.close()  # This unlinks the SHM segment
                    self.logger.info(f"Worker {self.worker_id}: Closed and unlinked SHM buffer for camera {camera_id}")
                except Exception as e:
                    self.logger.warning(f"Worker {self.worker_id}: Error closing SHM buffer {camera_id}: {e}")
            self._shm_buffers.clear()

        # Close Redis client
        if self.redis_client:
            await self.redis_client.close()
            self.logger.info(f"Worker {self.worker_id}: Closed Redis client")

        # Shutdown capture executor
        self.logger.info(f"Worker {self.worker_id}: Shutting down capture executor...")
        try:
            self.capture_executor.shutdown(wait=True, cancel_futures=False)
        except Exception as exc:
            self.logger.warning(f"Worker {self.worker_id}: Error shutting down capture pool: {exc}", exc_info=True)
        self.logger.info(f"Worker {self.worker_id}: Capture executor shut down")

        # Report final health
        self._report_health("stopped")

        self.logger.info(f"Worker {self.worker_id}: Shutdown complete")

    def _report_health(self, status: str, active_cameras: int = 0, error: Optional[str] = None):
        """Report health status to main process.

        Args:
            status: Worker status (running, stopped, error)
            active_cameras: Number of active camera tasks
            error: Error message if status is error
        """
        try:
            # Get CPU/memory metrics for this process
            proc_cpu = 0
            proc_memory_mb = 0
            try:
                proc_cpu = self._process_info.cpu_percent(interval=None)
                proc_memory_mb = self._process_info.memory_info().rss / 1024 / 1024
            except Exception:
                pass

            # Calculate average encoding time
            avg_encoding_ms = 0
            if self._encoding_times:
                avg_encoding_ms = sum(self._encoding_times) / len(self._encoding_times) * 1000

            # Collect per-camera statistics for metrics reporting
            per_camera_stats = {}
            for stream_key in self.camera_tasks.keys():
                try:
                    timing_stats = self.statistics.get_timing_statistics(stream_key)
                    if timing_stats:
                        per_camera_stats[stream_key] = {
                            'fps': timing_stats.get('fps', {}),
                            'read_time_ms': timing_stats.get('read_time_ms', {}),
                            'write_time_ms': timing_stats.get('write_time_ms', {}),
                            'encoding_time_ms': timing_stats.get('encoding_time_ms', {}),
                            'frame_size_bytes': timing_stats.get('frame_size_bytes', {}),
                        }
                except Exception:
                    pass

            health_report = {
                'worker_id': self.worker_id,
                'status': status,
                'active_cameras': active_cameras,
                'timestamp': time.time(),
                'error': error,
                # Extended metrics for debugging
                'metrics': {
                    'cpu_percent': proc_cpu,
                    'memory_mb': proc_memory_mb,
                    'frames_encoded': self._frames_encoded,
                    'encoding_errors': self._encoding_errors,
                    'avg_encoding_ms': avg_encoding_ms,
                    'encoding_processes': self.num_encoding_processes,
                    'capture_threads': self.num_capture_threads,
                    # PERFORMANCE: CPU affinity info
                    'pinned_cores': self.pinned_cores,
                    'drop_stale_frames': self.drop_stale_frames,
                },
                # Per-camera statistics for metrics reporting
                'per_camera_stats': per_camera_stats,
            }
            self.health_queue.put_nowait(health_report)
        except Exception as exc:
            self.logger.warning(f"Worker {self.worker_id}: Failed to report health: {exc}", exc_info=True)


def _encode_frame_worker(frame, quality: int):
    """Worker function for encoding frames in process pool.

    This runs in a separate process for true parallel execution.

    Args:
        frame: Frame data (numpy array)
        quality: JPEG quality

    Returns:
        Tuple of (success, encoded_buffer)
    """
    import cv2
    return cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), quality])


def run_async_worker(
    worker_id: int,
    camera_configs: List[Dict[str, Any]],
    stream_config: Dict[str, Any],
    stop_event: multiprocessing.Event,
    health_queue: multiprocessing.Queue,
    command_queue: multiprocessing.Queue = None,
    response_queue: multiprocessing.Queue = None,
    # ================================================================
    # SHM_MODE: New parameters for shared memory architecture
    # ================================================================
    use_shm: bool = True,
    shm_slot_count: int = 1000,
    shm_frame_format: str = "BGR",
    # ================================================================
    # PERFORMANCE: New parameters for optimized frame capture
    # ================================================================
    drop_stale_frames: bool = True,
    pin_cpu_affinity: bool = True,
    total_workers: int = 1,
    buffer_size: int = 1,
    # ================================================================
    # BLOCKING THREADS: Optimized capture architecture (Phase 1)
    # ================================================================
    use_blocking_threads: bool = USE_BLOCKING_THREADS,
):
    """Entry point for async worker process.

    This function is called by multiprocessing.Process to start a worker.

    Args:
        worker_id: Worker identifier
        camera_configs: List of camera configurations
        stream_config: Streaming configuration
        stop_event: Shutdown event
        health_queue: Health reporting queue
        command_queue: Queue for receiving dynamic camera commands
        response_queue: Queue for sending command responses
        use_shm: Enable SHM mode (raw frames in shared memory)
        shm_slot_count: Number of frame slots per camera ring buffer
        shm_frame_format: Frame format for SHM storage
        drop_stale_frames: Use grab()/grab()/retrieve() pattern for latest frame
        pin_cpu_affinity: Pin worker process to specific CPU cores
        total_workers: Total number of workers for CPU affinity calculation
        buffer_size: VideoCapture buffer size (1 = minimal latency)
        use_blocking_threads: Use blocking capture threads instead of asyncio tasks
    """
    # Setup logging for this process
    logging.basicConfig(
        level=logging.INFO,
        format=f'%(asctime)s - Worker-{worker_id} - %(name)s - %(levelname)s - %(message)s'
    )

    logger = logging.getLogger(f"AsyncWorker-{worker_id}")
    logger.info(f"Starting async worker {worker_id}")
    import os
    os.environ["OMP_NUM_THREADS"] = "1"
    os.environ["KMP_NUM_THREADS"] = "1"
    os.environ["KMP_BLOCKTIME"] = "0"
    os.environ["TBB_NUM_THREADS"] = "1"
    os.environ["OPENBLAS_NUM_THREADS"] = "1"
    os.environ["MKL_NUM_THREADS"] = "1"
    os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
    os.environ["NUMEXPR_NUM_THREADS"] = "1"
    import cv2
    cv2.setNumThreads(1)
    cv2.setUseOptimized(True)
    cv2.ocl.setUseOpenCL(False)
    try:
        # Create worker
        worker = AsyncCameraWorker(
            worker_id=worker_id,
            camera_configs=camera_configs,
            stream_config=stream_config,
            stop_event=stop_event,
            health_queue=health_queue,
            command_queue=command_queue,
            response_queue=response_queue,
            # SHM_MODE: Pass through shared memory parameters
            use_shm=use_shm,
            shm_slot_count=shm_slot_count,
            shm_frame_format=shm_frame_format,
            # PERFORMANCE: Pass through optimized frame capture parameters
            drop_stale_frames=drop_stale_frames,
            pin_cpu_affinity=pin_cpu_affinity,
            total_workers=total_workers,
            buffer_size=buffer_size,
            # BLOCKING THREADS: Pass through optimized capture architecture parameter
            use_blocking_threads=use_blocking_threads,
        )

        # Run event loop
        asyncio.run(worker.run())

    except Exception as exc:
        logger.error(f"Worker {worker_id} failed: {exc}", exc_info=True)
        raise
