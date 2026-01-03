"""Polling mode for the Claude Code agent - polls Redis queue for tasks."""
import json
import logging
import time
from typing import TYPE_CHECKING

import redis

if TYPE_CHECKING:
    from ..agent import ClaudeAgent

logger = logging.getLogger(__name__)


class RedisPublisher:
    """Publisher for sending events to Redis pub/sub."""

    def __init__(self, redis_url: str) -> None:
        self.redis_url = redis_url
        self._client: redis.Redis | None = None

    def _get_client(self) -> redis.Redis:
        """Get or create Redis client."""
        if self._client is None:
            self._client = redis.from_url(self.redis_url)
        return self._client

    def publish(self, channel: str, data: dict) -> None:
        """Publish data to a Redis channel."""
        try:
            client = self._get_client()
            client.publish(channel, json.dumps(data))
        except redis.RedisError as e:
            logger.warning(f"Failed to publish to Redis: {e}")


def run_polling_mode(agent: 'ClaudeAgent') -> None:
    """
    Run the agent in polling mode.

    In this mode, the agent polls a Redis queue for tasks at regular intervals.
    This is simpler and works with any network setup, but has higher latency
    than WebSocket mode.

    Args:
        agent: The ClaudeAgent instance
    """
    config = agent.config

    logger.info(f"Starting polling mode (interval: {config.poll_interval}s)")
    logger.info(f"Redis URL: {config.redis_url}")
    logger.info(f"Queue name: {config.task_queue_name}")

    # Set up Redis client
    try:
        redis_client = redis.from_url(config.redis_url)
        redis_client.ping()
        logger.info("Connected to Redis")
    except redis.RedisError as e:
        logger.error(f"Failed to connect to Redis: {e}")
        return

    # Set up event publisher
    publisher = RedisPublisher(config.redis_url)
    agent._event_publisher = publisher

    # Main polling loop
    while agent.is_running:
        try:
            # Try to dequeue a task (blocking with timeout)
            result = redis_client.brpop(
                config.task_queue_name,
                timeout=config.poll_interval,
            )

            if result:
                queue_name, task_data = result
                logger.debug(f"Received task from queue")

                try:
                    task = json.loads(task_data)
                    logger.info(f"Processing task: session {task.get('session_id')}")

                    # Execute the task
                    execution_result = agent.execute_task(task)

                    logger.info(
                        f"Task completed: exit_code={execution_result.exit_code}, "
                        f"events={len(execution_result.events)}, "
                        f"duration={execution_result.duration_ms}ms"
                    )

                except json.JSONDecodeError as e:
                    logger.error(f"Invalid task JSON: {e}")
                except Exception as e:
                    logger.exception(f"Error processing task: {e}")

            else:
                # No task received (timeout), just continue polling
                logger.debug("No tasks in queue")

        except redis.RedisError as e:
            logger.error(f"Redis error: {e}")
            # Try to reconnect
            time.sleep(5)
            try:
                redis_client = redis.from_url(config.redis_url)
                redis_client.ping()
                logger.info("Reconnected to Redis")
            except redis.RedisError:
                pass

        except Exception as e:
            logger.exception(f"Unexpected error in polling loop: {e}")
            time.sleep(1)

    logger.info("Polling mode stopped")
