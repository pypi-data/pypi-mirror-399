"""
GuardFive Data Models

These are the "shapes" of data we work with.
Think of them like blueprints that define what information we store.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class Severity(str, Enum):
    """How serious is the threat?"""
    CRITICAL = "critical"  # 🔴 Stop everything, fix now
    HIGH = "high"          # 🟠 Very dangerous, fix soon
    MEDIUM = "medium"      # 🟡 Could be a problem
    LOW = "low"            # 🟢 Minor issue
    INFO = "info"          # ℹ️ Just informational


class ThreatType(str, Enum):
    """What kind of threat did we find?"""
    TOOL_POISONING = "tool_poisoning"      # Hidden malicious instructions
    RUG_PULL = "rug_pull"                  # Tool changed after approval
    SHADOWING = "shadowing"                # Fake tool impersonating real one
    COMMAND_INJECTION = "command_injection" # Vulnerable to shell attacks
    DATA_EXFILTRATION = "data_exfiltration" # Stealing data
    EXCESSIVE_PERMISSIONS = "excessive_permissions"  # Too much access
    PROMPT_INJECTION = "prompt_injection"  # Indirect prompt attacks
    SECRETS_EXPOSURE = "secrets_exposure"  # Exposes API keys, tokens, credentials
    SSRF = "ssrf"                          # Server-Side Request Forgery (unsafe URL fetch)

@dataclass
class Tool:
    """
    Represents one tool/function that an MCP server provides.
    
    Example: A "send_email" tool that can send emails on your behalf.
    """
    name: str                          # e.g., "send_email"
    description: str                   # What the tool says it does
    parameters: dict[str, Any]         # What inputs it accepts
    server_name: str = ""              # Which server provides this tool
    
    def __repr__(self) -> str:
        return f"Tool({self.name})"


@dataclass
class Finding:
    """
    A security issue we found during scanning.
    
    This is the main thing we report to users.
    """
    threat_type: ThreatType            # What kind of threat
    severity: Severity                 # How serious
    title: str                         # Short description
    description: str                   # Detailed explanation
    tool_name: str = ""                # Which tool is affected
    server_name: str = ""              # Which server
    evidence: str = ""                 # Proof (e.g., suspicious code)
    recommendation: str = ""           # How to fix it
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON output"""
        return {
            "threat_type": self.threat_type.value,
            "severity": self.severity.value,
            "title": self.title,
            "description": self.description,
            "tool_name": self.tool_name,
            "server_name": self.server_name,
            "evidence": self.evidence,
            "recommendation": self.recommendation,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class MCPServer:
    """
    Represents one MCP server from a config file.
    
    A server is like an "app" that provides tools to AI agents.
    """
    name: str                          # e.g., "filesystem"
    command: str                       # How to run it
    args: list[str] = field(default_factory=list)  # Command arguments
    env: dict[str, str] = field(default_factory=dict)  # Environment variables
    tools: list[Tool] = field(default_factory=list)  # Tools it provides


@dataclass 
class ScanResult:
    """
    The complete result of scanning one or more servers.
    
    This is what we show to the user at the end.
    """
    servers_scanned: int               # How many servers we checked
    tools_scanned: int                 # How many tools total
    findings: list[Finding]            # All the issues we found
    scan_duration_seconds: float       # How long it took
    timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def critical_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == Severity.CRITICAL)
    
    @property
    def high_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == Severity.HIGH)
    
    @property
    def medium_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == Severity.MEDIUM)
    
    @property
    def low_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == Severity.LOW)
    
    @property
    def is_safe(self) -> bool:
        """No critical or high severity findings"""
        return self.critical_count == 0 and self.high_count == 0
    
    def summary(self) -> str:
        """One-line summary of results"""
        return (
            f"Scanned {self.servers_scanned} servers, {self.tools_scanned} tools. "
            f"Found: {self.critical_count} critical, {self.high_count} high, "
            f"{self.medium_count} medium, {self.low_count} low"
        )
