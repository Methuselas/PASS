---
object_id: PAT_put_player_input_in_the_player_controller
object_type: pattern
name: Put Player Input Events in the PlayerController
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
- player_controller
cross_links: []
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Put Player Input Events in the PlayerController

## Pattern Rule
**IF** you are wiring player input events for a Pawn or Character that a PlayerController possesses
**THEN** place the input events in the PlayerController's Event Graph rather than the Pawn's, so the input stays bound to the controller and survives swapping the possessed Pawn class — and keep whichever placement you choose consistent across the project.

## Do
- Remember that a Pawn or Character only receives input events while a PlayerController possesses it; possession is what connects the brain to the body.
- Use the Possess function to change which Pawn a PlayerController controls at runtime; only the currently possessed instance receives its commands.
- Keep the input placement consistent project-wide: all input in the PlayerController, or all in the Pawns — mixing the two makes the ownership of input unclear.

## Don't
- Don't scatter input events between the PlayerController and the Pawns; a consistent placement is what makes input ownership predictable.
- Don't assume input reaches a character that is not currently possessed — only the possessed instance responds.

## Checklist
- Input events live in one place (PlayerController or Pawn) and that place is the same across the project.
- Swapping the possessed Pawn class does not require rewiring the input.
- Only the currently possessed character responds to the player's input.

## Notes
The tradeoff the source states: input in the PlayerController is independent of the Pawn, which makes it easier to change the Pawn class a controller possesses. Input in the Pawn is also legal; the requirement is consistency.
