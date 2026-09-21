---
object_id: PAT_give_an_ai_sight_with_a_pawn_sensing_component
object_type: pattern
name: Give an AI Sight with a Pawn Sensing Component
library_path:
- software-engineering
- unreal-engine
- blueprints
- ai
stage_binding: 0 design
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: none
tags:
- unreal_engine
- blueprints
- ai
- sensing
- pawn_sensing
cross_links: []
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: low
references: []
variants: []
---

# Give an AI Sight with a Pawn Sensing Component

## Pattern Rule
**IF** you want an AI to detect the player (or other pawns) along its line of sight
**THEN** add a PawnSensing component to the AIController and use its On See Pawn event to react when a pawn is seen, storing the seen pawn where the decision logic can read it.

## Do
- Add the PawnSensing component to the AIController (the component that owns the AI's senses), not to the character.
- Use the On See Pawn event, which fires when the AI sees an instance of the Pawn class (or a child, such as Character) along its line of sight.
- Check that the seen pawn is the one you care about (cast it to the specific class, such as the player character) before reacting.
- Store the confirmed reference in the shared AI data (the Blackboard) so the Behavior Tree can base a decision on it.

## Don't
- Don't put the sensing component on the character when the AIController is the owner of the AI's perception.
- Don't assume every seen pawn is the target — cast to the specific class so the AI only reacts to the right actor.
- Don't react in the event graph when the decision belongs in the Behavior Tree; the event's job is to record what was seen, the tree decides what to do about it.

## Checklist
- A PawnSensing component is on the AIController.
- The On See Pawn event is wired to confirm the seen pawn's type.
- The confirmed reference is written to the shared AI data.
- The Behavior Tree can read that reference to make a decision.

## Notes
PawnSensing is how an AI gets vision. It lives on the AIController because the controller is the owner of the AI's perception, and its On See Pawn event is the moment the AI "sees" something. The event's job is narrow: confirm what was seen and record it. The decision about what to do with a sighted target belongs in the Behavior Tree, which reads the recorded reference. This separation — sensing records, the tree decides — is the core loop of AI: sense, decide, act.
