"""
Secrets Exposure Detector

Detects tools that might expose or steal credentials, API keys, and tokens.

Risks:
- Tools that read environment variables (often contain secrets)
- Tools that access credential files
- Tools that return sensitive data in responses
- OAuth token handling without proper scoping
"""

import re
from guardfive.models import Finding, Severity, ThreatType, Tool


# Tool names that handle secrets
SECRETS_TOOL_PATTERNS = [
    (r"get_?env", "Environment variable access", Severity.HIGH),
    (r"read_?env", "Environment variable access", Severity.HIGH),
    (r"env(ironment)?_?var", "Environment variable access", Severity.HIGH),
    (r"get_?(api_?)?key", "API key access", Severity.HIGH),
    (r"get_?(api_?)?token", "Token access", Severity.HIGH),
    (r"get_?secret", "Secret access", Severity.CRITICAL),
    (r"get_?password", "Password access", Severity.CRITICAL),
    (r"get_?credential", "Credential access", Severity.CRITICAL),
    (r"read_?credential", "Credential access", Severity.CRITICAL),
    (r"oauth_?token", "OAuth token handling", Severity.HIGH),
    (r"access_?token", "Access token handling", Severity.HIGH),
    (r"refresh_?token", "Refresh token handling", Severity.CRITICAL),
]

# Description patterns indicating secrets handling
SECRETS_DESCRIPTION_PATTERNS = [
    (r"returns?\s+(the\s+)?(api[_\s]?key|secret|password|token|credential)", 
     "Returns sensitive data", Severity.CRITICAL),
    (r"reads?\s+(the\s+)?environment\s+variable", 
     "Reads environment variables", Severity.HIGH),
    (r"access(es)?\s+(to\s+)?(api[_\s]?keys?|secrets?|passwords?|tokens?|credentials?)", 
     "Accesses sensitive data", Severity.HIGH),
    (r"retrieves?\s+(the\s+)?(api[_\s]?key|secret|password|token|credential)", 
     "Retrieves sensitive data", Severity.HIGH),
    (r"(store|save|log)s?\s+(the\s+)?(api[_\s]?key|secret|password|token|credential)", 
     "Stores/logs sensitive data", Severity.CRITICAL),
    (r"oauth\s+(2\.0\s+)?(token|flow|authentication)", 
     "OAuth handling", Severity.MEDIUM),
    (r"(aws|gcp|azure|github|stripe|openai)\s+(key|token|secret|credential)", 
     "Cloud provider credentials", Severity.CRITICAL),
]

# Parameter names that suggest secrets
SECRETS_PARAM_PATTERNS = [
    ("api_key", Severity.HIGH),
    ("apikey", Severity.HIGH),
    ("api_token", Severity.HIGH),
    ("secret", Severity.CRITICAL),
    ("password", Severity.CRITICAL),
    ("passwd", Severity.CRITICAL),
    ("credential", Severity.CRITICAL),
    ("token", Severity.MEDIUM),  # Could be legitimate
    ("access_token", Severity.HIGH),
    ("refresh_token", Severity.CRITICAL),
    ("private_key", Severity.CRITICAL),
    ("auth", Severity.MEDIUM),
]


def detect_secrets_exposure(tools: list[Tool]) -> list[Finding]:
    """
    Scan tools for potential secrets exposure.
    
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
    """Scan a single tool for secrets exposure risks"""
    findings = []
    tool_name_lower = tool.name.lower()
    description_lower = tool.description.lower()
    
    # 1. Check tool name
    for pattern, risk_name, severity in SECRETS_TOOL_PATTERNS:
        if re.search(pattern, tool_name_lower):
            findings.append(Finding(
                threat_type=ThreatType.SECRETS_EXPOSURE,
                severity=severity,
                title=f"Sensitive tool: {risk_name}",
                description=(
                    f"The tool '{tool.name}' appears to handle sensitive data "
                    f"like credentials or secrets. This could expose confidential information."
                ),
                tool_name=tool.name,
                server_name=tool.server_name,
                evidence=f"Tool name '{tool.name}' indicates secrets handling",
                recommendation=(
                    "Review what data this tool can access. "
                    "Ensure it follows least-privilege principles."
                ),
            ))
            break
    
    # 2. Check description
    for pattern, risk_name, severity in SECRETS_DESCRIPTION_PATTERNS:
        if re.search(pattern, description_lower):
            findings.append(Finding(
                threat_type=ThreatType.SECRETS_EXPOSURE,
                severity=severity,
                title=f"Description indicates: {risk_name}",
                description=(
                    f"The tool '{tool.name}' description suggests it handles "
                    f"sensitive data which could be exposed."
                ),
                tool_name=tool.name,
                server_name=tool.server_name,
                evidence=_extract_context(tool.description, pattern),
                recommendation=(
                    "Verify this tool properly protects sensitive data. "
                    "Consider if the AI should have access to this information."
                ),
            ))
            break
    
    # 3. Check parameters
    if tool.parameters:
        param_names = []
        if isinstance(tool.parameters, dict):
            param_names = [str(k).lower() for k in tool.parameters.keys()]
        
        for param_pattern, severity in SECRETS_PARAM_PATTERNS:
            for param in param_names:
                if param_pattern in param:
                    findings.append(Finding(
                        threat_type=ThreatType.SECRETS_EXPOSURE,
                        severity=severity,
                        title=f"Sensitive parameter: '{param}'",
                        description=(
                            f"The tool '{tool.name}' has a parameter '{param}' "
                            f"that appears to handle sensitive data."
                        ),
                        tool_name=tool.name,
                        server_name=tool.server_name,
                        evidence=f"Parameter '{param}' suggests secrets handling",
                        recommendation=(
                            "Ensure this parameter is properly validated and "
                            "sensitive data is not logged or exposed."
                        ),
                    ))
                    break
            else:
                continue
            break
    
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