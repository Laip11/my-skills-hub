---
name: research-visual-report
description: Build a polished interactive HTML research report from structured Markdown, with professional paper cards, selected main figures, method-family synthesis, search, filters, navigation, responsive layout, and delivery-blocking content checks. Use for literature reviews, research surveys, or comparison reports that need a professional web deliverable; do not use for conducting the underlying research unless the user also asks for it.
---

# Research Visual Report

Turn structured Markdown into a polished research-reading experience modeled on high-end editorial product pages. Preserve the source document as the single source of truth; treat generated HTML as a build artifact. The visual hierarchy should clarify the research argument without introducing new claims or replacing analytical prose with interface copy.

In command examples, resolve `<skill>` to the directory containing this `SKILL.md`; never pass the placeholder literally. This convention is portable across Codex, Claude Code and Cursor.

## Workflow

1. Inspect the source structure and identify the section that contains paper cards.
2. Copy the builder and assets into the project:

   ```bash
   mkdir -p .build
   cp <skill>/scripts/build.py <skill>/assets/{style.css,app.js} .build/
   ```

3. Create a literal `config.py` containing only `CONFIG = {...}`. Read [references/config.md](references/config.md) for configuration details.
4. Build the report:

   ```bash
   python3 .build/build.py report.md .build/config.py
   ```

5. Accept the build only when it exits with status `0`, prints `missing: 0`, and prints `date order ok: True`.
6. Serve the output locally and verify desktop and mobile rendering, search, family filters, sort, card folding, keyboard focus, theme switching, TOC scroll-spy, and print layout.

When modifying the Skill itself, run `python3 <skill>/scripts/self_test.py` before delivery.

## Source conventions

The builder recognizes:

- `#` as the hero title and the first pre-section blockquote as the hero introduction.
- `## N. Title` as page sections. Set `card_section` to the paper-card section identifier.
- `### A. Family` through `### H. Family` as method families inside the card section.
- A top-level list item with a bold title and named child fields as a paper card.
- Markdown tables, quotes, code blocks, paragraphs, nested lists, inline emphasis, code, and HTTP(S) links.

### Rendered card contract

Use this compact form when the Markdown is already written for the final report. These are the only three colored content blocks that should appear in each rendered paper card:

```markdown
- **Paper title**（optional note）
  - arXiv: https://arxiv.org/abs/2401.00001（Venue 2024）
  - 图示: ![Figure 2: Method overview](assets/papers/2401.00001/figure-002-01.png "原始图注")
  - 核心问题/背景: 用一个连贯段落说明研究问题、背景以及既有方法的关键缺口。
  - 具体方法: (1) 核心机制及其作用；(2) 与相关方法的关键差异；(3) 训练或推理流程。
  - 实验设置和结果: (1) 模型、任务、基线与指标；(2) 可核验的核心结果；(3) 最影响结论解读的消融、失败案例或局限。
```

The figure is separate from the three content blocks. The title, source link, venue, date, and optional note are metadata rather than colored content blocks.

### Detailed research-dossier fields

When the research Markdown needs finer-grained evidence for traceability, it may retain detailed source fields instead:

```markdown
- **Paper title**（optional note）
  - arXiv: https://arxiv.org/abs/2401.00001（Venue 2024）
  - 图示: ![Figure 2: Method overview](assets/papers/2401.00001/figure-002-01.png "原始图注")
  - 核心问题: ...
  - 背景与缺口: ...
  - 方法与训练: ...
  - 实验设置: ...
  - 主要结果: ...
  - 决策相关的消融或局限: ...
```

This is a source schema, not the visible card schema. Configure `field_groups` to map these detailed fields into exactly three rendered blocks: `核心问题 / 背景`, `具体方法`, and `实验设置和结果`. A card may use either the compact three-field form or the detailed form; do not duplicate both forms in the same card.

Give each rendered block a distinct color and keep those colors consistent across every paper. Render method components as separate points. Limit the visible experiment block to at most three points—normally the setup, headline comparison, and one decision-relevant ablation, failure case, or limitation—while allowing secondary evidence to remain searchable in the source dossier.

If a paper has a selected main figure, render exactly one figure immediately below the title and source metadata, before the three content blocks. Do not create a gallery unless the user explicitly requests one.

Treat prose immediately below a family heading as the family's analytical summary. Preserve it as continuous prose before the cards; do not replace it with a generated definition, a paper-name list, or fixed labels such as `这一类在做什么 / 方法演进 / 调研判断`.

For figure fields, use one Markdown image per field. Local PNG, JPEG, GIF, WebP, or passive SVG files are resolved relative to the report Markdown and embedded as data URLs by default, so the output remains a portable single HTML file. Keep the original caption and do not use a figure unless its source and reuse status were recorded during research.

Within a family list, do not mix card-shaped items with ordinary list items. The builder treats that as a structural error and refuses to overwrite the output.

## Invariants

- Edit content in Markdown and presentation in `style.css` or `app.js`; rebuild after every change.
- Do not silently rewrite, summarize, or fact-check research content. If the user requests content verification, perform that as a separate, explicitly scoped task before building.
- Preserve claim strength, qualification, terminology and numerical units from the Markdown. Interface labels may group fields, but must not strengthen conclusions or synthesize new prose.
- Keep family cards date-ascending in Markdown. Readers can switch to newest-first in the report.
- Treat `config.py` and Markdown as data. The builder does not execute the config and escapes generated HTML attributes and text.
- A failed build must return a nonzero exit status and leave the previous successful HTML untouched.
- The report is one HTML document, but KaTeX enhancement uses an optional CDN; mathematical source remains readable when the CDN is unavailable.
- Local figure paths must remain inside the report directory. Missing files, unsupported formats, path traversal, or images above the configured size limit fail the build before the previous output is replaced.

## Visual quality bar

Preserve the reference design language: restrained Apple-like typography, spacious hierarchy, translucent sticky controls, family-color accents, compact metadata badges, and responsive cards. The reading order within each card is title and metadata → main figure → `核心问题 / 背景` → `具体方法` → `实验设置和结果`. Improve the design through accessible keyboard controls, visible focus states, dark mode, reduced-motion support, mobile wrapping, and print-safe expansion.

Do not claim success from the structural Skill validator alone. Run the builder on a representative sample and inspect the rendered page in a browser.
