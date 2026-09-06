---
object_id: PAT_budget_mechanical_operating_cost_by_decision_value_and_activation_cadence
object_type: pattern
name: Budget Mechanical Operating Cost by Decision Value and Activation Cadence
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
- complexity
- operating-cost
- cadence
- throughput
cross_links:
- rel: related_to
  target_object_id: PAT_evaluate_mechanics_by_the_decisions_and_agency_they_create
- rel: related_to
  target_object_id: PAT_preserve_decision_relevant_state_while_compressing_resolution_procedure
reference:
  source_title: Designing TTRPGs For Dummies
  author: Martin Buinicki
confidence: high
references: []
variants: []
---

# Budget Mechanical Operating Cost by Decision Value and Activation Cadence

## Pattern Rule
**IF** a mechanic, subsystem, or rules layer is being judged for complexity or operating burden
**THEN** measure the human work it creates at its real activation cadence and under representative composition, then compare that cost with the meaningful decisions, consequences, state, clarity, or genre experience it buys
**ELSE** do not infer practical complexity from rule count, page count, arithmetic length, or isolated execution alone.

## Do
- Measure human execution work such as arithmetic, lookup, physical handling or counting, explanation, translation, branch handling, reminders, state writes, and later state maintenance.
- Record who pays each cost and how often: common runtime, conditional runtime, character creation, advancement, downtime, preparation, construction, facilitator integration, or another real cadence.
- Separate decision complexity from operator complexity. A dense choice can be valuable play; repeated translation, bookkeeping, or dependency propagation can consume the same time without creating an equivalent decision.
- Compare both additions and omissions. A low-frequency procedure can justify substantial detail when it creates durable strategic, ownership, identity, construction, or campaign decisions.
- Stress-test conditional mechanics under realistic concurrent activation because several individually cheap rules can become expensive when one scene activates them together or they alter the same resources, derived values, timers, or persistent state.
- Evaluate repeated procedures at table scale as well as action scale. When actors resolve serially, measure how per-resolution work multiplies across a representative cycle and how long participants go without a meaningful decision.
- Count persistent-state servicing after the visible resolution. Bleeding, stun, timers, penalties, recovery records, follow-up checks, and similar outputs continue consuming attention after the initial roll is finished.
- When a table or lookup compresses arithmetic, prose exceptions, or improvisation, compare the work it removes with retrieval distance, lookup frequency, interpretation steps, branch depth, and any future state the result creates.
- Separate purposeful character-facing friction from operator-facing friction. Preserve scarcity, uncertainty, injury, delay, or other hardship when managing that pressure is itself intended play; compress servicing work that does not buy equivalent decisions or causal feedback.
- When a procedure scales with simulated units such as bullets, targets, components, or actors, compare the growth in human operations with the growth in meaningful decisions. One decision should not silently multiply into large servicing work merely because the fiction contains many units.
- Treat a nominally specialist rule as common-path complexity when the genre or expected campaign makes it frequent. A separate section heading does not create a larger runtime budget.
- When useful, record **Human Operations Per Resolution (HOPR)** as the count of discrete servicing operations needed to complete one resolution, and **Time Between Meaningful Decisions (TBMD)** as the elapsed table time between consequential choices for a participant. Use them as diagnostic measures, not universal target numbers.

## Don't
- Treat extra precision, realism, or procedural detail as self-justifying when its operating cost exceeds the play value it produces.
- Compare mechanics only by raw rule count or arithmetic difficulty while ignoring who pays the cost, whether the user opted into it, and how often it recurs.
- Equate fewer rules with better design when the removed procedure would have created high-value decisions at an affordable cadence.
- Assume an optional, conditional, or event-gated rule is cheap without counting the cost of discovering whether it applies and the cost when several such rules activate together.
- Count automated arithmetic as player-facing decision complexity, or assume automation removes the need for players to understand state changes they must choose around.
- Spread a specialized layer across baseline play merely because it is enjoyable in the optional domain where it was first tested.
- Remove intended character-facing friction merely because it makes play inconvenient when that inconvenience is the pressure players are meant to manage.
- Call a redesign simpler without checking whether equivalent work moved into another common or genre-frequent procedure.

## Checklist
- The procedure's human servicing work has been observed or estimated separately from its meaningful decisions.
- The evaluation records who pays the cost, whether that user opted into it, and how often it recurs.
- Common runtime, conditional runtime, creation, advancement, downtime, preparation, construction, and facilitator-integration costs are distinguished where relevant.
- At least one plausible stacked state has been checked when conditional mechanics can overlap or modify shared state.
- A representative repeated-use test has checked whether tolerable local resolutions become excessive whole-table latency or participant downtime.
- Persistent state created by the procedure includes the later reminders, updates, recovery, or bookkeeping it requires.
- Tables and lookups are assessed by both what they compress and what retrieval, interpretation, branching, or state-maintenance cost they introduce.
- Any proposed simplification identifies which operating work disappears and which decisions, consequences, or causal distinctions would disappear with it.
- Genre-frequent or unit-scaling procedures have been assessed at their real frequency and scale rather than their nominal category.

## Notes
Mechanical complexity is paid through operation, not merely through the existence of rules. Placement and cadence therefore matter as much as amount. A moderately involved lifepath or construction procedure may be cheap in session time because it runs rarely and creates durable expressive decisions, while a smaller branch repeated every attack can dominate a session. Local costs also compound: injury, gear, environment, magic, vehicles, and adversary state may each be reasonable alone but expensive when one scene makes them active together. The useful budget is not a universal operation count. It is the relationship between human servicing work and the decisions, consequences, persistence, clarity, or genre experience that work creates under the conditions where the game will actually run.
