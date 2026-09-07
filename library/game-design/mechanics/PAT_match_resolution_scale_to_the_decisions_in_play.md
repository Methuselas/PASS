---
object_id: PAT_match_resolution_scale_to_the_decisions_in_play
object_type: pattern
name: Match Resolution Scale to the Decisions in Play
library_path:
- game-design
- mechanics
stage_binding: 0 design
lane_fit: both
foundation_role: foundation
routing_class: general
specialization_axis: none
foundation_object_id: none
tags:
- mechanics
- resolution
- scale
- abstraction
- mass-combat
cross_links: []
confidence: high
references: []
variants: []
---

# Match Resolution Scale to the Decisions in Play

## Pattern Rule
**IF** the same campaign can operate at materially different scales of actors, space, time, or consequence
**THEN** resolve each situation at the coarsest scale that preserves the decisions the players are supposed to make, and define explicit handoffs when state or consequences cross between scales
**ELSE** keep one resolution scale when changing representation would add conversion cost without changing meaningful choices.

## Do
- Decide whether the current choice is about an individual action, a squad, an army, a ship, a settlement, a project, or another aggregate before choosing the resolution procedure.
- Compress detail when lower-level distinctions would not change a decision, and return to finer resolution when positioning, named actors, equipment, or other local state becomes consequential.
- Define what information moves upward when fine-scale actions affect aggregate state, such as reconnaissance, sabotage, leadership loss, resource damage, or positional advantage.
- Define what information moves downward when aggregate resolution changes the local situation, such as territory, retreat routes, casualties around the protagonists, supply, objectives, or access.
- Keep focal-character consequences under the richer character-scale procedure when their survival or specific actions contain decisions worth playing rather than deriving them silently from an aggregate percentage.
- Allow different fidelity profiles for the same broad event when the group may care about logistics in one campaign and only strategic outcome in another.

## Don't
- Simulate every participant individually merely because individual rules exist.
- Collapse a scene to one aggregate roll when the omitted local choices are the reason the group is playing the scene.
- Let two scales both resolve the same consequence independently; assign ownership so results do not double-count or contradict each other.
- Use an aggregate casualty or damage result to erase a focal character when the game normally gives that character meaningful defensive or survival decisions.

## Checklist
- The chosen scale corresponds to the decisions the players can actually make in the scene.
- State removed by abstraction cannot change the intended outcome without first causing a handoff to a finer scale.
- Fine-scale actions that can alter aggregate results have an explicit conversion path.
- Aggregate results that alter later character-scale play return usable state rather than only narrative color.
- Overlapping scales have one declared owner for focal consequences.

## Notes
Changing scale is not merely a speed optimization. It changes what the game treats as an actor and which distinctions remain available for decision. A strong multi-scale design lets a campaign move from personal action to strategic resolution and back without losing causal continuity. The aggregate layer owns aggregate state; the finer layer retains consequences whose local decisions are still intended play.
