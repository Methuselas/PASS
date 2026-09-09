---
object_id: PAT_plan_town_distribution_from_settlement_support_and_regional_density
object_type: pattern
name: Plan Settlement Distribution From Support, Access, and Regional Density
library_path:
- art
- cartography
stage_binding: 0 design
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: domain
foundation_object_id: none
tags:
- cartography
- settlements
- towns
- cities
- placement
- density
- worldbuilding
cross_links: []
confidence: high
references: []
variants:
- variant_id: VAR_major_city_siting_emphasize_trade_water_and_ports
  variant_name: Major City Siting Emphasizes Trade, Water, and Ports
  variant_basis: context
  difference_from_foundation: For a major city, weight major trade routes, large rivers, ports or coasts, and substantial water access more heavily than for an ordinary town.
  when_to_use: Use when placing a large or prosperous city whose scale implies stronger transport and water relationships.
  when_not_to_use: Do not force the emphasis when the fictional setting supplies another credible mechanism for an unusual city location.
  absorbed_from_object_id: none
---

# Plan Settlement Distribution From Support, Access, and Regional Density

## Pattern Rule
**IF** a regional map needs towns or cities placed before their pictorial icons are committed
**THEN** keep settlement sites light and revisable, relate them intentionally to support, transport, or explicit setting logic, then judge the collective density and distribution for what it communicates about the region before committing the final symbols

## Do
- Use light markers first so settlement sites can move cheaply.
- Consider rivers, coasts, farmland, pasture, resources, roads, trade access, or another setting-specific support relationship when choosing sites.
- Judge many settlements together rather than approving each one in isolation.
- Use settlement density deliberately: a dense pattern can imply a flourishing or heavily settled region, while sparse settlement can imply a diminishing population or less exploited territory.
- Allow fictional setting logic to override ordinary site expectations when the map makes that reason coherent.

## Don't
- Do not commit detailed settlement icons before the distribution works.
- Do not require every settlement to sit beside the same resource.
- Do not treat one settlement-density pattern as universally correct.
- Do not place settlements randomly unless randomness itself fits the intended society or map logic.
- Do not let an unusual fantasy site become an excuse for a distribution with no intentional rationale.

## Checklist
- Settlement sites remain easy to revise until the distribution is judged as a whole.
- Each important site has intentional support, access, or setting logic.
- The collective density communicates the intended regional character.
- The distribution still reads coherently when the detailed settlement artwork is ignored.
- Unusual placements are supported by the fictional setting rather than accidental.

## Notes
This owner covers the placement decision for both towns and cities. The variant `VAR_major_city_siting_emphasize_trade_water_and_ports` strengthens the siting emphasis for major cities: favor major trade routes, large rivers, ports or coasts, and substantial water access when the city scale makes those relationships important, while preserving explicit setting-supported exceptions.
