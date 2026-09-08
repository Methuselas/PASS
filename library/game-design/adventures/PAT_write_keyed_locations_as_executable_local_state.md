---
object_id: PAT_write_keyed_locations_as_executable_local_state
object_type: pattern
name: Write Keyed Locations as Executable Local State
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
- location-keys
- maps
- referee-interface
- retrieval
- state
cross_links:
- rel: related_to
  target_object_id: PAT_layer_adventure_information_by_how_players_can_access_it
- rel: related_to
  target_object_id: PAT_externalize_live_rules_state_at_the_point_of_use
- rel: related_to
  target_object_id: PAT_make_the_game_operable_without_hidden_designer_knowledge
- rel: related_to
  target_object_id: PAT_match_information_precision_to_decision_precision
- rel: related_to
  target_object_id: PAT_encode_stable_spatial_state_on_the_map
- rel: related_to
  target_object_id: PAT_separate_mobile_actors_from_fixed_location_state
reference:
  source_title: The Keep on the Borderlands
  author: Gary Gygax
confidence: high
references: []
variants: []
---

# Write Keyed Locations as Executable Local State

## Pattern Rule
**IF** an adventure uses a map, node diagram, or other keyed location structure as a primary runtime interface
**THEN** make each key a locally executable state packet that tells the facilitator what is immediately available, what is hidden or triggered, what can act here, how nearby state can respond, and what changes when the location is disturbed
**ELSE** use the scene, event, timeline, relationship, or other structure that actually organizes play.

## Do
- Open with enough immediately perceptible spatial and sensory information for players to choose a first action without exposing referee-only truth.
- Order the key roughly by likely table use: immediate orientation first, then prominent interactable elements, then deeper facts reached through inspection, interaction, or triggers; move from general to specific without prescribing the players' actual order of action.
- Use descriptive headings, bullets, indentation, or other hierarchy around significant elements when that makes local state easier to scan; include a section because the location needs it, not because a rigid template demands it.
- Distinguish automatic information from details gained by questioning, searching, interaction, or a genuinely uncertain check.
- Put occupants, hazards, useful objects, mechanical statistics, special procedures, and discoverable rewards close to the decision that queries them.
- State how inhabitants normally behave and what changes when they are alerted, surprised, bargained with, bypassed, injured, reinforced, or otherwise pushed out of the default state when those branches matter.
- Record connections that can make another key react: alarms, noise, sight lines, secret routes, reinforcements, escape paths, shared leadership, or other local dependencies.
- Record persistent consequences that a later visit must inherit, such as removed treasure, dead or displaced occupants, opened barriers, broken traps, rescued prisoners, or changed defenses.
- Factor rules that repeat unchanged across many keys into a shared local procedure, but keep exceptions and state that must be adjudicated immediately at the key where they matter.
- Let the map carry stable geometry, ordinary exits, scale, and other spatial facts it already communicates clearly; use the key for special conditions, exceptions, hidden state, and interaction detail instead of narrating the map back into prose.
- Keep referee background brief and subordinate to information that can affect player discovery, interaction, or adjudication.

## Don't
- Begin every key with lore that the facilitator must read past before discovering what the players can perceive or do.
- Fill mandatory headings with redundant tactics, treasure, development, or other boilerplate when the location does not need those sections.
- Repeat ordinary map geometry in prose when the same information is already clear on the map and no exception changes how it works.
- Make the facilitator combine several distant sections of the book to learn the basic state of an ordinary room or location.
- Give an occupant statistics but no usable behavioral or response information when its reaction is likely to matter.
- Key a location only by what was there before play and omit the states created by alarms, escape, negotiation, casualties, or other expected interactions.
- Put a number on the map without enough local text to understand why that location is distinct in play.

## Checklist
- The first actionable description is safe to use without leaking hidden information.
- Hidden and triggered facts have explicit access conditions or triggers when they matter.
- The facilitator can find the ordinary occupants, hazards, useful resources, and mechanical data without reconstructing them from another chapter.
- Expected alerts, reinforcements, escapes, or adjacent reactions identify their local dependencies.
- Treasure and other rewards state how they can actually be found or obtained when discovery is not automatic.
- A revisited key has enough recorded consequences to determine how prior play changed it.
- Repeated global procedure is factored out, while location-specific exceptions remain at point of use.
- The key's information hierarchy follows how the location is likely to be queried during play rather than a one-size-fits-all content template.
- Stable geometry is not duplicated unnecessarily between map and key, and special spatial exceptions remain easy to find.

## Notes
A keyed map is not merely a coordinate index. At the table, each key becomes a temporary execution surface: the facilitator needs to orient the players, preserve hidden information, operate the inhabitants, resolve local hazards and rewards, and propagate consequences to connected locations. A strong key minimizes reconstruction without trying to narrate every possible action. It stores the local facts and dependencies from which unplanned play can be adjudicated.
