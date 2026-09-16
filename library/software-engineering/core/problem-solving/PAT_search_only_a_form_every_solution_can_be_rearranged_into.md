---
object_id: PAT_search_only_a_form_every_solution_can_be_rearranged_into
object_type: pattern
name: Search Only a Form Every Solution Can Be Rearranged Into
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
- optimization
- search_space
- problem_framing
cross_links:
- rel: related_to
  target_object_id: PAT_prove_a_greedy_rule_safe_before_calling_it_an_algorithm
- rel: related_to
  target_object_id: PAT_reduce_your_problem_to_one_that_is_already_solved
- rel: related_to
  target_object_id: PAT_define_the_subproblems_and_let_their_dependencies_set_the_order
reference:
  source_title: Introduction to Algorithms
  author: Thomas H. Cormen, Charles E. Leiserson, Ronald L. Rivest, Clifford Stein
confidence: high
references: []
variants: []
---

# Search Only a Form Every Solution Can Be Rearranged Into

## Pattern Rule
**IF** you are looking for a best arrangement — an order, a schedule, an allocation, a setting of continuous quantities — and the space of candidates is too large or too loose to search directly
**THEN** find a restricted shape that any candidate can be transformed into, step by step, without making it worse, prove that each step never worsens the result, and search only candidates of that shape
**ELSE** where no such transformation can be shown, the restriction may exclude every best answer, and the search has to stay over the full space.

## Do
- Look for a rearrangement that cannot hurt and apply it until nothing changes. For single-slot tasks with deadlines and penalties for lateness, moving an on-time task ahead of a late one leaves the first on time and the second late, and swapping two adjacent on-time tasks into deadline order keeps both on time; so every schedule can be turned, without raising its penalty, into one where the on-time tasks come first in deadline order and the late ones follow.
- Let the restricted shape change what you are searching for, not just how much. In that canonical schedule the order is fixed by the choice of which tasks are on time, so the problem becomes choosing a set: on eight tasks that is 256 candidates instead of 40,320 orders, and the best penalty over the sets matched the best over every order in 200 random instances.
- Use the same move on continuous problems. When the goal and the limits are all linear, the best value, whenever a finite one exists, is reached at a corner of the region the limits enclose, because the level line of the goal can be slid outward until it last touches the region, and that last contact includes a corner. A search over corners is finite: in a three-variable problem with three limits plus the three non-negativity bounds there are twenty ways to choose three limits to hold exactly, six of them feasible corners, and the best corner gave 28 at (8, 4, 0) — the same best as a grid of 8,312 feasible points.
- Convert the canonical answer back into the thing that was asked for. The set of on-time tasks is not a schedule until it is listed in deadline order with the late tasks after it; name that step, since it is where the reduced answer meets the original question.

## Don't
- Don't read the restriction as a claim about every best answer. It guarantees that at least one best answer has the canonical shape; others may not. Where the goal's level line lies along an edge of the region, every point on that edge is equally good, and the corners are only two of them.
- Don't expect the canonical candidates to inherit properties the rearrangement never promised. A corner of a region bounded by limits with whole-number coefficients need not have whole-number coordinates — maximizing x plus y under 2x plus 2y at most 3 reaches its best value, 3/2, at a corner where x is 3/2 — and a solution that must be whole numbers is a different and much harder problem.

## Checklist
- What rearrangement turns an arbitrary candidate into the restricted shape?
- Has each step of it been shown never to worsen the objective?
- How many candidates does the restricted shape leave, compared with the full space?
- What step converts a canonical answer back into an answer to the original question?
- Does anything downstream assume properties — uniqueness, whole numbers — that the canonical form does not guarantee?

## Notes
This is distinct from choosing a greedy rule, even though the proofs look alike. An exchange argument for a greedy rule shows that one particular choice can be made first without losing optimality; the argument here shows that a whole class of candidates can be discarded because each has an equal-or-better counterpart inside a smaller class. The search that follows may be greedy, exhaustive or anything else — the restriction only decides what it runs over.

The payoff is often a change of problem rather than a constant-factor pruning. An ordering problem became a subset problem, and a problem with infinitely many feasible points became one with finitely many corners, which is what makes a step-by-step method over corners possible at all. That is the reason to look for such a form before choosing any search technique: it can change which techniques apply.
