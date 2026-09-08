---
object_id: PAT_prepare_scenario_toolboxes_instead_of_predicted_player_branches
object_type: pattern
name: Prepare Scenario Toolboxes Instead of Predicted Player Branches
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
- preparation
- agency
- situations
- improvisation
cross_links:
- rel: related_to
  target_object_id: PAT_generate_sandbox_situations_from_world_state_and_player_needs
- rel: related_to
  target_object_id: PAT_prepare_executable_adventure_outcome_states
- rel: related_to
  target_object_id: PAT_separate_mobile_actors_from_fixed_location_state
- rel: related_to
  target_object_id: PAT_structure_adventure_narratives_with_milestones_plot_beats_and_player_agency
reference:
  source_title: Don't Prep Plots - Tools, Not Contingencies
  author: Justin Alexander
confidence: high
references: []
variants: []
---

# Prepare Scenario Toolboxes Instead of Predicted Player Branches

## Pattern Rule
**IF** players can approach a prepared situation through tactics the designer cannot reliably predict
**THEN** prepare the actors, goals, resources, locations, procedures, information, constraints, and response capabilities needed to derive consequences from current state rather than writing branches for guessed player actions
**ELSE** use explicit sequences or contingencies only where the trigger and resulting process are genuinely fixed parts of the scenario.

## Do
- Prepare the parts of the situation that remain useful across many approaches: who is present, what they want, what they know, what they can access, what they can do, and what limits them.
- Record security, terrain, schedules, communications, assets, relationships, procedures, and other reusable facts that let the referee answer unexpected tactics causally.
- Spend preparation effort on information that is difficult to improvise consistently or that will affect several possible approaches.
- Let opposition responses emerge from goals, knowledge, resources, and current state instead of from a hidden list of author-predicted player moves.
- Keep likely scenes or developments brief and disposable when they are only possibilities; reuse their ingredients when the situation supports them and discard them when play moves elsewhere.
- Write explicit contingencies for truly automatic processes such as alarms, countdowns, programmed defenses, scheduled events, or state-triggered procedures when those processes exist independently of predicted player choice.
- Use prepared solutions, tactics, and examples as executable support rather than as requirements the players must discover or imitate.

## Don't
- Write a separate branch for every tactic you can imagine and mistake the resulting tree for player freedom.
- Protect prepared material by forcing players toward the branch for which you already wrote an answer.
- Give an NPC, faction, or security system a response it could not derive from its current knowledge, capabilities, and circumstances.
- Spend large amounts of prep on mutually exclusive future scenes whose only justification is that the players might choose them.
- Treat a likely sequence as established future history before player decisions and resolved state have made it true.

## Checklist
- The scenario can answer at least one plausible unplanned player approach from prepared state rather than a bespoke contingency.
- Important actors have goals, knowledge, resources, capabilities, and constraints sufficient to derive their responses.
- Frequently reused locations, systems, or procedures are described as tools rather than repeated inside multiple branches.
- Potential scenes can be omitted or rearranged without invalidating unrelated prepared material.
- Any hard-coded contingency corresponds to an actual automatic trigger or process in the fiction.
- Prepared examples and expected tactics do not become invisible requirements for success.

## Notes
Open-ended play creates a combinatorial problem only if preparation tries to predict player decisions. A reusable scenario toolbox replaces that prediction burden with state the referee can operate: people, places, motives, assets, rules, information, and constraints. The same hospital guards, floor plan, access procedures, and police response can answer disguise, stealth, bribery, deception, violence, or a plan the author never imagined. This differs from sandbox situation generation: the sandbox owner creates recurring pressures from world state, while this Pattern governs how any particular prepared situation is represented so it can survive unexpected tactics.
