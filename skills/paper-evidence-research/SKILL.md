---
name: paper-evidence-research
description: Conduct evidence-first literature research from full paper text and other primary sources, extract traceable claims and selected figures, and produce a polished, visual-report-ready research dossier. Use when the user wants a literature survey, paper comparison, method taxonomy, or research report with paper figures; do not use merely to restyle an existing completed report.
---

# Paper Evidence Research

Build the research layer that feeds a visual report. Deliver a structured Markdown dossier, an evidence ledger, and a curated local figure collection. Base substantive analysis on the paper body rather than the abstract alone. Keep factual extraction separate from interpretation and preserve a trace from every important claim to a paper version and location.

In command examples, resolve `<skill>` to the directory containing this `SKILL.md`; never pass the placeholder literally. This convention is portable across Codex, Claude Code and Cursor.

## Source hierarchy

1. Use the latest official paper version as the default factual source: arXiv HTML when available, otherwise the official PDF.
2. Use the arXiv API for canonical metadata, authors, abstract, publication date, update date, DOI, and journal reference.
3. alphaXiv may accelerate discovery and provide an AI-generated intermediate analysis. Treat that analysis as a lead, not as evidence; verify every substantive or numerical claim against the paper text.
4. Use publisher pages, OpenReview, official code repositories, datasets, and appendices when a claim depends on them.
5. Do not use search-result snippets, blogs, or generated summaries as the sole support for a research conclusion.

Read [references/source-and-rights.md](references/source-and-rights.md) before collecting full text or figures.

## Research workflow

### 1. Freeze the question

Record the research question, time window, domain, inclusion and exclusion rules, comparison axes, and desired depth. Do not silently broaden the scope.

### 2. Build a candidate set

Search with multiple concept framings: exact method names, synonyms, problem terminology, benchmarks, foundational citations, and recent follow-up work. Keep a candidate ledger with inclusion status and reason.

For repeated arXiv API requests, cache results and wait at least three seconds between calls. Prefer smaller result pages and refined queries.

### 3. Read papers into an evidence matrix

For each included paper, record:

- canonical title, authors, arXiv ID and resolved version;
- research question and claimed contribution;
- method components and assumptions;
- datasets, environments, baselines and metrics;
- quantitative results with a section, table, figure, or page locator;
- limitations stated by the authors and limitations inferred by the researcher, labeled separately;
- relationships to prior and follow-up work;
- candidate figures and why each helps answer the research question.

Use the abstract for screening and orientation, not as the primary analytical source. Read the relevant method, experiment, ablation, limitation and appendix sections before drafting a paper card. Batch questions about one paper rather than repeatedly reading it for one field at a time.

### 4. Harvest figures selectively

Use the bundled helper to inspect official arXiv HTML without downloading images:

```bash
python3 <skill>/scripts/harvest_arxiv.py 2401.00001 --out evidence/2401.00001
```

Review `manifest.json` and `evidence.md`, then download only the useful figures:

```bash
python3 <skill>/scripts/harvest_arxiv.py 2401.00001 \
  --out evidence/2401.00001 --figures 1,3
```

The second call reuses the first call's manifest, avoiding another arXiv metadata request. Use `--refresh` only when a fresh version check is necessary. Across different papers or forced refreshes, cache results and keep repeated arXiv API calls at least three seconds apart.

Choose the single figure that best explains the paper's architecture, method pipeline, central result, or failure mode. Keep at most one displayed main figure per paper unless the user explicitly requests a gallery. Downstream visual reports should place that main figure immediately below the paper title and source metadata, before the detailed analysis. Preserve the original image, figure number, caption, source URL, paper version, retrieval date and detected license URL. Do not crop away legends or alter the scientific meaning.

If arXiv HTML is unavailable or conversion quality is poor, download the official PDF and use a PDF extraction workflow. Verify extracted figures visually against the PDF page before including them.

### 5. Synthesize across papers

Organize by research question or method family rather than writing one isolated summary after another. Compare papers in the same sentence or table when they differ on assumptions, mechanism, granularity, supervision, data, compute, evaluation, or limitations.

Label uncertainty explicitly:

- `paper-stated`: directly stated by the authors;
- `derived`: calculated from reported values;
- `researcher interpretation`: synthesis or critique;
- `alphaXiv lead`: useful lead not yet verified against the paper.

Do not invent missing results. If a paper does not report a value, write that it was not reported.

After each method-family heading, add one compact analytical paragraph that:

- identifies the shared objective and mechanism of the family;
- distinguishes the included methods on the comparison axes that matter;
- states what the available evidence supports and where it remains incomplete.

Write this as continuous prose, not as a fixed `这一类在做什么 / 方法演进 / 调研判断` template. Do not repeat the paper cards or reduce the summary to a list of paper names.

### 6. Deliver report-ready artifacts

Use [references/output-schema.md](references/output-schema.md). When drafting user-facing Chinese prose, also read [references/writing-and-synthesis.md](references/writing-and-synthesis.md). Produce:

- `report.md`: synthesized research narrative and paper cards;
- `evidence-ledger.md` or `.csv`: claim-to-source traceability;
- `assets/papers/<arxiv-id>/`: selected original figures;
- `assets/papers/<arxiv-id>/manifest.json`: source, caption, hashes and license status;
- an unresolved-items list for inaccessible papers, uncertain values, conflicting versions, or rights questions.

For visual-report paper cards, expose exactly three colored top-level content tags: `核心问题 / 背景`, `具体方法`, and `实验设置和结果`. Present method components as separate points. Keep `实验设置和结果` concise: normally show no more than three items covering the setup, headline result, and the single most decision-relevant ablation or limitation. The visible card should be detailed enough to understand the paper without consulting its abstract, while secondary costs, conflicts, locators and supporting results remain in the dossier or evidence ledger rather than accumulating in the card.

When `research-visual-report` is available, hand `report.md` and its relative `assets/` tree to that Skill for presentation. Research facts stay in the Markdown; the visual builder must not rewrite them.

## Quality gates

- Every included paper has a stable identifier and version/update date.
- Every numerical or comparative claim has a locator to the original paper or official artifact.
- Every displayed figure is the paper's one selected main figure and has a local file, original caption, source URL and rights status.
- alphaXiv-generated prose is paraphrased and independently verified before it becomes a report claim.
- The synthesis answers the frozen research question and distinguishes evidence from interpretation.
- Each method family has a short comparative synthesis rather than a generic definition or a paper-by-paper recap.
- User-facing prose uses consistent terminology, calibrated evidence verbs and direct academic sentences; it avoids marketing language, mechanical triads and repetitive stock transitions.
- No internal paths, scraping logs, API keys, or process notes appear in the public report.

When modifying this Skill, run `python3 <skill>/scripts/self_test.py` and the standard Skill validator.
