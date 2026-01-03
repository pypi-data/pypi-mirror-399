# 01 - Enhanced Debugging and CLI Options

**Date:** 2025-12-30
**Status:** Implemented
**Files Modified:**
- `src/yirifi_ops_code_claude_agent/config.py`
- `src/yirifi_ops_code_claude_agent/executor.py`
- `src/yirifi_ops_code_claude_agent/run.py`
- `src/yirifi_ops_code_claude_agent/stream_parser.py`

## Overview

This enhancement adds comprehensive debugging capabilities, configurable permission modes, and process monitoring to the Claude Code agent. The goal is to provide better visibility into agent execution, detect hangs, and offer flexibility in how Claude Code permissions are handled.

## Problem Statement

The original agent implementation had several limitations:
1. **Limited debugging visibility**: No process IDs, timing info, or event breakdowns in logs
2. **Hardcoded permission mode**: Only supported `--dangerously-skip-permissions`
3. **No hang detection**: If Claude hung, the agent would wait indefinitely
4. **Minimal CLI options**: Few configuration options exposed via command line

## Solution

### 1. New Configuration Options (`config.py`)

Added the following configuration fields:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `output_format` | `Literal['text', 'json', 'stream-json']` | `stream-json` | Claude CLI output format |
| `permission_mode` | `Literal['skip_all', 'allowed_tools', 'interactive']` | `skip_all` | How to handle permission requests |
| `max_turns` | `int \| None` | `None` | Maximum conversation turns |
| `append_system_prompt` | `str \| None` | `None` | Custom system prompt to append |
| `model` | `str \| None` | `None` | Model override |
| `process_check_interval` | `float` | `5.0` | Seconds between health checks |
| `process_hang_timeout` | `int` | `120` | Seconds before declaring a hang |
| `debug_subprocess` | `bool` | `False` | Enable verbose subprocess logging |

### 2. ExecutionContext Tracking (`executor.py`)

New `ExecutionContext` dataclass for tracking execution state:

```python
@dataclass
class ExecutionContext:
    session_id: int | None = None
    process_pid: int | None = None
    start_time: float = 0.0
    last_output_time: float = 0.0
    command: list[str] = field(default_factory=list)
    working_dir: str = ''
    events_received: int = 0
    state: str = 'starting'  # starting, running, waiting_input, completing, done, error
```

### 3. Process Monitoring Thread

A background thread monitors the Claude subprocess:
- Checks if process is still running every `process_check_interval` seconds
- Logs a warning if no output for `process_hang_timeout` seconds
- Logs periodic state updates when `debug_subprocess` is enabled

### 4. Enhanced ExecutionResult

The result now includes additional debugging information:

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
    events_by_type: dict[str, int] = field(default_factory=dict)
```

### 5. Permission Mode Handling

Three permission modes are now supported:

| Mode | Flag | Description |
|------|------|-------------|
| `skip_all` | `--dangerously-skip-permissions` | Auto-approve everything (YOLO mode) |
| `allowed_tools` | `--allowedTools <list>` | Only allow specific tools |
| `interactive` | (none) | Prompt for all permissions |

### 6. New CLI Arguments (`run.py`)

```
--permission-mode {skip_all,allowed_tools,interactive}
    Permission handling mode (default: skip_all)

--output-format {text,json,stream-json}
    Claude output format (default: stream-json)

--max-turns MAX_TURNS
    Maximum conversation turns (default: unlimited)

--system-prompt SYSTEM_PROMPT
    Additional system prompt to append to Claude

--model MODEL
    Model override (e.g., claude-sonnet-4-20250514)

--debug-subprocess
    Enable detailed subprocess debugging
```

### 7. New Event Types (`stream_parser.py`)

Added new event types for better state detection:
- `INPUT_REQUEST`: Generic input request (not just permission)
- `PROGRESS`: Progress indicator events

New helper properties on `StreamEvent`:
- `requires_input`: True if event requires user input
- `is_progress`: True if event is a progress indicator
- `is_thinking`: True if event is a thinking event

## Usage

### Basic Usage (default skip_all mode)

```bash
yirifi-claude-agent --mode polling --name my-agent
```

### With Debugging Enabled

```bash
yirifi-claude-agent --mode polling --debug-subprocess --verbose
```

Output includes:
```
[Session:123] Executing Claude Code
  Working dir: /path/to/repo
  Output format: stream-json
  Permission mode: skip_all
  Command: claude -p 'Create a file...' --output-format stream-json
  Started process PID: 12345
[PID:12345] Event: assistant (total: 1)
[PID:12345] Event: tool_use (total: 2)
[PID:12345] Execution complete: Exit: 0 | Duration: 5234ms | Events: 8 | PID: 12345
  Event breakdown: {'assistant': 3, 'tool_use': 2, 'tool_result': 2, 'result': 1}
```

### Using allowed_tools Mode (Safer)

```bash
yirifi-claude-agent --permission-mode allowed_tools
```

This uses `--allowedTools Read,Edit,Bash,Write,Glob,Grep` instead of `--dangerously-skip-permissions`.

### With Custom System Prompt

```bash
yirifi-claude-agent --system-prompt "Always explain your reasoning before making changes"
```

### Limiting Conversation Turns

```bash
yirifi-claude-agent --max-turns 10
```

### Using Environment Variables

All options can be set via environment variables:

```bash
export CLAUDE_OUTPUT_FORMAT=stream-json
export CLAUDE_PERMISSION_MODE=skip_all
export CLAUDE_MAX_TURNS=0
export CLAUDE_SYSTEM_PROMPT=""
export CLAUDE_MODEL=""
export DEBUG_SUBPROCESS=true
```

## Log Output Examples

### Normal Execution

```
2025-12-30 18:04:04 [INFO] executor: [Session:3] Executing Claude Code
2025-12-30 18:04:04 [INFO] executor:   Working dir: /Users/user/project
2025-12-30 18:04:04 [INFO] executor:   Output format: stream-json
2025-12-30 18:04:04 [INFO] executor:   Permission mode: skip_all
2025-12-30 18:04:04 [INFO] executor:   Started process PID: 97405
2025-12-30 18:04:10 [INFO] executor: [PID:97405] Execution complete: Exit: 0 | Duration: 6234ms | Events: 12 | PID: 97405
2025-12-30 18:04:10 [INFO] executor:   Event breakdown: {'thinking': 2, 'assistant': 4, 'tool_use': 3, 'tool_result': 2, 'result': 1}
```

### Hang Detection

```
2025-12-30 18:06:04 [WARNING] executor: [PID:97405] POTENTIAL HANG: No output for 125.3s (threshold: 120s)
```

### Debug Mode

```
2025-12-30 18:04:04 [DEBUG] executor:   Full command: claude -p 'Create an HTML file...' --output-format stream-json --dangerously-skip-permissions
2025-12-30 18:04:05 [DEBUG] executor: [PID:97405] Event: thinking (total: 1)
2025-12-30 18:04:05 [DEBUG] executor: [PID:97405] Monitor: state=running, events=1, elapsed=1.2s, since_output=0.1s
2025-12-30 18:04:06 [DEBUG] executor: [PID:97405] Event: assistant (total: 2)
```

## Testing

Test the different modes:

```bash
# Test skip_all mode with debugging
yirifi-claude-agent --mode polling --permission-mode skip_all --debug-subprocess --verbose

# Test allowed_tools mode
yirifi-claude-agent --mode polling --permission-mode allowed_tools --debug-subprocess

# Test with JSON output format
yirifi-claude-agent --mode polling --output-format json --debug-subprocess
```

## References

- [Claude Code CLI Reference](https://code.claude.com/docs/en/cli-reference)
- [Claude Code Headless Mode](https://code.claude.com/docs/en/headless)
- [Claude Code Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices)
