"""
Command Injection Detector

Detects tools that allow arbitrary command/code execution.

These are dangerous because:
- An attacker can run ANY system command
- They can install malware, steal files, or take over the system
- Even "safe" shells can be escaped

Examples of dangerous tools:
- run_command(cmd: string) - Direct shell access
- execute(code: string) - Code execution
- shell(command: string) - Shell access
"""

import re
from guardfive.models import Finding, Severity, ThreatType, Tool


# Tool names that indicate command execution
DANGEROUS_TOOL_NAMES = [
    (r"^(run_?)?command$", "Direct command execution"),
    (r"^(run_?)?shell$", "Shell access"),
    (r"^exec(ute)?$", "Code execution"),
    (r"^(run_?)?script$", "Script execution"),
    (r"^eval$", "Eval execution"),
    (r"^system$", "System command"),
    (r"^bash$", "Bash shell"),
    (r"^powershell$", "PowerShell"),
    (r"^cmd$", "Command prompt"),
    (r"^terminal$", "Terminal access"),
]

# Parameter names that suggest command input
DANGEROUS_PARAM_NAMES = [
    "command", "cmd", "shell", "script", "code", "exec",
    "bash", "powershell", "terminal", "query", "expression"
]

# Description patterns suggesting execution
DANGEROUS_DESCRIPTION_PATTERNS = [
    (r"executes?\s+(a\s+)?(shell\s+)?command", "Executes shell commands"),
    (r"runs?\s+(a\s+)?(shell\s+)?command", "Runs shell commands"),
    (r"runs?\s+(a\s+)?script", "Runs scripts"),
    (r"execute\s+arbitrary", "Arbitrary execution"),
    (r"run\s+any\s+command", "Any command execution"),
    (r"shell\s+access", "Shell access"),
    (r"system\s+command", "System command access"),
    (r"(bash|powershell|cmd)\s+(command|script)", "Shell-specific execution"),
]

# Safe patterns - these are okay even if they match above
SAFE_PATTERNS = [
    r"sql\s+(command|query)",  # SQL is different from shell
    r"database\s+command",
    r"git\s+command",  # Git commands are usually sandboxed
]


def detect_command_injection(tools: list[Tool]) -> list[Finding]:
    """
    Scan tools for command injection vulnerabilities.
    
    Args:
        tools: List of Tool objects to scan
        
    Returns:
        List of Finding objects for any threats detected
    """
    findings = []
    
    for tool in tools:
        tool_findings = _scan_tool(tool)
        findings.extend(tool_findings)
    
    return findings


def _scan_tool(tool: Tool) -> list[Finding]:
    """Scan a single tool for command injection risks"""
    findings = []
    
    # Check if it's a known safe pattern first
    description_lower = tool.description.lower()
    for safe_pattern in SAFE_PATTERNS:
        if re.search(safe_pattern, description_lower):
            return findings  # Skip this tool
    
    # 1. Check tool name
    for pattern, risk_name in DANGEROUS_TOOL_NAMES:
        if re.match(pattern, tool.name.lower()):
            findings.append(Finding(
                threat_type=ThreatType.COMMAND_INJECTION,
                severity=Severity.CRITICAL,
                title=f"Dangerous tool name: {risk_name}",
                description=(
                    f"The tool '{tool.name}' has a name that indicates it allows "
                    f"arbitrary command execution. This is extremely dangerous."
                ),
                tool_name=tool.name,
                server_name=tool.server_name,
                evidence=f"Tool name '{tool.name}' matches dangerous pattern",
                recommendation=(
                    "Remove this tool unless you absolutely need it. "
                    "If required, ensure it has strict input validation."
                ),
            ))
            break
    
    # 2. Check parameter names
    if tool.parameters:
        param_names = []
        if isinstance(tool.parameters, dict):
            param_names = [str(k).lower() for k in tool.parameters.keys()]
        
        for param in param_names:
            if param in DANGEROUS_PARAM_NAMES:
                findings.append(Finding(
                    threat_type=ThreatType.COMMAND_INJECTION,
                    severity=Severity.HIGH,
                    title=f"Suspicious parameter: '{param}'",
                    description=(
                        f"The tool '{tool.name}' has a parameter named '{param}' "
                        f"which suggests it accepts commands or code for execution."
                    ),
                    tool_name=tool.name,
                    server_name=tool.server_name,
                    evidence=f"Parameter '{param}' in tool '{tool.name}'",
                    recommendation=(
                        "Review what this parameter is used for. "
                        "Ensure proper input sanitization is in place."
                    ),
                ))
                break  # Only report once per tool
    
    # 3. Check description
    for pattern, risk_name in DANGEROUS_DESCRIPTION_PATTERNS:
        if re.search(pattern, description_lower):
            findings.append(Finding(
                threat_type=ThreatType.COMMAND_INJECTION,
                severity=Severity.HIGH,
                title=f"Description indicates: {risk_name}",
                description=(
                    f"The tool '{tool.name}' description suggests it can execute "
                    f"commands or scripts, which is a security risk."
                ),
                tool_name=tool.name,
                server_name=tool.server_name,
                evidence=_extract_context(tool.description, pattern),
                recommendation=(
                    "Verify this tool has proper sandboxing and input validation. "
                    "Consider if you really need this capability."
                ),
            ))
            break  # Only report once per tool
    
    return findings


def _extract_context(text: str, pattern: str, context: int = 40) -> str:
    """Extract text around a pattern match"""
    match = re.search(pattern, text, re.IGNORECASE)
    if not match:
        return ""
    
    start = max(0, match.start() - context)
    end = min(len(text), match.end() + context)
    
    result = text[start:end]
    if start > 0:
        result = "..." + result
    if end < len(text):
        result = result + "..."
    
    return result