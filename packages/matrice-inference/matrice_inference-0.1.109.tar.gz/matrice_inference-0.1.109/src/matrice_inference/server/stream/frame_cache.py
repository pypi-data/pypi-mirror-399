import asyncio
import logging
import threading
import time
from typing import Optional, Dict, Any

try:
    import redis.asyncio as aioredis  # Async Redis client
except ImportError:  # pragma: no cover
    aioredis = None  # type: ignore


class RedisFrameCache:
    """Async Redis cache for frames with high-throughput design.

    Uses redis.asyncio for non-blocking Redis operations, eliminating the need
    for worker threads. All operations are async and return immediately.

    Stores base64 string content under key 'stream:frames:{frame_id}' with field 'frame'.
    Each insert sets or refreshes the TTL.
    """

    DEFAULT_TTL_SECONDS = 300
    DEFAULT_CONNECT_TIMEOUT = 2.0
    DEFAULT_SOCKET_TIMEOUT = 0.5
    DEFAULT_PREFIX = "stream:frames:"
    DEFAULT_MAX_CONNECTIONS = 200  # Connection pool size for high concurrency

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        username: Optional[str] = None,
        ttl_seconds: int = DEFAULT_TTL_SECONDS,
        prefix: str = DEFAULT_PREFIX,
        max_queue: int = 10000,  # Kept for API compatibility, unused in async mode
        worker_threads: int = 16,  # Kept for API compatibility, unused in async mode
        connect_timeout: float = DEFAULT_CONNECT_TIMEOUT,
        socket_timeout: float = DEFAULT_SOCKET_TIMEOUT,
        max_connections: int = DEFAULT_MAX_CONNECTIONS,
        # SHM_MODE: Disable frame caching when SHM is active
        shm_mode: bool = False,
    ) -> None:
        self.logger = logging.getLogger(f"{__name__}.frame_cache")

        # SHM_MODE: Skip initialization if SHM mode is active
        self.shm_mode = shm_mode
        if shm_mode:
            self.logger.info(
                "[SHM_MODE] Frame cache DISABLED - frames stored in shared memory"
            )
            self.ttl_seconds = ttl_seconds
            self.prefix = prefix
            self.running = False
            self._client: Optional[aioredis.Redis] = None
            self._cached_frame_ids: set = set()
            self._cached_ids_lock = threading.Lock()
            self._metrics = {}
            self._metrics_lock = threading.Lock()
            return

        self.ttl_seconds = max(1, int(ttl_seconds))
        self.prefix = prefix
        self.running = False
        self._client: Optional[aioredis.Redis] = None

        # Connection parameters for lazy initialization
        self._host = host
        self._port = port
        self._db = db
        self._password = password
        self._username = username
        self._connect_timeout = connect_timeout
        self._socket_timeout = socket_timeout
        self._max_connections = max_connections

        # Track cached frame_ids to prevent duplicates
        self._cached_frame_ids: set = set()
        self._cached_ids_lock = threading.Lock()

        # Metrics for monitoring and debugging
        self._metrics = {
            "frames_queued": 0,
            "frames_cached": 0,
            "frames_failed": 0,
            "frames_dropped": 0,
            "frames_skipped_duplicate": 0,
            "frames_skipped_empty": 0,
            "last_cache_time": None,
            "last_frame_id": None,
        }
        self._metrics_lock = threading.Lock()

        # Semaphore for limiting concurrent Redis operations
        self._semaphore: Optional[asyncio.Semaphore] = None
        self._max_concurrent = max_connections // 2  # Leave room for other ops

    def _is_redis_available(self) -> bool:
        """Check if Redis package is available."""
        if aioredis is None:
            self.logger.warning("redis.asyncio package not installed; frame caching disabled")
            return False
        return True

    async def _ensure_client(self) -> Optional[aioredis.Redis]:
        """Lazily initialize async Redis client on first use."""
        if self._client is not None:
            return self._client

        if not self._is_redis_available():
            return None

        try:
            self.logger.info(
                f"[REDIS_ASYNC_INIT] Creating async Redis client: "
                f"host={self._host}:{self._port}, db={self._db}"
            )

            # Create async Redis client with connection pool
            self._client = aioredis.Redis(
                host=self._host,
                port=self._port,
                db=self._db,
                password=self._password,
                username=self._username,
                socket_connect_timeout=self._connect_timeout,
                socket_timeout=self._socket_timeout,
                max_connections=self._max_connections,
                decode_responses=False,  # Keep binary data as bytes
            )

            # Test connection
            await self._client.ping()
            self.logger.info(
                f"[REDIS_ASYNC_OK] Async Redis connection verified: "
                f"host={self._host}:{self._port}, max_connections={self._max_connections}"
            )

            # Initialize semaphore for concurrency control
            self._semaphore = asyncio.Semaphore(self._max_concurrent)

            return self._client

        except Exception as e:
            self.logger.error(
                f"[REDIS_ASYNC_FAIL] Failed to initialize async Redis client: {e}",
                exc_info=True
            )
            self._client = None
            return None

    def start(self) -> None:
        """Start the frame cache (marks as running, lazy client init)."""
        if self.shm_mode:
            self.logger.info("[SHM_MODE] Frame cache start skipped - using shared memory")
            return

        if self.running:
            self.logger.warning("[FRAME_CACHE_START] Frame cache already running")
            return

        self.running = True
        self.logger.info(
            f"[FRAME_CACHE_STARTED] Async RedisFrameCache ready: "
            f"prefix={self.prefix}, ttl={self.ttl_seconds}s, "
            f"max_concurrent={self._max_concurrent}"
        )

    def stop(self) -> None:
        """Stop the frame cache and cleanup resources."""
        if not self.running:
            return

        self.running = False
        # Note: Client cleanup should be done via close_async() in async context

    async def close_async(self) -> None:
        """Close async Redis client (call from async context)."""
        if self._client:
            try:
                await self._client.close()
            except Exception as e:
                self.logger.warning(f"Error closing async Redis client: {e}")
            self._client = None

    def put(self, frame_id: str, binary_content: bytes) -> None:
        """Queue a frame for async caching (fire-and-forget).

        This method is synchronous but creates an async task for the actual
        Redis operation. The task runs in the background without blocking.

        Args:
            frame_id: unique identifier for the frame
            binary_content: raw image bytes (JPEG/PNG/etc)
        """
        if self.shm_mode:
            return

        if not self.running:
            return

        # Quick validation
        if not frame_id or not binary_content:
            with self._metrics_lock:
                self._metrics["frames_skipped_empty"] += 1
            return

        # Check for duplicates
        with self._cached_ids_lock:
            if frame_id in self._cached_frame_ids:
                with self._metrics_lock:
                    self._metrics["frames_skipped_duplicate"] += 1
                return
            self._cached_frame_ids.add(frame_id)

        # Fire and forget - create async task
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self._put_async(frame_id, binary_content))
            with self._metrics_lock:
                self._metrics["frames_queued"] += 1
        except RuntimeError:
            # No running event loop - can't schedule async task
            with self._cached_ids_lock:
                self._cached_frame_ids.discard(frame_id)
            self.logger.debug(f"No event loop for frame {frame_id}")

    async def _put_async(self, frame_id: str, binary_content: bytes) -> None:
        """Async implementation of frame caching."""
        start_time = time.time()
        try:
            client = await self._ensure_client()
            if not client:
                with self._cached_ids_lock:
                    self._cached_frame_ids.discard(frame_id)
                return

            key = f"{self.prefix}{frame_id}"

            # Use semaphore to limit concurrent Redis operations
            async with self._semaphore:
                # Pipeline for atomic HSET + EXPIRE
                async with client.pipeline() as pipe:
                    await pipe.hset(key, "frame", binary_content)
                    await pipe.expire(key, self.ttl_seconds)
                    await pipe.execute()

            elapsed = time.time() - start_time
            with self._metrics_lock:
                self._metrics["frames_cached"] += 1
                self._metrics["last_cache_time"] = time.time()
                self._metrics["last_frame_id"] = frame_id

            self.logger.debug(
                f"[FRAME_CACHE_OK] frame_id={frame_id}, size={len(binary_content)}, "
                f"elapsed={elapsed:.3f}s"
            )

        except Exception as e:
            with self._cached_ids_lock:
                self._cached_frame_ids.discard(frame_id)
            with self._metrics_lock:
                self._metrics["frames_failed"] += 1
            self.logger.error(f"[FRAME_CACHE_ERROR] frame_id={frame_id}: {e}")

    def put_overlay(
        self,
        frame_id: str,
        camera_id: str,
        app_deployment_id: str,
        overlay_data: bytes,
        ttl_seconds: Optional[int] = None
    ) -> bool:
        """Queue overlay data for async storage (fire-and-forget).

        Key format: overlay:{frame_id}_{camera_id}_{app_deployment_id}

        Args:
            frame_id: Unique frame identifier
            camera_id: Camera identifier
            app_deployment_id: App deployment identifier
            overlay_data: Serialized overlay/results data (JSON bytes)
            ttl_seconds: Optional TTL override

        Returns:
            bool: True if task was scheduled, False otherwise
        """
        if self.shm_mode:
            return True  # No-op success in SHM mode

        if not self.running:
            return False

        if not frame_id or not camera_id or not app_deployment_id or not overlay_data:
            return False

        # Fire and forget
        try:
            loop = asyncio.get_running_loop()
            ttl = ttl_seconds if ttl_seconds is not None else self.ttl_seconds
            loop.create_task(
                self._put_overlay_async(frame_id, camera_id, app_deployment_id, overlay_data, ttl)
            )
            return True
        except RuntimeError:
            return False

    async def _put_overlay_async(
        self,
        frame_id: str,
        camera_id: str,
        app_deployment_id: str,
        overlay_data: bytes,
        ttl_seconds: int
    ) -> None:
        """Async implementation of overlay storage."""
        composite_key = f"overlay:{frame_id}_{camera_id}_{app_deployment_id}"
        start_time = time.time()

        try:
            client = await self._ensure_client()
            if not client:
                return

            async with self._semaphore:
                async with client.pipeline() as pipe:
                    await pipe.set(composite_key, overlay_data)
                    await pipe.expire(composite_key, ttl_seconds)
                    await pipe.execute()

            elapsed = time.time() - start_time
            self.logger.debug(
                f"[OVERLAY_OK] key={composite_key}, size={len(overlay_data)}, "
                f"elapsed={elapsed:.3f}s"
            )

        except Exception as e:
            self.logger.error(f"[OVERLAY_ERROR] key={composite_key}: {e}")

    def get_metrics(self) -> Dict[str, Any]:
        """Get cache performance metrics for monitoring."""
        with self._metrics_lock:
            metrics = dict(self._metrics)

        metrics.update({
            "running": self.running,
            "async_mode": True,
            "max_concurrent": self._max_concurrent,
            "prefix": self.prefix,
            "ttl_seconds": self.ttl_seconds,
            "shm_mode": self.shm_mode,
        })

        return metrics
