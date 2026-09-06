---
object_id: AP_define_a_game_foundation_and_scope
object_type: ap
name: Define a Game Foundation and Scope
library_path:
- game-design
- foundations
stage_binding: 0 design
lane_fit: both
foundation_role: foundation
routing_class: general
specialization_axis: none
foundation_object_id: none
tags:
- foundations
- scope
- audience
- production
- architecture
cross_links:
- rel: supports
  target_object_id: PAT_define_the_intended_player_before_designing_for_them
- rel: supports
  target_object_id: PAT_describe_the_game_by_player_fantasy_and_recurring_play
- rel: supports
  target_object_id: PAT_translate_genre_into_play_requirements
- rel: supports
  target_object_id: PAT_integrate_genre_blends_instead_of_merely_stacking_them
- rel: supports
  target_object_id: PAT_choose_a_game_foundation_by_the_experience_it_must_support
- rel: supports
  target_object_id: PAT_use_the_defining_affordances_of_an_adopted_game_system
- rel: supports
  target_object_id: PAT_account_for_the_intended_play_environment_before_freezing_the_design
- rel: supports
  target_object_id: PAT_scope_the_game_to_available_production_capability
- rel: supports
  target_object_id: PAT_cover_required_production_functions_with_explicit_ownership
- rel: supports
  target_object_id: PAT_keep_game_design_specification_living_and_dependency_aware
- rel: supports
  target_object_id: PAT_keep_common_path_procedures_inside_the_declared_playable_core
- rel: supports
  target_object_id: PAT_treat_optional_modules_as_removable_dependency_sets
- rel: supports
  target_object_id: PAT_define_completion_against_a_living_game_design_document
confidence: high
references: []
variants: []
---

# Define a Game Foundation and Scope

## Objective
Turn a game idea into a bounded current-version design foundation: identify who the game serves, what recurring play it promises, which genre and system assumptions carry that promise, which environments and production capabilities constrain it, what belongs in the playable core, and what conditions will count as design-complete for this version.

## Steps / Flow
1. **Enter with a game idea, not a frozen rules architecture.** The entry state may be a premise, desired fantasy, genre, inherited engine, or product concept, but no later implementation decision is trusted until the intended user and recurring experience are explicit.
2. **Define the intended user.** Use **Define the Intended Player Before Designing for Them** to state the audience assumptions that actually constrain complexity, prior knowledge, communication, and sustained play burden. If the audience is still broad or uncertain, keep hidden assumptions minimal and mark them for later testing rather than pretending a precise audience already exists.
3. **State the recurring player promise.** Use **Describe the Game by Player Fantasy and Recurring Play** to describe what players are expected to be, do repeatedly, and care about. Treat this as the invariant later foundation choices must preserve.
4. **Translate genre only when genre is part of the promise.** If the game adopts a recognizable genre or subgenre, use **Translate Genre into Play Requirements** to convert the label into required behaviors, capabilities, pressures, stakes, and assumptions. If the game deliberately combines genres, also use **Integrate Genre Blends Instead of Merely Stacking Them** so the blend has one coherent play contract instead of several unrelated trope lists. If no genre label carries a promise, skip this branch.
5. **Choose the rules foundation from the experience.** Use **Choose a Game Foundation by the Experience It Must Support** to test existing engines, frameworks, or structures before creating a new one. If an adopted system remains the foundation, use **Use the Defining Affordances of an Adopted Game System** to preserve the capabilities that made adoption useful instead of replacing them piecemeal with familiar but incompatible habits. If no existing foundation fits cleanly, record the specific mismatch that justifies new architecture and carry its added validation burden forward.
6. **Check the intended operating environment before freezing mechanics.** Use **Account for the Intended Play Environment Before Freezing the Design** to test controls, physical or digital components, space, information flow, remote/local assumptions, and platform conventions against the proposed foundation. If an environment is outside the real requirements, do not distort the core to support it hypothetically.
7. **Gate scope against actual production capacity.** Use **Scope the Game to Available Production Capability** to map the promised artifact to the writing, art, editing, implementation, component, time, money, tooling, and specialist capacity available. If the scope exceeds capacity, branch back to the player promise and reduce or reshape the deliverable, or deliberately increase resources; do not continue with an impossible current-version contract.
8. **Assign production ownership only after the required artifact is known.** Use **Cover Required Production Functions with Explicit Ownership** to identify the creative and technical functions the scoped artifact actually needs, assign capable ownership, and define handoff/acceptance conditions where work crosses roles. A smaller scope may remove functions; do not preserve a staffing structure after its work disappears.
9. **Externalize the current accepted design.** Use **Keep the Current Game Design Specification Living** to record the intended player, recurring play, chosen foundation, current scope, important interfaces, and other fundamentals in a recoverable specification. This record follows accepted design changes; it does not outrank evidence or accumulate every future idea.
10. **Define the actual base configuration.** If the product is presented as a complete playable core, use **Keep Common-Path Procedures Inside the Declared Playable Core** so ordinary resolution does not depend on undisclosed external material. If subsystems are labeled optional, use **Treat Optional Modules as Removable Dependency Sets** and verify that removing them leaves the defined base game executable. If an allegedly optional module proves required, either move it into the base configuration or change the base promise before advancing.
11. **Define the stopping gate for this version.** Use **Define Design Completion Against Current-Version Fundamentals** to name the fundamentals the current scope requires and give each a concrete completion condition. Keep release readiness separate: the design can become complete before editing, packaging, publication, or other downstream release gates are satisfied.
12. **Close only when the foundation is internally consistent.** Completion requires a named intended player, a recurring play promise, a foundation justified by that promise, a supported play environment, a production-feasible current scope with owned functions, an honest base/optional boundary, a recoverable current specification, and explicit current-version completion conditions. If any of these disagree, return to the earliest owner whose decision changed and re-run the dependent steps instead of patching the contradiction downstream.

## Notes
This protocol defines the current game's centerline and boundary; it does not design every subsystem. The order matters because later choices consume earlier ones: production scope is meaningless before the promised artifact exists, an engine cannot be judged without the intended experience, and completion cannot be defined until current-version fundamentals are known. Genre, adopted-system, and optional-module branches are conditional. Do not force them into games that do not need them.
