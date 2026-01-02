"""
GuardFive Threat Detectors

Each detector looks for a specific type of threat:
- tool_poisoning: Hidden malicious instructions
- rug_pull: Tools that change after approval  
- shadowing: Duplicate tools that intercept calls
"""

from guardfive.detectors.tool_poisoning import detect_tool_poisoning
from guardfive.detectors.rug_pull import detect_rug_pull, compute_tool_hash
from guardfive.detectors.shadowing import detect_shadowing, detect_suspicious_names
from guardfive.detectors.command_injection import detect_command_injection
from guardfive.detectors.secrets_exposure import detect_secrets_exposure
from guardfive.detectors.ssrf import detect_unsafe_fetch

__all__ = [
    "detect_tool_poisoning",
    "detect_rug_pull",
    "compute_tool_hash",
    "detect_shadowing",
    "detect_suspicious_names",
    "detect_command_injection",
    "detect_secrets_exposure",
    "detect_unsafe_fetch"
]
