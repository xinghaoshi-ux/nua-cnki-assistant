---
name: cnki-research
description: Search Chinese and international scholarly literature through CNKI in Codex or Claude Code on macOS, Windows, or Linux; control the plugin-managed Chrome session with Playwright, rank results, read accessible full text through each paper's detail page and CNKI AI阅读, download PDF or explicitly requested CAJ files, retrieve metadata, and generate citations. Use for requests such as NUA知网小助手, NUA论文小助手, cnki-research, CNKI, 知网, 使用知网搜索, 用知网查, 在知网搜, 帮我上知网, 查一下知网的文章, 查知网论文, 搜知网文献, 找知网论文, 知网检索, 高级检索, 专业检索, 查文献, 读知网全文, 知网全文阅读, 下载知网论文, PDF下载, CAJ下载, or equivalent requests to find, inspect, read, summarize, cite, export, or download papers through CNKI.
---

# CNKI Research

Use two distinct retrieval paths and label their results accurately:

- Use `scripts/scholar_metadata.py` for fast OpenAlex or Crossref metadata retrieval. Never describe these results as a direct CNKI search.
- Use the plugin-provided `cnki-playwright` MCP server for every direct CNKI task whenever its browser tools are available. On Codex, use the persistent `node_repl js` Playwright path only as a fallback when the plugin MCP tools are unavailable.

Do not bypass CAPTCHA, authentication, institutional access, paywalls, rate limits, or access controls.

## Select the retrieval path

1. If the user explicitly says `cnki-research`, CNKI, 知网, 进知网, 知网检索, professional search, or supplies a CNKI URL, launch or reuse the Playwright-controlled Google Chrome session and search CNKI directly. Treat close variants with the same intent as direct-CNKI requests; do not start with OpenAlex or Crossref.
2. If the user asks generally for papers, DOI metadata, citations, citation counts, or open-access availability, start with OpenAlex.
3. Use Crossref to verify DOI metadata or fill missing publication fields.
4. For systematic or high-recall work, combine sources, record the source of every result, and deduplicate by normalized DOI, then normalized title.
5. Ask for clarification only when an omitted constraint would materially change the search, such as topic, years, document type, or result limit.

## Search scholarly metadata

Inform the user that search terms or DOI values will be sent to the selected public API. Do not send unrelated private context.

Run:

```bash
python3 scripts/scholar_metadata.py search "人工智能 教育" --limit 10 --from-year 2020 --to-year 2026
python3 scripts/scholar_metadata.py doi "10.1000/example"
python3 scripts/scholar_metadata.py cite "10.1000/example" --style gbt7714
```

On native Windows, use `py -3` instead of `python3` when only the Python launcher is available.

The script URL-encodes inputs, validates limits, years, DOI syntax, and emits UTF-8 JSON or citation text. Use `--source crossref` when Crossref is specifically required.

For field meanings and search constraints, read [references/metadata-sources.md](references/metadata-sources.md).
For citation rules, read [references/citation-formats.md](references/citation-formats.md).

## Search CNKI directly

Use Playwright with the plugin-managed Google Chrome profile. Do not switch to a different browser surface merely to bypass authentication, verification, or access controls.

### Establish the Chrome session

1. Discover the plugin-provided `cnki-playwright` MCP browser tools. Their names are host-dependent; use the available tab, snapshot, navigation, click, fill, evaluation, screenshot, and download tools rather than assuming one fixed namespace.
2. List current tabs first and reuse a live CNKI tab. If the previous context is closed, create a new tab instead of calling methods on the dead page.
3. The MCP launcher reuses local endpoint `http://127.0.0.1:9337` or starts a dedicated Chrome profile. On macOS Chrome starts in the background without activation. On Windows Chrome starts minimized so it does not take focus; the user can restore it from the taskbar for login. Linux uses the same minimized best-effort path.
4. If MCP browser tools are unavailable in Codex but `node_repl js` is available, import `playwright`, connect to the same endpoint with `chromium.connectOverCDP`, and follow the same tab workflow. Claude Code should use the plugin MCP tools.
5. Start from the Nanjing University of the Arts proxy entry:
   `https://v.nua.edu.cn/https/77726476706e69737468656265737421e7e056d2243e635930068cb8/`
6. If institutional login is required, tell the user once to complete it manually in Chrome, then keep the task active and poll the current page every 5–10 seconds for up to 4 minutes. Continue automatically as soon as the CNKI page displays `南京艺术学院`; do not require the user to reply that login is complete. If the timeout expires, leave Chrome open and ask the user to confirm after completing login.
7. Never automate credentials, CAPTCHA solving, or browser permission approval.
8. Allow multiple tabs and popups when CNKI normally uses them. Keep the results tab open, select new detail or reader tabs through Playwright, and close them when finished.
9. Never call `bringToFront`, activate Chrome through the operating system, or otherwise raise its window. The user may switch to Chrome manually when login or verification is required.

1. Enter the CNKI advanced-search page through the live `高级检索` link on the proxied CNKI homepage.
2. Verify that the visible page is the CNKI advanced-search interface before interacting.
3. Inspect fresh page state before every interaction. Prefer Playwright roles, labels, visible text, or validated DOM attributes; use a screenshot when visual state matters.
4. Use advanced-search rows by default. Switch to `专业检索` only when the user supplies a professional expression or explicitly requests that mode.
5. Parse the topic into concept groups. Put synonyms or near-synonyms from one concept in the same theme box using ` + `; put distinct concepts in separate theme rows and use `AND` unless the user requests high recall, in which case use `OR`.
6. Keep the expansion compact and show the effective query to the user. Ask for confirmation only when the expansion materially changes the topic.
7. Apply requested document type, source category, date, discipline, and language filters. Do not silently force CSSCI, core journals, or a year range.
8. Submit once and wait for a visible results signal. If a CAPTCHA actually blocks the form or results, stop for manual completion.
9. Sort according to the user's goal: relevance by default; cited count descending for influential/classic papers; date descending for recent work.
10. Set 50 results per page when available. Use summary/detail view when abstracts are requested.
11. Extract only the requested number of records. Open detail pages only when the list view lacks an abstract or required metadata.

Read [references/cnki-browser-workflow.md](references/cnki-browser-workflow.md) before operating CNKI. It defines the Playwright Chrome interaction, ranking, extraction, and full-text workflow.

Use the field codes and expression rules in [references/cnki-query-guide.md](references/cnki-query-guide.md). Treat the live CNKI interface as authoritative if it differs.

## Handle verification and authentication

Treat CAPTCHA state as current page state, not persistent session state.

1. Take a fresh DOM snapshot or screenshot before reporting a CAPTCHA.
2. Report a slider, image challenge, or CAPTCHA only when its interactive control is currently visible and blocks the required search action.
3. Do not infer an active challenge from a `captchaId` URL parameter, hidden/stale CAPTCHA markup, a previous challenge, or an old snapshot.
4. If the user says verification is complete, immediately inspect fresh page state. When the search form or results are usable and no challenge control is visible, continue without mentioning verification again.
5. If a login prompt or institutional-access step is visible and blocking access, tell the user exactly what must be completed manually, keep the task active, and resume automatically when fresh page state becomes usable.

Never solve or circumvent anti-bot verification programmatically. Do not download subscription content unless the user has legitimate access and explicitly requests the download.

## Read and summarize accessible full text

When the user asks to read papers in full, repeat this exact UI path for every paper:

1. Click the paper title in the results tab and wait for its proxied `文献知网节` detail tab.
2. On that detail page, click the visible `CNKI AI阅读` button. Do not navigate directly to an AI URL copied from the results page or DOM.
3. Select the newly opened AI-reading tab through Playwright without raising Chrome, and verify that its title matches the paper.
4. Treat the AI reader as asynchronous and lazy-loaded. Poll the current title and reader state every 2 seconds for up to 30 seconds. Do not classify the article from the first screen, a short body-text snapshot, or a transient `暂无本文阅读权益` message.
5. Determine the expected document extent from a page counter, article outline, or page shells. For paginated readers, locate the document scroll container and visit every page shell in order. Wait for each page to load text, canvas, or image content; revisit any empty page once. Verify the last page and confirm that the loaded content covers the article body through its conclusion and references. Do not use total character count or the sidebar prompt containing `参考文献` as proof of full-text access.
6. Classify the reader state explicitly:
   - `verified accessible`: the title matches, all expected pages or complete sections load, and the terminal article content is present.
   - `still loading`: page shells exist but one or more pages remain empty or the document is still expanding.
   - `verified unavailable`: no article pages load and the current reader continues to show `暂无本文阅读权益` across two checks 3–5 seconds apart.
   - `reader error/incomplete`: the reader fails to settle, shows only metadata or generated notes, or cannot expose the expected document extent.
7. Before reporting `verified unavailable`, close the AI-reading tab, return to the same detail tab, click the visible `CNKI AI阅读` button again, and repeat steps 3–6 once. Report no access only when both independent attempts reach `verified unavailable` for the same title. Never infer no access from a prior paper's reader state.
8. Read the complete body, including introduction, methods or design process, results or analysis, conclusion, and references. PDF text may be extracted from the document stream already loaded by the AI reader, but only after completing the UI and page-validation sequence above. Do not save or redistribute the source file unless the user explicitly requests a download.
9. If both attempts expose only an abstract, recommendations, generated notes, or a trial fragment, mark the paper as incomplete rather than unavailable and replace it with another candidate. Never label an abstract-only synthesis as a full-text summary.
10. After completing the extraction, close the AI-reading and detail tabs without foregrounding Chrome, then continue from the preserved results tab.
11. If the paper is inaccessible or incomplete, close its reader and detail tabs before replacing it with another candidate.

For each full-text summary, distinguish the authors' claims from critical assessment and cover:

- bibliographic identity and research object
- research question and theoretical framework
- method, sample, materials, or design process actually reported
- major findings and conclusions
- contribution, limitations, and actionable implications supported by the paper
- topic-specific mechanisms, outcomes, and constraints when the paper reports them

## Download papers

When the user asks to download papers, repeat this exact UI path for every paper:

1. Click the paper title in the results tab and wait for its proxied `文献知网节` detail tab.
2. Click the visible `PDF下载` button on that detail page. PDF is the default format.
3. Click `CAJ下载` only when the user explicitly requests CAJ. Do not choose CAJ merely because it is available.
4. Do not use a download link captured from the results list, construct a download URL, or navigate directly to a download endpoint.
5. Use Playwright's download event, wait for completion, and verify that the saved file exists, is non-empty, and has the requested file type.
6. After the download is verified, close the detail tab without foregrounding Chrome, return to the preserved results tab, and repeat.

## Extract and report results

Prefer visible DOM state and semantic selectors. Page structure changes frequently; do not depend on a generic first `table`, fixed column indexes, or broad selectors such as `[class*="title"]` without validating the matched content.

Capture, when available:

- title
- authors
- source or journal
- publication date
- document type
- abstract and keywords
- DOI
- CNKI detail URL
- citation or download counts, labeled as CNKI values
- retrieval source and retrieval date

For every batch:

1. Report the query, filters, source, retrieval date, pages inspected, and result count.
2. Preserve missing values as empty/null; do not infer bibliographic facts.
3. Deduplicate before export.
4. Distinguish metadata links, landing pages, and verified direct PDF links.
5. For “most relevant” requests, rank by direct topic overlap first, then title/keyword overlap, abstract overlap, and finally citations as a tie-breaker. Do not equate high citation count with relevance.
6. Label summaries as `原始摘要` when faithfully translated or condensed from a visible abstract, and `内容概述` when synthesized from accessible full text. Never manufacture an abstract from a title.
7. Prefer a compact table in chat; export JSON, CSV, RIS, or CNKI Word records only when requested.

## Generate citations

Generate citations from retrieved metadata, not from search snippets. Verify title, author order, year, journal, volume, issue, pages, and DOI when accuracy matters.

- APA: preserve author order and use the canonical DOI URL.
- BibTeX: use a stable key and escape special characters.
- GB/T 7714: include the correct document-type marker and available publication fields.

State which fields are missing rather than silently inventing them.

## Failure handling

- Empty OpenAlex results: retry with translated terms, synonyms, or fewer filters; then offer direct CNKI search.
- Missing DOI: search by exact title and author; do not fabricate a DOI.
- Chrome launch failure: verify Node.js 18+, `npx`, and Google Chrome. On Windows also verify the standard Chrome install locations or set `CNKI_CHROME_EXECUTABLE`.
- Closed Playwright context: create a new MCP tab or reconnect the Codex Playwright fallback to the same local endpoint, then resume from the proxy entry.
- CNKI selector mismatch: inspect the live page and rebuild Playwright locators from current roles, text, and attributes.
- Stale CAPTCHA signal: discard the old signal, inspect the current visible page, and continue when search controls are usable.
- CNKI AI阅读 appears to have no full-text rights: apply the two-attempt, delayed, page-by-page validation workflow above. Exclude the record only after both attempts are `verified unavailable`; otherwise label it `reader error/incomplete` and do not claim a permissions failure.
- Access denied or repeated verification: stop and report the limitation.
- No abstract: record it as unavailable and avoid substituting unrelated page text.
