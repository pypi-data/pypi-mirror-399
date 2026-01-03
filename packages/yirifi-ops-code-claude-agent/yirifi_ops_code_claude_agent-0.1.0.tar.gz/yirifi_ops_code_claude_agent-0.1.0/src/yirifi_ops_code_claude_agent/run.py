#!/usr/bin/env python3
"""
Yirifi Ops Claude Code Agent Entry Point.

This is the main entry point for running the Claude Code agent.
Usage:
    python -m yirifi_ops_code_claude_agent.run [options]
    # or if installed:
    yirifi-claude-agent [options]

Options:
    --mode polling|websocket    Operating mode (default: from AGENT_MODE env or 'polling')
    --name NAME                 Agent name (default: from AGENT_NAME env or 'claude-agent-1')
    --flask-url URL             Flask server URL (default: from FLASK_URL env)
    --mock                      Use mock executor for testing
    --verbose                   Enable verbose logging
"""
import argparse
import logging
import os
import signal
import sys
from typing import NoReturn

from .agent import ClaudeAgent
from .config import AgentConfig, load_config


def setup_logging(verbose: bool = False) -> None:
    """Configure logging."""
    level = logging.DEBUG if verbose else logging.INFO

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
    )

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
    setup_logging(verbose=args.verbose)
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

    # Load configuration
    try:
        config = load_config()
        config.mode = args.mode  # type: ignore
        config.agent_name = args.name
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)

    logger.info(f"Agent Name: {config.agent_name}")
    logger.info(f"Mode: {config.mode}")
    logger.info(f"Flask URL: {config.flask_url}")
    if config.mode == 'polling':
        logger.info(f"Redis URL: {config.redis_url}")
    logger.info(f"Mock Mode: {args.mock}")
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
