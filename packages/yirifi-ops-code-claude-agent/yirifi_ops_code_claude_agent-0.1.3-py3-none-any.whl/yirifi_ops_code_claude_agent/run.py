#!/usr/bin/env python3
"""
Yirifi Ops Claude Code Agent Entry Point.

This is the main entry point for running the Claude Code agent.
Usage:
    python -m yirifi_ops_code_claude_agent.run [options]
    # or if installed:
    yirifi-claude-agent [options]

Options:
    --mode polling|websocket        Operating mode (default: from AGENT_MODE env or 'polling')
    --name NAME                     Agent name (default: from AGENT_NAME env or 'claude-agent-1')
    --flask-url URL                 Flask server URL (default: from FLASK_URL env)
    --permission-mode MODE          Permission mode: skip_all|allowed_tools|interactive
    --output-format FORMAT          Output format: text|json|stream-json
    --max-turns N                   Maximum conversation turns
    --system-prompt PROMPT          Additional system prompt to append
    --debug-subprocess              Enable detailed subprocess debugging
    --mock                          Use mock executor for testing
    --verbose                       Enable verbose logging
"""
import argparse
import logging
import os
import signal
import sys
from typing import NoReturn

from .agent import ClaudeAgent
from .config import AgentConfig, load_config


def setup_logging(verbose: bool = False, debug_subprocess: bool = False) -> None:
    """Configure logging."""
    level = logging.DEBUG if (verbose or debug_subprocess) else logging.INFO

    logging.basicConfig(
        level=level,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.StreamHandler(sys.stdout),
        ]
    )

    # Reduce noise from third-party libraries
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('socketio').setLevel(logging.WARNING)
    logging.getLogger('engineio').setLevel(logging.WARNING)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Yirifi Ops Claude Code Agent',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with default settings (skip_all permission mode)
  yirifi-claude-agent --mode polling --name my-agent

  # Run with safer allowed_tools permission mode
  yirifi-claude-agent --permission-mode allowed_tools

  # Run with verbose subprocess debugging
  yirifi-claude-agent --debug-subprocess --verbose

  # Run with custom system prompt
  yirifi-claude-agent --system-prompt "Always respond in JSON format"

Environment Variables:
  FLASK_URL               Flask server URL
  REDIS_URL               Redis URL for polling mode
  AGENT_NAME              Agent name
  AGENT_MODE              Operating mode (polling/websocket)
  CLAUDE_OUTPUT_FORMAT    Output format (text/json/stream-json)
  CLAUDE_PERMISSION_MODE  Permission mode (skip_all/allowed_tools/interactive)
  CLAUDE_MAX_TURNS        Maximum conversation turns
  CLAUDE_SYSTEM_PROMPT    Additional system prompt
  CLAUDE_MODEL            Model override
  DEBUG_SUBPROCESS        Enable subprocess debugging (true/false)
        """,
    )

    # Connection settings
    parser.add_argument(
        '--mode',
        choices=['polling', 'websocket'],
        default=os.getenv('AGENT_MODE', 'polling'),
        help='Operating mode (default: polling)',
    )

    parser.add_argument(
        '--name',
        default=os.getenv('AGENT_NAME', 'claude-agent-1'),
        help='Agent name (default: claude-agent-1)',
    )

    parser.add_argument(
        '--flask-url',
        default=os.getenv('FLASK_URL', 'http://localhost:5000'),
        help='Flask server URL',
    )

    parser.add_argument(
        '--redis-url',
        default=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
        help='Redis URL (for polling mode)',
    )

    # Claude Code CLI options
    parser.add_argument(
        '--permission-mode',
        choices=['skip_all', 'allowed_tools', 'interactive'],
        default=os.getenv('CLAUDE_PERMISSION_MODE', 'skip_all'),
        help='Permission handling mode (default: skip_all). '
             'skip_all: auto-approve everything (YOLO), '
             'allowed_tools: only allow specific tools, '
             'interactive: prompt for all permissions',
    )

    parser.add_argument(
        '--output-format',
        choices=['text', 'json', 'stream-json'],
        default=os.getenv('CLAUDE_OUTPUT_FORMAT', 'stream-json'),
        help='Claude output format (default: stream-json)',
    )

    parser.add_argument(
        '--max-turns',
        type=int,
        default=int(os.getenv('CLAUDE_MAX_TURNS', '0')) or None,
        help='Maximum conversation turns (default: unlimited)',
    )

    parser.add_argument(
        '--system-prompt',
        type=str,
        default=os.getenv('CLAUDE_SYSTEM_PROMPT'),
        help='Additional system prompt to append to Claude',
    )

    parser.add_argument(
        '--model',
        type=str,
        default=os.getenv('CLAUDE_MODEL'),
        help='Model override (e.g., claude-sonnet-4-20250514)',
    )

    # Debugging options
    parser.add_argument(
        '--debug-subprocess',
        action='store_true',
        default=os.getenv('DEBUG_SUBPROCESS', '').lower() in ('true', '1', 'yes'),
        help='Enable detailed subprocess debugging',
    )

    parser.add_argument(
        '--mock',
        action='store_true',
        help='Use mock executor for testing',
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging',
    )

    return parser.parse_args()


def main() -> NoReturn:
    """Main entry point."""
    args = parse_args()

    # Set up logging
    setup_logging(verbose=args.verbose, debug_subprocess=args.debug_subprocess)
    logger = logging.getLogger(__name__)

    logger.info("=" * 60)
    logger.info("Yirifi Ops Claude Code Agent")
    logger.info("=" * 60)

    # Override environment variables from CLI args
    if args.flask_url:
        os.environ['FLASK_URL'] = args.flask_url
    if args.redis_url:
        os.environ['REDIS_URL'] = args.redis_url
    if args.name:
        os.environ['AGENT_NAME'] = args.name
    if args.mode:
        os.environ['AGENT_MODE'] = args.mode
    if args.permission_mode:
        os.environ['CLAUDE_PERMISSION_MODE'] = args.permission_mode
    if args.output_format:
        os.environ['CLAUDE_OUTPUT_FORMAT'] = args.output_format
    if args.max_turns:
        os.environ['CLAUDE_MAX_TURNS'] = str(args.max_turns)
    if args.system_prompt:
        os.environ['CLAUDE_SYSTEM_PROMPT'] = args.system_prompt
    if args.model:
        os.environ['CLAUDE_MODEL'] = args.model
    if args.debug_subprocess:
        os.environ['DEBUG_SUBPROCESS'] = 'true'

    # Load configuration
    try:
        config = load_config()
        config.mode = args.mode  # type: ignore
        config.agent_name = args.name
        config.permission_mode = args.permission_mode  # type: ignore
        config.output_format = args.output_format  # type: ignore
        config.max_turns = args.max_turns
        config.append_system_prompt = args.system_prompt
        config.model = args.model
        config.debug_subprocess = args.debug_subprocess
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)

    # Log configuration
    logger.info(f"Agent Name: {config.agent_name}")
    logger.info(f"Mode: {config.mode}")
    logger.info(f"Flask URL: {config.flask_url}")
    if config.mode == 'polling':
        logger.info(f"Redis URL: {config.redis_url}")
    logger.info("-" * 60)
    logger.info("Claude Code Settings:")
    logger.info(f"  Permission Mode: {config.permission_mode}")
    logger.info(f"  Output Format: {config.output_format}")
    if config.max_turns:
        logger.info(f"  Max Turns: {config.max_turns}")
    if config.model:
        logger.info(f"  Model: {config.model}")
    if config.append_system_prompt:
        logger.info(f"  System Prompt: {config.append_system_prompt[:50]}...")
    logger.info(f"  Debug Subprocess: {config.debug_subprocess}")
    logger.info(f"  Mock Mode: {args.mock}")
    logger.info("-" * 60)

    # Create agent
    agent = ClaudeAgent(config, mock=args.mock)

    # Set up signal handlers
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, stopping...")
        agent.stop()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Run the agent
    try:
        agent.run()
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        sys.exit(1)

    logger.info("Agent shutdown complete")
    sys.exit(0)


if __name__ == '__main__':
    main()
