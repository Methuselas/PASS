---
object_id: PAT_order_the_search_by_an_admissible_cost_estimate
object_type: pattern
name: Order the Search by an Admissible Cost Estimate
library_path:
- software-engineering
- core
- problem-solving
stage_binding: 0 design
lane_fit: skill
foundation_role: foundation
routing_class: general
specialization_axis: none
foundation_object_id: none
tags:
- algorithm_design
- search
- heuristics
- optimization
cross_links:
- rel: related_to
  target_object_id: PAT_prune_a_partial_candidate_before_you_finish_building_it
- rel: related_to
  target_object_id: PAT_estimate_the_order_before_you_run_it
reference:
  source_title: 'Algorithms in a Nutshell: A Practical Guide'
  author: George T. Heineman, Gary Pollice, Stanley Selkow
confidence: high
references: []
variants: []
---

# Order the Search by an Admissible Cost Estimate

## Pattern Rule
**IF** you are searching for the least-cost path or solution among many reachable states, and blind traversal — breadth-first, depth-first — would visit states in an order unrelated to how promising they are
**THEN** expand states in order of cost already spent to reach them plus a heuristic estimate of what remains, using a heuristic that never overestimates the true remaining cost, so the search visits far fewer states while the first goal it reaches is still guaranteed optimal
**ELSE** where no such heuristic can be constructed, or the one available is uninformative, this reduces to blind search and buys nothing over it.

## Do
- Build the heuristic from a relaxation of the real problem. Drop a constraint the true solution must respect, and the cost of the easier problem is a legitimate lower bound on the real one's remaining cost — straight-line distance is a lower bound on road distance precisely because it drops the requirement to follow roads.
- Verify the heuristic never overestimates before trusting the result, not after. A search using a genuinely admissible heuristic still finds the optimal solution, only faster; one that can overestimate can return a worse solution with nothing in the output to say so, the same silent failure a pruning search suffers from an unsound bound.
- Expect the payoff to scale with how informative the heuristic is. One close to the true remaining cost explores barely more than the optimal path itself; one only weakly related to it degrades toward the blind search it was meant to replace, and which end of that range you land on is empirical, not something the algorithm's structure reveals on its own.
- Track the frontier in a priority structure ordered by the combined score, not a plain queue or stack. The ordering is the entire mechanism — reverting to first-in-first-out or last-in-first-out silently turns this back into breadth-first or depth-first search while looking unchanged everywhere else.

## Don't
- Don't confuse this with pruning a partial candidate. Pruning discards a branch once its bound proves it cannot win; this instead chooses which surviving branch to expand *next*. The two compose — a bound that kills branches and a heuristic that orders the rest are separate decisions, not alternatives.
- Don't assume the guarantee survives the bookkeeping that makes the search fast. A working implementation keeps a set of states it has already settled and skips any successor it finds there, which is what stops the search re-treading ground — but a cheaper route to an already-settled state can surface later, and skipping it silently keeps the worse cost. Notice the asymmetry in the usual implementation: it will happily replace a state still waiting on the frontier when a cheaper route to it appears, and will not do the same for one already settled. A heuristic that never overestimates is not enough to make that safe. What makes it safe is the stronger property that the estimate never drops from one state to the next by more than the step between them actually costs — consistency — because that is what guarantees no later route can undercut a settled state. Where you cannot argue for that stronger property, settled states have to be reopened when a cheaper route to them appears, exactly as frontier states already are.
- Don't assume a good heuristic is easy to find. Constructing one that is both admissible and informative is frequently the harder part of applying this technique, more work than the search machinery built around it.
- Don't test this the way you test deterministic code. Where several optimal paths exist, or the heuristic's tie-breaking changes which one is found first, the check worth writing is that the returned result is optimal-cost and valid — not that it is identical to one hand-traced reference answer.

## Checklist
- Does a legitimate relaxation of the problem produce the heuristic, or was it invented by intuition with no bound argument behind it?
- Has admissibility — never overestimating — actually been checked, rather than assumed because the heuristic "feels" conservative?
- Is the frontier ordered strictly by cost-so-far plus the heuristic, with nothing else driving expansion order?
- Would blind search already be fast enough here, making the heuristic's design cost not worth paying?
- Does the implementation skip states it has already settled — and if so, is the heuristic consistent, or are those states reopened when a cheaper route appears?

## Notes
A heuristic of zero everywhere is always admissible and degrades this exactly to the shortest-path search it is built on top of, which is a useful sanity check on an implementation: disable the heuristic, and the algorithm should slow toward blind-search speed while still returning a result of the same optimal cost. Be precise about what that check can conclude: a returned path that differs from the one the heuristic produced is not evidence of a defect, because ties among equally optimal results are broken by expansion order and the expansion order is exactly what was just changed. A result whose *cost* is worse is the signal, and that one does put the bug in the ordering machinery rather than in the heuristic.

The technique's value is concentrated in problems where the search space is too large to explore blindly but where *some* structural knowledge about remaining cost is available and cheap to compute at every state — pathfinding, puzzle solving, planning. Where that structural knowledge does not exist, no amount of engineering the search machinery recovers it.
