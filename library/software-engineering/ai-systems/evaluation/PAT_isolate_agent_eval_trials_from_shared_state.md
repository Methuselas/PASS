---
object_id: PAT_isolate_agent_eval_trials_from_shared_state
object_type: pattern
name: Isolate Agent Eval Trials from Shared State
library_path:
- software-engineering
- ai-systems
- evaluation
stage_binding: 3 rough
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: domain
foundation_object_id: PAT_use_shared_test_setup_carefully
tags:
- ai_agents
- evaluation
- testing
- isolation
- reproducibility
cross_links: []
reference:
  source_title: Demystifying evals for AI agents
  author: Mikaela Grace, Jeremy Hadfield, Rodrigo Olivares, Jiri De Jonghe, with Anthropic contributors
confidence: high
references: []
variants: []
---

# Isolate Agent Eval Trials from Shared State

## Pattern Rule
**IF** an agent evaluation modifies files, caches, databases, histories, quotas, processes, or other mutable environment state
**THEN** start each trial from an equivalent clean environment and prevent state from one trial from affecting another
**ELSE** shared immutable fixtures are acceptable when they cannot change outcomes or leak information across trials.

## Do
- Reset or recreate all outcome-affecting state before each trial.
- Isolate mutable workspaces, databases, caches, histories, and resource budgets when parallel trials can interfere.
- Verify that the eval environment resembles production enough to exercise the same agent behavior without inheriting production's uncontrolled state.
- Treat correlated failures across supposedly independent trials as a harness problem until infrastructure causes have been ruled out.
- Check for information leakage from previous trials, including logs, git history, generated artifacts, cached answers, and stateful services.

## Don't
- Don't let one trial leave artifacts that make a later task easier or harder.
- Don't count several failures caused by one exhausted shared resource as independent evidence of model failure.
- Don't share mutable state merely to make the eval harness cheaper if it changes the distribution being measured.
- Don't assume process isolation alone is enough when external services or caches remain shared.

## Checklist
- What mutable state can the agent observe or change during a trial?
- Is that state reset or uniquely namespaced for every trial?
- Can one trial exhaust a shared resource that affects another?
- Can later trials discover artifacts or history from earlier ones?
- Would rerunning the same task in a fresh environment produce the same starting conditions?

## Notes
Repeated trials are useful only when they are meaningfully independent. Shared files, cache entries, history, or exhausted resources can create correlated results that look like agent reliability data but are actually properties of the harness. Trial isolation protects both reproducibility and the interpretation of stochastic metrics.
