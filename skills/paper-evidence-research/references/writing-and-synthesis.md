# Chinese research writing and synthesis

Use this guide when `report.md` or another user-facing deliverable is written in Chinese. It governs presentation, not the underlying evidence standard.

## Register and terminology

- Use concise academic prose. Prefer concrete subjects such as the method, experiment, table or result over conversational framing such as “这篇论文问的是”.
- Introduce a technical term once and use it consistently. Keep established method names, benchmark names and objective functions in English where translation would reduce precision; avoid switching between several Chinese translations of the same term.
- Distinguish the external `Skill`, a repository such as `SkillBank`, and a general ability of the model. Do not use these terms interchangeably.
- Retain the unit and comparison basis for every number: absolute points, relative percent, score, success rate, token count or compute.

## Evidence strength

Match the verb to the evidence:

- use `报告` or `观察到` for a value stated in the paper;
- use `支持` when an experiment is consistent with a claim;
- use `提示` for a plausible interpretation with limited evidence;
- use `不能据此推断` when the evaluation does not identify the stronger claim;
- reserve `证明` for formal proof or unusually decisive evidence.

Do not turn benchmark improvements into general claims about intelligence, autonomy, robustness or continual learning. State when a result is limited to a model, environment, task split, prompt condition or paper version.

## Sentence and paragraph construction

- Lead with the analytical point, then provide the mechanism or result that supports it.
- Vary sentence length naturally. Avoid several adjacent sentences with the same `方法名 + 动词 + 结果` pattern.
- Use contrast only when the evidence establishes a real difference. Avoid ornamental `不是……而是……`, `不仅……还……` and forced three-part parallelism.
- Remove stock transitions such as `首先`, `其次`, `最后`, `综上所述` when paragraph logic is already clear.
- Avoid promotional or absolute phrases such as `开创性`, `颠覆性`, `不可替代`, `真正的瓶颈`, `最稳健的方案` and `显著领先`, unless the last term is tied to a reported statistical test.
- Do not end sections with slogans. State the recommendation together with its applicable conditions and evidence boundary.

## Paper-card prose

- `核心问题 / 背景` should explain the task, why the existing approach is insufficient, and what condition the paper changes. Do not restate the title or abstract opening.
- `具体方法` should separate mechanisms that play different roles. For each point, explain both the operation and its purpose.
- `实验设置和结果` should contain at most three visible points. Prefer one setup point, one headline comparison and one ablation, failure case or limitation that changes how the result should be interpreted.
- Use exact table values where available. If the abstract conflicts with a table, report the traceable value and note the conflict in the evidence ledger.

## Family synthesis and conclusion

A family summary should compare mechanisms, not merely list papers. State the shared objective, the main methodological distinction and the boundary of the evidence in one compact paragraph.

The conclusion should answer the frozen research questions directly. Separate what has been demonstrated in controlled benchmarks from what remains untested in open or changing environments. Recommendations should be conditional on factors such as update frequency, auditability, transfer range, deployment cost and error risk.

## Final editing pass

Before delivery:

1. remove repeated sentence frames and duplicated conclusions;
2. replace claims stronger than their cited evidence;
3. verify terminology, units, dates and comparison baselines;
4. check that each paragraph adds a distinct analytical point;
5. confirm that shortening the visual card did not remove the evidence needed to understand the paper.
