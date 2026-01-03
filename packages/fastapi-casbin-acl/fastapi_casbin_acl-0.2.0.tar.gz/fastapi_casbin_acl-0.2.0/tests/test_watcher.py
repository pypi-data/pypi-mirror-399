"""
Tests for fastapi_casbin_acl.watcher module.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi_casbin_acl.watcher import RedisPolicyWatcher


@pytest.fixture
def mock_reload_callback():
    """Mock reload callback function."""
    return AsyncMock()


@pytest.mark.asyncio
async def test_redis_policy_watcher_init():
    """Test RedisPolicyWatcher initialization."""
    with patch("fastapi_casbin_acl.watcher.aioredis") as mock_aioredis:
        watcher = RedisPolicyWatcher(
            redis_url="redis://localhost:6379/0",
            channel="test_channel",
            reload_callback=None,
        )
        assert watcher.redis_url == "redis://localhost:6379/0"
        assert watcher.channel == "test_channel"
        assert watcher.reload_callback is None
        assert watcher._running is False


@pytest.mark.asyncio
async def test_redis_policy_watcher_init_without_redis():
    """Test RedisPolicyWatcher raises ImportError when redis is not available."""
    with patch("fastapi_casbin_acl.watcher.aioredis", None):
        with pytest.raises(ImportError, match="redis package is required"):
            RedisPolicyWatcher(
                redis_url="redis://localhost:6379/0",
                channel="test_channel",
            )


@pytest.mark.asyncio
async def test_redis_policy_watcher_start(mock_reload_callback):
    """Test starting the Redis watcher."""
    with patch("fastapi_casbin_acl.watcher.aioredis") as mock_aioredis:
        # Setup mocks
        mock_pubsub = AsyncMock()
        mock_pubsub.subscribe = AsyncMock()
        mock_pubsub.get_message = AsyncMock(return_value=None)

        mock_client = AsyncMock()
        mock_client.pubsub = MagicMock(return_value=mock_pubsub)
        mock_client.close = AsyncMock()
        mock_aioredis.from_url = MagicMock(return_value=mock_client)

        watcher = RedisPolicyWatcher(
            redis_url="redis://localhost:6379/0",
            channel="test_channel",
            reload_callback=mock_reload_callback,
        )

        await watcher.start()

        assert watcher._running is True
        assert watcher._redis_client is not None
        assert watcher._pubsub is not None
        mock_pubsub.subscribe.assert_called_once_with("test_channel")

        # Cleanup
        await watcher.stop()


@pytest.mark.asyncio
async def test_redis_policy_watcher_start_already_running(mock_reload_callback):
    """Test starting watcher when already running."""
    with patch("fastapi_casbin_acl.watcher.aioredis") as mock_aioredis:
        mock_pubsub = AsyncMock()
        mock_pubsub.subscribe = AsyncMock()
        mock_pubsub.get_message = AsyncMock(return_value=None)

        mock_client = AsyncMock()
        mock_client.pubsub = MagicMock(return_value=mock_pubsub)
        mock_client.close = AsyncMock()
        mock_aioredis.from_url = MagicMock(return_value=mock_client)

        watcher = RedisPolicyWatcher(
            redis_url="redis://localhost:6379/0",
            channel="test_channel",
            reload_callback=mock_reload_callback,
        )

        await watcher.start()
        # Try to start again
        await watcher.start()  # Should not raise, just log warning

        await watcher.stop()


@pytest.mark.asyncio
async def test_redis_policy_watcher_stop(mock_reload_callback):
    """Test stopping the Redis watcher."""
    with patch("fastapi_casbin_acl.watcher.aioredis") as mock_aioredis:
        mock_pubsub = AsyncMock()
        mock_pubsub.subscribe = AsyncMock()
        mock_pubsub.unsubscribe = AsyncMock()
        mock_pubsub.close = AsyncMock()
        mock_pubsub.get_message = AsyncMock(side_effect=asyncio.TimeoutError())

        mock_client = AsyncMock()
        mock_client.pubsub = MagicMock(return_value=mock_pubsub)
        mock_client.close = AsyncMock()
        mock_aioredis.from_url = MagicMock(return_value=mock_client)

        watcher = RedisPolicyWatcher(
            redis_url="redis://localhost:6379/0",
            channel="test_channel",
            reload_callback=mock_reload_callback,
        )

        await watcher.start()
        await watcher.stop()

        assert watcher._running is False
        mock_pubsub.unsubscribe.assert_called_once_with("test_channel")
        mock_pubsub.close.assert_called_once()
        mock_client.close.assert_called_once()


@pytest.mark.asyncio
async def test_redis_policy_watcher_stop_not_running():
    """Test stopping watcher when not running."""
    with patch("fastapi_casbin_acl.watcher.aioredis") as mock_aioredis:
        watcher = RedisPolicyWatcher(
            redis_url="redis://localhost:6379/0",
            channel="test_channel",
        )
        # Should not raise
        await watcher.stop()


@pytest.mark.asyncio
async def test_redis_policy_watcher_notify_update(mock_reload_callback):
    """Test notifying policy update."""
    with patch("fastapi_casbin_acl.watcher.aioredis") as mock_aioredis:
        mock_pubsub = AsyncMock()
        mock_pubsub.subscribe = AsyncMock()
        mock_pubsub.get_message = AsyncMock(side_effect=asyncio.TimeoutError())

        mock_client = AsyncMock()
        mock_client.pubsub = MagicMock(return_value=mock_pubsub)
        mock_client.publish = AsyncMock()
        mock_client.close = AsyncMock()
        mock_aioredis.from_url = MagicMock(return_value=mock_client)

        watcher = RedisPolicyWatcher(
            redis_url="redis://localhost:6379/0",
            channel="test_channel",
            reload_callback=mock_reload_callback,
        )

        await watcher.start()
        await watcher.notify_update()

        mock_client.publish.assert_called_once_with("test_channel", "update")

        await watcher.stop()


@pytest.mark.asyncio
async def test_redis_policy_watcher_notify_update_with_model(mock_reload_callback):
    """Test notifying policy update with specific model."""
    with patch("fastapi_casbin_acl.watcher.aioredis") as mock_aioredis:
        mock_pubsub = AsyncMock()
        mock_pubsub.subscribe = AsyncMock()
        mock_pubsub.get_message = AsyncMock(side_effect=asyncio.TimeoutError())

        mock_client = AsyncMock()
        mock_client.pubsub = MagicMock(return_value=mock_pubsub)
        mock_client.publish = AsyncMock()
        mock_client.close = AsyncMock()
        mock_aioredis.from_url = MagicMock(return_value=mock_client)

        watcher = RedisPolicyWatcher(
            redis_url="redis://localhost:6379/0",
            channel="test_channel",
            reload_callback=mock_reload_callback,
        )

        await watcher.start()
        await watcher.notify_update("permission_rbac")

        mock_client.publish.assert_called_once_with(
            "test_channel", "update:permission_rbac"
        )

        await watcher.stop()


@pytest.mark.asyncio
async def test_redis_policy_watcher_notify_update_no_client():
    """Test notifying update when client is not initialized."""
    with patch("fastapi_casbin_acl.watcher.aioredis") as mock_aioredis:
        watcher = RedisPolicyWatcher(
            redis_url="redis://localhost:6379/0",
            channel="test_channel",
        )
        # Should not raise, just log warning
        await watcher.notify_update()

# TODO
# @pytest.mark.asyncio
# async def test_redis_policy_watcher_listen_receives_message(mock_reload_callback):
#     """Test watcher receives and processes update message."""
#     with patch("fastapi_casbin_acl.watcher.aioredis") as mock_aioredis:
#         # Create message mock - first return message, then timeout to exit loop
#         message = {
#             "type": "message",
#             "data": "update",
#         }

#         call_count = 0

#         async def get_message_side_effect(*args, **kwargs):
#             nonlocal call_count
#             call_count += 1
#             if call_count == 1:
#                 return message
#             else:
#                 raise asyncio.TimeoutError()

#         mock_pubsub = AsyncMock()
#         mock_pubsub.subscribe = AsyncMock()
#         mock_pubsub.get_message = AsyncMock(side_effect=get_message_side_effect)
#         mock_pubsub.unsubscribe = AsyncMock()
#         mock_pubsub.close = AsyncMock()

#         mock_client = AsyncMock()
#         mock_client.pubsub = MagicMock(return_value=mock_pubsub)
#         mock_client.close = AsyncMock()
#         mock_aioredis.from_url = MagicMock(return_value=mock_client)

#         watcher = RedisPolicyWatcher(
#             redis_url="redis://localhost:6379/0",
#             channel="test_channel",
#             reload_callback=mock_reload_callback,
#         )

#         await watcher.start()

#         # Manually trigger message processing by calling _listen logic
#         # Wait briefly for task to process
#         await asyncio.sleep(0.05)

#         # Stop watcher immediately
#         watcher._running = False
#         if watcher._listener_task:
#             watcher._listener_task.cancel()
#         await watcher.stop()

#         # Check that callback was called (may not be called if task cancelled too quickly)
#         # This test mainly verifies the structure works
#         assert watcher._running is False


# @pytest.mark.asyncio
# async def test_redis_policy_watcher_listen_receives_message_with_model(
#     mock_reload_callback,
# ):
#     """Test watcher receives message with model name."""
#     with patch("fastapi_casbin_acl.watcher.aioredis") as mock_aioredis:
#         # Create message mock with model name - first return message, then timeout
#         message = {
#             "type": "message",
#             "data": "update:permission_rbac",
#         }

#         call_count = 0

#         async def get_message_side_effect(*args, **kwargs):
#             nonlocal call_count
#             call_count += 1
#             if call_count == 1:
#                 return message
#             else:
#                 raise asyncio.TimeoutError()

#         mock_pubsub = AsyncMock()
#         mock_pubsub.subscribe = AsyncMock()
#         mock_pubsub.get_message = AsyncMock(side_effect=get_message_side_effect)
#         mock_pubsub.unsubscribe = AsyncMock()
#         mock_pubsub.close = AsyncMock()

#         mock_client = AsyncMock()
#         mock_client.pubsub = MagicMock(return_value=mock_pubsub)
#         mock_client.close = AsyncMock()
#         mock_aioredis.from_url = MagicMock(return_value=mock_client)

#         watcher = RedisPolicyWatcher(
#             redis_url="redis://localhost:6379/0",
#             channel="test_channel",
#             reload_callback=mock_reload_callback,
#         )

#         await watcher.start()

#         # Wait briefly for message processing
#         await asyncio.sleep(0.05)

#         # Stop watcher immediately
#         watcher._running = False
#         if watcher._listener_task:
#             watcher._listener_task.cancel()
#         await watcher.stop()

#         # This test mainly verifies the structure works
#         assert watcher._running is False


# @pytest.mark.asyncio
# async def test_redis_policy_watcher_is_running_property(mock_reload_callback):
#     """Test is_running property."""
#     with patch("fastapi_casbin_acl.watcher.aioredis") as mock_aioredis:
#         mock_pubsub = AsyncMock()
#         mock_pubsub.subscribe = AsyncMock()
#         mock_pubsub.get_message = AsyncMock(side_effect=asyncio.TimeoutError())
#         mock_pubsub.unsubscribe = AsyncMock()
#         mock_pubsub.close = AsyncMock()

#         mock_client = AsyncMock()
#         mock_client.pubsub = MagicMock(return_value=mock_pubsub)
#         mock_client.close = AsyncMock()
#         mock_aioredis.from_url = MagicMock(return_value=mock_client)

#         watcher = RedisPolicyWatcher(
#             redis_url="redis://localhost:6379/0",
#             channel="test_channel",
#             reload_callback=mock_reload_callback,
#         )

#         assert watcher.is_running is False

#         await watcher.start()
#         assert watcher.is_running is True

#         await watcher.stop()
#         assert watcher.is_running is False
