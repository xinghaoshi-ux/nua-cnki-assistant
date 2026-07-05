#!/usr/bin/env node

import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.dirname(scriptDir);
const mcpPath = path.join(repoRoot, "plugins", "cnki-research", ".mcp.json");
const remove = process.argv.includes("--remove");

function configPath() {
  if (process.env.CLAUDE_DESKTOP_CONFIG) {
    return path.resolve(process.env.CLAUDE_DESKTOP_CONFIG);
  }
  if (process.platform === "darwin") {
    return path.join(
      os.homedir(),
      "Library",
      "Application Support",
      "Claude",
      "claude_desktop_config.json",
    );
  }
  if (process.platform === "win32") {
    const appData = process.env.APPDATA
      || path.join(os.homedir(), "AppData", "Roaming");
    return path.join(appData, "Claude", "claude_desktop_config.json");
  }
  throw new Error("Claude Desktop chat configuration is supported on macOS and Windows.");
}

const destination = configPath();
let config = {};
if (fs.existsSync(destination)) {
  config = JSON.parse(fs.readFileSync(destination, "utf8"));
  const stamp = new Date().toISOString().replaceAll(":", "-");
  fs.copyFileSync(destination, `${destination}.backup-${stamp}`);
}

config.mcpServers = config.mcpServers || {};
if (remove) {
  delete config.mcpServers["cnki-playwright"];
} else {
  const pluginMcp = JSON.parse(fs.readFileSync(mcpPath, "utf8"));
  config.mcpServers["cnki-playwright"] = pluginMcp.mcpServers["cnki-playwright"];
}

fs.mkdirSync(path.dirname(destination), { recursive: true });
fs.writeFileSync(destination, `${JSON.stringify(config, null, 2)}\n`, "utf8");
process.stdout.write(
  `${remove ? "Removed from" : "Added to"} ${destination}. Restart Claude Desktop.\n`,
);
