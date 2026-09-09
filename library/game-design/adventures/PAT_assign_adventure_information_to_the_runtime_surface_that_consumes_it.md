---
object_id: PAT_assign_adventure_information_to_the_runtime_surface_that_consumes_it
object_type: pattern
name: Assign Adventure Information to the Runtime Surface That Consumes It
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
- information
- usability
- retrieval
- runtime
cross_links:
- rel: related_to
  target_object_id: PAT_layer_adventure_information_by_how_players_can_access_it
- rel: related_to
  target_object_id: PAT_write_keyed_locations_as_executable_local_state
- rel: related_to
  target_object_id: PAT_encode_stable_spatial_state_on_the_map
- rel: related_to
  target_object_id: PAT_separate_mobile_actors_from_fixed_location_state
- rel: related_to
  target_object_id: PAT_externalize_live_rules_state_at_the_point_of_use
confidence: high
references: []
variants: []
---

# Assign Adventure Information to the Runtime Surface That Consumes It

## Pattern Rule
**IF** an adventure contains information that different participants must retrieve at different times, frequencies, secrecy levels, or rates of change
**THEN** place each fact on the smallest runtime surface that can legally expose it to its consumer when needed and keep repeated or mutable information persistent instead of forcing it through transient narration
**ELSE** keep the information consolidated when one readable surface already serves the whole task without extra lookup or duplication.

## Do
- Identify the **consumer** of each operational fact: players, facilitator, one role, everyone at the table, or a specific live procedure.
- Separate **access permission** from **runtime placement**. First decide whether characters can know the information; then decide where the permitted information should live for use.
- Use brief spoken orientation for information needed once, immediately, and synchronously; move facts that must be checked later to a persistent reference.
- Put stable spatial relationships on a map or diagram when repeated verbal reconstruction would be slower or less reliable.
- Put local hidden state, triggers, responses, and consequences in the facilitator-facing key or other surface used to adjudicate that location.
- Put frequently changing state on a live tracker, roster, clock, marker, or equivalent record when repeatedly editing static descriptive text would create stale or duplicated information.
- Keep global procedures in one shared reference when many locations or scenes consume the same rule; do not repeat the complete procedure in every key.
- Duplicate a fact only when the second placement removes a real retrieval failure and establish which copy is authoritative if the fact can change.
- Check the surface at the moment of use: information should be available early enough to support the decision it is meant to inform without exposing hidden state prematurely.

## Don't
- Treat read-aloud as storage for routes, deadlines, procedures, names, codes, or other facts players must remember and consult later when a persistent surface is available.
- Put mutable actor state into a static room key when the actor can leave, change condition, or respond elsewhere.
- Scatter one global rule across many keyed entries and require the facilitator to reconcile inconsistent copies.
- Place facilitator-only truth beside player-facing material when ordinary use makes accidental disclosure likely.
- Create a new handout, tracker, table, or map for information that is consulted once and already clear where it is.
- Solve poor prose or weak information access by multiplying surfaces that still contain the same badly organized material.

## Checklist
- Every important fact has a named consumer and a clear moment or cadence of use.
- Character access and runtime placement are decided separately.
- Information needed repeatedly remains available on a persistent surface rather than depending on memory of spoken text.
- Stable spatial state, local hidden state, mobile state, and shared procedures are stored on surfaces suited to their different update patterns.
- Hidden information is not exposed merely because another participant needs a convenient reference.
- Duplicated information has a justified retrieval benefit and one authoritative owner when it can change.
- Small adventures remain simple when one consolidated surface is genuinely sufficient.

## Notes
Adventure information is not consumed uniformly. Some facts orient everyone once, some must remain visible to players, some belong only to the facilitator, some are stable spatial relationships, and some change every few minutes of play. Choosing the runtime surface after deciding fictional access reduces memory load and stale duplication without turning every piece of information into a separate artifact.

This Pattern owns **where operational adventure information is stored and delivered once its legal access is known**. Information-access design owns how characters gain knowledge; map, key, roster, and live-state Patterns own the internal structure of those individual surfaces.
