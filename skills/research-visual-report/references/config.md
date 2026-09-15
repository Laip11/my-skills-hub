# Configuration reference

Run:

```bash
python3 build.py report.md config.py
```

`config.py` must contain only a literal dictionary assignment:

```python
CONFIG = {
    'card_section': '4',
    'fams': {
        'a': ('#0071E3', '过程级'),
        'b': ('#AF52DE', '结果级'),
    },
    'field_style': {
        '核心问题/背景': ('f-q', '核心问题 / 背景'),
        '具体方法': ('f-m', '具体方法'),
        '实验设置和结果': ('f-r', '实验设置和结果'),
    },
    'field_groups': {
        '核心问题/背景': ('核心问题', '背景与缺口'),
        '具体方法': ('方法与训练', '系统结构', '记忆机制'),
        '实验设置和结果': ('实验设置', '主要结果', '消融与机制证据', '局限与适用边界', '决策相关的消融或局限'),
    },
    'point_group_fields': ('具体方法',),
    'group_item_limits': {'实验设置和结果': 3},
}
```

The builder parses this file without executing Python. Function calls, imports, computed values, and additional statements are rejected.

## Core settings

| Key | Default | Purpose |
|---|---|---|
| `out` | source name with `.html` | Output file path |
| `lang` | `zh-CN` | HTML document language |
| `card_section` | `3` | Identifier in the card section heading, such as `## 3. Methods` |
| `fam_heading` | `^([A-H])\.` | Family heading pattern; capture group 1 is the family key |
| `fams` | four sample families | Complete family map; supplying it replaces the defaults |
| `card_marker_fields` | core question and link fields | Fields that identify a list item as a card |
| `field_style` | styled fields | Field name to `(CSS class, displayed label)` |
| `field_groups` | none | Visible group name to source-field prefixes |
| `point_group_fields` | none | Group labels rendered as separate method/detail points |
| `group_item_limits` | none | Maximum visible source items in a grouped field |
| `steps_field` | `方法` | Legacy field whose `(1)…；(2)…` notation becomes visual steps |
| `link_fields` | arXiv and OpenReview | Fields promoted to header links and metadata |
| `figure_fields` | `('图示', 'Figure', 'Figures')` | Fields rendered as paper figures |
| `embed_local_images` | `True` | Embed local figures as data URLs in the single HTML |
| `max_image_bytes` | `12000000` | Maximum size allowed for each local figure |
| `alphaxiv` | `True` | Rewrite arXiv abstract links to alphaXiv |
| `default_date` | `('2026', '2026.99')` | Display value and sort key for undated cards |
| `nav_links` | Homepage and Research Blog | Ordered `(label, href)` pairs rendered on the right side of the fixed navigation |

Family keys must be lowercase `a` through `h`; colors must use `#RRGGBB`. Configure no more than eight families.

## Paper figures

Use exactly one Markdown image in a configured figure field:

```markdown
- 图示: ![Figure 2: Method overview](assets/papers/2401.00001/figure-002-01.png "Original caption")
```

Paths are resolved relative to `report.md` and must remain inside that directory. PNG, JPEG, GIF, WebP and passive SVG are accepted; SVG containing scripts, active embeds, or external references is rejected. With `embed_local_images=True`, the builder records the original relative path in `data-source` and embeds the bytes in the HTML; it never fetches remote images. An `https://` image URL may be rendered as a remote dependency when explicitly provided.

For research paper cards, select at most one main figure per paper and place the figure field near the card metadata in Markdown. The renderer promotes it directly below the card header, before grouped content. Prefer the method overview or the single figure that best explains the paper's central mechanism; do not display every figure collected during research.

## Canonical paper-card groups

For evidence-first literature reports, use the three-group configuration shown above:

- `核心问题 / 背景`: combine the research problem, motivation and prior-method gap;
- `具体方法`: render distinct mechanisms as separate points;
- `实验设置和结果`: show no more than three source items, prioritizing evaluation setup, headline result, and one interpretation-changing ablation or limitation.

Assign a different CSS class and color to each group, and keep the mapping stable across all cards. Additional fields may remain in the Markdown for traceability and search, but should not become additional colored top-level blocks.

The recommended compact source form uses the canonical group names directly:

```markdown
- **Paper title**
  - arXiv: https://arxiv.org/abs/2401.00001（Venue 2024）
  - 图示: ![Method overview](assets/papers/2401.00001/main.png "Original caption")
  - 核心问题/背景: One coherent problem-and-context paragraph.
  - 具体方法: (1) Mechanism one; (2) mechanism two; (3) training or inference flow.
  - 实验设置和结果: (1) Setup; (2) headline result; (3) one decision-relevant ablation or limitation.
```

`field_groups` also accepts the detailed source-field names listed in its tuples and folds them into the same three rendered blocks. This is useful when the Markdown doubles as a traceable research dossier. A card may use either the compact three-field form or the detailed form; do not duplicate both forms in the same card.

Prose below a family heading is rendered as a family introduction before its cards. Keep the source paragraph intact. The builder must not manufacture recurring sublabels or rewrite evidence into a more assertive conclusion.

## Page copy

Use `brand`, `eyebrow`, `meta_desc`, `footer`, `hero_stats`, and `nav_links` for report-specific copy. `hero_stats` accepts `{n_cards}` and `{n_fams}` placeholders. Prefer root-relative navigation destinations for reports published beneath a website:

```python
'nav_links': [('Homepage', '/'), ('Research Blog', '/blog/')],
```

The visible structure is defined by `assets/report-template.html`; `assets/page-shell.html` contains the build slots. Do not put report-specific prose into either template.

Toolbar text is configured with `search_placeholder`, `sort_button`, `sort_button_alt`, `collapse_button`, `expand_button`, `count_tpl`, and `toc_title`. `count_tpl` accepts `{visible}` and `{total}`.

## Optional spectrum

Set `spectrum` to `None` to disable it, or provide:

```python
'spectrum': {
    'detect': 'token',
    'detect_lines': ('token', '细', '方差'),
    'nodes': ['token', 'step', 'turn', 'trajectory'],
    'bar': ('细粒度', '粗粒度'),
    'labels': ('高定位能力', '低标注成本'),
}
```

A code block beginning with `detect` is replaced by the graphical spectrum. `detect_lines` tells the coverage audit how to compare the source diagram with its visual representation.

## Optional timeline

Set `timeline` to `None` to disable it, or provide:

```python
'timeline': {
    'cols': ['24Q1', '24Q2', '24Q3', '24Q4', '25Q1'],
    'year_base': 24,
    'extra_rows': [{
        'key': 'eval',
        'color': '#8E8E93',
        'label': '评测',
        'items': [(2, 'Benchmark', 'Full benchmark title')],
    }],
    'note': 'Timeline note',
}
```

Paper dates are inferred from arXiv identifiers. Undated papers remain in cards but are omitted from the automatic timeline.

## Build guarantees

A successful build uses an atomic replace: the previous output remains untouched when validation fails. Failure conditions include missing source fragments, mixed card/plain-list structures inside a family, invalid configuration, a missing timeline, or non-ascending card dates.

The coverage audit verifies normalized source fragments in the output and reports `missing: 0`. It is a strong regression check, not a formal proof that every semantic relationship is preserved. Browser review remains required.

The output embeds report CSS and interaction JS. KaTeX is loaded from jsDelivr when available; raw mathematical source remains readable offline.
