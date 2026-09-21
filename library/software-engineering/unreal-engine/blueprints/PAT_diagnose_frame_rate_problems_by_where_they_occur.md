---
object_id: PAT_diagnose_frame_rate_problems_by_where_they_occur
object_type: pattern
name: Diagnose Frame Rate Problems by Where They Occur
library_path:
- software-engineering
- unreal-engine
- blueprints
stage_binding: 4 final
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: none
tags:
- unreal_engine
- blueprints
- performance
- debugging
cross_links: []
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Diagnose Frame Rate Problems by Where They Occur

## Pattern Rule
**IF** you observe sluggish performance when testing the game on its target machines
**THEN** choose the initial investigation scope from where the slowdown occurs before changing anything: if frame rate is low everywhere, inspect global settings such as post-processing or anti-aliasing first; if it is low only in certain areas of a level, inspect local object density and unusually expensive models first.

## Do
- Test the game regularly on the machines you intend for people to play it on — that testing is the best way to optimize performance.
- Take note of where sluggishness occurs before choosing a fix; the location narrows the first place to investigate but does not by itself prove the cause.

## Don't
- Don't drop global graphics quality when only one area of the level stutters — you pay the visual cost on every frame everywhere to fix one spot.
- Don't tune from the editor machine alone and assume the target machines will agree with it.

## Checklist
- Performance was measured on a target machine, not just the development machine.
- The sluggishness has a recorded location: always low, or specific areas of a level.
- The applied fix matches that scope: global settings for a global problem, local density or model quality for a localized one.

## Notes
Frame-rate problems often present with a useful scope signal. A game that is slow everywhere makes baseline graphics settings such as post-processing and anti-aliasing reasonable first suspects. A game that slows only in certain places makes local density or expensive content in those places reasonable first suspects. That observation guides investigation; measurement still has to establish the actual cause before the fix is chosen.
