---
object_id: PAT_calibrate_llm_judges_against_human_graders
object_type: pattern
name: Calibrate LLM Judges Against Human Graders
library_path:
- software-engineering
- ai-systems
- evaluation
stage_binding: 3 rough
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: domain
foundation_object_id: none
tags:
- ai_agents
- evaluation
- llm_judge
- calibration
- human_review
cross_links: []
reference:
  source_title: Demystifying evals for AI agents
  author: Mikaela Grace, Jeremy Hadfield, Rodrigo Olivares, Jiri De Jonghe, with Anthropic contributors
confidence: high
references: []
variants: []
---

# Calibrate LLM Judges Against Human Graders

## Pattern Rule
**IF** an evaluation uses an LLM to judge subjective, semantic, or open-ended agent behavior
**THEN** measure that judge against qualified human judgments, tighten the rubric until disagreement is understood and acceptable, and preserve an explicit insufficient-evidence outcome
**ELSE** use deterministic grading when the success criterion can be established mechanically.

## Do
- Build a calibration sample that includes clear passes, clear failures, ambiguous cases, and difficult boundary examples.
- Have domain-qualified humans establish the reference judgment independently of the model judge.
- Compare disagreements by rubric dimension rather than only by aggregate agreement.
- Rewrite vague criteria and split unrelated dimensions when one judge prompt is trying to score too many things at once.
- Give the judge an `Unknown`, `insufficient evidence`, or equivalent abstention option when the evidence does not support a reliable grade.
- Recalibrate after material changes to the judge model, rubric, task distribution, or agent outputs.

## Don't
- Don't treat an LLM judge as ground truth because its explanations sound persuasive.
- Don't force the judge to choose pass or fail when the transcript lacks enough evidence.
- Don't use one broad rubric to hide disagreement across several independent quality dimensions.
- Don't assume calibration remains valid after swapping the judge model or changing the evaluated task distribution.

## Checklist
- What human reference standard is the judge intended to approximate?
- Has judge-human agreement been measured on representative cases?
- Are disagreements traceable to specific rubric dimensions?
- Can the judge abstain when evidence is insufficient?
- Is recalibration triggered by meaningful changes to the evaluator or evaluated system?

## Notes
A model judge is itself a probabilistic component. Its usefulness comes from approximating a human standard cheaply and repeatedly, not from possessing an independent guarantee of correctness. Calibration turns that approximation into something measurable and makes rubric defects visible before they contaminate system-level scores.
