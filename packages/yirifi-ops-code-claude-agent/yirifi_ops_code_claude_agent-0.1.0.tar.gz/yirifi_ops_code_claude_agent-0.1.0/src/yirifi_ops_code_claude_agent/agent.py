"""Main Claude Agent class that orchestrates task execution."""
import logging
import threading
import time
from typing import Any

import requests

from .config import AgentConfig
from .executor import ClaudeExecutor, ExecutionResult, MockExecutor
from .stream_parser import StreamEvent

logger = logging.getLogger(__name__)


class ClaudeAgent:
    """
    Main agent class for executing Claude Code tasks.

    This agent can operate in two modes:
    - Polling mode: Polls Redis queue for tasks
    - WebSocket mode: Maintains persistent WS connection for lower latency
    """

    def __init__(self, config: AgentConfig, mock: bool = False) -> None:
        """
        Initialize the agent.

        Args:
            config: Agent configuration
            mock: If True, use mock executor for testing
        """
        self.config = config
        self.mock = mock

        # State
        self._registered = False
        self._agent_id: int | None = None
        self._running = False
        self._current_session_id: int | None = None

        # Threading
        self._heartbeat_thread: threading.Thread | None = None
        self._stop_event = threading.Event()

        # Publisher for events (set by mode-specific runners)
        self._event_publisher: Any = None

        # Create executor
        ExecutorClass = MockExecutor if mock else ClaudeExecutor
        self._executor = ExecutorClass(
            config=config,
            on_event=self._on_stream_event,
            on_prompt=self._on_permission_prompt,
        )

        logger.info(f"Agent initialized: {config.agent_name} (mode: {config.mode}, mock: {mock})")

    def register(self) -> bool:
        """
        Register the agent with the Flask server.

        Returns:
            True if registration successful
        """
        try:
            url = f"{self.config.api_base_url}/agents/register"
            payload = {
                'agent_name': self.config.agent_name,
                'agent_type': self.config.agent_type,
            }

            response = requests.post(
                url,
                json=payload,
                headers=self.config.headers,
                timeout=30,
            )

            if response.status_code in (200, 201):
                data = response.json()
                self._agent_id = data.get('data', {}).get('id') or data.get('id')
                self._registered = True
                logger.info(f"Registered as agent ID: {self._agent_id}")
                return True
            else:
                logger.error(f"Registration failed: {response.status_code} - {response.text}")
                return False

        except requests.RequestException as e:
            logger.error(f"Registration request failed: {e}")
            return False

    def heartbeat(self) -> bool:
        """
        Send heartbeat to the server.

        Returns:
            True if heartbeat successful
        """
        if not self._registered:
            return False

        try:
            url = f"{self.config.api_base_url}/agents/heartbeat"
            payload = {
                'agent_id': self._agent_id,
                'status': 'busy' if self._current_session_id else 'online',
            }

            response = requests.post(
                url,
                json=payload,
                headers=self.config.headers,
                timeout=10,
            )

            if response.status_code == 200:
                return True
            else:
                logger.warning(f"Heartbeat failed: {response.status_code}")
                return False

        except requests.RequestException as e:
            logger.warning(f"Heartbeat request failed: {e}")
            return False

    def start_heartbeat_loop(self) -> None:
        """Start background heartbeat thread."""
        if self._heartbeat_thread and self._heartbeat_thread.is_alive():
            return

        def heartbeat_loop():
            while not self._stop_event.is_set():
                self.heartbeat()
                self._stop_event.wait(self.config.heartbeat_interval)

        self._heartbeat_thread = threading.Thread(target=heartbeat_loop, daemon=True)
        self._heartbeat_thread.start()
        logger.info("Heartbeat loop started")

    def stop_heartbeat_loop(self) -> None:
        """Stop background heartbeat thread."""
        self._stop_event.set()
        if self._heartbeat_thread:
            self._heartbeat_thread.join(timeout=5)
        logger.info("Heartbeat loop stopped")

    def execute_task(self, task: dict[str, Any]) -> ExecutionResult:
        """
        Execute a task from the queue.

        Args:
            task: Task dictionary with session_id, prompt, working_dir, etc.

        Returns:
            ExecutionResult from execution
        """
        session_id = task.get('session_id')
        prompt = task.get('prompt', task.get('initial_prompt', ''))
        working_dir = task.get('working_dir', task.get('path', '.'))
        allowed_tools = task.get('allowed_tools')
        timeout = task.get('timeout')
        env_vars = task.get('env_vars')

        if not prompt:
            logger.error("Task missing prompt")
            return ExecutionResult(exit_code=1, events=[], error="Missing prompt")

        logger.info(f"Executing task for session {session_id}: {prompt[:50]}...")

        # Track current session
        self._current_session_id = session_id

        try:
            # Update session status to in_progress
            self._update_session_status(session_id, 'in_progress')

            # Execute the task
            result = self._executor.execute(
                prompt=prompt,
                working_dir=working_dir,
                allowed_tools=allowed_tools,
                timeout=timeout,
                env_vars=env_vars,
            )

            # Update session status based on result
            final_status = 'completed' if result.exit_code == 0 else 'failed'
            self._update_session_status(
                session_id,
                final_status,
                exit_code=result.exit_code,
                error=result.error
            )

            return result

        except Exception as e:
            logger.exception(f"Error executing task: {e}")
            self._update_session_status(session_id, 'failed', error=str(e))
            return ExecutionResult(exit_code=1, events=[], error=str(e))

        finally:
            self._current_session_id = None

    def _on_stream_event(self, event: StreamEvent) -> None:
        """
        Handle a stream event from Claude Code.

        Publishes the event to Redis for the dashboard to pick up.
        """
        if not self._current_session_id:
            return

        # Publish to Redis channel
        channel = f"session_stream:{self._current_session_id}"
        event_data = event.to_dict()

        if self._event_publisher:
            try:
                self._event_publisher.publish(channel, event_data)
            except Exception as e:
                logger.warning(f"Failed to publish event: {e}")

        # Also send via HTTP as backup
        try:
            url = f"{self.config.api_base_url}/sessions/{self._current_session_id}/events"
            requests.post(
                url,
                json={'event': event_data},
                headers=self.config.headers,
                timeout=5,
            )
        except requests.RequestException:
            pass  # Non-critical

    def _on_permission_prompt(self, event: StreamEvent) -> str | None:
        """
        Handle a permission prompt from Claude Code.

        Publishes the prompt and waits for user response.
        """
        if not self._current_session_id:
            return None

        prompt_id = event.data.get('prompt_id', '')
        question = event.data.get('question', '')
        options = event.data.get('options', [])
        tool_name = event.data.get('tool_name')
        timeout = event.data.get('timeout', 300)

        logger.info(f"Permission prompt: {question[:50]}...")

        # Update session status
        self._update_session_status(self._current_session_id, 'waiting_input')

        # Publish prompt to Redis
        channel = f"session_questions:{self._current_session_id}"
        prompt_data = {
            'prompt_id': prompt_id,
            'question': question,
            'options': options,
            'tool_name': tool_name,
            'timeout': timeout,
        }

        if self._event_publisher:
            try:
                self._event_publisher.publish(channel, prompt_data)
            except Exception as e:
                logger.warning(f"Failed to publish prompt: {e}")

        # Also create interactive prompt record via API
        try:
            url = f"{self.config.api_base_url}/sessions/{self._current_session_id}/prompts"
            requests.post(
                url,
                json=prompt_data,
                headers=self.config.headers,
                timeout=5,
            )
        except requests.RequestException:
            pass

        # Wait for response from Redis
        response = self._wait_for_prompt_response(prompt_id, timeout)

        # Update session status back to in_progress
        if response:
            self._update_session_status(self._current_session_id, 'in_progress')

        return response

    def _wait_for_prompt_response(self, prompt_id: str, timeout: int) -> str | None:
        """
        Wait for a user response to a prompt.

        Args:
            prompt_id: The prompt ID to wait for
            timeout: Maximum time to wait in seconds

        Returns:
            User response string or None if timeout
        """
        # Try to get response from Redis
        if self._event_publisher:
            try:
                # Poll Redis for response
                import redis
                r = redis.from_url(self.config.redis_url)
                key = f"response:{prompt_id}"

                start = time.time()
                while time.time() - start < timeout:
                    response = r.get(key)
                    if response:
                        r.delete(key)
                        return response.decode('utf-8')
                    time.sleep(0.5)

            except Exception as e:
                logger.warning(f"Error waiting for prompt response: {e}")

        # Fallback: poll HTTP API
        try:
            url = f"{self.config.api_base_url}/sessions/{self._current_session_id}/prompts/{prompt_id}"

            start = time.time()
            while time.time() - start < timeout:
                response = requests.get(
                    url,
                    headers=self.config.headers,
                    timeout=5,
                )
                if response.status_code == 200:
                    data = response.json()
                    user_response = data.get('data', {}).get('user_response')
                    if user_response:
                        return user_response
                time.sleep(1)

        except requests.RequestException as e:
            logger.warning(f"Error polling for prompt response: {e}")

        logger.warning(f"Timeout waiting for response to prompt {prompt_id}")
        return None

    def _update_session_status(
        self,
        session_id: int,
        status: str,
        exit_code: int | None = None,
        error: str | None = None,
    ) -> None:
        """Update session status via API."""
        try:
            url = f"{self.config.api_base_url}/sessions/{session_id}/status"
            payload: dict[str, Any] = {'status': status}
            if exit_code is not None:
                payload['exit_code'] = exit_code
            if error:
                payload['error'] = error

            requests.patch(
                url,
                json=payload,
                headers=self.config.headers,
                timeout=10,
            )
        except requests.RequestException as e:
            logger.warning(f"Failed to update session status: {e}")

    def run(self) -> None:
        """
        Run the agent in the configured mode.

        This is the main entry point that delegates to the appropriate mode.
        """
        # Register first
        if not self.register():
            logger.error("Failed to register agent, exiting")
            return

        # Start heartbeat
        self.start_heartbeat_loop()

        self._running = True
        logger.info(f"Starting agent in {self.config.mode} mode...")

        try:
            if self.config.mode == 'websocket':
                from .modes.websocket import run_websocket_mode
                run_websocket_mode(self)
            else:
                from .modes.polling import run_polling_mode
                run_polling_mode(self)
        except KeyboardInterrupt:
            logger.info("Agent interrupted")
        finally:
            self._running = False
            self.stop_heartbeat_loop()
            logger.info("Agent stopped")

    def stop(self) -> None:
        """Stop the agent gracefully."""
        self._running = False
        self._stop_event.set()
        self._executor.cancel()

    @property
    def is_running(self) -> bool:
        """Check if agent is running."""
        return self._running

    @property
    def is_busy(self) -> bool:
        """Check if agent is currently executing a task."""
        return self._current_session_id is not None
