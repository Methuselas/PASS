---
object_id: PAT_establish_adventure_entry_premise_without_prescribing_personal_motivation
object_type: pattern
name: Establish Adventure Entry Premise Without Prescribing Personal Motivation
library_path:
- game-design
- adventures
stage_binding: 0 design
lane_fit: both
foundation_role: foundation
routing_class: general
specialization_axis: none
foundation_object_id: none
tags:
- adventures
- premise
- entry
- agency
cross_links:
- rel: related_to
  target_object_id: PAT_preserve_player_control_of_protagonist_response_in_adventure_text
- rel: related_to
  target_object_id: PAT_start_adventures_at_the_first_actionable_change
- rel: related_to
  target_object_id: PAT_turn_character_history_into_scenario_addressable_state
reference:
  source_title: Designing TTRPGs For Dummies
  author: Martin Buinicki
confidence: high
references: []
variants:
- variant_id: game_design_variant_personalize_entry_through_player_authored_character_stakes
  variant_name: Personalize Entry through Player-Authored Character Stakes
  variant_basis: method_sequence
  difference_from_foundation: Ask players for relevant facts about why their characters are present and what relationships, responsibilities, possessions, goals, or local ties belong to them, then intersect the same live situation with those player-authored facts so each character receives a concrete reason to engage without the adventure dictating the character's internal response.
  when_to_use: The adventure needs to connect a shared threat or opportunity to characters with different backgrounds, especially when the group does not begin with a strong preexisting bond.
  when_not_to_use: The premise already supplies sufficient participation, the players prefer impersonal hooks, or using a volunteered character fact would convert player-owned history into an involuntary emotion, decision, or loss the player did not consent to place in scope.
  absorbed_from_object_id: none
---

# Establish Adventure Entry Premise Without Prescribing Personal Motivation

## Pattern Rule
**IF** an adventure depends on the protagonists beginning play under a shared condition, obligation, location, assignment, relationship, or other participation premise
**THEN** state that premise clearly enough to put the party into play while leaving character-specific motives and reactions open wherever the premise does not genuinely require them
**ELSE** do not prescribe why each protagonist cares merely to make the opening easier to write.

## Do
- Define the minimum shared condition the adventure needs in order to begin operating.
- When participation is optional rather than already established by the premise, expose concrete player-evaluable reasons to engage such as reward, protection, discovery, duty, relationship, access, status, curiosity, or avoidance of a visible loss without declaring which reason a protagonist personally feels.
- Let employment, membership, mission assignment, captivity, shipwreck, shared duty, or another established condition supply participation when that condition is part of the premise.
- Separate the fact that a character is involved from the personal reason the player gives that involvement when both do not need to be authored.

## Don't
- Require every protagonist to share one emotional reason for participating when only a common situation is necessary.
- Script a protagonist's loyalty, fear, enthusiasm, grief, or moral interpretation merely to guarantee participation.
- Assume that an in-world patron request is automatically a usable hook when the players cannot tell why engaging with it would matter to them or their characters.

## Checklist
- The minimum condition required to begin the adventure can be stated without describing each protagonist's internal response.
- Characters can differ in why they accept, resist, interpret, or endure the shared premise when that difference does not break the adventure.
- The opening reaches playable action without requiring the facilitator to prescribe a hidden personal reason each protagonist must care.
- If the premise requires voluntary uptake, the players can identify at least one concrete reason to consider engaging with it.

## Notes
A shared premise is a participation contract, not a complete character biography. When participation must be chosen rather than assumed, the premise also needs player-visible value: something to gain, protect, discover, fulfill, prevent, or otherwise care about in play. That offer does not authorize the adventure to decide which motive a protagonist adopts. Some adventures legitimately begin with the party already employed, assigned, trapped, shipwrecked, enlisted, or otherwise involved. That can establish why play starts without deciding how each protagonist feels about it. The useful boundary is between **required situation** and **player-owned motivation**.

Variant `game_design_variant_personalize_entry_through_player_authored_character_stakes` starts from facts the players supply rather than motives the adventure assigns. Ask what places, people, duties, possessions, travel reasons, or current goals already put each character near the situation, then let the same external threat touch those facts in different ways. Several personalized intersections can converge into one shared opening, allowing the adventure itself to create a common problem without deciding what any protagonist must feel about it.
