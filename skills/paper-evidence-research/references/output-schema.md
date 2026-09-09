# Report-ready output schema

## Directory layout

```text
research-project/
├── report.md
├── evidence-ledger.md
├── unresolved.md
└── assets/
    └── papers/
        └── 2401.00001/
            ├── manifest.json
            ├── figure-001-01.png
            └── figure-003-01.svg
```

Use stable arXiv IDs without filesystem-hostile characters for directory names. Keep paths in `report.md` relative to the report.

## Paper card

```markdown
- **Paper title**（Venue or status）
  - arXiv: https://arxiv.org/abs/2401.00001（Venue 2024）
  - 图示: ![Figure 4: short accessible description](assets/papers/2401.00001/figure-004-01.png) — Original caption or a faithful shortened caption. Source: arXiv 2401.00001v2, Figure 4; license: CC BY 4.0.
  - 核心问题 / 背景: State the specific problem, deployment or scientific motivation, and the prior-method gap in one coherent block.
  - 具体方法:
    1. First mechanism and its role.
    2. Second mechanism and how it differs from the baseline.
    3. Training or inference procedure needed to understand the contribution.
  - 实验设置和结果:
    1. Evaluation setting: model, task/environment, baselines and principal metric.
    2. Headline verified result with the exact comparison and unit.
    3. One decision-relevant ablation, failure case or limitation.
```

Visual paper cards use only these three colored top-level content tags. Assign a distinct, consistent color to each tag across the report. Do not create separate top-level tags for innovation, ablation, limitations, evidence location, or rights. Select rather than accumulate: show at most three `实验设置和结果` subpoints, while retaining omitted evidence in the Markdown dossier and ledger. Merge method details only when they describe the same mechanism; otherwise keep them as separate points. The figure is separate from these tags and appears directly below the card title and source metadata.

Use `图示` only for a downloaded and visually verified main image. Keep at most one displayed figure per paper unless the user explicitly requests a gallery. The downstream renderer should lift this figure immediately below the paper title and source metadata, before the text fields.

## Evidence ledger

```markdown
| Claim ID | Report claim | Paper/version | Locator | Evidence type | Verification | Notes |
|---|---|---|---|---|---|---|
| C-001 | Method X improves metric Y by 4.2 points over baseline Z. | 2401.00001v2 | Table 2, row X | paper-stated | verified | Absolute points, not percent |
```

Use one row per meaningful numerical or comparative claim. `Evidence type` is one of `paper-stated`, `derived`, `researcher interpretation`, or `alphaXiv lead`. Only the first three may appear as completed report claims, and derived values must include the calculation in `Notes`.

## Figure manifest

Each paper's `manifest.json` should retain the helper's source inventory and add selection decisions:

```json
{
  "selection": {
    "figure-004-01.png": {
      "include": true,
      "reason": "Explains the method pipeline used in the taxonomy",
      "rights_status": "allowed-with-attribution",
      "transformation": "unchanged"
    }
  }
}
```

Do not mark rights as allowed solely because a file was downloadable.

## Synthesis sections

A report intended for the visual-report Skill should normally contain:

1. scope and research question;
2. terminology and comparison axes;
3. method taxonomy or evolution;
4. paper cards grouped by family;
5. cross-paper comparison;
6. selection guidance;
7. limitations, open problems and unresolved evidence;
8. references and source acknowledgements.

Adapt the section count and names to the research question; the structure is guidance, not a mandatory template.

## Method-family summary

Place one short paragraph immediately below each method-family heading and before its paper cards. A useful paragraph usually contains three analytical moves without exposing them as fixed labels:

1. define the family's shared technical objective and where the capability resides at deployment;
2. compare the included methods by training signal, memory representation, routing or lifecycle mechanism;
3. delimit the conclusion using the available experiments and unresolved evidence.

The paragraph should synthesize the family. Do not reproduce each card's abstract, enumerate every paper in order, or use the recurring headings `这一类在做什么`, `方法演进`, and `调研判断`.
