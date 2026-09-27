---
object_id: PAT_persist_subagent_artifacts_and_pass_references
object_type: pattern
name: Persist Subagent Artifacts and Pass References
library_path:
- software-engineering
- ai-systems
- context-engineering
stage_binding: 1 skeleton
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: domain
foundation_object_id: PAT_persist_agent_working_notes_outside_context
tags:
- ai_agents
- multi_agent
- context_engineering
- artifacts
- handoff
cross_links:
- rel: related_to
  target_object_id: PAT_persist_agent_working_notes_outside_context
- rel: related_to
  target_object_id: PAT_retrieve_agent_context_just_in_time
- rel: related_to
  target_object_id: PAT_isolate_ai_agents_by_task_context_and_permissions
reference:
  source_title: How we built our multi-agent research system
  author: Jeremy Hadfield, Barry Zhang, Kenneth Lien, Florian Scholz, Jeremy Fox, and Daniel Ford
confidence: high
references: []
variants: []
---

# Persist Subagent Artifacts and Pass References

## Pattern Rule
**IF** a subagent produces a substantial structured artifact whose full fidelity matters to downstream use but copying it through the coordinator would waste context or risk lossy restatement
**THEN** persist the artifact in an external store and return a lightweight reference plus the minimal summary needed for orchestration
**ELSE** return a concise result directly when the artifact is small enough and no later consumer needs its original form.

## Do
- Let specialized workers write durable outputs such as code, reports, datasets, or visualizations directly to an artifact store when those outputs should survive independently of the worker context.
- Return a stable reference, identity, or location that lets the coordinator and later workers retrieve the artifact when needed.
- Include a short handoff that states what the artifact contains, why it matters, and any unresolved caveats without reproducing the full payload.
- Keep the coordinator focused on planning and synthesis while preserving the worker's original artifact for downstream use.
- Make artifact identity and lifecycle explicit enough that retries do not silently overwrite or confuse outputs from different branches.

## Don't
- Don't force every large worker result through a prose summary if later stages need the original structured output.
- Don't copy full artifacts into coordinator history merely to make them available later.
- Don't pass an opaque reference with no indication of what it contains or whether creation succeeded.
- Don't use external artifacts as a substitute for preserving the small amount of decision state the coordinator actually needs in context.

## Checklist
- Does downstream work need the original artifact or only a distilled finding?
- Would copying the artifact into coordinator context materially increase token use or risk information loss?
- Can later stages retrieve the artifact from a stable reference?
- Does the handoff include enough metadata for the coordinator to decide what to do next?
- Are retries and multiple worker outputs distinguishable in the artifact store?
- Can the coordinator synthesize without importing the worker's full scratch history?

## Notes
Persisting a worker artifact and passing a reference can avoid a multi-stage “game of telephone” when later stages need the original structured output. The pattern is distinct from durable working notes: notes preserve decision state for continuity, while delegated artifacts preserve full-fidelity output for selective downstream retrieval.
