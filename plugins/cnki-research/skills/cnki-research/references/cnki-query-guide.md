# CNKI professional-query guide

Use codes only when the live CNKI professional-search interface accepts them. Confirm syntax on the current page.

| Field | Common code | Example |
|---|---|---|
| Subject | `SU` | `SU='生成式人工智能'` |
| Title | `TI` | `TI='大语言模型'` |
| Author | `AU` | `AU='张三'` |
| Institution | `AF` | `AF='复旦大学'` |
| Keyword | `KY` | `KY='教育数字化'` |
| Full text | `FT` | `FT='知识图谱'` |
| Source | `LY` | `LY='中国电化教育'` |
| Fund | `FU` | `FU='国家自然科学基金'` |
| Classification | `CLC` | `CLC=G434` |

Combine clauses with `AND`, `OR`, and parentheses:

```text
SU='生成式人工智能' AND (SU='教育' OR KY='教学')
AU='张三' AND SU='知识图谱'
AF='北京大学' AND TI='大语言模型'
```

When the live advanced-search form accepts term expressions instead of field codes, use the interface syntax shown on that page. CNKI commonly requires spaces around `*`, `+`, and `-`:

```text
认知负荷 * 儿童数字绘本 * 游戏化交互设计
(儿童数字绘本 + 数字绘本) * (游戏化 + 交互设计) * 认知负荷
```

For a narrow interdisciplinary topic, run searches in this order:

1. Exact intersection of all concepts.
2. Synonym-expanded intersection.
3. Pairwise searches when the exact intersection is empty or too small.
4. Record each expression and label pairwise results as adjacent literature rather than exact matches.

Prefer interface filters for date ranges and document types because filter syntax can change. Confirm whether the user means publication date, online-first date, or database update date.

Do not rely on copied element references such as `e124`; they are session-specific.
