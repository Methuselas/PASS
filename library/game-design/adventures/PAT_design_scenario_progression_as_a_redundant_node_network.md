---
object_id: PAT_design_scenario_progression_as_a_redundant_node_network
object_type: pattern
name: Design Scenario Progression as a Redundant Node Network
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
- scenarios
- nodes
- clues
- topology
- agency
cross_links:
- rel: related_to
  target_object_id: PAT_keep_progress_critical_information_from_becoming_a_single_failure_point
- rel: related_to
  target_object_id: PAT_design_exploration_spaces_as_informed_route_networks
- rel: related_to
  target_object_id: PAT_use_in_world_information_as_a_scenario_interface
- rel: related_to
  target_object_id: PAT_make_preparation_change_problem_topology
- rel: related_to
  target_object_id: PAT_prepare_scenario_toolboxes_instead_of_predicted_player_branches
reference:
  source_title: Node-Based Scenario Design
  author: Justin Alexander
confidence: high
references: []
variants: []
---

# Design Scenario Progression as a Redundant Node Network

## Pattern Rule
**IF** players are meant to choose among several prepared locations, people, events, factions, or other scenario elements while pursuing an objective
**THEN** represent those elements as independently runnable nodes connected by multiple actionable leads so losing or rejecting one transition does not collapse access to the rest of the scenario
**ELSE** use a simpler ordered structure when controlling sequence is useful and meaningful choice does not depend on node navigation.

## Do
- Define nodes by playable content that can be entered from more than one prior state, not by one exact scene that must happen at one exact time.
- Seed the initial state with several actionable leads when players are supposed to choose where to investigate or act next.
- Let visited nodes expose more than one onward lead when the scenario needs continued routing flexibility.
- Use clues, relationships, communications, physical routes, schedules, resources, faction links, or other causal connections as edges between nodes.
- Allow dead ends, missed leads, and optional nodes once enough other connections remain to keep the larger network operable.
- Preserve node state when players approach it by an unexpected route; prior actions can change who is there, what they know, and what remains available without requiring a new branch tree.
- Use the network at whatever scale is useful: rooms, neighborhoods, witnesses, criminal fronts, planets, political blocs, or whole adventures can all function as nodes when their internal details are handled separately.
- Mix node networks with linear, branching, or milestone structures when one section benefits from player-directed order and another benefits from deliberate sequencing.

## Don't
- Make every transition a single mandatory arrow whose failure or rejection strands the adventure.
- Replace a linear plot with an exponentially expanding choose-your-own-adventure tree in which most prepared branches can never be used.
- Require players to visit every node merely because it was authored.
- Treat three cosmetically different clues that all depend on the same failure point as robust independent routing.
- Assume a node graph guarantees agency when the players cannot learn that alternate nodes exist or cannot meaningfully choose among them.

## Checklist
- The scenario's major nodes can be named independently of the exact order in which they will be visited.
- The starting state exposes multiple viable leads when node choice is intended.
- Important downstream nodes have redundant access rather than one fragile transition.
- At least some nodes can be skipped, delayed, or reached in different orders without invalidating the scenario.
- Edges correspond to information, access, relationships, or other causal links the players can actually use.
- The network does not require preparation of mutually exclusive future branches for every possible choice.
- Any deliberately mandatory sequence has a stated structural reason rather than being an accidental chokepoint.

## Notes
Scenario topology is not limited to physical maps. An investigation can connect witnesses, records, crime scenes, institutions, suspects, and events in the same way a dungeon connects rooms. Redundant node links turn missed clues and unexpected priorities from structural failures into ordinary route changes. This Pattern owns the graph-level organization of scenario content; progress-critical information still owns the reliability of an individual required conclusion, while informed route networks own physical navigational topology.
