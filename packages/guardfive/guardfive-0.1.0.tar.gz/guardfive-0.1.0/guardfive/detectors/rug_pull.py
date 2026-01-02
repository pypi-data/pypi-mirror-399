"""
Rug Pull Detector

Detects when MCP tools change their definitions after initial approval.

The attack works like this:
1. Day 1: Tool looks safe, user approves it
2. Day 7: Tool silently changes to steal data
3. User has no idea because they already approved it

We detect this by hashing tool definitions and alerting on changes.
"""

import hashlib
import json
from pathlib import Path
from datetime import datetime
from typing import Optional

from guardfive.models import Finding, Severity, ThreatType, Tool


# Default location for storing tool hashes
DEFAULT_HASH_STORE = Path.home() / ".guardfive" / "tool_hashes.json"


def compute_tool_hash(tool: Tool) -> str:
    """
    Create a unique fingerprint of a tool's definition.
    
    If anything changes (name, description, parameters), the hash changes.
    """
    content = json.dumps({
        "name": tool.name,
        "description": tool.description,
        "parameters": tool.parameters,
    }, sort_keys=True)
    
    return hashlib.sha256(content.encode()).hexdigest()


def detect_rug_pull(
    tools: list[Tool], 
    hash_store_path: Optional[Path] = None
) -> list[Finding]:
    """
    Check if any tools have changed since last scan.
    
    Args:
        tools: List of tools to check
        hash_store_path: Where to store/load hashes (optional)
        
    Returns:
        List of findings for any tools that changed
    """
    store_path = hash_store_path or DEFAULT_HASH_STORE
    findings = []
    
    # Load existing hashes
    stored_hashes = _load_hashes(store_path)
    
    # Check each tool
    new_hashes = {}
    for tool in tools:
        tool_key = f"{tool.server_name}:{tool.name}"
        current_hash = compute_tool_hash(tool)
        new_hashes[tool_key] = {
            "hash": current_hash,
            "last_seen": datetime.now().isoformat(),
            "server": tool.server_name,
            "tool": tool.name,
        }
        
        # Check if this tool existed before
        if tool_key in stored_hashes:
            stored = stored_hashes[tool_key]
            if stored["hash"] != current_hash:
                # ALERT! Tool definition changed!
                findings.append(Finding(
                    threat_type=ThreatType.RUG_PULL,
                    severity=Severity.CRITICAL,
                    title=f"Tool definition changed: {tool.name}",
                    description=(
                        f"The tool '{tool.name}' from server '{tool.server_name}' "
                        f"has changed since it was last scanned on {stored.get('last_seen', 'unknown')}. "
                        f"This could indicate a rug pull attack where a safe tool is "
                        f"replaced with a malicious version."
                    ),
                    tool_name=tool.name,
                    server_name=tool.server_name,
                    evidence=f"Previous hash: {stored['hash'][:16]}... | New hash: {current_hash[:16]}...",
                    recommendation=(
                        "STOP using this tool immediately and review what changed. "
                        "Compare the old and new descriptions to see if malicious "
                        "instructions were added."
                    ),
                ))
        else:
            # First time seeing this tool
            findings.append(Finding(
                threat_type=ThreatType.RUG_PULL,
                severity=Severity.INFO,
                title=f"New tool discovered: {tool.name}",
                description=(
                    f"First time seeing tool '{tool.name}' from server '{tool.server_name}'. "
                    f"Its hash has been recorded for future change detection."
                ),
                tool_name=tool.name,
                server_name=tool.server_name,
                evidence=f"Hash: {current_hash[:16]}...",
                recommendation="Review this tool's description before approving it.",
            ))
    
    # Save updated hashes
    _save_hashes(store_path, {**stored_hashes, **new_hashes})
    
    return findings


def _load_hashes(path: Path) -> dict:
    """Load stored hashes from disk"""
    if not path.exists():
        return {}
    
    try:
        with open(path) as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def _save_hashes(path: Path, hashes: dict) -> None:
    """Save hashes to disk"""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(hashes, f, indent=2)


def clear_hash_store(hash_store_path: Optional[Path] = None) -> None:
    """Clear all stored hashes (useful for testing)"""
    store_path = hash_store_path or DEFAULT_HASH_STORE
    if store_path.exists():
        store_path.unlink()
