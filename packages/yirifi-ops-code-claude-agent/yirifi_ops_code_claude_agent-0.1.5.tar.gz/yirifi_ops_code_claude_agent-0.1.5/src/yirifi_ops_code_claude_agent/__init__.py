"""
Yirifi Ops Claude Code Agent.

This agent runs on Mac machines and executes Claude Code tasks
dispatched from the Yirifi Ops Dashboard. Supports two operating modes:
- Polling mode: Polls Redis queue for tasks (simpler, works with any network)
- WebSocket mode: Maintains persistent connection for lower latency
"""

__version__ = '0.1.0'
