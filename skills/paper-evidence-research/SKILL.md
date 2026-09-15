---
name: paper-evidence-research
description: Conduct comprehensive, evidence-first literature research over a specified field using full paper text and primary sources, with auditable search coverage, traceable claims, and selected figures. Use when the user wants a literature survey, related-work review, paper comparison, method taxonomy, or research report that must cover the complete in-scope literature; do not use for a representative reading list or merely to restyle an existing completed report.
---

# Paper Evidence Research

Build a comprehensive research layer for a specified field. Deliver a report-ready Markdown dossier and visual-report configuration alongside an evidence ledger, complete candidate and search records, a coverage audit, and a curated local figure collection. Base substantive analysis on the paper body rather than the abstract alone. Keep factual extraction separate from interpretation and preserve a trace from every important claim to a paper version and location.

## Coverage contract

This Skill has one operating mode: comprehensive systematic coverage. Always read and follow [references/comprehensive-review.md](references/comprehensive-review.md).

- Treat the user's specified field, conceptual definition, time cutoff, and publication policy as the coverage boundary.
- Search for every discoverable work inside that boundary. Do not select a representative subset or impose a paper-count cap.
- Do not discard work because it is less influential, creates too many cards, complicates the visual report, lacks code, reports negative results, or does not fit a preliminary taxonomy.
- If the request asks only for representative papers, key papers, or a short reading list, explain that this Skill is designed for comprehensive coverage and confirm the narrower output before using a different workflow. Do not silently downgrade this Skill.

Completeness means systematically searched and reconciled under the recorded protocol as of a stated cutoff date. Because open literature changes and databases have blind spots, never claim mathematically universal completeness; report unresolved access, indexing, language, and date limitations explicitly.

In command examples, resolve `<skill>` to the directory containing this `SKILL.md`; never pass the placeholder literally. This convention is portable across Codex, Claude Code and Cursor.

## Source hierarchy

1. Use the latest official paper version as the default factual source. For an arXiv paper, fetch and parse official arXiv HTML first for the paper body, section structure, tables, figure inventory and captions. Fall back to the official PDF only when HTML is unavailable, materially incomplete, conversion-corrupted, or insufficient for a claim that depends on equations, tables, appendices or layout.
2. Use the arXiv API for canonical metadata, authors, abstract, publication date, update date, DOI, and journal reference.
3. alphaXiv may accelerate discovery and provide an AI-generated intermediate analysis. Treat that analysis as a lead, not as evidence; verify every substantive or numerical claim against the paper text.
4. Use publisher pages, OpenReview, official code repositories, datasets, and appendices when a claim depends on them.
5. Do not use search-result snippets, blogs, or generated summaries as the sole support for a research conclusion.

Read [references/source-and-rights.md](references/source-and-rights.md) before collecting full text or figures.

## Research workflow

### 1. Freeze the question

Record the research question, operational definition of the specified field, time window, publication types, inclusion and exclusion rules, comparison axes, and desired depth. Do not silently broaden or narrow the scope. Exclusions must describe conceptual boundaries rather than convenience, prestige, venue, available space, or expected importance.

### 2. Build a candidate set

Search with multiple concept framings: exact method names, synonyms, problem terminology, benchmarks, foundational citations, and recent follow-up work. Keep a candidate ledger with inclusion status and reason.

Complete candidate discovery before drafting the taxonomy or paper cards. Do not let a preliminary taxonomy decide which papers are searched for or retained. Use discovery sources as a union, not as substitutes for one another:

- bibliographic/database searches using exact phrases, synonyms, acronyms, and mechanism-level terms;
- backward references and forward citations from seed papers and surveys;
- author, lab, benchmark, venue, and official-repository searches where relevant;
- stable preprints, peer-reviewed papers, workshop papers, and technical reports allowed by the frozen scope.

Canonicalize identifiers and deduplicate versions before screening. Keep every discovered candidate in the ledger, including excluded, inaccessible, withdrawn, superseded, and duplicate records. Do not begin full synthesis until the saturation and reconciliation checks in [references/comprehensive-review.md](references/comprehensive-review.md) pass.

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

For arXiv papers, begin the full-text pass from the resolved-version HTML endpoint rather than the abstract page. Treat HTML as a structured extraction surface, not as a guarantee of fidelity: compare suspicious equations, tables, missing sections or malformed captions against the official PDF before recording the claim.

Every direct paper receives a completed evidence-matrix row and a detailed report card covering its problem, concrete mechanism, training or inference procedure, evaluation setting, verified findings, and limitations. Extended papers may use a more compact card, but each must still state why it belongs, what technical role the topic plays, and what evidence was verified. Do not use title-only lists as a substitute for analysis. If full text is unavailable, mark the paper unresolved instead of converting abstract-only screening into a completed evidence card.

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

Use Figure 1 and Figure 2 as the default first-pass main-figure candidates because papers commonly place the overview or central result there. Inspect both when available, then select the single figure that best explains the paper's architecture, method pipeline, central result, or failure mode. This is a ranking prior, not a hard rule: skip an early teaser, decorative montage, qualitative example or unreadable composite when a later figure is more informative for the research question. Keep at most one displayed main figure per paper unless the user explicitly requests a gallery. Downstream visual reports should place that main figure immediately below the paper title and source metadata, before the detailed analysis. Preserve the original image, figure number, caption, source URL, paper version, retrieval date and detected license URL. Do not crop away legends or alter the scientific meaning.

If arXiv HTML is unavailable or conversion quality is poor, download the official PDF and use a PDF extraction workflow. Verify extracted figures visually against the PDF page before including them.

### 5. Synthesize across papers

Organize by research question or method family rather than writing one isolated summary after another. Compare papers in the same sentence or table when they differ on assumptions, mechanism, granularity, supervision, data, compute, evaluation, or limitations.

Label uncertainty explicitly:

- `paper-stated`: directly stated by the authors;
- `derived`: calculated from reported values;
- `researcher interpretation`: synthesis or critique;
- `alphaXiv lead`: useful lead not yet verified against the paper.

Do not invent missing results. If a paper does not report a value, write that it was not reported.

After each method-family heading, add a substantive synthesis of two to four focused paragraphs that:

- identifies the shared objective and mechanism of the family;
- distinguishes the included methods on the comparison axes that matter;
- states what the available evidence supports and where it remains incomplete.

Write this as continuous prose, not as a fixed `这一类在做什么 / 方法演进 / 调研判断` template. The synthesis must explain the shared objective, internal technical progression, conflicting evidence and practical boundary without opening individual cards. Do not repeat the paper cards or reduce the summary to a list of paper names.

### 6. Deliver report-ready artifacts

Use [references/output-schema.md](references/output-schema.md). When the result will be rendered with `research-visual-report`, also read [references/visual-report-handoff.md](references/visual-report-handoff.md). When drafting user-facing Chinese prose, read [references/writing-and-synthesis.md](references/writing-and-synthesis.md). Produce:

- `report.md`: synthesized research narrative and paper cards;
- `config.py`: literal visual-report configuration aligned with the method families, page copy, navigation and canonical three-field card schema;
- `evidence-ledger.md` or `.csv`: claim-to-source traceability;
- `assets/papers/<arxiv-id>/`: selected original figures;
- `assets/papers/<arxiv-id>/manifest.json`: source, caption, hashes and license status;
- an unresolved-items list for inaccessible papers, uncertain values, conflicting versions, or rights questions.

Also produce these mandatory coverage artifacts:

- search-log.md: exact queries, sources, dates, result counts, citation-chaining passes, and saturation evidence;
- candidate-ledger.csv or .md: one row for every discovered record, with canonical ID, deduplication status, relevance tier, inclusion decision, and reason;
- coverage-audit.md: retrieved/deduplicated/included/excluded/unresolved counts, reconciliation against seed surveys, and known blind spots.

When handing the result to `research-visual-report`, use the fixed template contract in [references/visual-report-handoff.md](references/visual-report-handoff.md). The public report follows the template's ten-section outline and the separate `config.py` carries page-specific labels, colors and navigation. Do not rebuild a different page structure in the research output.

For visual-report paper cards, expose exactly three colored top-level content tags: `核心问题 / 背景`, `具体方法`, and `实验设置和结果`. Present method components as separate points. Keep `实验设置和结果` concise: normally show no more than three items covering the setup, headline result, and the single most decision-relevant ablation or limitation. The visible card should be detailed enough to understand the paper without consulting its abstract, while secondary costs, conflicts, locators and supporting results remain in the dossier or evidence ledger rather than accumulating in the card.

Attempt to identify a useful main figure for every direct and extended paper. Display at most one visually verified figure per paper. When no suitable or reusable figure is available, omit the `图示` field and record the reason in the candidate ledger; never insert a generic placeholder into the finished report.

Keep public narrative separate from research operations. `report.md` may analyze corpus composition, but it must not expose crawler status, parsing counts, internal relevance labels, unresolved-file totals, local paths, or procedural messages. Put exact retrieval and screening statistics in `coverage-audit.md`, not in hero copy or paper-family prose.

When `research-visual-report` is available, hand `report.md` and its relative `assets/` tree to that Skill for presentation. Research facts stay in the Markdown; the visual builder must not rewrite them.

## Quality gates

- Every included paper has a stable identifier and version/update date.
- The recorded field boundary matches the actual retrieval and deliverable; there is no representative-only filtering or paper-count cap.
- Exact search strings, search dates, sources, result counts, deduplication decisions, citation-chaining passes, and stopping evidence are preserved.
- Every discovered candidate appears in the candidate ledger and every eligible paper appears in the report; excluded and unresolved records have explicit reasons.
- Every direct paper has the full detailed fields required above, and every extended paper has a substantive compact analysis rather than a citation-only entry.
- Candidate discovery is completed and audited before paper-card drafting; presentation constraints never determine corpus membership.
- Every numerical or comparative claim has a locator to the original paper or official artifact.
- Every displayed figure is the paper's one selected main figure and has a local file, original caption, source URL and rights status.
- Every direct and extended paper has a recorded main-figure decision: selected, unavailable, unsuitable, or rights-restricted.
- `report.md` follows the visual handoff outline and `config.py` passes the downstream literal-config parser.
- A paper title note contains only a useful method alias or organization; venue, publication status, source type and date are not duplicated in the title.
- Every visible paper has exactly one first-publication date badge downstream. Confirmed conference, journal, Findings or Workshop information is encoded separately as venue metadata; internal labels such as `Direct` and `Extended` never appear in the public report.
- alphaXiv-generated prose is paraphrased and independently verified before it becomes a report claim.
- The synthesis answers the frozen research question and distinguishes evidence from interpretation.
- Each method family has a short comparative synthesis rather than a generic definition or a paper-by-paper recap.
- User-facing prose uses consistent terminology, calibrated evidence verbs and direct academic sentences; it avoids marketing language, mechanical triads and repetitive stock transitions.
- No internal paths, scraping logs, API keys, or process notes appear in the public report.

When modifying this Skill, run `python3 <skill>/scripts/self_test.py` and the standard Skill validator.
