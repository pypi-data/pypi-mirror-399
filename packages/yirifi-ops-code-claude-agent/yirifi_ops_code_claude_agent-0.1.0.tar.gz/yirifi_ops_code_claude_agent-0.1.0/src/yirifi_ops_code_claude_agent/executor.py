"""Claude Code executor - manages subprocess execution."""
import asyncio
import logging
import os
import shutil
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from .config import AgentConfig
from .stream_parser import EventType, StreamEvent, StreamParser

logger = logging.getLogger(__name__)


@dataclass
class ExecutionResult:
    """Result of a Claude Code execution."""
    exit_code: int
    events: list[StreamEvent]
    error: str | None = None
    duration_ms: int = 0


class ClaudeExecutor:
    """
    Executor for Claude Code CLI.

    Manages the execution of Claude Code as a subprocess, parsing
    the stream-json output and handling interactive prompts.
    """

    def __init__(
        self,
        config: AgentConfig,
        on_event: Callable[[StreamEvent], None] | None = None,
        on_prompt: Callable[[StreamEvent], str | None] | None = None,
    ) -> None:
        """
        Initialize the executor.

        Args:
            config: Agent configuration
            on_event: Callback for each stream event
            on_prompt: Callback for permission prompts, returns user response
        """
        self.config = config
        self.on_event = on_event or (lambda e: None)
        self.on_prompt = on_prompt
        self._process: subprocess.Popen | None = None
        self._cancelled = False

    def execute(
        self,
        prompt: str,
        working_dir: str,
        allowed_tools: list[str] | None = None,
        timeout: int | None = None,
        env_vars: dict[str, str] | None = None,
    ) -> ExecutionResult:
        """
        Execute a Claude Code task synchronously.

        Args:
            prompt: The prompt/task to execute
            working_dir: Working directory for execution
            allowed_tools: List of allowed tools (uses default if None)
            timeout: Timeout in seconds (uses default if None)
            env_vars: Additional environment variables

        Returns:
            ExecutionResult with exit code and events
        """
        start_time = time.monotonic()

        # Validate working directory
        work_path = Path(working_dir)
        if not work_path.exists():
            return ExecutionResult(
                exit_code=1,
                events=[],
                error=f"Working directory does not exist: {working_dir}"
            )

        # Build command
        cmd = self._build_command(prompt, working_dir, allowed_tools)
        logger.info(f"Executing: {' '.join(cmd[:3])}...")

        # Set up environment
        env = os.environ.copy()
        if env_vars:
            env.update(env_vars)

        # Set up parser
        parser = StreamParser()
        events: list[StreamEvent] = []
        error: str | None = None

        try:
            # Start process
            self._process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                cwd=working_dir,
                env=env,
                text=True,
                bufsize=1,  # Line buffered
            )

            effective_timeout = timeout or self.config.default_timeout
            deadline = time.monotonic() + effective_timeout

            # Read stdout line by line
            assert self._process.stdout is not None
            for line in iter(self._process.stdout.readline, ''):
                if self._cancelled:
                    self._terminate_process()
                    error = "Execution cancelled"
                    break

                if time.monotonic() > deadline:
                    self._terminate_process()
                    error = f"Execution timed out after {effective_timeout}s"
                    break

                event = parser.parse_line(line)
                if event:
                    events.append(event)
                    self.on_event(event)

                    # Handle permission requests
                    if event.is_permission_request and self.on_prompt:
                        response = self.on_prompt(event)
                        if response and self._process.stdin:
                            self._process.stdin.write(f"{response}\n")
                            self._process.stdin.flush()

            # Wait for process to complete
            self._process.wait()
            exit_code = self._process.returncode

            # Capture any stderr
            assert self._process.stderr is not None
            stderr_output = self._process.stderr.read()
            if stderr_output and not error:
                logger.warning(f"Claude stderr: {stderr_output}")

        except Exception as e:
            logger.exception("Error during execution")
            error = str(e)
            exit_code = 1
            if self._process:
                self._terminate_process()

        finally:
            self._process = None
            self._cancelled = False

        duration_ms = int((time.monotonic() - start_time) * 1000)

        return ExecutionResult(
            exit_code=exit_code if error is None else 1,
            events=events,
            error=error,
            duration_ms=duration_ms
        )

    async def execute_async(
        self,
        prompt: str,
        working_dir: str,
        allowed_tools: list[str] | None = None,
        timeout: int | None = None,
        env_vars: dict[str, str] | None = None,
    ) -> ExecutionResult:
        """
        Execute a Claude Code task asynchronously.

        Args:
            prompt: The prompt/task to execute
            working_dir: Working directory for execution
            allowed_tools: List of allowed tools (uses default if None)
            timeout: Timeout in seconds (uses default if None)
            env_vars: Additional environment variables

        Returns:
            ExecutionResult with exit code and events
        """
        start_time = time.monotonic()

        # Validate working directory
        work_path = Path(working_dir)
        if not work_path.exists():
            return ExecutionResult(
                exit_code=1,
                events=[],
                error=f"Working directory does not exist: {working_dir}"
            )

        # Build command
        cmd = self._build_command(prompt, working_dir, allowed_tools)
        logger.info(f"Executing async: {' '.join(cmd[:3])}...")

        # Set up environment
        env = os.environ.copy()
        if env_vars:
            env.update(env_vars)

        # Set up parser
        parser = StreamParser()
        events: list[StreamEvent] = []
        error: str | None = None
        effective_timeout = timeout or self.config.default_timeout

        try:
            # Start async process
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                stdin=asyncio.subprocess.PIPE,
                cwd=working_dir,
                env=env,
            )

            async def read_stdout():
                nonlocal error
                assert process.stdout is not None
                while True:
                    if self._cancelled:
                        error = "Execution cancelled"
                        break

                    line = await process.stdout.readline()
                    if not line:
                        break

                    event = parser.parse_line(line.decode('utf-8'))
                    if event:
                        events.append(event)
                        self.on_event(event)

                        # Handle permission requests
                        if event.is_permission_request and self.on_prompt:
                            response = self.on_prompt(event)
                            if response and process.stdin:
                                process.stdin.write(f"{response}\n".encode())
                                await process.stdin.drain()

            # Run with timeout
            try:
                await asyncio.wait_for(read_stdout(), timeout=effective_timeout)
                await process.wait()
            except asyncio.TimeoutError:
                error = f"Execution timed out after {effective_timeout}s"
                process.terminate()
                await process.wait()

            exit_code = process.returncode or 0

        except Exception as e:
            logger.exception("Error during async execution")
            error = str(e)
            exit_code = 1

        finally:
            self._cancelled = False

        duration_ms = int((time.monotonic() - start_time) * 1000)

        return ExecutionResult(
            exit_code=exit_code if error is None else 1,
            events=events,
            error=error,
            duration_ms=duration_ms
        )

    def cancel(self) -> None:
        """Cancel the current execution."""
        self._cancelled = True
        if self._process:
            self._terminate_process()

    def _build_command(
        self,
        prompt: str,
        working_dir: str,
        allowed_tools: list[str] | None,
    ) -> list[str]:
        """Build the Claude Code command."""
        claude_path = self._find_claude_path()

        cmd = [
            claude_path,
            '-p', prompt,
            '--output-format', self.config.output_format,
        ]

        # Add allowed tools
        tools = allowed_tools or self.config.default_allowed_tools
        if tools:
            cmd.extend(['--allowedTools', ','.join(tools)])

        return cmd

    def _find_claude_path(self) -> str:
        """Find the Claude Code CLI path."""
        # Check configured path first
        if self.config.claude_path and shutil.which(self.config.claude_path):
            return self.config.claude_path

        # Try common paths
        common_paths = [
            'claude',
            '/usr/local/bin/claude',
            '/opt/homebrew/bin/claude',
            os.path.expanduser('~/.local/bin/claude'),
        ]

        for path in common_paths:
            if shutil.which(path):
                return path

        raise FileNotFoundError(
            "Claude Code CLI not found. Please install it or set CLAUDE_PATH."
        )

    def _terminate_process(self) -> None:
        """Terminate the current process gracefully."""
        if not self._process:
            return

        try:
            # Try graceful termination first
            self._process.terminate()
            try:
                self._process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # Force kill if needed
                self._process.kill()
                self._process.wait()
        except Exception as e:
            logger.warning(f"Error terminating process: {e}")


class MockExecutor(ClaudeExecutor):
    """Mock executor for testing without actual Claude Code."""

    def execute(
        self,
        prompt: str,
        working_dir: str,
        allowed_tools: list[str] | None = None,
        timeout: int | None = None,
        env_vars: dict[str, str] | None = None,
    ) -> ExecutionResult:
        """Execute a mock task that simulates Claude Code output."""
        logger.info(f"[MOCK] Executing: {prompt[:50]}...")

        # Simulate some processing time
        events = []
        parser = StreamParser()

        # Emit thinking event
        event = parser.parse_line('{"type": "thinking", "content": "Analyzing the request..."}')
        if event:
            events.append(event)
            self.on_event(event)
            time.sleep(0.5)

        # Emit assistant message
        event = parser.parse_line(f'{{"type": "assistant", "content": "I will help you with: {prompt[:100]}"}}')
        if event:
            events.append(event)
            self.on_event(event)
            time.sleep(0.5)

        # Emit tool use
        event = parser.parse_line('{"type": "tool_use", "tool": "Read", "input": {"file_path": "/example/file.py"}}')
        if event:
            events.append(event)
            self.on_event(event)
            time.sleep(0.3)

        # Emit tool result
        event = parser.parse_line('{"type": "tool_result", "content": "# Example file content\\ndef hello():\\n    pass"}')
        if event:
            events.append(event)
            self.on_event(event)
            time.sleep(0.3)

        # Emit completion
        event = parser.parse_line('{"type": "result", "exit_code": 0, "summary": "Task completed successfully"}')
        if event:
            events.append(event)
            self.on_event(event)

        return ExecutionResult(
            exit_code=0,
            events=events,
            error=None,
            duration_ms=1500
        )
