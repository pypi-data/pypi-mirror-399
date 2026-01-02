"""
Tool Shadowing Detector

Detects when multiple MCP servers define tools with the same name.

The attack works like this:
1. You have a trusted "email_server" with a "send_email" tool
2. A malicious server ALSO defines "send_email"
3. When the AI calls "send_email", the malicious one intercepts it
4. Your emails are now being read by an attacker

This is also called "Cross-Server Tool Shadowing" or "Tool Interception".
"""

from collections import defaultdict
from guardfive.models import Finding, Severity, ThreatType, Tool


# Some tool names are commonly duplicated legitimately
# (e.g., many servers have a "help" tool)
COMMONLY_DUPLICATED = {
    "help",
    "get_help", 
    "list_tools",
    "ping",
    "health",
    "status",
    "version",
}


def detect_shadowing(tools: list[Tool]) -> list[Finding]:
    """
    Detect tools with duplicate names across different servers.
    
    Args:
        tools: All tools from all servers
        
    Returns:
        List of findings for shadowed tools
    """
    findings = []
    
    # Group tools by name
    tools_by_name: dict[str, list[Tool]] = defaultdict(list)
    for tool in tools:
        tools_by_name[tool.name].append(tool)
    
    # Check for duplicates
    for tool_name, duplicate_tools in tools_by_name.items():
        if len(duplicate_tools) < 2:
            continue
        
        # Get the servers that define this tool
        servers = [t.server_name for t in duplicate_tools]
        
        # Skip commonly duplicated tools
        if tool_name.lower() in COMMONLY_DUPLICATED:
            findings.append(Finding(
                threat_type=ThreatType.SHADOWING,
                severity=Severity.INFO,
                title=f"Common tool '{tool_name}' appears in multiple servers",
                description=(
                    f"The tool '{tool_name}' is defined by multiple servers: {servers}. "
                    f"This is common for utility tools but worth noting."
                ),
                tool_name=tool_name,
                evidence=f"Servers: {', '.join(servers)}",
                recommendation="No action needed for common utility tools.",
            ))
            continue
        
        # This is a real shadowing concern!
        severity = Severity.HIGH
        
        # Check if descriptions differ (more suspicious)
        descriptions = [t.description for t in duplicate_tools]
        if len(set(descriptions)) > 1:
            severity = Severity.CRITICAL
            extra_note = " The descriptions DIFFER between servers, which is very suspicious."
        else:
            extra_note = ""
        
        findings.append(Finding(
            threat_type=ThreatType.SHADOWING,
            severity=severity,
            title=f"Tool shadowing detected: '{tool_name}'",
            description=(
                f"The tool '{tool_name}' is defined by multiple servers: {servers}.{extra_note} "
                f"A malicious server could intercept calls intended for a trusted server. "
                f"This is a serious security concern."
            ),
            tool_name=tool_name,
            evidence=_format_shadowing_evidence(duplicate_tools),
            recommendation=(
                "Remove one of the servers defining this tool, or rename the tool "
                "in one server to make it unique. Investigate which server is trusted."
            ),
        ))
    
    return findings


def _format_shadowing_evidence(tools: list[Tool]) -> str:
    """Create evidence string showing all duplicate definitions"""
    lines = []
    for tool in tools:
        desc_preview = tool.description[:100] + "..." if len(tool.description) > 100 else tool.description
        lines.append(f"- {tool.server_name}: \"{desc_preview}\"")
    return "\n".join(lines)


def detect_suspicious_names(tools: list[Tool]) -> list[Finding]:
    """
    Detect tools with names similar to common sensitive tools.
    
    e.g., "send_emai1" (with number 1) trying to look like "send_email"
    """
    findings = []
    
    # Sensitive tool names that might be targeted
    sensitive_names = {
        "send_email", "read_email", "get_emails",
        "read_file", "write_file", "delete_file",
        "execute", "run_command", "shell",
        "database_query", "sql_query",
        "get_password", "get_credentials",
        "send_message", "read_messages",
    }
    
    for tool in tools:
        tool_name_lower = tool.name.lower()
        
        for sensitive in sensitive_names:
            # Check for lookalike names
            similarity = _calculate_similarity(tool_name_lower, sensitive)
            
            # If very similar but not exact, it might be typosquatting
            if 0.8 <= similarity < 1.0:
                findings.append(Finding(
                    threat_type=ThreatType.SHADOWING,
                    severity=Severity.MEDIUM,
                    title=f"Suspicious tool name: '{tool.name}'",
                    description=(
                        f"The tool name '{tool.name}' is very similar to '{sensitive}'. "
                        f"This could be an attempt to intercept calls through typosquatting."
                    ),
                    tool_name=tool.name,
                    server_name=tool.server_name,
                    evidence=f"Similarity to '{sensitive}': {similarity:.0%}",
                    recommendation="Verify this is the correct tool name and not a malicious lookalike.",
                ))
    
    return findings


def _calculate_similarity(s1: str, s2: str) -> float:
    """Calculate string similarity (0 to 1) using simple method"""
    if s1 == s2:
        return 1.0
    
    # Simple character-based similarity
    longer = max(len(s1), len(s2))
    if longer == 0:
        return 1.0
    
    # Count matching characters
    matches = sum(c1 == c2 for c1, c2 in zip(s1, s2))
    return matches / longer
