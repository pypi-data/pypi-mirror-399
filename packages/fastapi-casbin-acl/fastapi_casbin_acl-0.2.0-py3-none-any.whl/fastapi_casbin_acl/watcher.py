"""
Policy Watcher for multi-worker synchronization.

This module provides Redis-based policy synchronization to ensure all workers
have consistent policy state when running in a multi-process environment (e.g., gunicorn).
"""

import asyncio
import logging
from typing import Optional, Callable, Any, Awaitable

try:
    import redis.asyncio as aioredis
except ImportError:
    aioredis = None

from .exceptions import ACLNotInitialized

logger = logging.getLogger(__name__)


class RedisPolicyWatcher:
    """
    Redis Pub/Sub based policy watcher for multi-worker synchronization.

    When a policy is updated in one worker, this watcher notifies all other workers
    to reload their policies from the database, ensuring consistency across all workers.

    Example:
        watcher = RedisPolicyWatcher(
            redis_url="redis://localhost:6379/0",
            channel="fastapi_casbin:policy_update",
            reload_callback=acl.load_policy
        )
        await watcher.start()
        # ... later ...
        await watcher.notify_update()  # Notify all workers
        await watcher.stop()
    """

    def __init__(
        self,
        redis_url: str,
        channel: str = "fastapi_casbin:policy_update",
        reload_callback: Optional[Callable[[Optional[str]], Awaitable[None]]] = None,
    ):
        """
        Initialize the Redis policy watcher.

        :param redis_url: Redis connection URL (e.g., "redis://localhost:6379/0")
        :param channel: Redis Pub/Sub channel name for policy updates
        :param reload_callback: Async callable to reload policies when update is received.
                               Should accept optional model_name parameter.
        """
        if aioredis is None:
            raise ImportError(
                "redis package is required for RedisPolicyWatcher. "
                "Install it with: pip install redis[hiredis]"
            )

        self.redis_url = redis_url
        self.channel = channel
        self.reload_callback = reload_callback

        self._redis_client: Optional[Any] = None  # aioredis.Redis
        self._pubsub: Optional[Any] = None  # aioredis.client.PubSub
        self._listener_task: Optional[asyncio.Task] = None
        self._running = False

    async def start(self) -> None:
        """
        Start the watcher by connecting to Redis and subscribing to the channel.

        This will start a background task that listens for policy update notifications.
        """
        if self._running:
            logger.warning("Watcher is already running")
            return

        try:
            # Create Redis client
            self._redis_client = aioredis.from_url(
                self.redis_url, decode_responses=True
            )

            # Create PubSub client
            self._pubsub = self._redis_client.pubsub()

            # Subscribe to the channel
            await self._pubsub.subscribe(self.channel)
            logger.info(f"Subscribed to Redis channel: {self.channel}")

            # Start listener task
            self._running = True
            self._listener_task = asyncio.create_task(self._listen())

        except Exception as e:
            logger.error(f"Failed to start Redis watcher: {e}", exc_info=True)
            await self.stop()
            raise

    async def stop(self) -> None:
        """
        Stop the watcher by unsubscribing and closing connections.
        """
        if not self._running:
            return

        self._running = False

        # Cancel listener task and wait for it to finish
        if self._listener_task and not self._listener_task.done():
            self._listener_task.cancel()
            try:
                # Wait for task to complete with timeout
                await asyncio.wait_for(self._listener_task, timeout=2.0)
            except asyncio.TimeoutError:
                logger.warning("Watcher listener task did not stop in time")
            except asyncio.CancelledError:
                pass
            except Exception as e:
                logger.warning(f"Error waiting for listener task: {e}")
            self._listener_task = None

        # Unsubscribe and close PubSub
        if self._pubsub:
            try:
                await self._pubsub.unsubscribe(self.channel)
                await self._pubsub.close()
            except Exception as e:
                logger.warning(f"Error closing PubSub: {e}")
            self._pubsub = None

        # Close Redis client
        if self._redis_client:
            try:
                await self._redis_client.close()
            except Exception as e:
                logger.warning(f"Error closing Redis client: {e}")
            self._redis_client = None

        logger.info("Redis watcher stopped")

    async def notify_update(self, model_name: Optional[str] = None) -> None:
        """
        Notify all workers that policies have been updated.

        This publishes a message to the Redis channel, which will trigger
        all subscribed workers to reload their policies.

        :param model_name: Optional model name to reload. If None, all models are reloaded.
        """
        if not self._redis_client:
            logger.warning("Redis client not initialized, cannot notify update")
            return

        try:
            message = "update"
            if model_name:
                message = f"update:{model_name}"

            await self._redis_client.publish(self.channel, message)
            logger.debug(f"Published policy update notification to {self.channel}")
        except Exception as e:
            logger.error(f"Failed to notify policy update: {e}", exc_info=True)

    async def _listen(self) -> None:
        """
        Background task that listens for policy update messages.

        When a message is received, it calls the reload_callback to reload policies.
        """
        try:
            while self._running:
                try:
                    # Wait for message with timeout to allow checking _running flag
                    # Use shorter timeout for more responsive shutdown
                    message = await asyncio.wait_for(
                        self._pubsub.get_message(ignore_subscribe_messages=True),
                        timeout=0.5,
                    )

                    if message and message["type"] == "message":
                        data = message["data"]
                        logger.info(f"Received policy update notification: {data}")

                        # Parse model name if provided
                        model_name = None
                        if isinstance(data, str) and ":" in data:
                            parts = data.split(":", 1)
                            if len(parts) == 2 and parts[0] == "update":
                                model_name = parts[1] if parts[1] else None

                        # Call reload callback
                        if self.reload_callback is not None:
                            try:
                                # reload_callback is an async method that accepts Optional[str]
                                # Create a coroutine and await it
                                if model_name:
                                    await self.reload_callback(model_name)
                                else:
                                    await self.reload_callback(None)
                            except Exception as e:
                                logger.error(
                                    f"Error calling reload_callback: {e}", exc_info=True
                                )
                        else:
                            logger.warning(
                                "No reload_callback set, cannot reload policies"
                            )

                except asyncio.TimeoutError:
                    # Timeout is expected, continue loop to check _running flag
                    continue
                except asyncio.CancelledError:
                    # Task was cancelled, break the loop
                    logger.debug("Watcher listener task cancelled during message wait")
                    break
                except Exception as e:
                    logger.error(f"Error in watcher listener: {e}", exc_info=True)
                    # Continue listening despite errors, but check _running flag
                    if not self._running:
                        break
                    await asyncio.sleep(0.5)

        except asyncio.CancelledError:
            logger.debug("Watcher listener task cancelled")
        except KeyboardInterrupt:
            logger.debug("Watcher listener task interrupted")
        except Exception as e:
            logger.error(f"Watcher listener task error: {e}", exc_info=True)

    @property
    def is_running(self) -> bool:
        """Check if the watcher is currently running."""
        return self._running
