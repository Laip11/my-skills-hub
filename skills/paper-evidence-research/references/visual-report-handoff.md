# Visual-report handoff

Read this reference when the research will be rendered with `research-visual-report`.

## Required public outline

Use these section roles in `report.md` unless the research question requires a documented variation:

1. 范围、问题与纳入标准
2. 术语与统一视角
3. 方法演化与研究图谱
4. 核心论文（按方法族分组）
5. 覆盖结果与语料结构
6. 跨论文综合判断
7. 方法选择与实现建议
8. 开放问题
9. 证据边界
10. 主要来源

The page template supplies the navigation and section chrome. Do not put crawler logs, candidate counts, parser messages or local filesystem paths into this public narrative.

## Required config.py

Write a literal `CONFIG = {...}` file that can be passed directly to the visual builder. It must include the actual card section number, complete family map and canonical field groups:

```python
CONFIG = {
    'card_section': '4',
    'brand': '主题名称',
    'eyebrow': '研究领域 · 时间范围',
    'meta_desc': '一句话描述报告范围',
    'footer': 'Research report',
    'nav_links': [('Homepage', '/'), ('Research Blog', '/blog/')],
    'fams': {'a': ('#0071E3', '方法族 A')},
    'field_style': {
        '核心问题/背景': ('f-q', '核心问题 / 背景'),
        '具体方法': ('f-m', '具体方法'),
        '实验设置和结果': ('f-r', '实验设置和结果'),
    },
    'field_groups': {
        '核心问题/背景': ('核心问题', '背景与缺口'),
        '具体方法': ('方法与训练', '系统结构'),
        '实验设置和结果': ('实验设置', '主要结果', '决策相关的消融或局限'),
    },
    'point_group_fields': ('具体方法',),
    'group_item_limits': {'实验设置和结果': 3},
}
```

## Paper metadata contract

Each visible card must have one canonical first-publication date. Put a confirmed venue in the parenthetical note after the arXiv or OpenReview link; the renderer promotes it to a separate venue badge. Keep method aliases or organizations in the title note only when useful. Do not write `Direct`, `Extended`, `arXiv`, or update-history text as title decorations.

Recommended card:

```markdown
- **Paper title**（Method alias or organization, only if useful）
  - arXiv: https://arxiv.org/abs/2401.00001（Conference 2025）
  - 图示: ![Method overview](assets/papers/2401.00001/figure-002-01.png "Original caption")
  - 核心问题/背景: Problem, motivation and prior gap.
  - 具体方法: (1) Mechanism and its purpose; (2) training or inference procedure.
  - 实验设置和结果: (1) Models, tasks, baselines and metric; (2) verified headline result with units; (3) decision-relevant ablation, failure case or limitation.
```

The card needs enough detail to understand the paper without opening the abstract, but secondary locators, conflicting values and long result tables belong in `evidence-ledger.md`. Use inline `(1)…; (2)…` points inside each named card field. Do not place nested Markdown ordered lists below a card field: the current visual builder treats those lines as separate list nodes and its content audit will reject the build.

## Figure decision

Attempt one main-figure decision per direct or extended paper. Select the unchanged method overview, pipeline, central result or failure-mode figure when it is available and rights are recorded. If no figure is usable, omit `图示` and record `unavailable`, `unsuitable` or `rights-restricted` with a reason in the candidate ledger. Never add a decorative or generic placeholder to `report.md`.

## Handoff check

Before handing off, run:

```bash
python3 .build/build.py report.md config.py
```

The downstream builder must report `missing: 0` and `date order ok: True`. The research Skill remains responsible for evidence quality; the visual Skill remains responsible for layout and interaction.
