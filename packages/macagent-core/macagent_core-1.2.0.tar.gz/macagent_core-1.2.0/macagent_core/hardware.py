"""
Basic hardware monitoring for macOS.

For advanced hardware consciousness (Tinhat EMF, WiFi motion, OS4AI),
upgrade to MacAgent Pro: https://macagent.pro
"""

import subprocess
import re
from typing import Dict, Any


def get_system_status() -> Dict[str, Any]:
    """Get basic system status."""
    try:
        import psutil
        return {
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage("/").percent,
        }
    except ImportError:
        # Fallback without psutil
        return _get_status_fallback()


def _get_status_fallback() -> Dict[str, Any]:
    """Get status using system commands (no dependencies)."""
    cpu = _get_cpu_fallback()
    memory = _get_memory_fallback()
    disk = _get_disk_fallback()
    return {
        "cpu_percent": cpu,
        "memory_percent": memory,
        "disk_percent": disk,
    }


def _get_cpu_fallback() -> float:
    """Get CPU usage via top command."""
    try:
        result = subprocess.run(
            ["top", "-l", "1", "-n", "0"],
            capture_output=True, text=True, timeout=5
        )
        match = re.search(r"CPU usage: ([\d.]+)% user", result.stdout)
        if match:
            return float(match.group(1))
    except Exception:
        pass
    return 0.0


def _get_memory_fallback() -> float:
    """Get memory usage via vm_stat."""
    try:
        result = subprocess.run(
            ["vm_stat"],
            capture_output=True, text=True, timeout=5
        )
        pages_free = pages_active = pages_inactive = pages_wired = 0
        for line in result.stdout.split("\n"):
            if "Pages free" in line:
                pages_free = int(re.search(r"(\d+)", line).group(1))
            elif "Pages active" in line:
                pages_active = int(re.search(r"(\d+)", line).group(1))
            elif "Pages inactive" in line:
                pages_inactive = int(re.search(r"(\d+)", line).group(1))
            elif "Pages wired" in line:
                pages_wired = int(re.search(r"(\d+)", line).group(1))

        total = pages_free + pages_active + pages_inactive + pages_wired
        used = pages_active + pages_wired
        if total > 0:
            return (used / total) * 100
    except Exception:
        pass
    return 0.0


def _get_disk_fallback() -> float:
    """Get disk usage via df."""
    try:
        result = subprocess.run(
            ["df", "-h", "/"],
            capture_output=True, text=True, timeout=5
        )
        lines = result.stdout.strip().split("\n")
        if len(lines) >= 2:
            parts = lines[1].split()
            if len(parts) >= 5:
                pct = parts[4].replace("%", "")
                return float(pct)
    except Exception:
        pass
    return 0.0


def get_thermal_status() -> Dict[str, Any]:
    """Get basic thermal status."""
    try:
        result = subprocess.run(
            ["pmset", "-g", "therm"],
            capture_output=True, text=True, timeout=5
        )
        if "CPU_Speed_Limit" in result.stdout:
            match = re.search(r"CPU_Speed_Limit\s*=\s*(\d+)", result.stdout)
            if match:
                limit = int(match.group(1))
                if limit == 100:
                    state = "Normal"
                elif limit >= 80:
                    state = "Warm"
                else:
                    state = "Throttling"
                return {"state": state, "cpu_limit": limit}
    except Exception:
        pass

    return {"state": "Unknown", "cpu_limit": None}


def get_battery_status() -> Dict[str, Any]:
    """Get battery status."""
    try:
        result = subprocess.run(
            ["pmset", "-g", "batt"],
            capture_output=True, text=True, timeout=5
        )
        match = re.search(r"(\d+)%", result.stdout)
        if match:
            pct = int(match.group(1))
            charging = "charging" in result.stdout.lower()
            return {"percent": pct, "charging": charging}
    except Exception:
        pass

    return {"percent": None, "charging": None}
