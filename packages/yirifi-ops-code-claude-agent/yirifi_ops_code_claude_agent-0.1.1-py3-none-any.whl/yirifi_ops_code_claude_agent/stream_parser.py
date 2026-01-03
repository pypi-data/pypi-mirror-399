"""Parser for Claude Code stream-json output format."""
import json
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Generator

logger = logging.getLogger(__name__)


class EventType(str, Enum):
    """Event types from Claude Code stream output."""
    SYSTEM = 'system'
    ASSISTANT = 'assistant'
    TOOL_USE = 'tool_use'
    TOOL_RESULT = 'tool_result'
    THINKING = 'thinking'
    ERROR = 'error'
    PERMISSION_REQUEST = 'permission_request'
    INPUT_REQUEST = 'input_request'  # Generic input request (not just permission)
    PROGRESS = 'progress'  # Progress indicator
    RESULT = 'result'
    UNKNOWN = 'unknown'


@dataclass
class StreamEvent:
    """Parsed event from Claude Code stream."""
    type: EventType
    data: dict[str, Any] = field(default_factory=dict)
    raw: str = ''

    @property
    def is_assistant_message(self) -> bool:
        """Check if this is an assistant text message."""
        return self.type == EventType.ASSISTANT

    @property
    def is_tool_use(self) -> bool:
        """Check if this is a tool use event."""
        return self.type == EventType.TOOL_USE

    @property
    def is_permission_request(self) -> bool:
        """Check if this requires user permission."""
        return self.type == EventType.PERMISSION_REQUEST

    @property
    def is_error(self) -> bool:
        """Check if this is an error event."""
        return self.type == EventType.ERROR

    @property
    def is_complete(self) -> bool:
        """Check if this indicates completion."""
        return self.type == EventType.RESULT

    @property
    def requires_input(self) -> bool:
        """Check if this event requires user input."""
        return self.type in (EventType.PERMISSION_REQUEST, EventType.INPUT_REQUEST)

    @property
    def is_progress(self) -> bool:
        """Check if this is a progress indicator."""
        return self.type == EventType.PROGRESS

    @property
    def is_thinking(self) -> bool:
        """Check if this is a thinking event."""
        return self.type == EventType.THINKING

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'type': self.type.value,
            **self.data
        }


class StreamParser:
    """
    Parser for Claude Code's stream-json output format.

    The stream-json format outputs one JSON object per line, with various
    event types including assistant messages, tool uses, and results.
    """

    def __init__(self) -> None:
        """Initialize the stream parser."""
        self._buffer = ''
        self._sequence_num = 0

    def parse_line(self, line: str) -> StreamEvent | None:
        """
        Parse a single line of stream-json output.

        Args:
            line: A single line from the stream output

        Returns:
            Parsed StreamEvent or None if line is empty/invalid
        """
        line = line.strip()
        if not line:
            return None

        try:
            data = json.loads(line)
            return self._parse_event(data, line)
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON line: {e}")
            # Return as raw text event
            return StreamEvent(
                type=EventType.ASSISTANT,
                data={'message': line, 'raw': True},
                raw=line
            )

    def _parse_event(self, data: dict[str, Any], raw: str) -> StreamEvent:
        """Parse a JSON object into a StreamEvent."""
        self._sequence_num += 1
        event_type = self._determine_event_type(data)

        # Extract relevant fields based on event type
        event_data: dict[str, Any] = {'sequence_num': self._sequence_num}

        if event_type == EventType.ASSISTANT:
            event_data['message'] = data.get('content', data.get('text', ''))
            if 'thinking' in data:
                event_data['thinking'] = data['thinking']

        elif event_type == EventType.TOOL_USE:
            event_data['tool_name'] = data.get('tool', data.get('name', 'unknown'))
            event_data['tool_input'] = data.get('input', data.get('parameters', {}))
            event_data['tool_use_id'] = data.get('id', data.get('tool_use_id'))

        elif event_type == EventType.TOOL_RESULT:
            event_data['tool_use_id'] = data.get('tool_use_id', data.get('id'))
            event_data['content'] = data.get('content', data.get('output', ''))
            event_data['is_error'] = data.get('is_error', False)

        elif event_type == EventType.PERMISSION_REQUEST:
            event_data['prompt_id'] = data.get('id', data.get('prompt_id'))
            event_data['question'] = data.get('question', data.get('message', ''))
            event_data['options'] = data.get('options', [])
            event_data['tool_name'] = data.get('tool', data.get('tool_name'))
            event_data['timeout'] = data.get('timeout', 300)

        elif event_type == EventType.THINKING:
            event_data['content'] = data.get('thinking', data.get('content', ''))

        elif event_type == EventType.ERROR:
            event_data['message'] = data.get('error', data.get('message', 'Unknown error'))
            event_data['code'] = data.get('code')

        elif event_type == EventType.RESULT:
            event_data['exit_code'] = data.get('exit_code', data.get('exitCode', 0))
            event_data['summary'] = data.get('summary', '')

        elif event_type == EventType.SYSTEM:
            event_data['message'] = data.get('message', data.get('content', ''))

        else:
            # Include all data for unknown types
            event_data.update(data)

        return StreamEvent(type=event_type, data=event_data, raw=raw)

    def _determine_event_type(self, data: dict[str, Any]) -> EventType:
        """Determine the event type from JSON data."""
        # Check for explicit type field
        if 'type' in data:
            type_str = data['type'].lower()
            type_map = {
                'assistant': EventType.ASSISTANT,
                'text': EventType.ASSISTANT,
                'message': EventType.ASSISTANT,
                'tool_use': EventType.TOOL_USE,
                'tool_call': EventType.TOOL_USE,
                'tool_result': EventType.TOOL_RESULT,
                'tool_output': EventType.TOOL_RESULT,
                'thinking': EventType.THINKING,
                'error': EventType.ERROR,
                'permission_request': EventType.PERMISSION_REQUEST,
                'permission': EventType.PERMISSION_REQUEST,
                'question': EventType.PERMISSION_REQUEST,
                'input_request': EventType.INPUT_REQUEST,
                'input': EventType.INPUT_REQUEST,
                'progress': EventType.PROGRESS,
                'status': EventType.PROGRESS,
                'result': EventType.RESULT,
                'complete': EventType.RESULT,
                'done': EventType.RESULT,
                'system': EventType.SYSTEM,
            }
            return type_map.get(type_str, EventType.UNKNOWN)

        # Infer type from structure
        if 'tool' in data or 'tool_use' in data or ('name' in data and 'input' in data):
            return EventType.TOOL_USE
        if 'tool_result' in data or ('content' in data and 'tool_use_id' in data):
            return EventType.TOOL_RESULT
        if 'question' in data and 'options' in data:
            return EventType.PERMISSION_REQUEST
        if 'thinking' in data and not 'content' in data:
            return EventType.THINKING
        if 'error' in data:
            return EventType.ERROR
        if 'exit_code' in data or 'exitCode' in data:
            return EventType.RESULT
        if 'content' in data or 'text' in data:
            return EventType.ASSISTANT

        return EventType.UNKNOWN

    def parse_stream(self, stream: Generator[str, None, None]) -> Generator[StreamEvent, None, None]:
        """
        Parse a stream of lines.

        Args:
            stream: Generator yielding lines from Claude Code output

        Yields:
            Parsed StreamEvent objects
        """
        for line in stream:
            event = self.parse_line(line)
            if event:
                yield event

    def reset(self) -> None:
        """Reset parser state for a new session."""
        self._buffer = ''
        self._sequence_num = 0


def parse_stream_output(output: str) -> list[StreamEvent]:
    """
    Convenience function to parse complete stream output.

    Args:
        output: Complete stream-json output as a string

    Returns:
        List of parsed StreamEvent objects
    """
    parser = StreamParser()
    events = []
    for line in output.splitlines():
        event = parser.parse_line(line)
        if event:
            events.append(event)
    return events
