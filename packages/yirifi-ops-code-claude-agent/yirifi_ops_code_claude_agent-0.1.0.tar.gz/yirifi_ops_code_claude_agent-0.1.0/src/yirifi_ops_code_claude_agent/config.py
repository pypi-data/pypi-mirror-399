"""Configuration for Yirifi Ops Claude Code Agent."""
from dataclasses import dataclass, field
from typing import Literal
import os


@dataclass
class AgentConfig:
    """Configuration for the Claude Code agent."""

    # Server connection
    flask_url: str = field(default_factory=lambda: os.getenv('FLASK_URL', 'http://localhost:5000'))
    api_token: str = field(default_factory=lambda: os.getenv('AGENT_API_TOKEN', ''))

    # Agent identity
    agent_name: str = field(default_factory=lambda: os.getenv('AGENT_NAME', 'claude-agent-1'))
    agent_type: str = field(default_factory=lambda: os.getenv('AGENT_TYPE', 'mac'))

    # Operating mode
    mode: Literal['polling', 'websocket'] = field(
        default_factory=lambda: os.getenv('AGENT_MODE', 'polling')  # type: ignore
    )

    # Redis config (for polling mode)
    redis_url: str = field(default_factory=lambda: os.getenv('REDIS_URL', 'redis://localhost:6379/0'))
    task_queue_name: str = 'claude_tasks'
    poll_interval: int = 5  # seconds

    # WebSocket config
    ws_reconnect_delay: int = 5  # seconds
    ws_max_reconnect_delay: int = 60  # seconds (with exponential backoff)

    # Heartbeat config
    heartbeat_interval: int = 30  # seconds

    # Claude Code execution
    claude_path: str = field(default_factory=lambda: os.getenv('CLAUDE_PATH', 'claude'))
    default_timeout: int = 600  # 10 minutes
    output_format: str = 'stream-json'

    # Allowed tools (default set)
    default_allowed_tools: list[str] = field(
        default_factory=lambda: ['Read', 'Edit', 'Bash', 'Write', 'Glob', 'Grep']
    )

    # Logging
    log_level: str = field(default_factory=lambda: os.getenv('LOG_LEVEL', 'INFO'))

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if not self.flask_url:
            raise ValueError('FLASK_URL is required')
        if self.mode not in ('polling', 'websocket'):
            raise ValueError(f"Invalid mode: {self.mode}. Must be 'polling' or 'websocket'")

    @property
    def api_base_url(self) -> str:
        """Get the API base URL."""
        return f"{self.flask_url.rstrip('/')}/api/v1"

    @property
    def ws_url(self) -> str:
        """Get the WebSocket URL."""
        base = self.flask_url.replace('http://', 'ws://').replace('https://', 'wss://')
        return f"{base.rstrip('/')}/claude"

    @property
    def headers(self) -> dict[str, str]:
        """Get default headers for API requests."""
        headers = {'Content-Type': 'application/json'}
        if self.api_token:
            headers['Authorization'] = f'Bearer {self.api_token}'
        return headers


def load_config() -> AgentConfig:
    """Load configuration from environment variables."""
    return AgentConfig()
