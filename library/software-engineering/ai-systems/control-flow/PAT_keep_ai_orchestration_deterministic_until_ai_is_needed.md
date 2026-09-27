---
object_id: PAT_keep_ai_orchestration_deterministic_until_ai_is_needed
object_type: pattern
name: Keep AI Orchestration Deterministic Until AI Is Needed
library_path:
- software-engineering
- ai-systems
- control-flow
stage_binding: 0 design
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: domain
foundation_object_id: none
tags:
- ai
- orchestration
- routing
- queues
- performance
cross_links: []
reference:
  source_title: The Hot New AI Model Nobody's Heard Of, But We Already Use the Concept
  author: Rob Braxman Tech Deep Dive
confidence: medium
references: []
variants: []
---

# Keep AI Orchestration Deterministic Until AI Is Needed

## Pattern Rule
**IF** an AI workflow has queueing, state tracking, wake/sleep decisions, or routes that can be decided from explicit data
**THEN** keep those control-plane decisions in ordinary deterministic code and invoke an AI task only when a queued item reaches a step that actually requires model judgment or generation
**ELSE** if the routing decision itself depends on semantic interpretation that deterministic code cannot make, isolate that interpretation in a bounded classifier step and return the result to the deterministic controller.

## Do
- Let ordinary code own intake, queue inspection, state transitions, persistence, retries, and selection of which worker should run next.
- Persist the result of an AI classification before routing to the next task so orchestration can resume without reconstructing the model's prior reasoning.
- Wake expensive AI workers only when work for their route exists; let them remain idle otherwise.
- Use a bounded classifier as a narrow boundary when semantic judgment is necessary, then hand its discrete result back to deterministic control flow.
- Make each queue state observable enough to tell whether an item is waiting, being classified, classified, dispatched, completed, or failed.

## Don't
- Don't use an AI agent as a polling loop, queue manager, scheduler, or state machine when ordinary code can perform that work exactly.
- Don't make every item enter a large general-purpose agent just so that agent can decide which specialized action should have been called.
- Don't leave routing state only inside model context; a restart or context change then erases the workflow's control state.
- Don't call idle agents continuously to discover that there is no work.

## Checklist
- Which workflow decisions can be made from explicit state without model inference?
- Is semantic classification isolated to the smallest step that needs it?
- Are classification and processing results persisted before the controller advances?
- Can expensive workers sleep until the deterministic router has work for them?
- Can the workflow recover its position from stored state without replaying an agent conversation?

## Notes
An agentic system still needs a control plane. When queue management and state transitions can be decided from explicit data, ordinary software can make them cheaper, faster, and easier to inspect than model-mediated control; verify those effects against the actual workload. Keep the model at points where semantic judgment or generation is the work.

This separation can also localize performance tuning: a deterministic router can dispatch a rejection path, classifier, retrieval-heavy worker, or web-enabled worker without loading every capability into every request.
