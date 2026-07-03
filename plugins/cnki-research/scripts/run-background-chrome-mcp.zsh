#!/bin/zsh
set -euo pipefail

readonly port="${CNKI_CHROME_DEBUG_PORT:-9337}"
readonly endpoint="http://127.0.0.1:${port}"
readonly profile="${CNKI_CHROME_PROFILE:-${HOME}/.codex/browser-profiles/cnki-research}"
readonly chrome="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

if [[ "$(uname -s)" != "Darwin" || ! -x "${chrome}" ]]; then
  exec npx -y @playwright/mcp@0.0.77 --extension
fi

if ! curl -fsS "${endpoint}/json/version" >/dev/null 2>&1; then
  mkdir -p "${profile}"
  open -g -na "Google Chrome" --args \
    --remote-debugging-address=127.0.0.1 \
    --remote-debugging-port="${port}" \
    --user-data-dir="${profile}" \
    --no-first-run \
    --no-default-browser-check \
    about:blank

  for _ in {1..100}; do
    if curl -fsS "${endpoint}/json/version" >/dev/null 2>&1; then
      break
    fi
    sleep 0.1
  done
fi

if ! curl -fsS "${endpoint}/json/version" >/dev/null 2>&1; then
  print -u2 "NUA CNKI Assistant could not start background Chrome on ${endpoint}"
  exit 1
fi

exec npx -y @playwright/mcp@0.0.77 --endpoint "${endpoint}"
