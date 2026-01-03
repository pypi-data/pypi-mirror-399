"""
HMAC-SHA256 Audit Trail - Tamper-evident action logging

Every action is cryptographically signed. Any tampering breaks the chain.
"""

import hashlib
import hmac
import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Optional


class AuditLog:
    """Tamper-evident audit log with HMAC-SHA256 chain."""

    def __init__(self, log_dir: Optional[Path] = None):
        self.log_dir = log_dir or Path.home() / ".macagent" / "audit"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_dir / "actions.jsonl"
        self._hmac_key = self._get_hmac_key()

    def _get_hmac_key(self) -> bytes:
        """Get or generate HMAC key."""
        key_env = os.environ.get("MACAGENT_AUDIT_HMAC_KEY")
        if key_env:
            return bytes.fromhex(key_env)

        key_file = self.log_dir / ".hmac_key"
        if key_file.exists():
            return key_file.read_bytes()

        # Generate new key
        key = os.urandom(32)
        key_file.write_bytes(key)
        key_file.chmod(0o600)
        return key

    def record(self, action: str, risk_tier: int = 0, metadata: dict = None) -> str:
        """Record an action to the audit log."""
        prev_hash = self._get_last_hash()

        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "action": action,
            "risk_tier": risk_tier,
            "metadata": metadata or {},
            "prev_hash": prev_hash,
        }

        # Compute HMAC signature
        entry_bytes = json.dumps(entry, sort_keys=True).encode()
        signature = hmac.new(self._hmac_key, entry_bytes, hashlib.sha256).hexdigest()
        entry["signature"] = signature

        # Append to log
        with open(self.log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")

        return signature

    def _get_last_hash(self) -> str:
        """Get hash of last entry for chain linking."""
        if not self.log_file.exists():
            return "genesis"

        with open(self.log_file, "r") as f:
            lines = f.readlines()
            if not lines:
                return "genesis"
            last = json.loads(lines[-1])
            return last.get("signature", "genesis")

    def verify_chain(self) -> Tuple[bool, str]:
        """Verify the entire audit chain integrity."""
        if not self.log_file.exists():
            return True, "No audit entries yet"

        with open(self.log_file, "r") as f:
            lines = f.readlines()

        prev_hash = "genesis"
        for i, line in enumerate(lines):
            entry = json.loads(line)
            stored_sig = entry.pop("signature", None)

            # Check chain link
            if entry.get("prev_hash") != prev_hash:
                return False, f"Chain broken at entry {i}: prev_hash mismatch"

            # Verify HMAC
            entry_bytes = json.dumps(entry, sort_keys=True).encode()
            expected_sig = hmac.new(self._hmac_key, entry_bytes, hashlib.sha256).hexdigest()

            if stored_sig != expected_sig:
                return False, f"Tampering detected at entry {i}: signature mismatch"

            prev_hash = stored_sig

        return True, f"All {len(lines)} entries verified"

    def get_recent(self, limit: int = 10) -> List[dict]:
        """Get recent audit entries."""
        if not self.log_file.exists():
            return []

        with open(self.log_file, "r") as f:
            lines = f.readlines()

        entries = [json.loads(line) for line in lines[-limit:]]
        return entries
