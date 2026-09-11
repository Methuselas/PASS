---
object_id: PAT_match_adventure_rewards_to_meaningful_risk
object_type: pattern
name: Match Adventure Rewards to Meaningful Risk
library_path:
- game-design
- adventures
stage_binding: 0 design
lane_fit: both
foundation_role: foundation
routing_class: general
specialization_axis: none
foundation_object_id: none
tags:
- adventures
- risk
- rewards
- stakes
- agency
cross_links:
- rel: related_to
  target_object_id: PAT_calibrate_encounters_to_their_purpose_challenge_and_response_space
- rel: related_to
  target_object_id: PAT_give_high_consequence_risks_a_learnable_information_basis
- rel: related_to
  target_object_id: PAT_align_repeated_and_rewarded_behavior_with_intended_outcomes
- rel: related_to
  target_object_id: PAT_match_the_cost_of_failure_to_the_players_prior_investment
- rel: related_to
  target_object_id: PAT_shape_adventure_challenge_progression_deliberately
reference:
  source_title: "How to Write Adventure Modules That Don't Suck!"
  author: Jim Wampler
confidence: high
references: []
variants:
- variant_id: game_design_variant_offer_tempting_player_activated_risks
  variant_name: Offer Tempting Player-Activated Risks
  variant_basis: context
  difference_from_foundation: Present an optional deal, artifact, shortcut, control, resource opportunity, or other attractive upside whose meaningful downside is activated by the players' decision to pursue or push it, so risk becomes a chosen tradeoff rather than only imposed pressure.
  when_to_use: An encounter should tempt players to trade safety, time, resources, exposure, or another live cost for an unusually valuable payoff and declining the temptation still leaves valid play.
  when_not_to_use: The downside is effectively unknowable before commitment, refusal blocks required progress, or the payoff is so dominant that accepting the risk ceases to be a meaningful choice.
  absorbed_from_object_id: none
---

# Match Adventure Rewards to Meaningful Risk

## Pattern Rule
**IF** an adventure presents a challenge or opportunity with a materially greater chance or cost of failure than surrounding play
**THEN** give successful engagement a commensurately stronger payoff and preserve a viable route by which informed, skillful, or resourceful play can earn it
**ELSE** do not enlarge rewards merely because a low-risk situation happened to resolve badly.

## Do
- Evaluate the **prospective** risk before resolution: severity, likelihood, threatened resources, reversibility, retreat options, available information, and prior player investment can all change what the same nominal danger costs.
- Scale payoff in forms that matter to the current game, such as objective progress, treasure, access, information, leverage, advancement, persistent assets, strategic position, or a memorable change in the situation.
- Preserve a credible success path. A scenario whose catastrophic outcome is effectively assured is not a high-risk bargain; it is a foregone conclusion.
- Make severe risks learnable enough for the intended decision. Players can knowingly accept danger, prepare against it, retreat from it, or decline it only when the game exposes an appropriate information basis.
- Let clever preparation or strong execution reduce the realized danger without retroactively shrinking a reward that was earned by mastering the underlying challenge.
- Use extreme risk selectively. Contrast between ordinary pressure and dangerous peaks gives the high-risk opportunity meaning that constant maximum intensity cannot.

## Don't
- Put campaign-scale loss, near-certain death, or severe irreversible cost behind a payoff that is trivial relative to the threatened state when the choice is supposed to be attractive.
- Call guaranteed destruction "risk" merely because the numbers are high.
- Hide the existence of a severe downside when the intended play is informed risk-taking rather than surprise punishment.
- Increase reward only after seeing that the players suffered unusually bad luck; calibrate the opportunity rather than paying for pain after the fact.
- Make the highest-risk option automatically correct by attaching an upside so dominant that safer approaches become fake choices.

## Checklist
- The high-risk opportunity has a payoff players can identify as materially valuable in the current game.
- The danger includes a viable success, mitigation, retreat, or refusal path appropriate to the intended experience.
- Severe consequences have enough information support for players to treat commitment as a decision rather than a blind trap.
- The reward is scaled against the threatened cost and intended challenge, not merely against how much damage happened to occur at the table.
- Skilled preparation can make success easier without causing the earned payoff to evaporate.
- High-risk peaks remain distinguishable from the adventure's ordinary pressure.

## Notes
Risk and reward are linked at the decision point, not by retrospective casualty count. A difficult opportunity feels worth confronting when success changes something the players value and when failure was genuinely possible without being predetermined. The payoff can be material, strategic, informational, relational, or experiential; it does not have to be a larger pile of currency. The important property is that the upside justifies why a rational player would consider the danger at all.

Variant `game_design_variant_offer_tempting_player_activated_risks` turns that relationship into temptation. Put an unusually useful object, shortcut, bargain, control, or resource behind a danger the players can choose to activate or push. Let investigation or experimentation expose enough of the tradeoff to support judgment, and keep refusal viable. The technique fails when the "choice" is mandatory, the downside is an unknowable gotcha, or the reward dominates every safer alternative so completely that no real tradeoff remains.
