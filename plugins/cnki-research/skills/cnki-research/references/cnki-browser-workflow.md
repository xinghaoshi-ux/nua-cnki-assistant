# CNKI Playwright Chrome workflow

Use this workflow with the plugin-managed Google Chrome session controlled through Playwright MCP. On Codex, the persistent `node_repl js` Playwright connection is an allowed fallback when MCP browser tools are unavailable.

## 1. Start and reuse Chrome

- Prefer the plugin-provided `cnki-playwright` MCP browser tools and list current tabs before navigating.
- Keep one dedicated Chrome profile, browser context, and search tab for the full task.
- On macOS the launcher uses background activation. On Windows it starts Chrome minimized. Never raise the window programmatically on any platform.
- When Codex MCP tools are unavailable, import `playwright` through `node_repl js` and connect to the launcher endpoint with `chromium.connectOverCDP`.
- Allow multiple CNKI tabs. Preserve the results tab, use separate detail and AI-reading tabs, and close worker tabs after each paper.
- Never call `bringToFront` or use operating-system activation for automated interactions.
- Open the Nanjing University of the Arts proxy entry and request manual login when required.
- Keep the current turn active and inspect the current page every 5–10 seconds for up to 4 minutes. Continue automatically when `南京艺术学院` appears; do not wait for a confirmation message from the user. If the polling window expires, leave Chrome open and ask the user to confirm when ready.
- Enter advanced search through the live `高级检索` link.

## 2. Choose the search surface

- Use `高级检索` rows for natural-language topics, synonyms, dates, sources, and document types.
- Use `专业检索` only for a user-provided expression or when field-code precision is necessary.
- Inspect current page state after every navigation or UI change. Never reuse old element IDs or coordinates.

## 3. Build the query

Split the request into concept groups:

- Put synonyms and near-synonyms in one theme box, separated by ` + `.
- Put distinct required concepts in separate theme rows joined with `AND`.
- Use `OR` between concept rows only for exploratory or high-recall work.
- Keep each box below the live interface limit.

Example:

```text
儿童数字绘本 + 数字绘本 + 电子绘本 + 交互绘本
AND
认知发展 + 认知理论
AND
游戏体验 + 交互设计 + 互动设计
```

If this strict query returns too few results, broaden in this order:

1. Combine the second and third groups with `OR`.
2. Remove the narrowest synonym group.
3. Search adjacent terms such as `绘本阅读`, `数字阅读`, or `教育游戏`, then rank manually.

## 4. Interact robustly

1. Prefer Playwright roles, labels, visible text, and validated DOM attributes.
2. Use a viewport screenshot when visual state or CAPTCHA geometry matters.
3. Wait for a concrete URL, result count, or content signal after actions.
4. When a row is added, re-inspect it before changing its field or Boolean operator.
5. Treat hidden CAPTCHA text as stale markup. Report verification only when a visible challenge blocks interaction.

## 5. Filter and sort

- Do not force journal type, CSSCI, core journal, date, or language filters unless the request calls for them.
- For relevance: keep CNKI relevance order, then rerank the requested candidate set using title, keywords, and abstract.
- For influence: sort cited count descending and verify the direction.
- For recency: sort publication date descending.
- Switch to 50 results per page when available.
- Switch to summary/detail view when it exposes abstracts.

## 6. Extract

Capture when visible:

- title
- authors
- source
- publication date
- document type
- abstract
- keywords
- DOI
- CNKI detail URL
- CNKI cited/download counts

For a top-N abstract request:

1. Collect a candidate pool larger than N when possible.
2. Remove duplicates.
3. Score direct concept coverage before citations.
4. Keep the top N.
5. Open detail pages only for missing abstracts.
6. Mark unavailable abstracts explicitly.

## 7. Read full text

For every paper:

1. Click its title in the result list.
2. Wait for the proxied CNKI detail page.
3. Click the visible `CNKI AI阅读` button on that detail page.
4. Select the newly opened reader tab through Playwright without activating Chrome.
5. Poll the matching title and reader state every 2 seconds for up to 30 seconds. Treat the first screen, a short text snapshot, and an early `暂无本文阅读权益` message as provisional.
6. Determine the expected extent from the page counter, outline, or page shells. If the reader uses lazy-loaded pages, locate its document scroll container, visit every page shell, wait for text/canvas/image content, and revisit empty pages once.
7. Verify the final page or final section and confirm coverage through the conclusion and references. Sidebar prompts, recommendation text, total body character count, and the mere presence of the word `参考文献` are not proof of a loaded article.
8. Mark the paper `verified accessible` only when the matching article's complete expected extent loads. Mark it `verified unavailable` only when zero article pages load and the current no-rights message persists across two checks 3–5 seconds apart.
9. Before reporting no rights, close the reader tab, return to the same detail tab, click `CNKI AI阅读` again, and repeat the complete validation once. Require two independent `verified unavailable` attempts for the same title. Treat other failures as `reader error/incomplete`, not permissions failures.
10. Read all body sections. Only after this UI and page-validation sequence, extract text from the document data loaded by the reader when needed for complete coverage.
11. Close the reader and detail tabs after full-text extraction or an access failure, then continue from the preserved results tab.
12. Return to the results list and repeat.

Never jump directly from a result-row AI URL to the reader. Never treat an abstract, AI-generated note, or incomplete preview as full text.

## 8. Download papers

For every paper:

1. Click its title in the result list.
2. Wait for the proxied CNKI detail page.
3. Click `PDF下载` on the detail page by default.
4. Click `CAJ下载` only when the user explicitly asks for CAJ.
5. Never use a result-row download URL or construct a direct download endpoint.
6. Capture the Playwright download event and verify the completed file is non-empty and has the requested type.
7. Close the detail tab, return to the preserved results tab, and repeat.

## 9. Export

When the user requests an export:

1. Select only the requested records.
2. Prefer CNKI `导出与分析` when available.
3. Use `查新（引文格式）` when complete records and abstracts are needed.
4. Verify that the downloaded file exists and is non-empty.
5. If CNKI export is unavailable, extract visible records and create CSV or JSON locally.

Do not download subscription full text without legitimate access and an explicit user request.
