---
object_id: PAT_draw_debug_lines_to_diagnose_a_trace
object_type: pattern
name: Draw Debug Lines to Diagnose a Trace
library_path:
- software-engineering
- unreal-engine
- blueprints
- traces
stage_binding: 4 final
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: none
tags:
- unreal_engine
- blueprints
- traces
- debugging
cross_links: []
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Draw Debug Lines to Diagnose a Trace

## Pattern Rule
**IF** a trace is not behaving as expected and you need to see the line it is actually testing
**THEN** set the trace's Draw Debug Type to render the line in the viewport — For One Frame for a quick look, For Duration for a set time, or Persistent until you remove it — and use the trace and hit colors to tell the line from the hit.

## Do
- Set Draw Debug Type to For One Frame for a quick check, For Duration (with a Draw Time) to watch it for a while, or Persistent to keep it on screen while you investigate.
- Use Trace Color and Trace Hit Color to distinguish the trace line from the point it hit.
- Turn the debug line off (None) once the trace behaves, and before shipping.

## Don't
- Don't leave Persistent debug lines in a shipping build; they clutter the scene and cost draw calls.
- Don't use Persistent for a one-off check; For One Frame or For Duration is enough.
- Don't debug a trace by guessing; draw the line and see where it actually goes.

## Checklist
- The Draw Debug Type renders the trace line while you investigate.
- The trace and hit colors distinguish the line from the hit.
- The debug line is removed (None) before shipping.

## Notes
The Draw Debug Type parameter renders a trace's line in the viewport so you can see what it is actually testing: None draws nothing, For One Frame shows the line for a single frame, For Duration keeps it for the Draw Time, and Persistent keeps it until removed. Use it to find the problem when a trace is not acting as expected — a wrong start or end, an unexpected hit, or a line that never reaches the target. Remove the debug line before shipping.
