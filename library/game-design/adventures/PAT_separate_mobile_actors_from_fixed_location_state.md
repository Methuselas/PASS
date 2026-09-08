---
object_id: PAT_separate_mobile_actors_from_fixed_location_state
object_type: pattern
name: Separate Mobile Actors from Fixed Location State
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
- adversaries
- locations
- rosters
- state
- referee-interface
cross_links:
- rel: related_to
  target_object_id: PAT_write_keyed_locations_as_executable_local_state
- rel: related_to
  target_object_id: PAT_externalize_live_rules_state_at_the_point_of_use
- rel: related_to
  target_object_id: PAT_express_faction_power_as_deployable_response_capacity
- rel: related_to
  target_object_id: PAT_generate_sandbox_situations_from_world_state_and_player_needs
- rel: related_to
  target_object_id: PAT_layer_dynamic_events_over_static_location_state
reference:
  source_title: The Art of the Key
  author: Justin Alexander
confidence: high
references: []
variants: []
---

# Separate Mobile Actors from Fixed Location State

## Pattern Rule
**IF** actors can move, coordinate, patrol, reinforce, flee, or be reassigned across multiple keyed locations during play
**THEN** track those actors on a separate live roster or equivalent state surface while the location keys retain fixed features and truly stationary occupants
**ELSE** keep actors in the local key when their position is effectively part of that location's stable state.

## Do
- Group mobile actors into action groups at the smallest granularity that is likely to move or decide independently.
- Give each action group a default position plus enough behavior, role, destination, or conditional placement to move it coherently when play changes the situation.
- Use alternate states such as day/night, normal/alert, or occupied/evacuated only when the site changes enough to justify the extra reference surface.
- Update the roster directly when actors are killed, recruited, replaced, retasked, split, merged, or relocated instead of rewriting every affected location key.
- Preserve fog of war: alarms and movement should propagate through communication, travel time, duties, and actual knowledge rather than making every actor instantly omniscient.
- Keep fixed hazards, architecture, furnishings, and other durable local facts in the location key so the roster remains about mobile state.
- Mark likely stationary actors explicitly when a shared roster would otherwise make it unclear which keyed occupants should remain local.
- Switch to a coarser abstraction when the number of independently tracked groups exceeds what the facilitator can operate comfortably.

## Don't
- Duplicate a mobile actor as if it permanently occupies several location keys at once.
- Track every individual separately when a group normally moves and acts as one unit.
- Keep a large moving force embedded in prose spread across many keys and require the facilitator to reconstruct its current position from memory.
- Let an alarm teleport knowledge or responders through walls, distance, sealed routes, or duties that should delay or prevent response.
- Build several alternate rosters when a simple conditional note on one or two groups would be cheaper.
- Use a live roster for a tomb, ruin, or other site whose occupants are genuinely fixed and independent.

## Checklist
- Every mobile actor belongs to one identifiable live group or individual entry.
- Action-group granularity matches likely independent movement and decision-making.
- Default locations and meaningful conditional placements are easy to find.
- Casualties and reassignments can be recorded without rewriting the static location key.
- Communication and travel constraints limit how the site responds to intrusion.
- Stationary occupants remain unambiguous.
- The number of tracked groups is within the intended facilitator's operating capacity or has been compressed into a cheaper procedure.

## Notes
Location keys are excellent local execution surfaces because they isolate the facts needed for the current place. Mobile actors break that isolation: once guards can leave a barracks, patrol a corridor, reinforce a gate, or flee to another level, storing their current state inside one room description turns the key into stale data. Separating mobile actors preserves both advantages. The map and keys remain stable references while a small live roster carries the state that actually moves.
