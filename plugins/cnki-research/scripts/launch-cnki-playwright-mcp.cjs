const fs = require("node:fs");
const http = require("node:http");
const os = require("node:os");
const path = require("node:path");
const { spawn, spawnSync } = require("node:child_process");

const MCP_PACKAGE = "@playwright/mcp@0.0.77";
const dryRun = process.env.CNKI_LAUNCHER_DRY_RUN === "1";
const platform = dryRun && process.env.CNKI_TEST_PLATFORM
  ? process.env.CNKI_TEST_PLATFORM
  : process.platform;
const isWsl = platform === "linux" && (
  process.env.CNKI_TEST_WSL === "1"
  || Boolean(process.env.WSL_DISTRO_NAME)
  || (!dryRun
    && fs.existsSync("/proc/version")
    && /microsoft/i.test(fs.readFileSync("/proc/version", "utf8")))
);
const port = Number(process.env.CNKI_CHROME_DEBUG_PORT || "9337");

if (!Number.isInteger(port) || port < 1 || port > 65535) {
  throw new Error("CNKI_CHROME_DEBUG_PORT must be an integer from 1 to 65535.");
}

const endpoint = `http://127.0.0.1:${port}`;

function wslNativeProfile() {
  if (!isWsl || dryRun) return null;
  const localAppData = spawnSync(
    "cmd.exe",
    ["/d", "/s", "/c", "echo", "%LOCALAPPDATA%"],
    { encoding: "utf8" },
  );
  if (localAppData.status !== 0 || !localAppData.stdout.trim()) return null;
  const converted = spawnSync(
    "wslpath",
    ["-u", localAppData.stdout.trim()],
    { encoding: "utf8" },
  );
  if (converted.status !== 0 || !converted.stdout.trim()) return null;
  return path.join(converted.stdout.trim(), "NUA-CNKI-Assistant", "chrome-profile");
}

const neutralProfile = wslNativeProfile()
  || path.join(os.homedir(), ".nua-cnki-assistant", "chrome-profile");
const legacyProfile = path.join(
  os.homedir(),
  ".codex",
  "browser-profiles",
  "cnki-research",
);
const profile = process.env.CNKI_CHROME_PROFILE
  || (fs.existsSync(legacyProfile) && !fs.existsSync(neutralProfile)
    ? legacyProfile
    : neutralProfile);

function chromeCandidates(targetPlatform) {
  if (targetPlatform === "darwin") {
    return [
      "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
      path.join(
        os.homedir(),
        "Applications",
        "Google Chrome.app",
        "Contents",
        "MacOS",
        "Google Chrome",
      ),
    ];
  }

  if (targetPlatform === "win32") {
    return [
      process.env.LOCALAPPDATA && path.join(
        process.env.LOCALAPPDATA,
        "Google",
        "Chrome",
        "Application",
        "chrome.exe",
      ),
      process.env.PROGRAMFILES && path.join(
        process.env.PROGRAMFILES,
        "Google",
        "Chrome",
        "Application",
        "chrome.exe",
      ),
      process.env["PROGRAMFILES(X86)"] && path.join(
        process.env["PROGRAMFILES(X86)"],
        "Google",
        "Chrome",
        "Application",
        "chrome.exe",
      ),
    ].filter(Boolean);
  }

  if (isWsl) {
    return [
      "/mnt/c/Program Files/Google/Chrome/Application/chrome.exe",
      "/mnt/c/Program Files (x86)/Google/Chrome/Application/chrome.exe",
    ];
  }

  return [
    "/usr/bin/google-chrome",
    "/usr/bin/google-chrome-stable",
    "/usr/bin/chromium",
    "/usr/bin/chromium-browser",
    "/opt/google/chrome/google-chrome",
  ];
}

function findChrome() {
  if (process.env.CNKI_CHROME_EXECUTABLE) {
    if (dryRun || fs.existsSync(process.env.CNKI_CHROME_EXECUTABLE)) {
      return process.env.CNKI_CHROME_EXECUTABLE;
    }
    throw new Error(
      `CNKI_CHROME_EXECUTABLE does not exist: ${process.env.CNKI_CHROME_EXECUTABLE}`,
    );
  }

  return chromeCandidates(platform).find((candidate) => fs.existsSync(candidate)) || null;
}

function endpointIsReady() {
  return new Promise((resolve) => {
    const request = http.get(`${endpoint}/json/version`, (response) => {
      response.resume();
      resolve(response.statusCode >= 200 && response.statusCode < 300);
    });
    request.setTimeout(750, () => request.destroy());
    request.on("error", () => resolve(false));
  });
}

async function waitForEndpoint() {
  for (let attempt = 0; attempt < 150; attempt += 1) {
    if (await endpointIsReady()) return true;
    await new Promise((resolve) => setTimeout(resolve, 100));
  }
  return false;
}

function browserProfilePath() {
  if (!isWsl || dryRun) return profile;
  const converted = spawnSync("wslpath", ["-w", profile], { encoding: "utf8" });
  if (converted.status !== 0 || !converted.stdout.trim()) {
    throw new Error("Unable to convert the Chrome profile path with wslpath.");
  }
  return converted.stdout.trim();
}

function chromeArguments() {
  const args = [
    "--remote-debugging-address=127.0.0.1",
    `--remote-debugging-port=${port}`,
    `--user-data-dir=${browserProfilePath()}`,
    "--no-first-run",
    "--no-default-browser-check",
  ];
  if (platform === "win32" || platform === "linux" || isWsl) {
    args.push("--start-minimized");
  }
  args.push("about:blank");
  return args;
}

function launchChrome(chrome) {
  fs.mkdirSync(profile, { recursive: true });
  const args = chromeArguments();
  let child;

  if (platform === "darwin" && chrome.includes(".app/Contents/MacOS/")) {
    const appPath = chrome.slice(0, chrome.indexOf(".app/") + 4);
    child = spawn(
      "/usr/bin/open",
      ["-g", "-n", "-a", appPath, "--args", ...args],
      { detached: true, stdio: "ignore" },
    );
  } else {
    child = spawn(chrome, args, {
      detached: true,
      stdio: "ignore",
      windowsHide: false,
    });
  }

  child.unref();
}

function mcpInvocation() {
  const args = ["-y", MCP_PACKAGE, "--cdp-endpoint", endpoint];
  if (platform === "win32") {
    return {
      command: process.env.ComSpec || "cmd.exe",
      args: ["/d", "/s", "/c", "npx", ...args],
    };
  }
  return { command: "npx", args };
}

function startMcp() {
  const invocation = mcpInvocation();
  const child = spawn(invocation.command, invocation.args, {
    env: process.env,
    stdio: "inherit",
    windowsHide: true,
  });

  child.on("error", (error) => {
    process.stderr.write(`Unable to start Playwright MCP: ${error.message}\n`);
    process.exit(1);
  });
  child.on("exit", (code, signal) => {
    if (signal) process.kill(process.pid, signal);
    else process.exit(code == null ? 1 : code);
  });
  for (const signal of ["SIGINT", "SIGTERM"]) {
    process.on(signal, () => child.kill(signal));
  }
}

async function main() {
  const chrome = findChrome();

  if (dryRun) {
    process.stderr.write(`${JSON.stringify({
      platform,
      isWsl,
      chrome,
      endpoint,
      profile,
      chromeArgs: chromeArguments(),
      mcp: mcpInvocation(),
    })}\n`);
    return;
  }

  if (!(await endpointIsReady())) {
    if (!chrome) {
      throw new Error(
        "Google Chrome was not found. Install Chrome or set CNKI_CHROME_EXECUTABLE.",
      );
    }
    launchChrome(chrome);
    if (!(await waitForEndpoint())) {
      throw new Error(`Google Chrome did not expose its local endpoint at ${endpoint}.`);
    }
  }

  startMcp();
}

main().catch((error) => {
  process.stderr.write(`NUA CNKI Assistant: ${error.message}\n`);
  process.exit(1);
});
