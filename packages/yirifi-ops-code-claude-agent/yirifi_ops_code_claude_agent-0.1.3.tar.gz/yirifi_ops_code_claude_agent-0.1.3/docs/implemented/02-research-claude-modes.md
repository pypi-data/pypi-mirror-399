# Plan: Enhance Claude Code Agent for Better Debugging and Flexibility

## Overview
Enhance the `yirifi-ops-code-claude-agent` to include comprehensive debugging information, configurable permission modes, and better subprocess monitoring.

## Research Summary

From [Claude Code CLI Reference](https://code.claude.com/docs/en/cli-reference) and [Headless Mode Docs](https://code.claude.com/docs/en/headless):

**Output Formats:**
- `--output-format text` (default)
- `--output-format json` (single JSON at completion)
- `--output-format stream-json` (realtime streaming)

**Permission Modes:**
- `--dangerously-skip-permissions` - Skip ALL prompts (YOLO mode)
- `--allowedTools <tools>` - Granular tool permissions (safer)

**Other Useful Flags:**
- `--append-system-prompt` - Add custom instructions
- `--max-turns N` - Limit conversation turns
- `--model <model>` - Specify model

## Files to Modify

1. `config.py` - Add new configuration options
2. `executor.py` - Enhanced logging, process monitoring, flexible CLI options
3. `run.py` - Expose new CLI arguments
4. `stream_parser.py` - Minor enhancements for state detection

---

## Implementation Steps

### Step 1: Enhance `config.py`

Add new configuration fields:

```python
@dataclass
class AgentConfig:
    # ... existing fields ...

    # Claude Code CLI options
    output_format: Literal['text', 'json', 'stream-json'] = 'stream-json'
    permission_mode: Literal['skip_all', 'allowed_tools', 'interactive'] = 'skip_all'
    max_turns: int | None = None  # None = unlimited
    append_system_prompt: str | None = None  # Custom system instructions
    model: str | None = None  # Override model (e.g., 'claude-sonnet-4-20250514')

    # Process monitoring
    process_check_interval: float = 5.0  # Seconds between health checks
    process_hang_timeout: int = 120  # Consider hung if no output for this long

    # Debug options
    debug_subprocess: bool = False  # Log subprocess details
    capture_stderr: bool = True  # Always capture stderr
```

### Step 2: Enhance `executor.py`

**A. Add ExecutionContext dataclass for tracking:**

```python
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
    state: str = 'starting'  # starting, running, waiting_input, completing, done
```

**B. Improve `_build_command()` method:**

```python
def _build_command(self, prompt: str, working_dir: str, allowed_tools: list[str] | None) -> list[str]:
    """Build the Claude Code command with all configured options."""
    claude_path = self._find_claude_path()

    cmd = [
        claude_path,
        '-p', prompt,
        '--output-format', self.config.output_format,
    ]

    # Permission mode
    if self.config.permission_mode == 'skip_all':
        cmd.append('--dangerously-skip-permissions')
    elif self.config.permission_mode == 'allowed_tools':
        tools = allowed_tools or self.config.default_allowed_tools
        if tools:
            cmd.extend(['--allowedTools', ','.join(tools)])
    # 'interactive' mode: no permission flags, will prompt

    # Optional flags
    if self.config.max_turns:
        cmd.extend(['--max-turns', str(self.config.max_turns)])

    if self.config.append_system_prompt:
        cmd.extend(['--append-system-prompt', self.config.append_system_prompt])

    if self.config.model:
        cmd.extend(['--model', self.config.model])

    return cmd
```

**C. Add process monitoring thread:**

```python
def _start_process_monitor(self, context: ExecutionContext) -> threading.Thread:
    """Start a thread to monitor subprocess health."""
    def monitor():
        while context.state not in ('done', 'error'):
            time.sleep(self.config.process_check_interval)

            if not self._process:
                break

            # Check if process is still running
            poll_result = self._process.poll()
            if poll_result is not None:
                logger.info(f"[PID:{context.process_pid}] Process exited with code {poll_result}")
                break

            # Check for hang (no output for too long)
            since_last_output = time.monotonic() - context.last_output_time
            if since_last_output > self.config.process_hang_timeout:
                logger.warning(
                    f"[PID:{context.process_pid}] No output for {since_last_output:.1f}s - possible hang"
                )

            # Log process state
            if self.config.debug_subprocess:
                logger.debug(
                    f"[PID:{context.process_pid}] state={context.state} "
                    f"events={context.events_received} "
                    f"elapsed={time.monotonic() - context.start_time:.1f}s"
                )

    thread = threading.Thread(target=monitor, daemon=True)
    thread.start()
    return thread
```

**D. Enhanced execute() with detailed logging:**

```python
def execute(self, prompt: str, working_dir: str, ...) -> ExecutionResult:
    # Create execution context
    context = ExecutionContext(
        session_id=session_id,  # Pass from task
        start_time=time.monotonic(),
        working_dir=working_dir,
    )

    # Build command
    cmd = self._build_command(prompt, working_dir, allowed_tools)
    context.command = cmd

    # Log full command (with prompt truncated)
    logger.info(f"Command: {' '.join(cmd[:3])}... --output-format {self.config.output_format}")
    logger.debug(f"Full command: {cmd}")
    logger.info(f"Working directory: {working_dir}")
    logger.info(f"Permission mode: {self.config.permission_mode}")

    # Start process
    self._process = subprocess.Popen(...)
    context.process_pid = self._process.pid
    context.state = 'running'
    context.last_output_time = time.monotonic()

    logger.info(f"Started Claude process PID: {context.process_pid}")

    # Start monitor thread
    monitor_thread = self._start_process_monitor(context)

    # ... process output with context updates ...

    # On each event:
    context.events_received += 1
    context.last_output_time = time.monotonic()

    # Detect waiting for input
    if event.is_permission_request:
        context.state = 'waiting_input'
        logger.info(f"[PID:{context.process_pid}] Waiting for user input...")
```

### Step 3: Enhance `run.py`

Add new CLI arguments:

```python
parser.add_argument(
    '--permission-mode',
    choices=['skip_all', 'allowed_tools', 'interactive'],
    default='skip_all',
    help='Permission handling mode (default: skip_all)',
)

parser.add_argument(
    '--output-format',
    choices=['text', 'json', 'stream-json'],
    default='stream-json',
    help='Claude output format (default: stream-json)',
)

parser.add_argument(
    '--max-turns',
    type=int,
    default=None,
    help='Maximum conversation turns',
)

parser.add_argument(
    '--system-prompt',
    type=str,
    default=None,
    help='Additional system prompt to append',
)

parser.add_argument(
    '--debug-subprocess',
    action='store_true',
    help='Enable detailed subprocess debugging',
)
```

Update logging output:

```python
logger.info(f"Permission Mode: {config.permission_mode}")
logger.info(f"Output Format: {config.output_format}")
if config.max_turns:
    logger.info(f"Max Turns: {config.max_turns}")
```

### Step 4: Enhance `stream_parser.py`

Add state detection helpers:

```python
class EventType(str, Enum):
    # ... existing ...
    INPUT_REQUEST = 'input_request'  # Generic input request (not just permission)
    PROGRESS = 'progress'  # Progress indicator

@dataclass
class StreamEvent:
    # ... existing ...

    @property
    def requires_input(self) -> bool:
        """Check if this event requires user input."""
        return self.type in (EventType.PERMISSION_REQUEST, EventType.INPUT_REQUEST)

    @property
    def is_progress(self) -> bool:
        """Check if this is a progress indicator."""
        return self.type == EventType.PROGRESS
```

### Step 5: Add ExecutionResult enhancements

```python
@dataclass
class ExecutionResult:
    exit_code: int
    events: list[StreamEvent]
    error: str | None = None
    duration_ms: int = 0

    # New fields
    process_pid: int | None = None
    command: list[str] = field(default_factory=list)
    working_dir: str = ''
    events_by_type: dict[str, int] = field(default_factory=dict)  # Count by type

    def summary(self) -> str:
        """Generate a human-readable summary."""
        return (
            f"Exit: {self.exit_code} | "
            f"Duration: {self.duration_ms}ms | "
            f"Events: {len(self.events)} | "
            f"PID: {self.process_pid}"
        )
```

---

## Testing

After implementation:

1. **Test skip_all mode:**
   ```bash
   yirifi-claude-agent --mode polling --permission-mode skip_all --debug-subprocess
   ```

2. **Test allowed_tools mode:**
   ```bash
   yirifi-claude-agent --mode polling --permission-mode allowed_tools --debug-subprocess
   ```

3. **Test stream-json vs json:**
   ```bash
   yirifi-claude-agent --output-format stream-json --debug-subprocess
   yirifi-claude-agent --output-format json --debug-subprocess
   ```

4. Verify logging shows:
   - Process PID
   - Full command (in debug)
   - Working directory
   - Event counts
   - Timing information
   - Hang detection warnings
