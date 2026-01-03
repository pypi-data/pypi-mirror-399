"""Claude Code executor - manages subprocess execution."""
import asyncio
import json as json_module
import logging
import os
import shutil
import subprocess
import threading
import time
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from .config import AgentConfig
from .stream_parser import EventType, StreamEvent, StreamParser

logger = logging.getLogger(__name__)


@dataclass
class ExecutionContext:
    """Context for tracking a Claude execution."""

    session_id: int | None = None
    process_pid: int | None = None
    start_time: float = 0.0
    last_output_time: float = 0.0
    command: list[str] = field(default_factory=list)
    working_dir: str = ''
    events_received: int = 0
    state: str = 'starting'  # starting, running, waiting_input, completing, done, error

    def elapsed_seconds(self) -> float:
        """Get elapsed time since start."""
        return time.monotonic() - self.start_time if self.start_time else 0.0

    def time_since_last_output(self) -> float:
        """Get time since last output."""
        return time.monotonic() - self.last_output_time if self.last_output_time else 0.0


@dataclass
class ExecutionResult:
    """Result of a Claude Code execution."""

    exit_code: int
    events: list[StreamEvent]
    error: str | None = None
    duration_ms: int = 0

    # Enhanced fields
    process_pid: int | None = None
    command: list[str] = field(default_factory=list)
    working_dir: str = ''
    events_by_type: dict[str, int] = field(default_factory=dict)

    def summary(self) -> str:
        """Generate a human-readable summary."""
        return (
            f"Exit: {self.exit_code} | "
            f"Duration: {self.duration_ms}ms | "
            f"Events: {len(self.events)} | "
            f"PID: {self.process_pid}"
        )


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
        self._context: ExecutionContext | None = None
        self._monitor_thread: threading.Thread | None = None

    def execute(
        self,
        prompt: str,
        working_dir: str,
        allowed_tools: list[str] | None = None,
        timeout: int | None = None,
        env_vars: dict[str, str] | None = None,
        session_id: int | None = None,
    ) -> ExecutionResult:
        """
        Execute a Claude Code task synchronously.

        Args:
            prompt: The prompt/task to execute
            working_dir: Working directory for execution
            allowed_tools: List of allowed tools (uses default if None)
            timeout: Timeout in seconds (uses default if None)
            env_vars: Additional environment variables
            session_id: Optional session ID for tracking

        Returns:
            ExecutionResult with exit code and events
        """
        start_time = time.monotonic()

        # Create execution context
        self._context = ExecutionContext(
            session_id=session_id,
            start_time=start_time,
            last_output_time=start_time,
            working_dir=working_dir,
            state='starting',
        )

        # Validate working directory
        work_path = Path(working_dir)
        if not work_path.exists():
            logger.error(f"Working directory does not exist: {working_dir}")
            return ExecutionResult(
                exit_code=1,
                events=[],
                error=f"Working directory does not exist: {working_dir}",
                working_dir=working_dir,
            )

        # Build command
        cmd = self._build_command(prompt, working_dir, allowed_tools)
        self._context.command = cmd

        # Log execution details
        logger.info(f"[Session:{session_id}] Executing Claude Code")
        logger.info(f"  Working dir: {working_dir}")
        logger.info(f"  Output format: {self.config.output_format}")
        logger.info(f"  Permission mode: {self.config.permission_mode}")
        # Always log the full command for debugging
        logger.info(f"  Full command: {cmd}")
        if not self.config.debug_subprocess:
            # Log truncated command
            logger.info(f"  Command: claude -p '{prompt[:50]}...' --output-format {self.config.output_format}")

        # Set up environment
        env = os.environ.copy()
        if env_vars:
            env.update(env_vars)

        # Set up parser
        parser = StreamParser()
        events: list[StreamEvent] = []
        event_counts: Counter = Counter()
        error: str | None = None
        exit_code = 0

        try:
            # Determine stdin handling based on permission mode
            # For skip_all mode, we don't need stdin (no permission prompts)
            # For other modes, we might need to respond to permission prompts
            if self.config.permission_mode == 'skip_all':
                stdin_arg = subprocess.DEVNULL
            else:
                stdin_arg = subprocess.PIPE

            # Start process
            self._process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=stdin_arg,
                cwd=working_dir,
                env=env,
                text=True,
                bufsize=1,  # Line buffered
            )

            self._context.process_pid = self._process.pid
            self._context.state = 'running'
            logger.info(f"  Started process PID: {self._process.pid}")

            # Start monitoring thread
            self._start_process_monitor()

            effective_timeout = timeout or self.config.default_timeout

            # Handle different output formats
            if self.config.output_format == 'json':
                # JSON mode: use communicate() to get all output at once
                exit_code, error = self._execute_json_mode(
                    effective_timeout, parser, events, event_counts
                )
            else:
                # stream-json or text mode: read line by line
                exit_code, error = self._execute_stream_mode(
                    effective_timeout, parser, events, event_counts
                )

        except Exception as e:
            logger.exception(f"[PID:{self._context.process_pid}] Error during execution")
            error = str(e)
            exit_code = 1
            self._context.state = 'error'
            if self._process:
                self._terminate_process()

        finally:
            self._context.state = 'done'
            self._process = None
            self._cancelled = False

        duration_ms = int((time.monotonic() - start_time) * 1000)

        # Build result with enhanced fields
        result = ExecutionResult(
            exit_code=exit_code if error is None else 1,
            events=events,
            error=error,
            duration_ms=duration_ms,
            process_pid=self._context.process_pid,
            command=cmd,
            working_dir=working_dir,
            events_by_type=dict(event_counts),
        )

        logger.info(f"[PID:{self._context.process_pid}] Execution complete: {result.summary()}")
        if event_counts:
            logger.info(f"  Event breakdown: {dict(event_counts)}")

        self._context = None
        return result

    def _execute_json_mode(
        self,
        timeout: int,
        parser: StreamParser,
        events: list[StreamEvent],
        event_counts: Counter,
    ) -> tuple[int, str | None]:
        """Execute in JSON output mode using communicate()."""
        error: str | None = None
        exit_code = 0

        assert self._process is not None
        assert self._context is not None

        try:
            logger.debug(f"[PID:{self._context.process_pid}] Using JSON mode with communicate()")
            stdout_output, stderr_output = self._process.communicate(timeout=timeout)
            exit_code = self._process.returncode

            self._context.last_output_time = time.monotonic()

            # Parse the JSON output
            if stdout_output:
                if self.config.debug_subprocess:
                    logger.debug(f"[PID:{self._context.process_pid}] Output: {stdout_output[:500]}...")

                try:
                    result_data = json_module.loads(stdout_output)
                    event = StreamEvent(
                        type=EventType.RESULT,
                        data=result_data,
                    )
                    events.append(event)
                    event_counts[EventType.RESULT.value] += 1
                    self._context.events_received += 1
                    self.on_event(event)
                except json_module.JSONDecodeError as e:
                    logger.warning(f"[PID:{self._context.process_pid}] Failed to parse JSON: {e}")
                    # Try to extract useful info anyway
                    event = StreamEvent(
                        type=EventType.ASSISTANT,
                        data={'message': stdout_output, 'raw': True},
                    )
                    events.append(event)
                    event_counts[EventType.ASSISTANT.value] += 1
                    self.on_event(event)

            if stderr_output:
                logger.warning(f"[PID:{self._context.process_pid}] Stderr: {stderr_output}")

        except subprocess.TimeoutExpired:
            logger.error(f"[PID:{self._context.process_pid}] Timeout after {timeout}s")
            self._terminate_process()
            error = f"Execution timed out after {timeout}s"
            exit_code = 1

        return exit_code, error

    def _execute_stream_mode(
        self,
        timeout: int,
        parser: StreamParser,
        events: list[StreamEvent],
        event_counts: Counter,
    ) -> tuple[int, str | None]:
        """Execute in stream-json mode reading line by line."""
        error: str | None = None
        exit_code = 0

        assert self._process is not None
        assert self._process.stdout is not None
        assert self._context is not None

        deadline = time.monotonic() + timeout

        logger.debug(f"[PID:{self._context.process_pid}] Using stream mode, reading lines...")

        for line in iter(self._process.stdout.readline, ''):
            if self._cancelled:
                logger.info(f"[PID:{self._context.process_pid}] Execution cancelled")
                self._terminate_process()
                error = "Execution cancelled"
                break

            if time.monotonic() > deadline:
                logger.error(f"[PID:{self._context.process_pid}] Timeout after {timeout}s")
                self._terminate_process()
                error = f"Execution timed out after {timeout}s"
                break

            # Update last output time
            self._context.last_output_time = time.monotonic()

            # Parse the line
            event = parser.parse_line(line)
            if event:
                events.append(event)
                event_counts[event.type.value] += 1
                self._context.events_received += 1
                self.on_event(event)

                # Update state based on event
                if event.is_permission_request:
                    self._context.state = 'waiting_input'
                    logger.info(f"[PID:{self._context.process_pid}] Waiting for user input...")

                # Handle permission requests (only if stdin is available)
                if event.is_permission_request and self.on_prompt and self._process.stdin:
                    response = self.on_prompt(event)
                    if response:
                        self._process.stdin.write(f"{response}\n")
                        self._process.stdin.flush()
                        self._context.state = 'running'

                if self.config.debug_subprocess:
                    logger.debug(
                        f"[PID:{self._context.process_pid}] Event: {event.type.value} "
                        f"(total: {self._context.events_received})"
                    )

        # Wait for process to complete
        self._process.wait()
        exit_code = self._process.returncode

        # Capture any stderr
        if self._process.stderr:
            stderr_output = self._process.stderr.read()
            if stderr_output and not error:
                logger.warning(f"[PID:{self._context.process_pid}] Stderr: {stderr_output}")

        return exit_code, error

    def _start_process_monitor(self) -> None:
        """Start a thread to monitor subprocess health."""
        if not self._context:
            return

        def monitor():
            while self._context and self._context.state not in ('done', 'error'):
                time.sleep(self.config.process_check_interval)

                if not self._process or not self._context:
                    break

                # Check if process is still running
                poll_result = self._process.poll()
                if poll_result is not None:
                    logger.debug(
                        f"[PID:{self._context.process_pid}] Process exited with code {poll_result}"
                    )
                    break

                # Check for hang (no output for too long)
                since_last_output = self._context.time_since_last_output()
                if since_last_output > self.config.process_hang_timeout:
                    logger.warning(
                        f"[PID:{self._context.process_pid}] POTENTIAL HANG: "
                        f"No output for {since_last_output:.1f}s "
                        f"(threshold: {self.config.process_hang_timeout}s)"
                    )

                # Log process state periodically
                if self.config.debug_subprocess:
                    logger.debug(
                        f"[PID:{self._context.process_pid}] Monitor: "
                        f"state={self._context.state}, "
                        f"events={self._context.events_received}, "
                        f"elapsed={self._context.elapsed_seconds():.1f}s, "
                        f"since_output={since_last_output:.1f}s"
                    )

        self._monitor_thread = threading.Thread(target=monitor, daemon=True, name='process-monitor')
        self._monitor_thread.start()

    async def execute_async(
        self,
        prompt: str,
        working_dir: str,
        allowed_tools: list[str] | None = None,
        timeout: int | None = None,
        env_vars: dict[str, str] | None = None,
        session_id: int | None = None,
    ) -> ExecutionResult:
        """
        Execute a Claude Code task asynchronously.

        Args:
            prompt: The prompt/task to execute
            working_dir: Working directory for execution
            allowed_tools: List of allowed tools (uses default if None)
            timeout: Timeout in seconds (uses default if None)
            env_vars: Additional environment variables
            session_id: Optional session ID for tracking

        Returns:
            ExecutionResult with exit code and events
        """
        start_time = time.monotonic()

        # Create execution context
        self._context = ExecutionContext(
            session_id=session_id,
            start_time=start_time,
            last_output_time=start_time,
            working_dir=working_dir,
            state='starting',
        )

        # Validate working directory
        work_path = Path(working_dir)
        if not work_path.exists():
            return ExecutionResult(
                exit_code=1,
                events=[],
                error=f"Working directory does not exist: {working_dir}",
                working_dir=working_dir,
            )

        # Build command
        cmd = self._build_command(prompt, working_dir, allowed_tools)
        self._context.command = cmd
        logger.info(f"[Session:{session_id}] Executing async: {' '.join(cmd[:3])}...")
        logger.info(f"  Working dir: {working_dir}")

        # Set up environment
        env = os.environ.copy()
        if env_vars:
            env.update(env_vars)

        # Set up parser
        parser = StreamParser()
        events: list[StreamEvent] = []
        event_counts: Counter = Counter()
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

            self._context.process_pid = process.pid
            self._context.state = 'running'
            logger.info(f"  Started async process PID: {process.pid}")

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

                    self._context.last_output_time = time.monotonic()

                    event = parser.parse_line(line.decode('utf-8'))
                    if event:
                        events.append(event)
                        event_counts[event.type.value] += 1
                        self._context.events_received += 1
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
            self._context.state = 'error'

        finally:
            self._context.state = 'done'
            self._cancelled = False

        duration_ms = int((time.monotonic() - start_time) * 1000)

        result = ExecutionResult(
            exit_code=exit_code if error is None else 1,
            events=events,
            error=error,
            duration_ms=duration_ms,
            process_pid=self._context.process_pid,
            command=cmd,
            working_dir=working_dir,
            events_by_type=dict(event_counts),
        )

        logger.info(f"[PID:{self._context.process_pid}] Async execution complete: {result.summary()}")
        self._context = None
        return result

    def cancel(self) -> None:
        """Cancel the current execution."""
        self._cancelled = True
        if self._process:
            logger.info(f"[PID:{self._process.pid}] Cancelling execution")
            self._terminate_process()

    def _build_command(
        self,
        prompt: str,
        working_dir: str,
        allowed_tools: list[str] | None,
    ) -> list[str]:
        """Build the Claude Code command with all configured options."""
        claude_path = self._find_claude_path()

        cmd = [
            claude_path,
            '-p', prompt,
            '--output-format', self.config.output_format,
        ]

        # Permission mode handling
        if self.config.permission_mode == 'skip_all':
            # Skip all permission prompts (YOLO mode)
            cmd.append('--dangerously-skip-permissions')
        elif self.config.permission_mode == 'allowed_tools':
            # Use granular tool permissions (safer)
            tools = allowed_tools or self.config.default_allowed_tools
            if tools:
                cmd.extend(['--allowedTools', ','.join(tools)])
        # 'interactive' mode: no permission flags, will prompt for everything

        # Optional: max turns
        if self.config.max_turns:
            cmd.extend(['--max-turns', str(self.config.max_turns)])

        # Optional: system prompt
        if self.config.append_system_prompt:
            cmd.extend(['--append-system-prompt', self.config.append_system_prompt])

        # Optional: model override
        if self.config.model:
            cmd.extend(['--model', self.config.model])

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

        pid = self._process.pid
        try:
            # Try graceful termination first
            logger.info(f"[PID:{pid}] Terminating process...")
            self._process.terminate()
            try:
                self._process.wait(timeout=5)
                logger.info(f"[PID:{pid}] Process terminated gracefully")
            except subprocess.TimeoutExpired:
                # Force kill if needed
                logger.warning(f"[PID:{pid}] Force killing process...")
                self._process.kill()
                self._process.wait()
                logger.info(f"[PID:{pid}] Process killed")
        except Exception as e:
            logger.warning(f"[PID:{pid}] Error terminating process: {e}")

    @property
    def current_context(self) -> ExecutionContext | None:
        """Get the current execution context."""
        return self._context


class MockExecutor(ClaudeExecutor):
    """Mock executor for testing without actual Claude Code."""

    def execute(
        self,
        prompt: str,
        working_dir: str,
        allowed_tools: list[str] | None = None,
        timeout: int | None = None,
        env_vars: dict[str, str] | None = None,
        session_id: int | None = None,
    ) -> ExecutionResult:
        """Execute a mock task that simulates Claude Code output."""
        logger.info(f"[MOCK] Executing: {prompt[:50]}...")
        logger.info(f"[MOCK] Working dir: {working_dir}")
        logger.info(f"[MOCK] Permission mode: {self.config.permission_mode}")

        start_time = time.monotonic()

        # Simulate some processing time
        events = []
        event_counts: Counter = Counter()
        parser = StreamParser()

        # Emit thinking event
        event = parser.parse_line('{"type": "thinking", "content": "Analyzing the request..."}')
        if event:
            events.append(event)
            event_counts[event.type.value] += 1
            self.on_event(event)
            time.sleep(0.5)

        # Emit assistant message
        event = parser.parse_line(f'{{"type": "assistant", "content": "I will help you with: {prompt[:100]}"}}')
        if event:
            events.append(event)
            event_counts[event.type.value] += 1
            self.on_event(event)
            time.sleep(0.5)

        # Emit tool use
        event = parser.parse_line('{"type": "tool_use", "tool": "Read", "input": {"file_path": "/example/file.py"}}')
        if event:
            events.append(event)
            event_counts[event.type.value] += 1
            self.on_event(event)
            time.sleep(0.3)

        # Emit tool result
        event = parser.parse_line('{"type": "tool_result", "content": "# Example file content\\ndef hello():\\n    pass"}')
        if event:
            events.append(event)
            event_counts[event.type.value] += 1
            self.on_event(event)
            time.sleep(0.3)

        # Emit completion
        event = parser.parse_line('{"type": "result", "exit_code": 0, "summary": "Task completed successfully"}')
        if event:
            events.append(event)
            event_counts[event.type.value] += 1
            self.on_event(event)

        duration_ms = int((time.monotonic() - start_time) * 1000)

        return ExecutionResult(
            exit_code=0,
            events=events,
            error=None,
            duration_ms=duration_ms,
            process_pid=99999,  # Mock PID
            command=['claude', '-p', prompt[:50], '--mock'],
            working_dir=working_dir,
            events_by_type=dict(event_counts),
        )
