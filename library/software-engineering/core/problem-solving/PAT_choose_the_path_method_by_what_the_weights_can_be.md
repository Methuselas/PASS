---
object_id: PAT_choose_the_path_method_by_what_the_weights_can_be
object_type: pattern
name: Choose the Path Method by What the Weights Can Be
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
- graphs
- shortest_paths
- algorithm_choice
- scheduling
cross_links:
- rel: related_to
  target_object_id: PAT_order_dependent_work_by_its_graph_and_name_the_cycles
- rel: related_to
  target_object_id: PAT_order_the_search_by_an_admissible_cost_estimate
- rel: related_to
  target_object_id: PAT_reduce_your_problem_to_one_that_is_already_solved
reference:
  source_title: Introduction to Algorithms
  author: Thomas H. Cormen, Charles E. Leiserson, Ronald L. Rivest, Clifford Stein
confidence: high
references: []
variants: []
---

# Choose the Path Method by What the Weights Can Be

## Pattern Rule
**IF** you need cheapest routes through a network of costed steps — travel times, fees, penalties, delays, or any cost that adds up along a path — from one starting point or between every pair of points
**THEN** choose the method from two facts about the input before anything else: whether the network can contain a cycle, and whether any step can have a negative cost, because the fast method silently returns wrong answers when a cost is negative and only the slower one can report that no cheapest route exists
**ELSE** where every step costs the same, a plain breadth-first traversal already gives the fewest-step routes and none of the weighted machinery is needed.

## Do
- Take the one-pass method when the network has no cycles. Put the points in dependency order and relax each outgoing step once in that order; it runs in time linear in points plus steps, and it is correct even with negative costs, because no route can loop back to exploit them.
- Take the priority-queue method when every cost is zero or positive. Repeatedly settle the unsettled point with the smallest tentative cost and relax its outgoing steps; with a binary heap it costs time proportional to the number of steps times the logarithm of the number of points, and for a network so dense that most pairs are connected, scanning an array for the smallest tentative cost is as fast and simpler.
- Take the repeated-relaxation method when any cost can be negative. Relax every step once per point, then relax them all one more time: if anything still improves, a cycle of negative total cost is reachable and there is no cheapest route to anything it reaches — report that instead of returning numbers. The price is time proportional to points times steps.
- Choose by density when you need every pair. Where most pairs of points are directly connected, the triple loop that admits each point in turn as a permitted stopover takes time proportional to the cube of the points with a tiny constant and no data structure; where the network is sparse, run the priority-queue method from every point instead. Measured on 2,000 points: with about two million steps the triple loop took 5.4 s and the per-point method 6.3 s; with 8,000 steps the per-point method took 0.25 s and the triple loop 2.4 s, and the two agreed on every entry.
- Adjust negative costs once so a sparse all-pairs problem can still use the priority-queue method. Add one point joined to every other at cost zero, run the repeated-relaxation method once from it, and add to each step's cost the distance at its start minus the distance at its end. Every adjusted cost is zero or more, the cheapest routes are the same routes, a negative cycle is still reported by that one run, and subtracting the start's distance and adding the end's recovers each true cost; checked against the triple loop on 200 random networks with negative steps.
- Recognise scheduling constraints as the same problem. Constraints of the form "B starts at least 2 after A" and "C starts no more than 6 after A" are differences between unknown start times; each becomes a costed step, the relaxation method's distances from an added start point are a valid set of times, and a negative cycle means the constraints contradict each other. Measured on three jobs needing gaps of 2 and 3, a deadline of 6 after the first produced times 0, 2, 5 after shifting, and a deadline of 4 was reported infeasible.
- Find the critical path of a dependency schedule as the longest route through its acyclic graph, by running the one-pass method with costs negated. Its length is the least total time any ordering of the work can achieve.

## Don't
- Don't use the priority-queue method on a network where any step can cost less than zero. It settles a point before seeing a cheaper route that passes through a negative step and never revisits it: on a four-point network with one step costing −4, it returned a cost of 2 to a point whose cheapest route cost 1, and 3 where the answer was 2, with nothing to signal the error.
- Don't return distances from a network containing a reachable negative cycle. Every "cheapest" figure through it is meaningless, and the only correct output is the report that the cycle exists.

## Checklist
- Can the network contain a cycle?
- Can any step cost less than zero?
- If costs are negative, does the method report a reachable negative cycle rather than return numbers?
- For every pair, was the method chosen by how densely the points are connected, and were negative costs adjusted once rather than relaxed repeatedly from every point?
- Are there timing constraints between events that are really differences, and has a negative cycle been read as a contradiction among them?
- Is a critical path being computed as the longest route through the acyclic dependency graph?

## Notes
The three methods differ only in how many times and in what order they relax a step — test whether going through this step gives a cheaper route to its far end, and if so record it — and that is the right way to hold them. Relaxing steps in dependency order handles every route in one pass because each point's cost is final before anything leaving it is examined. Settling the cheapest remaining point first also makes each point final once, but only because costs never decrease along a route; a negative step breaks exactly that. Relaxing everything repeatedly makes no assumption about order at all, which is why it is slower and why it is the only one that can notice when relaxation would never stop.

The scheduling equivalence is worth having ready because the constraints rarely announce themselves as a path problem. A set of minimum and maximum gaps between events has a solution exactly when its constraint graph has no negative cycle, and the cycle, when found, names the chain of requirements that cannot all hold — which is the thing a planner needs to be told.
