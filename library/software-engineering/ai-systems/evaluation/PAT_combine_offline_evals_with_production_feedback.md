---
object_id: PAT_combine_offline_evals_with_production_feedback
object_type: pattern
name: Combine Offline Evals with Production Feedback
library_path:
- software-engineering
- ai-systems
- evaluation
stage_binding: 4 final
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: domain
foundation_object_id: none
tags:
- ai_agents
- evaluation
- observability
- production
- feedback_loops
cross_links: []
reference:
  source_title: Demystifying evals for AI agents
  author: Mikaela Grace, Jeremy Hadfield, Rodrigo Olivares, Jiri De Jonghe, with Anthropic contributors
confidence: high
references: []
variants: []
---

# Combine Offline Evals with Production Feedback

## Pattern Rule
**IF** an AI agent is deployed to real users or real workloads
**THEN** combine offline automated evals with production monitoring, user feedback, representative trace review, and periodic human calibration, feeding important production failures back into the offline suite
**ELSE** use offline evals as the primary predeployment signal while preparing the instrumentation needed to close the loop after launch.

## Do
- Run automated evals before release and on model, prompt, tool, or orchestration changes.
- Monitor live errors, quality signals, cost, latency, routing behavior, and other relevant production outcomes after deployment.
- Triage user-reported failures and representative production traces into candidate regression cases.
- Use controlled experiments such as A/B tests when the question depends on actual user outcomes rather than an offline proxy.
- Periodically use qualified humans to recalibrate subjective judges and review quality dimensions that automated checks miss.
- Promote recurring or high-impact production failures into durable offline tasks so the same class of issue is caught before the next release.

## Don't
- Don't assume a strong offline score covers real distributions the suite has never seen.
- Don't rely on production complaints as the first and only detection mechanism for known failure classes.
- Don't treat sparse user feedback as a statistically representative performance metric.
- Don't leave production incidents as one-off fixes without adding coverage when the failure can be reproduced safely offline.
- Don't use one measurement layer as proof that all other layers are unnecessary.

## Checklist
- What does the offline suite catch before deployment?
- What production signals reveal distribution shift or unforeseen failure modes?
- Is there a regular path from real failures into new eval tasks?
- Which subjective dimensions still require periodic human calibration?
- Are high-impact changes validated with real-user outcome data when appropriate?

## Notes
Offline evals are fast and reproducible but bounded by the scenarios designers imagined. Production monitoring sees the real distribution but discovers some problems only after users encounter them. Human review captures subtle quality but does not scale. Treating these as complementary layers creates a feedback loop in which production expands the test suite and the test suite prevents known failures from recurring.
