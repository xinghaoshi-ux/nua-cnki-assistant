#!/usr/bin/env python3
"""Portable repository checks for NUA CNKI Assistant."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "cnki-research"


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def require_files(paths: tuple[Path, ...]) -> None:
    for path in paths:
        if not path.is_file():
            fail(f"missing required file: {path.relative_to(ROOT)}")


def validate_launcher(node: str, launcher: Path, mcp: dict) -> None:
    subprocess.run([node, "--check", str(launcher)], check=True)
    embedded = mcp["mcpServers"]["cnki-playwright"]["args"][1]
    if embedded != launcher.read_text(encoding="utf-8"):
        fail(".mcp.json launcher is stale; run scripts/sync-mcp-config.py")

    for platform in ("darwin", "win32", "linux"):
        env = os.environ.copy()
        env.update(
            {
                "CNKI_LAUNCHER_DRY_RUN": "1",
                "CNKI_TEST_PLATFORM": platform,
                "CNKI_CHROME_EXECUTABLE": "/validation/chrome",
            }
        )
        result = subprocess.run(
            [node, str(launcher)],
            check=True,
            capture_output=True,
            text=True,
            env=env,
        )
        plan = json.loads(result.stderr.strip().splitlines()[-1])
        if plan["platform"] != platform:
            fail(f"launcher dry-run platform mismatch: {platform}")
        if platform == "win32":
            command_name = Path(plan["mcp"]["command"]).name.lower()
            if command_name not in {"cmd", "cmd.exe"}:
                fail("Windows launcher must invoke npx through cmd.exe")
            if "--start-minimized" not in plan["chromeArgs"]:
                fail("Windows Chrome must start minimized")
        elif plan["mcp"]["command"] != "npx":
            fail(f"{platform} launcher must invoke npx directly")

    wsl_env = os.environ.copy()
    wsl_env.update(
        {
            "CNKI_LAUNCHER_DRY_RUN": "1",
            "CNKI_TEST_PLATFORM": "linux",
            "CNKI_TEST_WSL": "1",
            "CNKI_CHROME_EXECUTABLE": (
                "/mnt/c/Program Files/Google/Chrome/Application/chrome.exe"
            ),
        }
    )
    wsl_result = subprocess.run(
        [node, str(launcher)],
        check=True,
        capture_output=True,
        text=True,
        env=wsl_env,
    )
    wsl_plan = json.loads(wsl_result.stderr.strip().splitlines()[-1])
    if not wsl_plan.get("isWsl") or "--start-minimized" not in wsl_plan["chromeArgs"]:
        fail("WSL launcher plan is incomplete")


def validate_desktop_installer(node: str, installer: Path) -> None:
    subprocess.run([node, "--check", str(installer)], check=True)
    with tempfile.TemporaryDirectory() as directory:
        config_path = Path(directory) / "claude_desktop_config.json"
        config_path.write_text(
            json.dumps({"mcpServers": {"existing": {"command": "example"}}}),
            encoding="utf-8",
        )
        env = os.environ.copy()
        env["CLAUDE_DESKTOP_CONFIG"] = str(config_path)
        subprocess.run([node, str(installer)], check=True, env=env, capture_output=True)
        installed = load_json(config_path)
        if "existing" not in installed["mcpServers"]:
            fail("Claude Desktop installer removed an existing MCP server")
        if "cnki-playwright" not in installed["mcpServers"]:
            fail("Claude Desktop installer did not add cnki-playwright")
        subprocess.run(
            [node, str(installer), "--remove"],
            check=True,
            env=env,
            capture_output=True,
        )
        removed = load_json(config_path)
        if "cnki-playwright" in removed["mcpServers"]:
            fail("Claude Desktop installer did not remove cnki-playwright")
        if "existing" not in removed["mcpServers"]:
            fail("Claude Desktop uninstaller removed an existing MCP server")


def main() -> None:
    codex_manifest_path = PLUGIN / ".codex-plugin" / "plugin.json"
    claude_manifest_path = PLUGIN / ".claude-plugin" / "plugin.json"
    mcp_path = PLUGIN / ".mcp.json"
    codex_marketplace_path = ROOT / ".agents" / "plugins" / "marketplace.json"
    claude_marketplace_path = ROOT / ".claude-plugin" / "marketplace.json"
    skill_path = PLUGIN / "skills" / "cnki-research" / "SKILL.md"
    browser_reference = (
        PLUGIN
        / "skills"
        / "cnki-research"
        / "references"
        / "cnki-browser-workflow.md"
    )
    metadata_script = (
        PLUGIN / "skills" / "cnki-research" / "scripts" / "scholar_metadata.py"
    )
    launcher = PLUGIN / "scripts" / "launch-cnki-playwright-mcp.cjs"
    sync_script = PLUGIN / "scripts" / "sync-mcp-config.py"
    desktop_installer = ROOT / "scripts" / "configure-claude-desktop.mjs"
    readme = ROOT / "README.md"

    require_files(
        (
            codex_manifest_path,
            claude_manifest_path,
            mcp_path,
            codex_marketplace_path,
            claude_marketplace_path,
            skill_path,
            browser_reference,
            metadata_script,
            launcher,
            sync_script,
            desktop_installer,
            readme,
        )
    )

    codex_manifest = load_json(codex_manifest_path)
    claude_manifest = load_json(claude_manifest_path)
    mcp = load_json(mcp_path)
    codex_marketplace = load_json(codex_marketplace_path)
    claude_marketplace = load_json(claude_marketplace_path)

    for field in ("name", "version", "description", "author"):
        if field not in codex_manifest:
            fail(f"Codex manifest is missing {field}")
        if field not in claude_manifest:
            fail(f"Claude manifest is missing {field}")
    if codex_manifest["name"] != "cnki-research":
        fail("Codex plugin name must be cnki-research")
    if claude_manifest["name"] != codex_manifest["name"]:
        fail("Codex and Claude plugin names differ")
    if not re.fullmatch(
        r"\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?",
        codex_manifest["version"],
    ):
        fail("Codex plugin version is not semantic versioning")
    if codex_manifest["version"].split("+", 1)[0] != claude_manifest["version"]:
        fail("Codex base version and Claude version differ")
    if codex_manifest.get("mcpServers") != "./.mcp.json":
        fail("Codex manifest must reference ./.mcp.json")

    server = mcp.get("mcpServers", {}).get("cnki-playwright")
    if not isinstance(server, dict):
        fail("cnki-playwright MCP server is missing")
    if server.get("command") != "node" or server.get("args", [])[:1] != ["-e"]:
        fail("MCP server must use the portable embedded Node launcher")

    codex_entries = codex_marketplace.get("plugins", [])
    if len(codex_entries) != 1 or codex_entries[0].get("name") != "cnki-research":
        fail("Codex marketplace entry does not match the plugin")
    if codex_entries[0].get("source", {}).get("path") != "./plugins/cnki-research":
        fail("Codex marketplace plugin path is incorrect")

    claude_entries = claude_marketplace.get("plugins", [])
    if len(claude_entries) != 1 or claude_entries[0].get("name") != "cnki-research":
        fail("Claude marketplace entry does not match the plugin")
    if claude_entries[0].get("source") != "./plugins/cnki-research":
        fail("Claude marketplace plugin path is incorrect")
    if claude_marketplace.get("name") != codex_marketplace.get("name"):
        fail("Codex and Claude marketplace names differ")

    skill_text = skill_path.read_text(encoding="utf-8")
    if not skill_text.startswith("---\n") or "name: cnki-research" not in skill_text[:1500]:
        fail("skill front matter is invalid")
    for required_phrase in ("Claude Code", "Windows", "cnki-playwright"):
        if required_phrase not in skill_text:
            fail(f"skill is missing cross-platform guidance: {required_phrase}")

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
    compile(sync_script.read_text(encoding="utf-8"), str(sync_script), "exec")

    node = shutil.which("node")
    if not node:
        fail("Node.js is required for validation")
    validate_launcher(node, launcher, mcp)
    validate_desktop_installer(node, desktop_installer)

    readme_text = readme.read_text(encoding="utf-8")
    for command in (
        "codex plugin add cnki-research@nua-cnki-assistant",
        "claude plugin install cnki-research@nua-cnki-assistant",
    ):
        if command not in readme_text:
            fail(f"README is missing installation command: {command}")

    print("NUA CNKI Assistant cross-platform repository validation passed.")


if __name__ == "__main__":
    try:
        main()
    except (
        json.JSONDecodeError,
        KeyError,
        TypeError,
        OSError,
        subprocess.CalledProcessError,
    ) as exc:
        fail(str(exc))
