"""
GuardFive Scanner

The main scanning engine that brings all detectors together.

This is the heart of GuardFive - it:
1. Finds or loads MCP server configs
2. Connects to servers and gets their tools
3. Runs all detectors on the tools
4. Returns a comprehensive scan result
"""

import time
from pathlib import Path
from typing import Optional

from guardfive.models import Finding, MCPServer, ScanResult, Severity, Tool
from guardfive.detectors import (
    detect_tool_poisoning,
    detect_rug_pull,
    detect_shadowing,
    detect_suspicious_names,
    detect_command_injection,
    detect_secrets_exposure,
    detect_unsafe_fetch,
)
from guardfive.connectors import (
    find_config_files,
    parse_config_file,
    fetch_tools_sync,
)


class Scanner:
    """
    Main scanner class for GuardFive.
    
    Usage:
        scanner = Scanner()
        result = scanner.scan_config("~/.cursor/mcp.json")
        print(result.summary())
    """
    
    def __init__(self, skip_rug_pull: bool = False):
        """
        Initialize scanner.
        
        Args:
            skip_rug_pull: If True, don't check for tool changes (faster)
        """
        self.skip_rug_pull = skip_rug_pull
    
    def scan_config(self, config_path: str | Path) -> ScanResult:
        """
        Scan all MCP servers defined in a config file.
        
        Args:
            config_path: Path to MCP config file (e.g., ~/.cursor/mcp.json)
            
        Returns:
            ScanResult with all findings
        """
        start_time = time.time()
        config_path = Path(config_path).expanduser()
        
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        # Parse config file to get servers
        servers = parse_config_file(config_path)
        
        if not servers:
            return ScanResult(
                servers_scanned=0,
                tools_scanned=0,
                findings=[],
                scan_duration_seconds=time.time() - start_time,
            )
        
        # Fetch tools from all servers
        tools = fetch_tools_sync(servers)
        
        # Run all detectors
        findings = self._run_detectors(tools)
        
        return ScanResult(
            servers_scanned=len(servers),
            tools_scanned=len(tools),
            findings=findings,
            scan_duration_seconds=time.time() - start_time,
        )
    
    def scan_tools(self, tools: list[Tool]) -> ScanResult:
        """
        Scan a list of tools directly (without connecting to servers).
        
        Useful for testing or when you already have tool definitions.
        """
        start_time = time.time()
        
        findings = self._run_detectors(tools)
        
        # Count unique servers
        servers = set(t.server_name for t in tools)
        
        return ScanResult(
            servers_scanned=len(servers),
            tools_scanned=len(tools),
            findings=findings,
            scan_duration_seconds=time.time() - start_time,
        )
    
    def scan_all_configs(self) -> ScanResult:
        """
        Find and scan all MCP config files on this system.
        
        Looks in common locations like ~/.cursor/mcp.json
        """
        start_time = time.time()
        
        config_files = find_config_files()
        
        if not config_files:
            return ScanResult(
                servers_scanned=0,
                tools_scanned=0,
                findings=[Finding(
                    threat_type=Severity.INFO,
                    severity=Severity.INFO,
                    title="No MCP config files found",
                    description="No MCP configuration files were found in common locations.",
                    recommendation="If you use MCP, specify the config file path directly.",
                )],
                scan_duration_seconds=time.time() - start_time,
            )
        
        # Parse all configs
        all_servers = []
        for config_path in config_files:
            try:
                servers = parse_config_file(config_path)
                all_servers.extend(servers)
            except Exception as e:
                print(f"Warning: Could not parse {config_path}: {e}")
        
        # Fetch all tools
        tools = fetch_tools_sync(all_servers)
        
        # Run detectors
        findings = self._run_detectors(tools)
        
        return ScanResult(
            servers_scanned=len(all_servers),
            tools_scanned=len(tools),
            findings=findings,
            scan_duration_seconds=time.time() - start_time,
        )
    
    def _run_detectors(self, tools: list[Tool]) -> list[Finding]:
        """Run all threat detectors on a list of tools"""
        findings = []
        
        # 1. Tool Poisoning Detection
        findings.extend(detect_tool_poisoning(tools))
        
        # 2. Rug Pull Detection (check for changes)
        if not self.skip_rug_pull:
            findings.extend(detect_rug_pull(tools))
        
        # 3. Shadowing Detection (duplicate tool names)
        findings.extend(detect_shadowing(tools))
        
        # 4. Suspicious Names Detection
        findings.extend(detect_suspicious_names(tools))
        
        # 5. Command Injection Detection
        findings.extend(detect_command_injection(tools))
        
        # 6. Secrets Exposure Detection
        findings.extend(detect_secrets_exposure(tools))
        
        # 7. SSRF / Unsafe URL Fetch Detection
        findings.extend(detect_unsafe_fetch(tools))
        
        # Sort by severity (critical first)
        severity_order = {
            Severity.CRITICAL: 0,
            Severity.HIGH: 1,
            Severity.MEDIUM: 2,
            Severity.LOW: 3,
            Severity.INFO: 4,
        }
        findings.sort(key=lambda f: severity_order.get(f.severity, 99))
        
        return findings


def quick_scan(config_path: Optional[str] = None) -> ScanResult:
    """
    Quick scan function for simple use cases.
    
    Args:
        config_path: Optional path to config file. If not provided,
                    searches for configs automatically.
    
    Returns:
        ScanResult with findings
    """
    scanner = Scanner()
    
    if config_path:
        return scanner.scan_config(config_path)
    else:
        return scanner.scan_all_configs()
