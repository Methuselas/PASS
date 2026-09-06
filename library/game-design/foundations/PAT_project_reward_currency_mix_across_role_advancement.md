---
object_id: PAT_project_reward_currency_mix_across_role_advancement
object_type: pattern
name: Project Reward Currency Mix Across Role Advancement
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
- rewards
- advancement
- balance
- currencies
- campaign-economy
cross_links:
- rel: related_to
  target_object_id: PAT_align_repeated_and_rewarded_behavior_with_intended_outcomes
- rel: related_to
  target_object_id: PAT_balance_character_roles_by_consequential_contribution
- rel: related_to
  target_object_id: PAT_audit_character_economy_exchange_rates_across_creation_and_advancement
reference:
  source_title: Designing TTRPGs For Dummies
  author: Martin Buinicki
confidence: high
references: []
variants: []
---

# Project Reward Currency Mix Across Role Advancement

## Pattern Rule
**IF** a campaign awards multiple nonfungible or differently convertible currencies that different roles use to gain persistent capability
**THEN** project representative roles through the expected reward mix and make unequal long-term growth an intentional property rather than an unnoticed conversion advantage
**ELSE** use the ordinary advancement-economy checks when one currency or one equivalent conversion path governs persistent growth.

## Do
- List each recurring reward currency, including experience, money, downtime, training access, reputation, favors, salvage, licenses, or other advancement-relevant assets.
- Record which capability classes each role can purchase with each currency and which currencies are gated, lossy, vulnerable to confiscation, or unusable without additional access.
- Estimate the campaign's expected mix and cadence of those rewards rather than comparing one award in isolation.
- Project at least two materially different roles through the same representative reward sequence and compare the durable capability each can actually buy.
- Distinguish a deliberate economic identity—such as a gear-dependent role advancing mainly through money—from accidental advantage caused by one currency being easier to earn, preserve, or convert.
- Include mixed-cost capabilities whose acquisition requires more than one currency or a currency plus permission, time, or fictional access.
- Re-test the projection when scenario structure changes the reward mix, because a combat-heavy, exploration-heavy, or institution-heavy campaign can alter which role economy is favored.

## Don't
- Assume equal nominal awards create equal advancement when roles spend them through different economies.
- Compare only listed prices while ignoring how often the relevant currency enters play.
- Treat money, experience, downtime, reputation, or access as fungible when the rules do not allow players to exchange them freely.
- Ignore loss exposure, upkeep, gates, or conversion prerequisites that make one currency less durable than another.
- Flatten intentional role economies into one universal currency merely to make projections numerically equal.

## Checklist
- Every advancement-relevant reward currency has an expected campaign cadence or mix.
- At least two different roles have been projected through the same reward sequence.
- Durable capability gained from that sequence has been compared rather than only nominal currency totals.
- Currency-specific gates, losses, and conversion prerequisites are included in the projection.
- Any persistent divergence in role growth is identified as intentional, compensated elsewhere, or repaired.
- A changed campaign reward mix has been tested for whether it changes which roles advance fastest.

## Notes
Reward balance is not determined by the face value of an award when characters convert rewards through different economies. One role may turn money directly into equipment, another may depend on experience, another on downtime and training access, and another on a gated mixture. The campaign's **reward mix** therefore becomes a balance variable: identical sessions can yield unequal durable growth because the awarded currencies have different conversion routes, loss exposure, and role-specific utility. This Pattern owns the campaign-level projection of reward currencies into role growth. It does not decide what actions should earn those rewards; `PAT_align_repeated_and_rewarded_behavior_with_intended_outcomes` owns that incentive question.
