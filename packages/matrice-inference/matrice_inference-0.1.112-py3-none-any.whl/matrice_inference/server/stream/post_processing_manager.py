"""
High-performance multiprocessing post-processing worker for stateful tracking.

Architecture:
- Multiprocessing: Multiple separate processes - TRUE PARALLELISM
- Camera Routing: hash(camera_id) % num_workers for state isolation - ORDER PRESERVATION
- Isolated Tracker States: Each process maintains trackers for assigned cameras
- CPU-bound Processing: Object tracking, aggregation, analytics
- SYNC SEQUENTIAL: Simple blocking loop for CPU-bound work (no asyncio overhead)

Architecture Flow:
- PostProcessor creates per-camera tracker states (stateful tracking)
- Each process handles subset of cameras (e.g., 250 cameras per process)
- Camera-based routing ensures same camera always goes to same worker
- Tracker states remain isolated within each process

Performance Targets:
- 15,000+ FPS throughput
- <100ms latency per frame
- Isolated tracker state per camera
- True parallelism (bypasses Python GIL)

Optimizations (v3 - Sync Sequential):
- Removed asyncio overhead for CPU-bound work (~2x throughput gain)
- Simple blocking loop: get() → process() → put()
- No concurrent task management (CPU-bound work doesn't benefit)
- Eliminates event loop, task scheduling, and ThreadPoolExecutor overhead
"""

import logging
import multiprocessing as mp
import queue
import time
from typing import Any, Dict, List, Optional


def postprocessing_worker_process(
    worker_id: int,
    num_workers: int,
    input_queue: mp.Queue,
    output_queue: mp.Queue,
    post_processor_config: Dict[str, Any],
    metrics_queue: Optional[mp.Queue] = None,
):
    """
    Worker process for CPU-bound post-processing with stateful tracking.

    SYNC SEQUENTIAL ARCHITECTURE (v3):
    - Simple blocking loop: input_queue.get() → process() → output_queue.put()
    - No asyncio overhead (CPU-bound work doesn't benefit from async)
    - Direct synchronous processing for maximum throughput
    - ~2x throughput improvement over async concurrent pattern

    IMPORTANT: Each worker reads from its OWN dedicated queue (input_queue).
    Inference workers route frames based on hash(camera_id) % num_workers.
    This ensures strict ordering per camera and isolated tracker states.

    Each process:
    1. Initializes PostProcessor with config
    2. Runs simple blocking loop (no asyncio)
    3. Processes frames sequentially (CPU-bound, no parallelism benefit)
    4. Maintains isolated tracker states for assigned cameras
    5. Outputs results to dedicated output queue

    Args:
        worker_id: Worker process ID
        num_workers: Total number of worker processes
        input_queue: This worker's dedicated queue (routed by inference workers)
        output_queue: This worker's dedicated output queue
        post_processor_config: Configuration for PostProcessor initialization
        metrics_queue: Queue for sending metrics back to main process
    """
    # Set up logging for this process
    logger = logging.getLogger(f"postproc_worker_{worker_id}")
    logger.setLevel(logging.INFO)

    try:
        # Import dependencies inside process to avoid pickle issues
        import asyncio
        from matrice_analytics.post_processing.post_processor import PostProcessor
        from matrice_inference.server.stream.worker_metrics import MultiprocessWorkerMetrics

        # Initialize post-processor with config
        post_processor = PostProcessor(**post_processor_config)

        # Initialize metrics for this worker (multiprocess-safe via queue)
        metrics = None
        if metrics_queue is not None:
            metrics = MultiprocessWorkerMetrics(
                worker_id=f"post_processing_{worker_id}",
                worker_type="post_processing",
                metrics_queue=metrics_queue
            )
        else:
            logger.warning(f"Worker {worker_id}: No metrics_queue provided, metrics will not be collected")

        if metrics:
            metrics.mark_active()

        logger.info(
            f"Post-processing worker {worker_id}/{num_workers} initialized - "
            f"mode=SYNC_SEQUENTIAL (optimized for CPU-bound work)"
        )

        # =================================================================
        # SYNC SEQUENTIAL PROCESSING LOOP
        # =================================================================
        # Simple blocking loop - optimal for CPU-bound work
        # No asyncio overhead, no task scheduling, no thread pool

        frames_processed = 0
        last_log_time = time.time()

        while True:
            try:
                # Blocking get with timeout (allows periodic health checks)
                try:
                    task_data = input_queue.get(timeout=0.1)
                except queue.Empty:
                    continue

                start_time = time.time()

                # Extract task fields
                camera_id = task_data.get("camera_id")
                frame_id = task_data.get("frame_id")
                model_result = task_data.get("model_result")
                stream_key = task_data.get("stream_key", camera_id)
                input_stream = task_data.get("input_stream", {})

                # Validate required fields
                if not camera_id:
                    logger.error("Task missing camera_id - skipping")
                    continue

                if not frame_id:
                    logger.error(f"[FRAME_ID_MISSING] camera={camera_id} - No frame_id. Skipping.")
                    continue

                if model_result is None:
                    logger.debug(f"Skipping frame for camera {camera_id} - no model result")
                    continue

                # Extract input bytes if available
                input_bytes = None
                if isinstance(input_stream, dict):
                    content = input_stream.get("content")
                    if isinstance(content, bytes):
                        input_bytes = content

                # Extract stream_info and add frame_id
                stream_info = {}
                if isinstance(input_stream, dict):
                    stream_info = input_stream.get("stream_info", {})
                    if not isinstance(stream_info, dict):
                        stream_info = {}
                    if frame_id:
                        stream_info["frame_id"] = frame_id

                # Process using asyncio.run() since PostProcessor.process() is async
                # This gives us the benefit of sync worker loop while supporting async process()
                try:
                    result = asyncio.run(post_processor.process(
                        data=model_result,
                        stream_key=stream_key,
                        input_bytes=input_bytes,
                        stream_info=stream_info,
                    ))
                except Exception as e:
                    logger.error(f"Post-processing error for camera {camera_id}: {e}", exc_info=True)
                    continue

                # Serialize ProcessingResult to dict
                post_processed_dict = result.to_dict() if hasattr(result, "to_dict") else result

                # Extract message_key from original_message
                original_message = task_data.get("original_message")
                message_key = original_message.message_key if hasattr(original_message, "message_key") else str(frame_id)

                # Flatten nested data structure if present
                if isinstance(post_processed_dict, dict) and "data" in post_processed_dict:
                    inner_data = post_processed_dict.pop("data", {})
                    post_processed_dict.update(inner_data)

                # Build output data
                output_data = {
                    "camera_id": camera_id,
                    "message_key": message_key,
                    "frame_id": frame_id,
                    "input_stream": task_data.get("input_stream", {}),
                    "data": {
                        "post_processing_result": post_processed_dict,
                        "model_result": model_result,
                        "metadata": task_data.get("metadata", {}),
                        "processing_time": task_data.get("processing_time", 0),
                        "stream_key": task_data.get("stream_key"),
                        "frame_id": frame_id,
                    }
                }

                # Put result to output queue
                output_queue.put(output_data)

                # Record metrics
                latency_ms = (time.time() - start_time) * 1000
                if metrics:
                    metrics.record_latency(latency_ms)
                    metrics.record_throughput(count=1)

                frames_processed += 1

                # Periodic logging (every 60 seconds)
                now = time.time()
                if now - last_log_time > 60.0:
                    logger.info(
                        f"Worker {worker_id}: processed {frames_processed} frames"
                    )
                    last_log_time = now

            except Exception as e:
                logger.error(f"Worker loop error: {e}", exc_info=True)
                time.sleep(0.01)

    except Exception as e:
        logger.error(f"Worker {worker_id} crashed: {e}", exc_info=True)
        raise
    finally:
        if metrics:
            metrics.mark_inactive()
        logger.info(f"Post-processing worker {worker_id} stopped")


class MultiprocessPostProcessingPool:
    """
    Pool of multiprocessing post-processing workers with per-worker queues.

    Architecture:
    - Creates multiple worker processes (4 workers for CPU-bound tasks)
    - Each worker has its OWN dedicated input queue (routed by inference workers)
    - Each worker writes to its OWN dedicated output queue (eliminates lock contention)
    - Each process maintains isolated tracker states for assigned cameras
    - 100% order preservation per camera (no re-queuing)
    - Processes communicate via multiprocessing queues
    - True parallelism (bypasses Python GIL)
    - Metrics sent back to main process via metrics_queue for aggregation
    """

    def __init__(
        self,
        pipeline: Any,
        post_processor_config: Dict[str, Any],
        input_queues: List[mp.Queue],
        output_queues: List[mp.Queue],
        num_processes: int = 4,
        metrics_queue: Optional[mp.Queue] = None,
    ):
        """
        Initialize post-processing pool with per-worker queues.

        Args:
            pipeline: Reference to StreamingPipeline (not used in workers, for compatibility)
            post_processor_config: Configuration for PostProcessor initialization
            input_queues: List of mp.Queues (one per worker, routed by inference workers)
            output_queues: List of mp.Queues (one per worker, eliminates lock contention)
            num_processes: Number of worker processes
            metrics_queue: Queue for sending metrics back to main process
        """
        self.pipeline = pipeline
        self.post_processor_config = post_processor_config
        self.num_processes = num_processes
        self.running = False

        # Per-worker input queues from pipeline (one per worker)
        self.input_queues = input_queues
        # Per-worker output queues (eliminates lock contention)
        self.output_queues = output_queues
        self.metrics_queue = metrics_queue

        # Validate queue counts
        if len(input_queues) != num_processes:
            raise ValueError(f"Expected {num_processes} input queues, got {len(input_queues)}")
        if len(output_queues) != num_processes:
            raise ValueError(f"Expected {num_processes} output queues, got {len(output_queues)}")

        self.processes = []

        self.logger = logging.getLogger(f"{__name__}.MultiprocessPostProcessingPool")

    def start(self):
        """Start all worker processes with dedicated input and output queues."""
        self.running = True

        # Start worker processes (each reads from its dedicated queue, writes to its own output queue)
        for i in range(self.num_processes):
            process = mp.Process(
                target=postprocessing_worker_process,
                args=(
                    i,
                    self.num_processes,
                    self.input_queues[i],  # Worker's dedicated input queue
                    self.output_queues[i],  # Worker's dedicated output queue (no lock contention)
                    self.post_processor_config,
                    self.metrics_queue,  # For sending metrics back to main process
                ),
                daemon=True,
            )
            process.start()
            self.processes.append(process)

        self.logger.info(
            f"Started {self.num_processes} post-processing workers with dedicated input/output queues "
            f"(metrics_queue={'enabled' if self.metrics_queue else 'disabled'})"
        )

    def stop(self):
        """Stop all worker processes."""
        self.running = False

        # Terminate processes
        for process in self.processes:
            if process.is_alive():
                process.terminate()
                process.join(timeout=5)
                if process.is_alive():
                    process.kill()

        self.processes.clear()
        self.logger.info("Stopped all post-processing worker processes")

    def submit_task(self, task_data: Dict[str, Any], timeout: float = 0.1) -> bool:
        """
        Submit task to shared worker pool queue.

        Workers pull from shared queue and route internally by camera hash.
        Camera-based routing within workers ensures:
        - Same camera always goes to same worker process
        - Tracker state remains isolated within that process
        - Per-camera ordering is preserved

        Args:
            task_data: Task data with camera_id, model_result, etc.
            timeout: Max time to wait if queue is full

        Returns:
            True if task was submitted, False if queue full (backpressure)
        """
        try:
            # Submit to shared input queue (workers handle routing internally)
            self.input_queue.put(task_data, block=True, timeout=timeout)
            return True

        except Exception:
            # Queue full - apply backpressure
            return False

    def get_result(self, timeout: float = 0.001) -> Optional[Dict[str, Any]]:
        """
        Get result from worker pool.

        Args:
            timeout: Max time to wait for result

        Returns:
            Result dict or None if no result available
        """
        try:
            return self.output_queue.get(timeout=timeout)
        except Exception:
            return None
