---
object_id: PAT_inspect_unreal_blueprint_component_templates_across_inheritance
object_type: pattern
name: Inspect Unreal Blueprint Component Templates Across Inheritance
library_path:
- software-engineering
- unreal-engine
- editor
stage_binding: 2 block
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: none
tags:
- unreal_engine
- editor_tools
- blueprints
- components
- reflection
cross_links:
- rel: related_to
  target_object_id: PAT_scope_unreal_asset_validation_with_registry_queries
reference:
  source_title: Extending and Customizing Unreal Engine Editor
  author: Roger Mattsson
confidence: medium
references: []
variants: []
---

# Inspect Unreal Blueprint Component Templates Across Inheritance

## Pattern Rule
**IF** an Unreal editor validator needs component defaults from an actor class without spawning or running construction logic
**THEN** combine native CDO components with Blueprint SCS templates across the generated-class hierarchy, state the unexecuted dynamic-component boundary, and validate every class, node and template encountered.

## Do
- Accept an actor class and desired component base type; return an empty result for a null or incompatible class.
- Keep the original most-derived generated class available when resolving actual component templates.
- Walk Blueprint-generated superclasses until the native boundary. At each level, validate the `SimpleConstructionScript`, nodes and component classes before resolving matching templates.
- Separately query native components from the actor CDO, because code-created defaults and Blueprint SCS templates have different storage paths.
- Deduplicate results by template identity or stable component key and document override/inheritance ordering.
- Treat returned objects as templates: inspect defaults without mutating them, invoking instance-only behavior or assuming an owning world.
- Report that components created dynamically by construction scripts, timelines or runtime graph execution are absent; use a controlled spawned-instance audit when those are in scope.

## Don't
- Don't assume the most-derived CDO enumerates every Blueprint-added component template.
- Don't execute arbitrary construction logic in a commandlet merely to discover defaults without a sandboxed-world contract.
- Don't mutate component templates as though they were actor instances.
- Don't silently claim complete component coverage when graph-created components are excluded.

## Checklist
- Are native and Blueprint-added templates both included across inherited classes?
- Are null SCS nodes, unloaded classes and template-resolution failures handled?
- Are duplicates and overridden templates resolved deterministically?
- Is the dynamic construction/runtime exclusion visible to the validation rule and its users?

## Notes
This is a static-default inspection technique. It is appropriate for policy checks on authored defaults, not for questions whose answer depends on construction-script execution or world state.
