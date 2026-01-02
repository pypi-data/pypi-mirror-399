# GuardFive 🛡️

**The security scanner for AI agent tools (MCP servers)**

GuardFive scans the apps/tools that AI agents use to make sure they're safe and not secretly malicious.

## What It Does

1. **SCAN** → Find all MCP servers your AI uses
2. **ANALYZE** → Check for hidden threats
3. **MONITOR** → Watch for changes over time
4. **ALERT** → Tell you when something's wrong
5. **REPORT** → Give you proof for compliance

## Threats We Detect

| Threat | Description |
|--------|-------------|
| 🎭 **Tool Poisoning** | Hidden instructions in tool descriptions |
| 🔄 **Rug Pull** | Tools that change after you trust them |
| 👯 **Shadowing** | Malicious tools pretending to be legitimate ones |
| 💉 **Command Injection** | Vulnerable code that hackers can exploit |

## Quick Start

```bash
# Install
pip install -e .

# Scan your MCP config
guardfive scan ~/.cursor/mcp.json

# Or scan a specific server
guardfive scan --server "npx -y @modelcontextprotocol/server-filesystem /"
```

## Installation

```bash
# Clone the repo
git clone https://github.com/yourusername/guardfive.git
cd guardfive

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .
```

## Project Structure

```
guardfive/
├── guardfive/
│   ├── cli.py              # Command line interface
│   ├── scanner.py          # Main scanning logic
│   ├── models.py           # Data structures
│   ├── detectors/          # Threat detection modules
│   │   ├── tool_poisoning.py
│   │   ├── rug_pull.py
│   │   └── shadowing.py
│   └── connectors/
│       └── mcp_client.py   # Connect to MCP servers
└── tests/
```

## License

MIT
