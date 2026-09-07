---
object_id: PAT_scale_voluntary_output_with_escalating_current_risk
object_type: pattern
name: Scale Voluntary Output with Escalating Current Risk
library_path:
- game-design
- characters
stage_binding: 0 design
lane_fit: both
foundation_role: foundation
routing_class: general
specialization_axis: none
foundation_object_id: none
tags:
- characters
- risk
- escalation
- tradeoffs
cross_links:
- rel: related_to
  target_object_id: PAT_attach_persistent_costs_to_capability_gains
- rel: related_to
  target_object_id: PAT_price_character_options_by_mechanical_leverage_and_constraint
reference:
  source_title: Cyberpunk 2020 (2.0.2.0 Version)
  author: Mike Pondsmith and R. Talsorian Games contributors
confidence: high
references: []
variants: []
---

# Scale Voluntary Output with Escalating Current Risk

## Pattern Rule
**IF** a capability is meant to let players choose how hard to push it in the current situation
**THEN** make greater immediate output purchase correspondingly greater current fatigue, backlash, exposure, instability, depletion, or another consequence the player knowingly accepts
**ELSE** use a fixed operating cost when variable output would not create a meaningful decision.

## Do
- Give the player a legible choice among output levels rather than hiding escalation inside facilitator judgment.
- Make the added cost increase with leverage strongly enough that the highest output is not the automatic default whenever the capability is available.
- Use costs that matter in the current situation or in reliably connected future state: fatigue, heat, instability, evidence, depletion, injury risk, detection, or another live pressure.
- Test several output levels to see whether the middle choices remain useful rather than collapsing into minimum-safe and maximum-output extremes.
- For count-based pushing such as extra dice, actions, charges, targets, or similar units, calculate both the success curve and the backlash curve at each selectable setting; the tradeoff is only real when greater leverage changes both in ways the player can rationally compare.
- Let context change the attractive output level; a risk that is tolerable in one scene should become expensive when reserves, exposure, or recovery capacity are already strained.
- Keep the fiction and mechanics aligned so players can understand what pushing harder means before committing to it.

## Don't
- Charge a flat surcharge for every output level and call the result escalating risk.
- Make the highest setting so efficient that lower settings exist only as trap choices.
- Hide the consequence until after commitment when the intended play is informed risk-taking.
- Use a nominal risk that ordinary recovery or abundant resources erase before it can affect any later decision.

## Checklist
- The player can identify at least two materially different output/risk choices before acting.
- Greater leverage creates greater current or reliably connected future exposure rather than a cosmetic cost increase.
- At least one intermediate output level is rational in a representative situation.
- When escalation is count-based, representative settings have been checked for both success probability and adverse-outcome probability rather than only for average output.
- The risk changes with current state enough that the same output choice is not automatically correct in every scene.
- Players can understand the consequence they are accepting well enough to treat escalation as a decision rather than a surprise tax.

## Notes
A capability can remain dangerous after acquisition when its strongest use is available but not free. Voluntary escalation turns danger into agency: the player chooses whether the present need justifies more fatigue, exposure, instability, depletion, or another consequence. The useful pressure comes from the slope between output and risk, not from merely attaching a recurring fee. If the top setting dominates regardless of context, the design has converted a supposed tradeoff into a routine operating mode.
