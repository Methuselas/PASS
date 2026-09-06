---
object_id: PAT_align_repeated_and_rewarded_behavior_with_intended_outcomes
object_type: pattern
name: Align Repeated and Rewarded Behavior with Intended Outcomes
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
- player-behavior
- rewards
- outcomes
- practice
cross_links:
- rel: related_to
  target_object_id: PAT_evaluate_mechanics_by_the_decisions_and_agency_they_create
- rel: related_to
  target_object_id: PAT_balance_character_roles_by_consequential_contribution
- rel: related_to
  target_object_id: PAT_calibrate_encounters_to_their_purpose_challenge_and_response_space
- rel: related_to
  target_object_id: PAT_project_reward_currency_mix_across_role_advancement
- rel: related_to
  target_object_id: PAT_test_recovery_loops_for_repeatable_reset_incentives
reference:
  source_title: Designing TTRPGs For Dummies
  author: Martin Buinicki
confidence: high
references: []
variants: []
---

# Align Repeated and Rewarded Behavior with Intended Outcomes

## Pattern Rule
**IF** a game or subsystem uses repeatable rewards, advancement triggers, treasure, status, or other incentives
**THEN** make the rewarded actions reinforce the behavior and priorities the game intends players to repeat
**ELSE** when rewards are meant to be behaviorally neutral, verify that their triggers do not quietly redirect play toward a different priority.

## Do
- Inspect what earns experience, development points, advancement checks, wealth, status, or other rewards, because repeatable rewards create strong incentives.
- At encounter scale, compare rewards for fighting, bypassing, negotiating, rescuing, discovering, mapping, surviving, completing objectives, or other supported approaches. Reward placement should both fit the fiction and reinforce the behaviors the game wants players to repeat.
- Distinguish the reward economy from the development economy: what earns growth and what that growth can buy are separate design decisions.

## Don't
- Reward shortcuts, farming behaviors, or dominant routines that contradict the activity the game is supposed to value.
- Assume a reward is behaviorally neutral merely because it is traditional for the genre.
- Put the strongest repeatable rewards behind combat by default when the intended play also values avoidance, negotiation, exploration, rescue, investigation, or other approaches.

## Checklist
- Reward triggers have been compared against the actions the game wants players to repeat.
- Encounter rewards have been checked against the response space the adventure actually supports, and their fictional placement makes sense.
- Obvious farming or optimization strategies do not produce a stronger incentive than the intended play.

## Notes
Players learn a game's priorities from what the system rewards. A reward structure can therefore reshape play even when the rulebook describes broader goals. Advancement currency also has two jobs that should not be conflated: the game decides how growth is earned, then separately decides how players may direct that growth. At encounter scale, treasure, information, advancement, useful items, relationships, and other rewards teach players which approaches are worth repeating. A game that says negotiation and exploration matter but pays reliably only for defeated enemies creates a different behavioral loop from the one its prose describes. Asymmetric currency conversion is owned by `PAT_project_reward_currency_mix_across_role_advancement`; repeatable healing/recharge incentives are owned by `PAT_test_recovery_loops_for_repeatable_reset_incentives`; applied training alignment is owned by `PAT_match_practiced_behavior_to_the_intended_outcome`. This Pattern owns only **which behavior the reward trigger reinforces**.
