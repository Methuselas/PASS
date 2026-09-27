---
object_id: AP_route_external_inputs_through_specialized_ai_workers
object_type: ap
name: Route External Inputs Through Specialized AI Workers
library_path:
- software-engineering
- ai-systems
- design
stage_binding: 0 design
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: domain
foundation_object_id: none
tags:
- ai
- agents
- routing
- isolation
- workflow
cross_links:
- rel: supports
  target_object_id: PAT_keep_ai_orchestration_deterministic_until_ai_is_needed
- rel: supports
  target_object_id: PAT_isolate_ai_agents_by_task_context_and_permissions
- rel: supports
  target_object_id: PAT_route_bounded_ai_decisions_through_classification
reference:
  source_title: The Hot New AI Model Nobody's Heard Of, But We Already Use the Concept
  author: Rob Braxman Tech Deep Dive
confidence: medium
references: []
variants: []
---

# Route External Inputs Through Specialized AI Workers

## Objective
Turn an incoming stream of untrusted or heterogeneous requests into a recoverable workflow that uses deterministic software for orchestration, a bounded AI step for semantic classification, and task-specific workers for the capabilities each classified route actually needs. Success means every item has explicit stored state, unsafe or rejected items never reach more privileged workers, and each accepted item is dispatched only to a worker provisioned for its route.

## Steps / Flow
1. **Persist intake before inference.** Accept the new item with ordinary code, assign an identity, and record a queue/state value such as `waiting`. The controller, not a model conversation, owns lifecycle state. This activates `PAT_keep_ai_orchestration_deterministic_until_ai_is_needed`.
2. **Run the narrowest semantic gate.** When an item needs interpretation, invoke a classifier whose outputs correspond to the decisions the controller can act on. Keep its output bounded as described by `PAT_route_bounded_ai_decisions_through_classification`. If the classifier cannot produce a trustworthy route, mark the item for a defined fallback or human path rather than guessing a privileged branch.
3. **Isolate the evaluator.** Give the classifier only the directives, context, workspace, memory, and permissions it needs to evaluate the current item. It should not inherit broad tools merely because later workers have them. This activates `PAT_isolate_ai_agents_by_task_context_and_permissions`.
4. **Persist the classification before dispatch.** Store the route, score, and evaluation-complete state. **Advance gate:** do not launch a task worker until the controller can read a durable classification for the item. On restart, resume from stored state rather than replaying earlier model work.
5. **Dispatch by resource and authority requirements.** Let deterministic routing select the worker for the stored class. A rejection route may need no AI at all; a retrieval route may get a knowledge base; a web route may get external API access; a normal response route may need only the model and directives. Each branch receives only what it requires.
6. **Sleep workers without work.** Poll or trigger from the deterministic controller and wake a worker only when an item for its route is ready. Avoid continuous agent loops that spend inference capacity discovering an empty queue.
7. **Complete or recover explicitly.** Persist completion or failure. Retry only the stage whose durable state shows it failed. If a route changes because policy or classification logic changes, re-enter at the semantic gate rather than silently passing an old class into a newly privileged worker.
8. **Completion check.** Verify that every live item is in a named durable state, every dispatch came from a stored route, rejected items did not reach privileged workers, and each worker's tools/context match its declared task.

## Notes
The sequence matters. Classification before privileged dispatch keeps untrusted input out of more capable workers until a narrow evaluation has run; persisting state between stages makes the workflow recoverable; specializing workers avoids loading every resource into every request. An unordered bag of the same patterns would not guarantee these gates or the recovery point between them.

This protocol does not prescribe a particular queue, agent framework, model, threat scale, or set of routes. Those are implementation choices. The durable structure is deterministic intake and lifecycle control, bounded semantic gating, persisted routing state, and capability-scoped workers.
