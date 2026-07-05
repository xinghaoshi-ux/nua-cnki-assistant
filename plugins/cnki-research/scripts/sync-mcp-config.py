#!/usr/bin/env python3
"""Embed the portable launcher in the shared Codex/Claude MCP manifest."""

from __future__ import annotations

import json
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parent.parent
LAUNCHER = PLUGIN_ROOT / "scripts" / "launch-cnki-playwright-mcp.cjs"
MCP_MANIFEST = PLUGIN_ROOT / ".mcp.json"


def main() -> None:
    launcher_source = LAUNCHER.read_text(encoding="utf-8")
    payload = {
        "mcpServers": {
            "cnki-playwright": {
                "command": "node",
                "args": ["-e", launcher_source],
            }
        }
    }
    MCP_MANIFEST.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Updated {MCP_MANIFEST}")


if __name__ == "__main__":
    main()
