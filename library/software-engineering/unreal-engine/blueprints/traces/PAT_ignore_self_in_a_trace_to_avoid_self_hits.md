---
object_id: PAT_ignore_self_in_a_trace_to_avoid_self_hits
object_type: pattern
name: Ignore Self in a Trace to Avoid Self-Hits
library_path:
- software-engineering
- unreal-engine
- blueprints
- traces
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: none
tags:
- unreal_engine
- blueprints
- traces
- collision
cross_links: []
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Ignore Self in a Trace to Avoid Self-Hits

## Pattern Rule
**IF** the actor or component calling a trace is itself in the world and could be hit by that trace
**THEN** set Ignore Self to True so the trace skips the calling instance, and use the Actors to Ignore array to exclude any other specific actors that should not be hit.

## Do
- Set Ignore Self to True when the tracer is a placed actor or component that the trace line could pass through.
- Use the Actors to Ignore array to exclude specific other actors from the test.
- Keep the start and end locations clear of the tracer when Ignore Self is not enough.

## Don't
- Don't leave Ignore Self False when the tracer sits on the trace line; the trace will report the tracer itself as the hit.
- Don't assume the trace ignores its caller by default; the setting must be set.
- Don't rely on Ignore Self to exclude other actors; use Actors to Ignore for those.

## Checklist
- Ignore Self is True when the tracer could hit itself.
- Other actors to exclude are listed in Actors to Ignore.
- The trace does not report the caller as its own hit.

## Notes
The Ignore Self parameter controls whether the Blueprint instance calling the trace is ignored in the collision test. Set it to True when the tracer is in the world and the trace line could pass through it, so the trace does not report the caller as the hit. Use the Actors to Ignore array to exclude specific other actors from the test.
