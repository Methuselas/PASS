---
object_id: PAT_reuse_core_resolution_grammar_before_adding_new_mechanics
object_type: pattern
name: Reuse Core Resolution Grammar Before Adding New Mechanics
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
- architecture
- resolution
- refactoring
cross_links:
- rel: related_to
  target_object_id: PAT_evaluate_mechanics_by_the_decisions_and_agency_they_create
- rel: related_to
  target_object_id: PAT_use_the_defining_affordances_of_an_adopted_game_system
- rel: related_to
  target_object_id: PAT_build_complete_resolution_procedures_incrementally
- rel: related_to
  target_object_id: PAT_expand_resolution_detail_only_after_consequential_state_change
- rel: related_to
  target_object_id: PAT_factor_repeated_resolution_structures_into_shared_procedures_and_data
- rel: related_to
  target_object_id: PAT_keep_semantic_difficulty_labels_mechanically_consistent
reference:
  source_title: Designing TTRPGs For Dummies
  author: Martin Buinicki
confidence: high
references: []
variants: []
---

# Reuse Core Resolution Grammar Before Adding New Mechanics

## Pattern Rule
**IF** a new task, conflict, or gameplay domain asks a rules question similar to situations the game already resolves
**THEN** first express it through the established mechanical primitives and resolution vocabulary, extending or refactoring that grammar when recurring gaps appear and creating a separate subsystem only when the activity needs a different decision structure or experience
**ELSE** when the activity genuinely requires different play, define the subsystem and its interfaces deliberately rather than treating it as an isolated exception.

## Do
- Map the new situation onto existing inputs, uncertainty, consequences, and state changes before inventing a new procedure.
- Test whether a new domain can reuse the same recognizable resolution sentence with different inputs such as vehicle, ship, tool, environment, or other domain ratings.
- Before adding another die family, table family, or action subsystem, test whether the existing randomizer or result language can encode the needed distinction legibly.
- Ask whether the requirement poses a genuinely new rules question or merely a new fictional instance of a question the game already answers.
- Separate a change in entity detail or fictional context from a change in resolution logic; different data does not automatically require different rules.
- Prefer a reusable extension when one small addition broadens the current grammar across several related cases.
- Treat repeated adapters, exception chains, or bespoke conversions as evidence that the underlying grammar may need refactoring.
- Treat specialized subsystems as possible laboratories for general mechanics: when a local solution repeatedly transfers beyond its original domain, promote the reusable concept into shared grammar and remove duplicated infrastructure where that does not erase distinctive play.
- When a specialized subsystem is justified, define how play enters it, what decisions it adds, how it resolves, and how its results return to the rest of the game.
- Carry established grammar into downtime and extended tasks when the underlying uncertainty is the same; longer fictional duration alone does not justify a new mechanic.
- When time pressure changes an existing task, first express that pressure through established difficulty, assistance, scope, quality, risk, or consequence language before inventing a rushed-task subsystem.
- When a proposed replacement mainly translates information the current grammar already expresses, identify the decision, clarity, pacing, uncertainty profile, or other meaningful play benefit that the translation purchases before adopting it.
- After choosing or extending the grammar, treat dependency ordering and full trigger-to-termination procedure construction as a separate responsibility owned by **Build Complete Resolution Procedures Incrementally**.

## Don't
- Add a dedicated mechanic merely because the fiction presents a situation the first draft did not name explicitly.
- Preserve a weak core mechanic by surrounding it with patches that each solve only one new case.
- Force every activity through one generic check when doing so erases decisions or an experience the game is specifically built to support.
- Confuse broad mechanical coverage with enumerating a separate rule for every conceivable action.
- Create a bespoke rushed-task rule when the normal difficulty and consequence grammar already expresses the increased demand.
- Replace a familiar core resolution language merely to make the rules look more unified when the established grammar already answers the same question efficiently.
- Add a lookup or translation layer around a value the player already understands unless the new layer creates a meaningful difference in play.
- Assume that reusing the same dice, modifiers, or damage vocabulary automatically produces a complete working resolution procedure.
- Treat shared physical dice as proof of shared resolution grammar when the decisions, sequencing, interpretation, or output structure differ enough that learning one procedure does not teach the next.

## Checklist
- At least one unforeseen but ordinary situation can be resolved through the established grammar without a new rule.
- Recurring edge cases are handled by a reusable extension or refactor rather than an expanding exception list.
- Any separate subsystem names the distinctive decisions or experience that justify its additional procedure.
- The subsystem's inputs and outputs connect cleanly to the rest of the game.
- Removing a proposed bespoke rule does not leave a case the established grammar already resolves adequately.
- A pressured version of an ordinary task can be expressed through established difficulty or consequence language before a new time-specific procedure is considered.
- A proposed replacement has been compared against the current grammar on representative situations, including migration or relearning cost.
- Any added translation layer can name what meaningful play it creates beyond restating information the current grammar already communicates.
- A cross-domain extension preserves a recognizable decision-and-resolution sentence even when the inputs represent a different scale or actor type.
- Existing resolution primitives have been checked for inexpensive additional meaning before a new randomizer, lookup family, or action subsystem is introduced.

## Notes
Coherent mechanics achieve coverage through generalization: a small vocabulary can absorb many fictional situations while preserving recognizable play. Consistency does not require one mechanic for literally everything. A tactical subsystem, vehicle procedure, magic system, or other specialized structure may earn its place when it creates meaningful decisions that a generic resolution cannot preserve economically. The important move is to test the existing grammar first and treat repeated patches as a refactoring signal rather than normal growth.

A mature system may discover stronger general grammar inside a successful specialty. Once a local mechanic proves broadly reusable, generalize the concept and re-audit the originating subsystem for duplicated machinery. The criterion is recognizable decision structure, not identical dice. This Pattern owns the choice to apply, extend, refactor, or replace the game's resolution grammar; **Build Complete Resolution Procedures Incrementally** owns how selected mechanics are dependency-ordered into an executable action.
