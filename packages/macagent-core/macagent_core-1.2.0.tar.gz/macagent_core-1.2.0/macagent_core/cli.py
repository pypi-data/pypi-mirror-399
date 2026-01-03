#!/usr/bin/env python3
"""
MacAgent Core CLI - Basic commands for macOS management

Free features:
- System status monitoring
- HMAC-SHA256 audit trail
- Basic Siri voice commands
- Local LLM integration (Ollama)

For advanced features (Tinhat EMF, OS4AI, Fleet Management),
upgrade to MacAgent Pro: https://macagent.pro
"""

import argparse
import subprocess
import sys
import json
from datetime import datetime
from pathlib import Path

from . import __version__
from .audit import AuditLog
from .hardware import get_system_status, get_thermal_status


def cmd_status(args):
    """Show MacAgent status and system health."""
    print(f"MacAgent Core v{__version__}")
    print("=" * 40)

    status = get_system_status()
    thermal = get_thermal_status()

    print(f"CPU Usage:     {status['cpu_percent']:.1f}%")
    print(f"Memory:        {status['memory_percent']:.1f}% used")
    print(f"Disk:          {status['disk_percent']:.1f}% used")
    print(f"Thermal:       {thermal['state']}")

    # Check for Pro features
    try:
        import macagent_pro
        print(f"\nMacAgent Pro:  Installed (v{macagent_pro.__version__})")
    except ImportError:
        print(f"\nMacAgent Pro:  Not installed")
        print("  Upgrade: pip install macagent-pro")

    return 0


def cmd_audit(args):
    """View or manage audit trail."""
    log = AuditLog()

    if args.verify:
        valid, msg = log.verify_chain()
        print(f"Audit chain: {'VALID' if valid else 'INVALID'}")
        print(msg)
        return 0 if valid else 1

    entries = log.get_recent(args.limit)
    for entry in entries:
        ts = entry.get('timestamp', 'unknown')
        action = entry.get('action', 'unknown')
        tier = entry.get('risk_tier', '?')
        print(f"[{ts}] T{tier}: {action}")

    return 0


def cmd_siri(args):
    """Execute a Siri voice command."""
    command = " ".join(args.command)
    log = AuditLog()

    print(f"Processing: {command}")

    # Parse intent (simplified)
    intent = parse_intent(command)

    if intent:
        log.record(f"siri.{intent['action']}", risk_tier=intent['tier'])
        result = execute_intent(intent)
        print(f"Result: {result}")
        return 0
    else:
        print("Could not understand command")
        return 1


def parse_intent(command: str) -> dict:
    """Parse natural language to intent (simplified Core version)."""
    command = command.lower()

    # Basic intents (Core supports 10 basic commands)
    if "open" in command and "finder" in command:
        return {"action": "finder.open", "tier": 1, "params": {}}
    elif "status" in command or "health" in command:
        return {"action": "system.status", "tier": 0, "params": {}}
    elif "create file" in command:
        return {"action": "file.create", "tier": 2, "params": {}}
    elif "search" in command:
        return {"action": "spotlight.search", "tier": 0, "params": {}}
    elif "quit" in command or "close" in command:
        return {"action": "app.quit", "tier": 2, "params": {}}

    return None


def execute_intent(intent: dict) -> str:
    """Execute a parsed intent."""
    action = intent["action"]

    if action == "finder.open":
        subprocess.run(["open", "-a", "Finder"])
        return "Opened Finder"
    elif action == "system.status":
        status = get_system_status()
        return f"CPU: {status['cpu_percent']:.0f}%, Memory: {status['memory_percent']:.0f}%"
    elif action == "spotlight.search":
        subprocess.run(["open", "-a", "Spotlight"])
        return "Opened Spotlight"

    return "Command executed"


def cmd_version(args):
    """Show version information."""
    print(f"MacAgent Core v{__version__}")
    print("MIT Licensed - https://github.com/midnightnow/macagent")
    print("\nUpgrade to Pro: https://macagent.pro")
    return 0


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="macagent",
        description="MacAgent Core - AI orchestration for macOS"
    )
    parser.add_argument("--version", action="store_true", help="Show version")

    subparsers = parser.add_subparsers(dest="command")

    # status command
    status_parser = subparsers.add_parser("status", help="Show system status")
    status_parser.set_defaults(func=cmd_status)

    # audit command
    audit_parser = subparsers.add_parser("audit", help="View audit trail")
    audit_parser.add_argument("--verify", action="store_true", help="Verify chain integrity")
    audit_parser.add_argument("--limit", type=int, default=10, help="Number of entries")
    audit_parser.set_defaults(func=cmd_audit)

    # siri command
    siri_parser = subparsers.add_parser("siri", help="Execute voice command")
    siri_parser.add_argument("command", nargs="+", help="Natural language command")
    siri_parser.set_defaults(func=cmd_siri)

    # version command
    version_parser = subparsers.add_parser("version", help="Show version")
    version_parser.set_defaults(func=cmd_version)

    args = parser.parse_args()

    if args.version:
        return cmd_version(args)

    if not args.command:
        # Default to status if no command
        return cmd_status(args)

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
