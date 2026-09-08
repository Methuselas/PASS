---
object_id: PAT_encode_stable_spatial_state_on_the_map
object_type: pattern
name: Encode Stable Spatial State on the Map
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
- maps
- cartography
- referee-interface
- spatial-state
- retrieval
cross_links:
- rel: related_to
  target_object_id: PAT_write_keyed_locations_as_executable_local_state
- rel: related_to
  target_object_id: PAT_match_information_precision_to_decision_precision
- rel: related_to
  target_object_id: PAT_externalize_live_rules_state_at_the_point_of_use
- rel: related_to
  target_object_id: PAT_design_exploration_spaces_as_informed_route_networks
reference:
  source_title: Better Dungeon Maps
  author: Justin Alexander
confidence: high
references: []
variants: []
---

# Encode Stable Spatial State on the Map

## Pattern Rule
**IF** a map is repeatedly consulted to adjudicate movement, visibility, access, proximity, elevation, or other spatial consequences
**THEN** encode stable decision-relevant spatial facts directly on the map with consistent notation and reserve the key or live tracker for conditional, changing, or nonspatial state
**ELSE** keep the map simpler when those facts do not affect decisions or can be retrieved more cheaply elsewhere.

## Do
- Show the scale and orientation needed by the movement and range rules that will actually be used.
- Make traversable connections legible: doors, passages, openings, blocked routes, stairs, ladders, pits, shafts, bridges, portals, and off-map connections should communicate where they lead when that matters.
- Encode vertical direction, destination, elevation, ceiling height, or depth when those dimensions change movement, visibility, tactics, or access.
- Use a small consistent symbol vocabulary and provide a legend when the notation is not self-evident.
- Put stable room or area identifiers, concise names, or other local labels on the referee map when they reduce repeated key lookup without overwhelming the drawing.
- Use visual distinctions for stable terrain or construction categories when those distinctions repeatedly change play.
- Keep concealed information on the referee-facing map or an overlay and remove it from player-facing versions unless the characters have learned it.
- Let the key explain special conditions and exceptions rather than repeating ordinary geometry that the map already communicates clearly.

## Don't
- Leave the referee to reconstruct basic connections, destinations, elevations, or distances from prose every time the map is used.
- Put so much textual or symbolic detail on the map that routes and spatial relationships become harder to read.
- Encode rapidly changing actor positions, alarms, casualties, or other live state as if they were permanent map features when a tracker or roster is easier to update.
- Use the same symbol for materially different spatial states without a clear disambiguator.
- Expose secret doors, hidden hazards, concealed routes, or other referee-only state on a player map before discovery.
- Add exact dimensions, labels, or decorative notation that the rules and decisions never consume.

## Checklist
- A referee can trace every ordinary legal route and determine where vertical or off-map connections lead.
- Scale and orientation are stated at the precision the rules require.
- Stable spatial facts that are repeatedly needed do not require unnecessary page flipping.
- Symbols and visual distinctions are consistent and legible at the map's intended size.
- Hidden information is separated appropriately between referee and player views.
- Conditional or changing state remains easy to update without redrawing the base map.
- Map and key agree on identifiers, connections, and mechanically meaningful dimensions.

## Notes
A play map is a spatial rules surface, not merely an illustration. Stable geometry is often cheaper to understand visually than through repeated prose: one marked stair can communicate direction and destination faster than several keyed reminders, while one room label can prevent multiple lookups when nearby activity matters. The useful boundary is stability. Put persistent spatial truth where the eye already looks for space; keep changing actors and conditional events on surfaces designed to change.
