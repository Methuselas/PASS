---
object_id: PAT_constrain_random_consequences_by_causal_fit
object_type: pattern
name: Constrain Random Consequences by Causal Fit
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
- randomness
- consequences
- causality
- tables
cross_links:
- rel: related_to
  target_object_id: PAT_choose_a_randomizer_by_the_uncertainty_profile_it_must_produce
- rel: related_to
  target_object_id: PAT_add_resolution_factors_only_when_they_expose_actionable_causes
- rel: related_to
  target_object_id: PAT_preserve_stable_challenge_conditions_against_reactive_difficulty_protection
reference:
  source_title: Warhammer Fantasy Roleplay, Third Edition
  author: Jay Little with Daniel Lovat Clark, Michael Hurley, and Tim Uren
confidence: high
references: []
variants: []
---

# Constrain Random Consequences by Causal Fit

## Pattern Rule
**IF** a random procedure selects among differentiated consequences whose plausibility depends on what caused the consequence
**THEN** restrict eligible results by the triggering cause before accepting the random outcome so randomness chooses among causally valid states instead of replacing causality
**ELSE** use an unrestricted result set when every listed consequence is valid for every trigger that can invoke it.

## Do
- Tag or partition consequence entries by the kinds of events that can reasonably produce them, such as trauma, violence, supernatural exposure, equipment stress, environmental hazard, or another causal domain.
- Let one trigger match several tags and one result carry several tags when causal categories genuinely overlap.
- State the mismatch procedure in advance: redraw, draw until a match, treat the draw as no consequence, or use another explicit rule appropriate to the randomizer.
- Keep **type** and **severity** separable when the cause determines what kind of consequence is plausible while another input determines how severe it is.
- Build the eligible set before resolution when practical; when a physical deck or similar device makes rejection sampling cheaper, make that filtering rule part of the procedure rather than an improvised veto.
- Preserve enough causal information after resolution that the resulting state can be explained and used consistently in later play.

## Don't
- Force an unrelated injury, disorder, malfunction, or complication into the fiction solely because a table or card produced it.
- Let the facilitator reject inconvenient results after the roll without a declared causal filter; that turns a random procedure into hidden fiat.
- Make every result carry every tag, which preserves the appearance of filtering while eliminating its function.
- Confuse causal fit with favorable outcome selection; a consequence can be severe and still be the correct member of the eligible set.
- Add detailed causal categories that never change which results can occur.

## Checklist
- Each differentiated consequence can name at least one triggering domain under which it is eligible.
- A trigger that should not plausibly produce a particular result actually excludes that result under the written procedure.
- The handling of an incompatible draw or roll is explicit and repeatable.
- Severity and consequence type are not accidentally coupled when the design needs them to vary independently.
- The filter changes at least one real outcome set rather than serving as descriptive tagging only.
- The procedure constrains randomness before or during selection rather than relying on post hoc narrative repair.

## Notes
Randomness is useful for selecting among uncertain consequences, but an unrestricted table can produce states that sever the link between event and aftermath. A causal filter preserves surprise while keeping the result attributable to what happened. The same structure can support trauma, injuries, corruption, magical backlash, equipment faults, social fallout, environmental damage, or any other result family in which several outcomes are possible but not all are plausible under every cause.
