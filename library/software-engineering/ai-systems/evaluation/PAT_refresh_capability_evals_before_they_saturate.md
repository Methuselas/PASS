---
object_id: PAT_refresh_capability_evals_before_they_saturate
object_type: pattern
name: Refresh Capability Evals Before They Saturate
library_path:
- software-engineering
- ai-systems
- evaluation
stage_binding: 3 rough
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: domain
foundation_object_id: PAT_keep_capability_and_regression_evals_separate
tags:
- ai_agents
- evaluation
- capability
- benchmarks
- testing
cross_links: []
reference:
  source_title: Demystifying evals for AI agents
  author: Mikaela Grace, Jeremy Hadfield, Rodrigo Olivares, Jiri De Jonghe, with Anthropic contributors
confidence: high
references: []
variants: []
---

# Refresh Capability Evals Before They Saturate

## Pattern Rule
**IF** a capability eval is approaching the point where the agent reliably solves nearly every task
**THEN** add harder or more representative tasks before the suite loses improvement headroom, while retaining solved tasks as regression coverage
**ELSE** keep the current capability set while it still separates meaningful system improvements.

## Do
- Track pass-rate distribution and difficulty, not only the aggregate score, so saturation is visible before the suite reaches a perfect score.
- Add longer, more complex, or more realistic tasks when existing items no longer discriminate between candidate systems.
- Move reliably solved tasks into regression coverage instead of deleting their historical contract.
- Preserve enough stable anchor tasks to understand whether score changes come from model progress or a moving benchmark.
- Revisit task difficulty after major model upgrades, tool changes, or capability jumps.

## Don't
- Don't interpret a ceilinged score as evidence that further capability differences do not exist.
- Don't keep adding easy tasks to a capability suite whose purpose is to expose headroom.
- Don't delete solved tasks and lose protection for behavior users now expect.
- Don't change the entire suite at once without retaining anchors that make old and new results interpretable.

## Checklist
- Is the capability suite still producing meaningful separation among candidate systems?
- Are most tasks already solved reliably?
- Do remaining failures represent important work or merely broken/ambiguous tasks?
- Have solved tasks been preserved as regression coverage?
- Are there anchor tasks that let you interpret results across suite revisions?

## Notes
A capability benchmark can outlive its usefulness without becoming technically incorrect. Once nearly every solvable task passes, the score becomes mostly a regression signal and stops exposing where better models or architectures improve the product. The suite should evolve with the system while its solved contracts remain protected elsewhere.
