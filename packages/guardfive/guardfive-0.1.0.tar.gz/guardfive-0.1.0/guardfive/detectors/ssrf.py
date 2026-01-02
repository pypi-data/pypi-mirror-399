"""
Unsafe URL Fetch Detector (SSRF - Server Side Request Forgery)

Detects tools that allow fetching arbitrary URLs.

Risks:
- Attackers can make the server fetch internal URLs (localhost, 169.254.169.254)
- Can scan internal networks
- Can exfiltrate data by encoding it in URLs
- Can access cloud metadata endpoints (AWS, GCP, Azure)

30% of MCP servers have unrestricted URL fetching!
"""

import re
from guardfive.models import Finding, Severity, ThreatType, Tool


# Tool names that indicate URL fetching
FETCH_TOOL_PATTERNS = [
    (r"^fetch$", "Generic fetch"),
    (r"^fetch_?url$", "URL fetching"),
    (r"^get_?url$", "URL fetching"),
    (r"^http_?(get|request|fetch)$", "HTTP requests"),
    (r"^(web_?)?scrape", "Web scraping"),
    (r"^download$", "Download"),
    (r"^curl$", "Curl access"),
    (r"^wget$", "Wget access"),
    (r"^request$", "HTTP request"),
    (r"^browse$", "URL browsing"),
]

# Description patterns indicating URL fetching
FETCH_DESCRIPTION_PATTERNS = [
    (r"fetch(es)?\s+(a\s+)?(any\s+)?url", "Fetches URLs"),
    (r"(get|retrieve)s?\s+(content\s+)?from\s+(a\s+)?(any\s+)?url", "Gets content from URLs"),
    (r"downloads?\s+(from\s+)?(a\s+)?(any\s+)?url", "Downloads from URLs"),
    (r"makes?\s+(http|https)\s+requests?", "Makes HTTP requests"),
    (r"(scrape|crawl)s?\s+(a\s+)?(web\s+)?page", "Scrapes web pages"),
    (r"access(es)?\s+(any\s+)?(external\s+)?url", "Accesses external URLs"),
]

# Parameter names suggesting URL input
URL_PARAM_PATTERNS = [
    "url", "uri", "link", "href", "endpoint", "target",
    "destination", "source_url", "fetch_url", "download_url"
]

# Dangerous URL patterns that should be blocked
DANGEROUS_URL_MENTIONS = [
    (r"169\.254\.169\.254", "AWS metadata endpoint", Severity.CRITICAL),
    (r"metadata\.google", "GCP metadata endpoint", Severity.CRITICAL),
    (r"localhost", "Localhost access", Severity.HIGH),
    (r"127\.0\.0\.1", "Loopback address", Severity.HIGH),
    (r"0\.0\.0\.0", "All interfaces", Severity.HIGH),
    (r"internal", "Internal network", Severity.MEDIUM),
    (r"192\.168\.", "Private network", Severity.MEDIUM),
    (r"10\.\d+\.", "Private network", Severity.MEDIUM),
    (r"172\.(1[6-9]|2\d|3[01])\.", "Private network", Severity.MEDIUM),
]


def detect_unsafe_fetch(tools: list[Tool]) -> list[Finding]:
    """
    Scan tools for SSRF/unsafe URL fetching vulnerabilities.
    
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
    """Scan a single tool for SSRF risks"""
    findings = []
    tool_name_lower = tool.name.lower()
    description_lower = tool.description.lower()
    
    is_fetch_tool = False
    
    # 1. Check tool name
    for pattern, risk_name in FETCH_TOOL_PATTERNS:
        if re.search(pattern, tool_name_lower):
            is_fetch_tool = True
            findings.append(Finding(
                threat_type=ThreatType.SSRF,
                severity=Severity.HIGH,
                title=f"URL fetch tool: {risk_name}",
                description=(
                    f"The tool '{tool.name}' appears to fetch URLs. Without proper "
                    f"validation, this can be exploited for SSRF attacks."
                ),
                tool_name=tool.name,
                server_name=tool.server_name,
                evidence=f"Tool name '{tool.name}' indicates URL fetching",
                recommendation=(
                    "Ensure this tool validates URLs and blocks internal/private addresses. "
                    "Consider using an allowlist of permitted domains."
                ),
            ))
            break
    
    # 2. Check description
    if not is_fetch_tool:
        for pattern, risk_name in FETCH_DESCRIPTION_PATTERNS:
            if re.search(pattern, description_lower):
                is_fetch_tool = True
                findings.append(Finding(
                    threat_type=ThreatType.SSRF,
                    severity=Severity.MEDIUM,
                    title=f"Description indicates: {risk_name}",
                    description=(
                        f"The tool '{tool.name}' description suggests it can fetch URLs "
                        f"which could be exploited for SSRF if not properly validated."
                    ),
                    tool_name=tool.name,
                    server_name=tool.server_name,
                    evidence=_extract_context(tool.description, pattern),
                    recommendation=(
                        "Verify this tool validates URLs and blocks dangerous destinations."
                    ),
                ))
                break
    
    # 3. Check parameters
    if tool.parameters:
        param_names = []
        if isinstance(tool.parameters, dict):
            param_names = [str(k).lower() for k in tool.parameters.keys()]
        
        for param in param_names:
            if param in URL_PARAM_PATTERNS:
                if not is_fetch_tool:
                    is_fetch_tool = True
                    findings.append(Finding(
                        threat_type=ThreatType.SSRF,
                        severity=Severity.MEDIUM,
                        title=f"URL parameter: '{param}'",
                        description=(
                            f"The tool '{tool.name}' has a parameter '{param}' "
                            f"that accepts URLs, which could be exploited."
                        ),
                        tool_name=tool.name,
                        server_name=tool.server_name,
                        evidence=f"Parameter '{param}' accepts URL input",
                        recommendation=(
                            "Ensure URL validation is in place to prevent SSRF attacks."
                        ),
                    ))
                break
    
    # 4. Check for mentions of dangerous URLs in description
    for pattern, risk_name, severity in DANGEROUS_URL_MENTIONS:
        if re.search(pattern, description_lower):
            findings.append(Finding(
                threat_type=ThreatType.SSRF,
                severity=severity,
                title=f"Dangerous URL mentioned: {risk_name}",
                description=(
                    f"The tool '{tool.name}' mentions '{risk_name}' in its description. "
                    f"This could indicate access to sensitive internal resources."
                ),
                tool_name=tool.name,
                server_name=tool.server_name,
                evidence=_extract_context(tool.description, pattern),
                recommendation=(
                    "Block access to metadata endpoints and internal networks."
                ),
            ))
    
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