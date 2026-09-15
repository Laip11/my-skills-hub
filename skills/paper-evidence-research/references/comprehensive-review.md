# Comprehensive literature-review protocol

Use this procedure for every research request handled by this Skill. Its purpose is complete, high-recall coverage of the specified field under an explicit and auditable boundary, not a promise that an open literature can be proven mathematically complete.

## 1. Freeze a reproducible protocol

Before retrieval, record:

- research questions and the operational definition of relevance;
- start date, cutoff date, and timezone;
- domains, modalities, task settings, and publication types in scope;
- whether non-peer-reviewed preprints, workshops, technical reports, withdrawn papers, and non-English papers are included;
- exclusion rules and the evidence needed to apply each rule;
- databases and search surfaces to be queried;
- the full-text depth required for direct, extended, adjacent, and unresolved records.

Default to including stable preprints and technical reports when the topic is recent. Do not exclude work because it is obscure, has few citations, lacks code, reports negative results, or does not fit the preliminary taxonomy.

## 2. Build the candidate universe

Run independent retrieval routes and take their union:

1. **Lexical search:** exact topic phrase, hyphenation variants, abbreviations, spelling variants, synonyms, and translations where relevant.
2. **Mechanism search:** objectives, estimators, feedback types, data-generation regimes, theoretical framings, failure modes, and deployment terms that can describe the topic without naming it.
3. **Seed expansion:** backward references and forward citations from foundational papers, surveys, and highly connected recent papers.
4. **Entity search:** authors, labs, projects, benchmark names, method families, official repositories, proceedings, and model/system reports.
5. **Adversarial search:** queries intended to find work the current taxonomy would miss, including negative results, cross-domain applications, alternative terminology, and papers that challenge the dominant framing.

Log the exact query, source, execution date, returned count, and newly added canonical records for every search. Search-result snippets are discovery leads only.

## 3. Canonicalize before screening

Merge records by DOI, arXiv ID, OpenReview/forum ID, publisher identifier, and normalized title. Preserve:

- all known identifiers and URLs;
- preprint-to-proceedings relationships;
- version and update history;
- superseded, withdrawn, duplicate, or renamed status.

One intellectual work should normally have one canonical ledger row. Keep venue and version aliases in that row rather than counting them as separate papers.

## 4. Screen with visible tiers

Assign every unique candidate one relevance tier:

- **Direct:** the paper's method, theory, or central experiment satisfies the frozen operational definition.
- **Extended:** the topic is a substantive component or adaptation in another domain, modality, agent setting, or system.
- **Foundational adjacent:** the work supplies a necessary predecessor, formal connection, or baseline but is not itself an instance of the topic.
- **Mention-only:** the topic appears only in related work, discussion, or an incidental component.
- **Unresolved:** relevance cannot be decided because identity, version, or full text is unavailable.

Direct and extended papers must remain report-visible. Foundational-adjacent papers appear in a dedicated context section or index. Mention-only, duplicates, and exclusions remain visible in the candidate ledger with reasons.

Use title and abstract only for initial screening. Before final exclusion for conceptual irrelevance, inspect enough primary text to confirm that the paper does not satisfy the operational definition.

## 5. Full-text evidence depth

For every direct and extended paper, read the primary method and experiment sections. Also inspect the relevant ablation, limitation, and appendix sections when they affect the report claim. Record:

- canonical metadata and resolved version;
- research question, contribution, and assumptions;
- method components and training/inference workflow;
- teacher or feedback access, data origin, sampling distribution, and objective;
- models, datasets, baselines, metrics, and compute when reported;
- exact quantitative/comparative results with locators;
- author-stated limitations and separately labeled researcher inferences;
- predecessor, competing, and follow-up relationships.

Do not publish an abstract-only summary as a completed evidence card. If full text is inaccessible, retain the record as unresolved and state what remains unverified.

Minimum report depth is tier-specific:

- Every direct paper gets a full card: operational problem and gap; mechanism and objective; training/data-generation or inference procedure; teacher, feedback, or environment access; evaluation setup; at least one verified principal finding when reported; and limitations or evidence gaps.
- Every extended paper gets a substantive compact card: why it is in scope; where the topic enters the system; the concrete adaptation; the evaluation context; and the strongest verified result or limitation.
- Foundational-adjacent papers get enough explanation to make the dependency or formal connection explicit.

Do not satisfy coverage with a bibliography-only appendix, title-only cards, or generic abstract paraphrases. Compress wording and navigation before reducing analytical fields.

## 6. Saturation and reconciliation

Candidate discovery may stop only after all of the following:

- every planned lexical, mechanism, entity, and adversarial query family has been run;
- backward and forward citation chaining has been completed for the seed set and for newly discovered method families;
- at least two consecutive refinement/citation passes add no new direct or extended paper;
- all papers in each selected seed survey or authoritative method table have been reconciled to a candidate-ledger row;
- remaining database, language, access, indexing, and cutoff-date blind spots are documented.

If these conditions are not met, label the corpus provisional. Never use an arbitrary target count, deadline pressure, or report length as evidence of saturation.

## 7. Coverage audit

Report:

- raw records retrieved by source and query family;
- unique records after deduplication;
- counts by relevance tier, publication type, year, domain, and evidence status;
- included, excluded, unresolved, withdrawn, and superseded counts;
- which retrieval route uniquely discovered each included paper;
- reconciliation coverage against seed surveys;
- known blind spots and the final search date.

Use careful language: say “systematically searched under the stated protocol” or “no additional eligible papers were found after two saturation passes.” Do not claim universal completeness for an open, changing literature.

## 8. Presentation boundary

Corpus membership is decided by the research protocol, never by the visual format. If the corpus is too large for identical long cards:

- keep every direct and extended paper visible and searchable;
- vary card density by relevance and evidence richness without omitting entries;
- move secondary numerical evidence to the ledger;
- provide overview tables and filters for navigation;
- keep all exclusions and unresolved records in the audit artifacts.

The visual report may summarize navigation, but it must not turn a comprehensive corpus into a representative subset.
