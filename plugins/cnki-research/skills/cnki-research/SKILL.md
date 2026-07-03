---
name: cnki-research
description: Search Chinese and international scholarly literature, operate CNKI through the Nanjing University of the Arts proxy with the available Codex browser or Playwright MCP session, retrieve OpenAlex or Crossref metadata, inspect DOI and open-access availability, extract CNKI results, abstracts, and accessible CNKI AI full text, produce structured full-text paper summaries, download papers, and generate APA, BibTeX, or GB/T 7714 citations. Use for requests such as CNKI, 知网, 使用知网搜索, 用知网查, 在知网搜, 帮我上知网, 查一下知网的文章, 查知网论文, 搜知网文献, 找知网论文, 知网检索, 高级检索, 专业检索, 读知网全文, 知网全文阅读, 下载知网论文, or equivalent requests to find, inspect, read, summarize, cite, export, or download papers through CNKI.
---

# CNKI Research

Use two distinct retrieval paths and label their results accurately:

- Use `scripts/scholar_metadata.py` for fast OpenAlex or Crossref metadata retrieval. Never describe these results as a direct CNKI search.
- Use the plugin-provided `cnki-playwright` MCP server for searches that must run directly on CNKI, including CNKI professional expressions, CNKI filters, result pages, article abstracts, downloads, and accessible full text. On macOS, it connects to the plugin-managed visible Chrome instance through a local remote-debugging endpoint; other platforms fall back to Playwright MCP extension mode.

Do not bypass CAPTCHA, authentication, institutional access, paywalls, rate limits, or access controls.

## Select the retrieval path

1. If the user explicitly says CNKI, 知网, professional search, or supplies a CNKI URL, use direct CNKI browser search.
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

The script URL-encodes inputs, validates limits, years, DOI syntax, and emits UTF-8 JSON or citation text. Use `--source crossref` when Crossref is specifically required.

For field meanings and search constraints, read [references/metadata-sources.md](references/metadata-sources.md).
For citation rules, read [references/citation-formats.md](references/citation-formats.md).

## Search CNKI directly

Choose the browser surface before interacting:

1. For every direct CNKI browser task, use the plugin-provided `cnki-playwright` MCP server to control Chrome by default whenever its tools are callable. Its tools may appear under a namespaced MCP tool group; discover and use the browser tab, snapshot, navigation, click, fill, evaluation, and screenshot tools from that server. Apply this default when the user invokes `cnki-research` without naming a browser surface; do not ask the user to choose.
2. Use the `browser:control-in-app-browser` skill only when Playwright MCP is unavailable or the user explicitly requests the in-app Browser. Read that skill before using it.
3. If the user explicitly requests another available browser surface, follow that request.
4. Do not switch browser surfaces merely to bypass authentication or verification.

Do not assume OpenClaw actions such as `action: navigate`, `kind: fill`, or persistent `ref=e123` identifiers exist in Codex.

### Establish a Playwright MCP session

1. List tabs first. Reuse a live CNKI tab when one exists.
2. If the previous browser or page was closed, create a new tab at the proxy entry instead of calling page methods on the dead context.
3. The plugin launcher starts a dedicated, visible Chrome instance with macOS background activation and connects Playwright over its remote-debugging endpoint. Do not replace this with ordinary foreground launch or extension mode.
4. Allow multiple tabs. Keep the results tab open, select new detail or reader tabs through Playwright, and close worker tabs after each paper.
5. Never call `bringToFront`, activate Chrome through the operating system, or otherwise raise its window. The user may switch to Chrome manually for institutional login or a visible verification challenge.

1. Start from the Nanjing University of the Arts proxy entry:
   `https://v.nua.edu.cn/https/77726476706e69737468656265737421e7e056d2243e635930068cb8/`
2. Wait for the CNKI homepage and confirm the page shows the institutional identity `南京艺术学院`. If the proxy requires login, tell the user once to complete it manually, then keep the turn active and monitor the current tab. Continue automatically as soon as the CNKI homepage or institutional identity appears.
3. Enter advanced search through the live `高级检索` link. Prefer this in-site navigation over constructing or reusing a deep proxy URL because proxy host encodings and application context vary across CNKI services.
4. Inspect the current page before every interaction. With Playwright MCP, use a fresh accessibility snapshot for locator ground truth and take a viewport screenshot when visual state matters.
5. Locate controls using current accessible roles, labels, visible text, or inspected DOM. Never reuse element identifiers copied from old sessions.
6. Enter a professional expression or configure the visible advanced-search rows.
7. Apply requested date, source, document-type, discipline, or sorting filters.
8. Submit once and wait for a concrete results-page signal to settle. Prefer a result count, result-list container, URL change, or enabled pagination control over a fixed sleep.
9. Extract only the requested number of pages. Keep a modest pace and avoid repeated retries.
10. Open article pages only when abstracts or additional metadata are requested.

Use ordinary CNKI at `https://kns.cnki.net/kns8s/AdvSearch?type=expert` only when the user explicitly requests it or when the Nanjing University of the Arts proxy is unavailable and the user accepts the fallback.

Use the field codes and expression rules in [references/cnki-query-guide.md](references/cnki-query-guide.md). Treat the live CNKI interface as authoritative if it differs.

### Monitor user-controlled access steps

For browser-connection approval, institutional login, or a visible verification challenge:

1. Explain the required manual action once in commentary.
2. Do not send a final response merely to wait, and do not require messages such as “已完成” or “继续”.
3. Keep the task active and re-inspect fresh tab, URL, viewport, and DOM state at a modest pace. Prefer a browser-native wait tool; otherwise use repeated tab and snapshot checks without aggressive requests or blocking sleeps longer than 60 seconds.
4. Treat user messages received during monitoring as additional input, but do not depend on them to resume.
5. Continue the original workflow immediately when the expected page state becomes usable.
6. Never automate credentials, CAPTCHA solving, `Allow & select`, or any other user-controlled security action.
7. Stop only when the browser connection is genuinely unavailable, access is denied, repeated verification prevents progress, or the product ends the active turn.

## Handle verification and authentication

Treat CAPTCHA state as current page state, not persistent session state.

1. Take both a fresh viewport screenshot and a fresh DOM/accessibility snapshot before reporting a CAPTCHA.
2. Report a slider, image challenge, or CAPTCHA only when its interactive control intersects the current viewport and blocks the required search action.
3. Do not infer an active challenge from a `captchaId` URL parameter, hidden/stale CAPTCHA markup, a previous challenge, or an old snapshot.
4. Do not rely on `isVisible()` alone. Confirm that the challenge has a nonzero bounding box whose rectangle overlaps the viewport. Treat large negative coordinates, offscreen transforms, zero-area boxes, and clipped overlays as inactive. For example, an element at `y=-999985` is stale/offscreen even if computed CSS says `visibility: visible`.
5. If the screenshot and raw DOM text disagree, use viewport geometry and the screenshot to determine whether the challenge is actionable. Continue when the normal search interface is usable.
6. When reporting a real challenge, include or link the fresh screenshot so the user can verify the same state.
7. If the user says verification is complete, immediately inspect fresh page state. When the search form or results are usable and no actionable challenge is visible, continue without mentioning verification again.
8. If a login prompt or institutional-access step is currently visible and blocking access, tell the user exactly what must be completed manually, then monitor it under `Monitor user-controlled access steps`.

Never solve or circumvent anti-bot verification programmatically. Do not download subscription content unless the user has legitimate access and explicitly requests the download.

## Extract and report results

Prefer visible DOM state and semantic selectors. Page structure changes frequently; do not depend on a generic first `table`, fixed column indexes, or broad selectors such as `[class*="title"]` without validating the matched content. Before bulk extraction, identify the exact results container and validate its headers or repeated row structure. Extract one bounded page at a time with one DOM projection when possible.

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
5. Prefer a compact table in chat; export JSON or CSV only when requested.

## Read and summarize accessible full text

When the user asks to read a paper in full and summarize it:

1. Click the paper title in the results tab and wait for its detail tab. Click the visible `CNKI AI阅读` control on that detail page; do not jump directly to a captured AI-reader URL.
2. Verify that the reader title matches the target paper. Treat the reader as asynchronous and lazy-loaded: poll the title and state every 2 seconds for up to 30 seconds. Do not classify access from the first screen, a short body-text snapshot, or a transient `暂无本文阅读权益` message.
3. Determine the expected document extent from a page counter, complete outline, or page shells. For paginated readers, locate the document scroll container and visit every page shell in order. Wait for each page to load text, canvas, or image content; revisit any empty page once.
4. Verify the last page or final section and confirm coverage through the conclusion and references. Do not use total character count, recommendation text, generated notes, or a sidebar prompt containing `参考文献` as evidence that the article loaded.
5. Classify the state as `verified accessible`, `still loading`, `verified unavailable`, or `reader error/incomplete`. Use `verified unavailable` only when no article pages load and the current no-rights message persists across two checks 3–5 seconds apart.
6. Before reporting no rights, close the reader tab, return to the same detail tab, click `CNKI AI阅读` again, and repeat steps 2–5 once. Require two independent `verified unavailable` attempts for the same title. Never inherit reader state from a previously opened paper.
7. Confirm that actual body sections are present, not only the title, abstract, recommendations, or generated notes. Treat unresolved or partial readers as `reader error/incomplete`, not as permissions failures.
8. Read the complete article body, including introduction, section headings, conclusion, and references. Use an accessible PDF as a cross-check when available.
9. Separate the authors' claims from critical assessment. Do not infer methods, samples, data, or conclusions that the article does not report.
10. Summarize in original language; do not reproduce the full article or extended verbatim passages.
11. Use this structure by default unless the user requests another format:
   - `全文总结`: bibliographic identity, target population or object, problem, and central proposition.
   - `研究背景`: why the problem matters and the gap identified by the authors.
   - Topic-specific analytical sections following the paper's own argument, with numbered subsections when useful.
   - `核心结论`: the paper's final claims, compressed into a small set of principles or relationships.
   - `研究贡献`: conceptual, methodological, empirical, or practical value actually supported by the paper.
   - `研究局限`: evidence quality, method, sampling, measurement, validation, scope, and causal limitations.
   - `后续研究方向`: concrete ways to test, extend, or operationalize the paper.
12. For design or interaction papers, explicitly map user characteristics, media affordances, interaction mechanisms, outcomes, and constraints when the paper supports them.
13. Do not label the output “博士” or repeatedly mention academic level. Achieve rigor through structure, evidence distinctions, and critical evaluation.
14. After finishing the paper, close its reader and detail tabs without raising Chrome, then continue from the preserved results tab.

## Generate citations

Generate citations from retrieved metadata, not from search snippets. Verify title, author order, year, journal, volume, issue, pages, and DOI when accuracy matters.

- APA: preserve author order and use the canonical DOI URL.
- BibTeX: use a stable key and escape special characters.
- GB/T 7714: include the correct document-type marker and available publication fields.

State which fields are missing rather than silently inventing them.

## Failure handling

- Empty OpenAlex results: retry with translated terms, synonyms, or fewer filters; then offer direct CNKI search.
- Missing DOI: search by exact title and author; do not fabricate a DOI.
- CNKI selector mismatch: inspect the live page and rebuild selectors from current semantics.
- Closed Playwright context: create a new Playwright MCP tab at the proxy entry, complete any browser-connection approval if prompted, then resume in the new session.
- Stale CAPTCHA signal: discard the old signal, capture a fresh screenshot, check viewport intersection, and continue when search controls are usable.
- Apparent CNKI AI no-rights state: run the delayed, page-by-page, two-attempt validation above. Report a permissions failure only after both attempts are `verified unavailable`; otherwise report `reader error/incomplete`.
- Access denied or repeated verification: stop and report the limitation.
- No abstract: record it as unavailable and avoid substituting unrelated page text.
