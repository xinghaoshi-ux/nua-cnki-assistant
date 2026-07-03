#!/usr/bin/env python3
"""Portable repository checks for NUA CNKI Assistant."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

try:
    import tomllib
except ImportError:  # Python 3.9/3.10 can optionally provide the compatible tomli package.
    try:
        import tomli as tomllib  # type: ignore[no-redef]
    except ImportError:
        tomllib = None  # type: ignore[assignment]


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "cnki-research"


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def main() -> None:
    manifest_path = PLUGIN / ".codex-plugin" / "plugin.json"
    mcp_path = PLUGIN / ".mcp.json"
    codex_config_path = PLUGIN / ".codex" / "config.toml"
    marketplace_path = ROOT / ".agents" / "plugins" / "marketplace.json"
    skill_path = PLUGIN / "skills" / "cnki-research" / "SKILL.md"
    metadata_script = PLUGIN / "skills" / "cnki-research" / "scripts" / "scholar_metadata.py"
    launcher = PLUGIN / "scripts" / "run-background-chrome-mcp.zsh"

    for path in (
        manifest_path,
        mcp_path,
        codex_config_path,
        marketplace_path,
        skill_path,
        metadata_script,
        launcher,
    ):
        if not path.is_file():
            fail(f"missing required file: {path.relative_to(ROOT)}")

    manifest = load_json(manifest_path)
    mcp = load_json(mcp_path)
    marketplace = load_json(marketplace_path)
    if tomllib is not None:
        with codex_config_path.open("rb") as handle:
            tomllib.load(handle)

    for field in ("name", "version", "description", "author", "interface"):
        if field not in manifest:
            fail(f"plugin manifest is missing {field}")
    if manifest["name"] != "cnki-research":
        fail("plugin name must be cnki-research")
    if not re.fullmatch(r"\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?", manifest["version"]):
        fail("plugin version is not semantic versioning")
    if manifest.get("mcpServers") != "./.mcp.json":
        fail("plugin manifest must reference ./.mcp.json")
    if "cnki-playwright" not in mcp.get("mcpServers", {}):
        fail("cnki-playwright MCP server is missing")

    entries = marketplace.get("plugins", [])
    if len(entries) != 1 or entries[0].get("name") != manifest["name"]:
        fail("marketplace entry does not match the plugin manifest")
    if entries[0].get("source", {}).get("path") != "./plugins/cnki-research":
        fail("marketplace plugin path is incorrect")

    skill_text = skill_path.read_text(encoding="utf-8")
    if not skill_text.startswith("---\n") or "name: cnki-research" not in skill_text[:1000]:
        fail("skill front matter is invalid")

    repository_text = "\n".join(
        path.read_text(encoding="utf-8", errors="ignore")
        for path in PLUGIN.rglob("*")
        if path.is_file()
    )
    for forbidden in ("/Users/", "$HOME/plugins/cnki-research"):
        if forbidden in repository_text:
            fail(f"non-portable local path found: {forbidden}")
    for secret_pattern in (
        r"(?i)api[_-]?key\s*[:=]\s*['\"][^'\"]+",
        r"(?i)access[_-]?token\s*[:=]\s*['\"][^'\"]+",
        r"(?i)password\s*[:=]\s*['\"][^'\"]+",
        r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
    ):
        if re.search(secret_pattern, repository_text):
            fail("a secret-shaped value was found")

    compile(metadata_script.read_text(encoding="utf-8"), str(metadata_script), "exec")

    zsh = shutil.which("zsh")
    if zsh:
        subprocess.run([zsh, "-n", str(launcher)], check=True)
        command = mcp["mcpServers"]["cnki-playwright"]["args"][1]
        subprocess.run([zsh, "-n"], input=command, text=True, check=True)

    print("NUA CNKI Assistant repository validation passed.")


if __name__ == "__main__":
    try:
        main()
    except (json.JSONDecodeError, KeyError, TypeError, subprocess.CalledProcessError) as exc:
        fail(str(exc))
