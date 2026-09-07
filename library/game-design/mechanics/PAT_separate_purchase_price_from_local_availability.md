---
object_id: PAT_separate_purchase_price_from_local_availability
object_type: pattern
name: Separate Purchase Price from Local Availability
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
- economy
- availability
- scarcity
- access
- settlements
cross_links:
- rel: related_to
  target_object_id: PAT_couple_resource_pools_through_shared_bottlenecks_and_conversion
- rel: related_to
  target_object_id: PAT_spend_worldbuilding_detail_where_it_changes_play
- rel: related_to
  target_object_id: PAT_use_time_to_structure_opportunity
reference:
  source_title: Warhammer Fantasy Roleplay, First Edition
  author: Richard Halliwell, Rick Priestley, Graeme Davis, Jim Bambra, and Phil Gallagher
confidence: high
references: []
variants: []
---

# Separate Purchase Price from Local Availability

## Pattern Rule
**IF** local scarcity, settlement scale, supplier access, or regional supply is supposed to matter to acquisition
**THEN** model ability to pay and ability to obtain as separate constraints, and require a meaningful change in time, place, supplier, relationship, or circumstances before retrying failed access
**ELSE** let price alone resolve ordinary purchases when local supply is not part of the intended decision space.

## Do
- Let price answer whether the buyer can afford the good while availability answers whether the current market can supply it.
- Tie availability to causal local conditions such as settlement size, specialist presence, trade routes, legal status, season, or regional production when those factors matter.
- After a failed availability check, require elapsed time, travel, a new supplier, improved access, or another changed condition before repeating the same search.
- Once a routine commodity is established as locally available, avoid rerolling every identical purchase unless stock, quantity, or conditions materially change.
- Override generic rarity procedures when established local facts make the result nonsensical; a production center should not randomly lack its defining ordinary tools without a specific shortage.
- Track quantity only when buying enough to exhaust local stock would change play.
- Let item quality, condition, legality, or another causal property deliberately modify both price and availability when it truly affects both axes; separation does not require independence.
- When selling, let a changed asking price alter how easy a buyer is to find if willingness to pay is part of the local access problem.

## Don't
- Treat wealth as automatic access when the setting intends distance, scarcity, law, or specialist supply to constrain acquisition.
- Allow repeated immediate availability rolls until one succeeds; that converts scarcity into meaningless dice fishing.
- Make generic rarity tables override obvious local production or established world state.
- Track individual stock for every common purchase when quantity cannot affect later decisions.
- Collapse price and availability into one rarity number merely because some modifiers happen to change both at once.

## Checklist
- A character can be able to afford an item yet still have a meaningful acquisition problem when local scarcity is intended.
- Failed access cannot be retried unchanged until some relevant condition changes.
- Local world facts can supersede a generic rarity result when they clearly establish supply.
- Repeated routine purchases do not trigger redundant checks once availability is established.
- Quantity tracking activates only when local stock or depletion changes a decision.
- A modifier that affects both cost and scarcity changes each axis explicitly rather than replacing the two-axis model.

## Notes
Price and access answer different questions. Separating them keeps wealth from collapsing geography, local economy, specialist networks, and scarcity into one number. The useful procedure is not constant shopping friction; it is a gate that matters when supply itself creates route, timing, relationship, or planning choices. Once the market fact is known, repeated checks should disappear until the situation changes. The axes can still interact: superior craftsmanship may legitimately cost more and be harder to source, while a lower asking price may make a buyer easier to find. The design benefit comes from preserving the distinction even when one causal property moves both values.
