---
object_id: PAT_choose_the_input_mode_by_who_should_receive_input
object_type: pattern
name: Choose the Input Mode by Who Should Receive Input
library_path:
- software-engineering
- unreal-engine
- blueprints
stage_binding: 1 skeleton
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: none
tags:
- unreal_engine
- blueprints
- input
- input_mode
- ui
cross_links: []
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Choose the Input Mode by Who Should Receive Input

## Pattern Rule
**IF** you need to decide whether user input events go to the UI, to the Player Controller, or to both
**THEN** use the Set Input Mode nodes to set the priority.

## Do
- Use Set Input Mode Game Only when only the Player Controller should receive input events (normal gameplay).
- Use Set Input Mode UI Only when only the UI should receive input events (a mouse-driven menu).
- Use Set Input Mode Game and UI when the UI has priority in handling an input event but unhandled input should fall through to the Player Controller (for example, a shop UI the player can still move away from with the arrow keys).

## Don't
- Don't leave the input mode at its default when a menu needs the mouse — the Player Controller may consume the input the UI needs.
- Don't use UI Only when the player should still be able to move — use Game and UI.

## Checklist
- The input mode matches who should receive input: game only, UI only, or both.
- A mouse-driven menu uses UI Only or Game and UI.
- Normal gameplay uses Game Only.

## Notes
There are three Set Input Mode nodes: Game Only (only the Player Controller receives input events), UI Only (only the UI receives input events), and Game and UI (the UI has priority, but if the UI does not handle an input event, the Player Controller receives it). Example: a shop UI displayed when the player overlaps a shop — Game and UI lets the player use the mouse for the menu but still move away with the arrow keys.
