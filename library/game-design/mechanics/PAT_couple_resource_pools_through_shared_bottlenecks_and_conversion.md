---
object_id: PAT_couple_resource_pools_through_shared_bottlenecks_and_conversion
object_type: pattern
name: Couple Resource Pools Through Shared Bottlenecks and Conversion
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
- resource-management
- logistics
- scarcity
- conversion
- planning
- decisions
cross_links:
- rel: related_to
  target_object_id: PAT_compress_resource_contents_without_erasing_resource_constraints
- rel: related_to
  target_object_id: PAT_budget_renewable_reserves_against_future_demands
reference:
  source_title: FrontierSpace Player's Handbook
  author: Bill Logan
confidence: high
references: []
variants: []
---

# Couple Resource Pools Through Shared Bottlenecks and Conversion

## Pattern Rule
**IF** several distinct resources compete inside the same planning horizon
**THEN** connect them through the shared bottlenecks, substitutions, conversions, and resupply constraints that make spending or recovering one resource change the options for another
**ELSE** keep the pools independent when no meaningful shared constraint or exchange exists.

## Do
- Identify shared bottlenecks such as time, labor, cargo capacity, mobility, money, access, exposure, maintenance bandwidth, or future risk.
- Preserve separate resource identities when their depletion changes capabilities or consequences differently, then make those pools compete through the bottleneck that actually connects them.
- Preserve substitution when one physical stock can answer more than one need and choosing one use necessarily reduces another.
- Define conversion rules when players can transform one resource into another, including the time, loss, access, tooling, specialist help, or risk that prevents conversion from erasing scarcity.
- Make recovery and resupply consume meaningful route, time, money, access, exposure, scavenging effort, specialist capacity, or other planning resources when logistics are intended to matter.
- Test the coupled system under pressure where at least two needs compete before the shared bottleneck refreshes or expands.
- Let the fiction determine which exchanges are possible instead of forcing every pool into a universal market.

## Don't
- Track several resources as isolated meters when the intended planning problem depends on them competing for the same capacity or effort.
- Merge resources merely because they share a bottleneck when their depletion produces different capabilities, risks, or recovery needs.
- Add free or lossless conversion that makes nominally separate scarcity interchangeable in every important situation unless that fungibility is intentional.
- Treat resupply as an automatic meter reset when the intended play depends on logistics, route choice, exposure, or specialist support.
- Invent cross-resource interactions that the fiction and expected decisions do not support merely to make the economy appear interconnected.

## Checklist
- Every coupled pair shares a named bottleneck, substitution path, conversion path, or recovery constraint.
- At least one representative situation forces two resource needs to compete before the shared constraint resets.
- Separate pools remain separate because their depletion changes behavior differently.
- Any substitution or conversion has an explicit opportunity cost or constraint unless free exchange is an intentional property of the setting.
- Recovery or resupply changes at least one route, timing, access, money, exposure, labor, or specialist decision when logistics are meant to matter.
- Removing the coupling would remove a planning tradeoff rather than merely reduce bookkeeping.

## Notes
Several resource pools do not become strategically interesting simply by existing beside one another. Interaction emerges when they compete for something players cannot maximize simultaneously: cargo space, repair time, money, specialist labor, safe access, movement, or exposure. A fuel shortage and a medical shortage can remain mechanically distinct while still competing for the same cargo capacity or detour time. Likewise, one stock can support several uses without becoming a universal supply meter when choosing one use forecloses another. This Pattern owns **how distinct resources interact**; `PAT_compress_resource_contents_without_erasing_resource_constraints` owns how much internal detail each pool needs to retain.
