---
object_id: PAT_layer_dynamic_events_over_static_location_state
object_type: pattern
name: Layer Dynamic Events over Static Location State
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
- exploration
- random-encounters
- time-pressure
- locations
- dynamic-state
cross_links:
- rel: related_to
  target_object_id: PAT_write_keyed_locations_as_executable_local_state
- rel: related_to
  target_object_id: PAT_separate_mobile_actors_from_fixed_location_state
- rel: related_to
  target_object_id: PAT_generate_sandbox_situations_from_world_state_and_player_needs
- rel: related_to
  target_object_id: PAT_use_time_to_structure_opportunity
reference:
  source_title: 'Designing Dungeons: Or, How to Kill a Party in 30 Rooms or Less'
  author: Josh McCrowell and Warren D.
confidence: high
references: []
variants: []
---

# Layer Dynamic Events over Static Location State

## Pattern Rule
**IF** location-based exploration should change with time, movement, pressure, or roaming activity but exact continuous simulation is not worth its operating cost
**THEN** pair the stable location key with a cadence-based dynamic event procedure whose results combine with the current place and world state
**ELSE** use only the static key or explicitly track mobile state when either is sufficient.

## Do
- Choose an event cadence tied to an actual exploration procedure such as turns, travel intervals, noise, resource use, alert state, or another recurring trigger.
- Treat the location key as the static layer and the event procedure as the dynamic layer; let both contribute to the scene instead of allowing one to replace the other.
- Include more than roaming combatants when the location supports it: patrols, travelers, faction activity, environmental shifts, clues, curiosities, resource attrition, warnings, or other time-dependent events can all make movement consequential.
- Write event results as small situations with an activity, direction, motive, evidence, or immediate choice when that context matters.
- Let the current room, route, faction state, alert level, prior casualties, weather, time, or other stored conditions modify how a result manifests.
- Use dynamic results to telegraph nearby threats and opportunities when informed navigation is part of play.
- Update, replace, or retire entries when persistent events make the original result impossible or materially change the site's state.
- Prefer an explicit live roster when exact actor positions, routes, and coordinated response are themselves important decisions.

## Don't
- Use random events as unrelated interruptions that ignore the location's inhabitants, ecology, recent events, and current state.
- Roll so often that movement becomes procedural noise without creating meaningful pressure or novelty.
- Let a random table respawn eliminated actors or restore depleted resources without an in-world process that explains the change.
- Put critical progress behind a single low-probability event unless another reliable access path exists.
- Track exact positions through random abstraction when players are making decisions that depend on those positions.
- Make every result a combat encounter when other forms of movement, evidence, depletion, or opportunity would better animate the place.

## Checklist
- The trigger or cadence for dynamic events is explicit.
- Static keys remain usable independently as the durable location state.
- Dynamic results fit the place and can combine with the current local situation.
- At least some results create information, pressure, opportunity, movement, or state change rather than only another fight.
- Persistent changes can alter or invalidate future results.
- The procedure does not recreate actors or resources that prior play removed without explanation.
- The chosen abstraction is cheaper than tracking every mobile element directly while preserving the decisions the design cares about.

## Notes
A keyed location answers what is normally here. Exploration often also needs an answer to what happens while the characters spend time moving through it. A dynamic event layer supplies that second answer without forcing the facilitator to simulate every footstep of every inhabitant. Its strongest use is not randomness for its own sake, but pressure and recombination: a patrol encountered in a shrine, a warning heard near a dangerous route, or dwindling light during a detour produces a different scene from either the room key or the event entry alone.
