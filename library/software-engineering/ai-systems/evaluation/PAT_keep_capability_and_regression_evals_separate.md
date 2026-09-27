---
object_id: PAT_keep_capability_and_regression_evals_separate
object_type: pattern
name: Keep Capability and Regression Evals Separate
library_path:
- software-engineering
- ai-systems
- evaluation
stage_binding: 3 rough
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: domain
foundation_object_id: AP_choose_test_cases_systematically
tags:
- ai_agents
- evaluation
- regression
- capability
- testing
cross_links: []
reference:
  source_title: Demystifying evals for AI agents
  author: Mikaela Grace, Jeremy Hadfield, Rodrigo Olivares, Jiri De Jonghe, with Anthropic contributors
confidence: high
references: []
variants: []
---

# Keep Capability and Regression Evals Separate

## Pattern Rule
**IF** an AI system needs both room to measure new capability and protection against losing behavior it already performs reliably
**THEN** maintain separate capability and regression eval sets, using difficult low-baseline tasks to measure improvement and near-solved tasks to detect backsliding
**ELSE** a single suite is sufficient only when the system is too early or too narrow for those objectives to diverge.

## Do
- Put unsolved or unreliable tasks in a capability set so there is visible headroom for improvement.
- Keep established behaviors in a regression set whose expected pass rate is close to the system's reliable ceiling.
- Run regression coverage while hill-climbing capability so a gain in one area cannot hide damage elsewhere.
- Graduate consistently solved capability tasks into regression coverage rather than deleting them once they become easy.
- Report the two suites separately so a stable regression score does not masquerade as capability progress and a difficult capability score does not masquerade as a regression.

## Don't
- Don't demand near-100-percent performance from a suite whose purpose is to expose what the system cannot do yet.
- Don't fill a capability suite entirely with solved tasks; it then measures stability rather than progress.
- Don't discard solved capability tasks if they represent behavior users now depend on.
- Don't aggregate capability and regression tasks into one number that obscures whether a change improved frontier behavior or broke established behavior.

## Checklist
- Does the capability set contain meaningful unsolved or unreliable tasks?
- Does the regression set cover behavior the system is already expected to preserve?
- Are both suites run when prompts, models, tools, or agent logic change?
- Is there a rule for graduating solved capability tasks into regression coverage?
- Can a reader distinguish improvement from preservation in the reported results?

## Notes
The two suites answer different engineering questions. Capability evals ask how far the system can be pushed; regression evals ask whether yesterday's working behavior still works today. Keeping those questions separate gives each score an interpretable target and lets the test corpus evolve with the system.
