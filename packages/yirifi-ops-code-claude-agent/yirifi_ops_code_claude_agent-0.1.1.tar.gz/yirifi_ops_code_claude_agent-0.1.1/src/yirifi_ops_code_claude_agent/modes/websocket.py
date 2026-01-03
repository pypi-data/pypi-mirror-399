"""WebSocket mode for the Claude Code agent - maintains persistent connection."""
import json
import logging
import time
from typing import TYPE_CHECKING

try:
    import socketio
except ImportError:
    socketio = None  # type: ignore

if TYPE_CHECKING:
    from ..agent import ClaudeAgent

logger = logging.getLogger(__name__)


class SocketIOPublisher:
    """Publisher for sending events via Socket.IO."""

    def __init__(self, sio: 'socketio.Client') -> None:
        self.sio = sio

    def publish(self, channel: str, data: dict) -> None:
        """Publish data to the server."""
        try:
            # Parse channel to determine event type
            if 'session_stream' in channel:
                session_id = channel.split(':')[-1]
                self.sio.emit('agent_event', {
                    'session_id': session_id,
                    'event': data,
                })
            elif 'session_questions' in channel:
                session_id = channel.split(':')[-1]
                self.sio.emit('agent_prompt', {
                    'session_id': session_id,
                    'prompt': data,
                })
        except Exception as e:
            logger.warning(f"Failed to emit via Socket.IO: {e}")


def run_websocket_mode(agent: 'ClaudeAgent') -> None:
    """
    Run the agent in WebSocket mode.

    In this mode, the agent maintains a persistent WebSocket connection
    to the Flask server. Tasks are pushed directly to the agent, resulting
    in lower latency than polling mode.

    Features:
    - Auto-reconnect with exponential backoff
    - Direct task push from server
    - Real-time event streaming

    Args:
        agent: The ClaudeAgent instance
    """
    if socketio is None:
        logger.error("python-socketio not installed. Install with: pip install python-socketio[client]")
        logger.info("Falling back to polling mode...")
        from .polling import run_polling_mode
        run_polling_mode(agent)
        return

    config = agent.config

    logger.info("Starting WebSocket mode")
    logger.info(f"WebSocket URL: {config.ws_url}")

    # Create Socket.IO client
    sio = socketio.Client(
        reconnection=True,
        reconnection_attempts=0,  # Infinite
        reconnection_delay=config.ws_reconnect_delay,
        reconnection_delay_max=config.ws_max_reconnect_delay,
        logger=False,
    )

    # Set up event publisher
    publisher = SocketIOPublisher(sio)
    agent._event_publisher = publisher

    # Track connection state
    connected = False
    current_reconnect_delay = config.ws_reconnect_delay

    @sio.event
    def connect():
        nonlocal connected, current_reconnect_delay
        connected = True
        current_reconnect_delay = config.ws_reconnect_delay
        logger.info("Connected to server")

        # Register as agent
        sio.emit('agent_register', {
            'agent_id': agent._agent_id,
            'agent_name': config.agent_name,
            'agent_type': config.agent_type,
        })

    @sio.event
    def disconnect():
        nonlocal connected
        connected = False
        logger.warning("Disconnected from server")

    @sio.event
    def connect_error(data):
        logger.error(f"Connection error: {data}")

    @sio.on('registered')
    def on_registered(data):
        logger.info(f"Registered with server: {data}")

    @sio.on('task_assigned')
    def on_task_assigned(data):
        """Handle a task assignment from the server."""
        logger.info(f"Task assigned: session {data.get('session_id')}")

        # Acknowledge receipt
        sio.emit('task_acknowledged', {
            'session_id': data.get('session_id'),
            'agent_id': agent._agent_id,
        })

        # Execute the task
        try:
            execution_result = agent.execute_task(data)

            # Report completion
            sio.emit('task_completed', {
                'session_id': data.get('session_id'),
                'exit_code': execution_result.exit_code,
                'error': execution_result.error,
                'duration_ms': execution_result.duration_ms,
                'event_count': len(execution_result.events),
            })

        except Exception as e:
            logger.exception(f"Error executing task: {e}")
            sio.emit('task_failed', {
                'session_id': data.get('session_id'),
                'error': str(e),
            })

    @sio.on('prompt_response')
    def on_prompt_response(data):
        """Handle a prompt response from the server."""
        prompt_id = data.get('prompt_id')
        response = data.get('response')
        logger.info(f"Prompt response received: {prompt_id} = {response}")

        # Store in Redis for the executor to pick up
        try:
            import redis
            r = redis.from_url(config.redis_url)
            r.setex(f"response:{prompt_id}", 300, response)
        except Exception as e:
            logger.warning(f"Failed to store prompt response: {e}")

    @sio.on('cancel_task')
    def on_cancel_task(data):
        """Handle a task cancellation request."""
        session_id = data.get('session_id')
        logger.info(f"Cancel request for session {session_id}")

        if agent._current_session_id == session_id:
            agent._executor.cancel()

    # Main connection loop
    while agent.is_running:
        try:
            if not connected:
                logger.info(f"Connecting to {config.ws_url}...")
                sio.connect(
                    config.flask_url,
                    namespaces=['/claude'],
                    wait_timeout=30,
                )
                connected = True

            # Keep alive while connected
            while connected and agent.is_running:
                sio.sleep(1)

        except socketio.exceptions.ConnectionError as e:
            logger.warning(f"Connection failed: {e}")
            connected = False

            # Exponential backoff
            logger.info(f"Retrying in {current_reconnect_delay}s...")
            time.sleep(current_reconnect_delay)
            current_reconnect_delay = min(
                current_reconnect_delay * 2,
                config.ws_max_reconnect_delay
            )

        except Exception as e:
            logger.exception(f"Unexpected error: {e}")
            connected = False
            time.sleep(5)

    # Cleanup
    if sio.connected:
        sio.disconnect()

    logger.info("WebSocket mode stopped")
