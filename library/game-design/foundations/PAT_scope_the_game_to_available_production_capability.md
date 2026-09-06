---
object_id: PAT_scope_the_game_to_available_production_capability
object_type: pattern
name: Scope the Game to Available Production Capability
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
- production
- scope
- feasibility
- resources
cross_links:
- rel: related_to
  target_object_id: PAT_cover_required_production_functions_with_explicit_ownership
- rel: related_to
  target_object_id: PAT_define_completion_against_a_living_game_design_document
- rel: related_to
  target_object_id: PAT_account_for_the_intended_play_environment_before_freezing_the_design
reference:
  source_title: Designing TTRPGs For Dummies
  author: Martin Buinicki
confidence: high
references: []
variants: []
---

# Scope the Game to Available Production Capability

## Pattern Rule
**IF** the intended game artifact requires more writing, art, editing, layout, implementation, time, money, specialist skill, or other production capacity than the project can currently supply
**THEN** reduce or reshape the deliverable until its required production work fits available capability, or deliberately increase the resources needed to close the gap
**ELSE** keep the current scope stable until a real capability or requirement change justifies revisiting it.

## Do
- Define the version of the game artifact that can be responsibly produced with the money, time, skills, tools, and labor currently available.
- Trace major scope promises into the production work they require instead of estimating feasibility from page count or ambition alone.
- When physical components are mandatory, include sourcing, manufacturing or print-on-demand feasibility, packaging, shipping or distribution, replacement, and quality-control burden in the production capability required by the current scope.
- Prefer simpler substitute components when they preserve the intended play and materially reduce production or fulfillment burden.
- Let scope expand or contract when available resources, production methods, quality requirements, or delivery constraints materially change.
- Prefer a smaller coherent and usable game over an idealized version whose required creative or technical work cannot presently be completed to the intended standard.
- Distinguish a design feature that is valuable from a feature the current project can afford to finish; preserve deferred ideas without making them obligations of the current version.

## Don't
- Add artifact features whose required writing, art, layout, implementation, editing, or other work exceeds actual capability without deliberately changing scope or resources.
- Treat outsourcing, automation, or AI assistance as infinite capacity; include specification, review, correction, integration, and acceptance work in the production budget.
- Require a custom or difficult-to-source component merely because it is distinctive when its play value does not justify the production, price, fulfillment, and replacement burden it adds.
- Assume self-publishing requires a traditional bulk print run when digital distribution or print-on-demand can change inventory and fulfillment risk.
- Keep an impossible scope merely because every individual feature is desirable in isolation.
- Cut required core functionality to protect optional breadth; reduce optional content or presentation ambition before making the promised game inoperable.

## Checklist
- The current version's major deliverables can be mapped to available money, time, skills, tools, and labor.
- Production methods include their review, correction, integration, and handoff costs rather than only generation time.
- Mandatory components are practical to source or manufacture, package, deliver, and replace at the intended release scale, or the current scope provides a feasible substitute.
- Any known capability gap is closed by a deliberate resource change, scope change, quality change, or deferred deliverable.
- Required core play remains coherent after scope reductions.
- Deferred features are outside the current completion contract rather than silently remaining required work.

## Notes
Production feasibility is a scope decision, not a headcount rule. A solo creator with strong tools may responsibly ship work that once required several specialists, while a larger team can still over-scope a project if its promises exceed available time, integration capacity, or quality control. The test is whether the current artifact can actually be completed and integrated to its declared standard with the resources the project can command. Mandatory physical components belong in that budget because somebody must source or manufacture, package, distribute, and replace them; digital distribution and print-on-demand can materially change those constraints. Ownership answers who is responsible for required work; this decision answers how much work the current version can responsibly require.
