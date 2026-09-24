---
object_id: PAT_shape_blueprint_function_nodes_for_graph_use
object_type: pattern
name: Shape Blueprint Function Nodes for Graph Use
library_path:
- software-engineering
- unreal-engine
- editor
stage_binding: 0 design
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: none
tags:
- unreal_engine
- blueprints
- reflection
- node_design
- usability
cross_links:
- rel: related_to
  target_object_id: PAT_encode_unreal_property_intent_in_reflection_metadata
reference:
  source_title: Extending and Customizing Unreal Engine Editor
  author: Roger Mattsson
confidence: medium
references: []
variants: []
---

# Shape Blueprint Function Nodes for Graph Use

## Pattern Rule
**IF** a C++ function will appear as a Blueprint node
**THEN** design its reflection metadata around graph reading and evaluation semantics: make discovery explicit, expose execution only when it communicates real work, and collapse visual detail only when meaning remains unambiguous.

## Do
- Give every Blueprint-facing function a stable, domain-oriented category and a concise tooltip that explains effects, constraints and exceptional outcomes. Treat names and pin labels as part of the public API.
- Mark a node pure only when repeated evaluation is cheap, deterministic for the same visible inputs and free of externally observable side effects. Remember that Blueprint may reevaluate a pure node for each consumer.
- Prefer execution pins for costly work, mutations, latent expectations or operations whose ordering must be visible. Do not use purity merely to save graph space.
- Use a compact title only for a familiar operation whose remaining pin meanings are obvious without labels. Verify the compact form in a realistic graph, not only in isolation.
- Expand a Boolean or enum into execution outputs when most callers would otherwise add an immediate branch or switch and the paths form a small, stable choice set. Keep a value-returning form only when it serves a distinct composition use case.
- Put infrequently changed optional inputs behind `AdvancedDisplay`; keep inputs that determine the normal meaning or safety of the call visible.
- Review representative call sites and search menus after metadata changes. Check category placement, discoverability, tooltip clarity, pin labels, node width and the graph produced by ordinary composition.

## Don't
- Don't publish duplicate value and execution-expanded functions by default; duplicate only when observed call-site shapes justify both APIs and give each a clear role.
- Don't make a function pure when it mutates state, performs substantial work or can return different results within one apparent evaluation.
- Don't hide required context behind advanced pins or remove labels from domain-specific arguments just to make a node smaller.
- Don't patch engine tooling to enforce a project convention until a project-owned validation or linting path has proved insufficient.

## Checklist
- Can users find the node under a predictable category and understand it without opening C++?
- Does the presence or absence of execution pins accurately communicate cost, effects and ordering?
- Do compact and advanced forms preserve the meaning of every visible connection?
- Is each alternate node form justified by real graph composition rather than blanket policy?

## Notes
Node metadata is interface design. The goal is not minimum area at any cost, but minimum visual burden consistent with correct expectations about evaluation, effects and choices.
