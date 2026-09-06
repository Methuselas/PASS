---
object_id: PAT_reduce_your_problem_to_one_that_is_already_solved
object_type: pattern
name: Reduce Your Problem to One That Is Already Solved
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
- reduction
- reuse
- problem_framing
cross_links:
- rel: related_to
  target_object_id: PAT_choose_a_problem_representation_before_solving
- rel: related_to
  target_object_id: PAT_reduce_the_problem_until_you_can_already_solve_it
reference:
  source_title: Algorithms
  author: Sanjoy Dasgupta, Christos Papadimitriou, Umesh Vazirani
confidence: high
references: []
variants: []
---

# Reduce Your Problem to One That Is Already Solved

## Pattern Rule
**IF** the problem in front of you resembles a standard one for which solvers already exist
**THEN** write the translation rather than the algorithm — convert your input into an instance of the standard problem, call its solver, convert the result back — and price the instance you produce, because a translation can be perfectly correct and still unusable.

## Do
- Write both halves down as named steps, because the conversion back is where the reasoning usually goes wrong. Finding the longest route through a network is answered by negating every weight and asking for the shortest, and the second step is remembering that the returned cost has to be negated too.
- Price the translation by the size of the instance it builds, not by how long the translation takes. A formulation carrying one variable for every possible route through a network is a faithful statement of the problem and produces exponentially many variables on a network of any size, which makes it a proof that the problem is expressible rather than a way to solve it.
- Run the same move inward to shrink what you must support. A solver that accepts one shape of input can absorb the others through small rewrites — an inequality becomes an equation by adding a nonnegative amount of slack, an equation becomes two inequalities, a quantity that may go either way becomes the difference of two that may not — so the variety lives in the translation and the engine has one case to get right.
- Prefer the target with the most existing work behind it. Problems become standard precisely because many things reduce to them, so the well-populated target is both more likely to fit and more likely to have a solver worth borrowing.
- Say which problem you actually solved when you report the result. The solver answered its question about your translated instance; that this answers your question is a claim your conversion makes, and it is the claim that breaks when either end of the translation is later edited.

## Don't
- Don't translate into a harder problem than you need. Requiring that the answers come out as whole numbers reads like a detail and can move a problem from routinely solvable to intractable, so a constraint added for tidiness deserves the same scrutiny as one the domain demands.
- Don't assume the conversion preserves everything you care about. It has to carry the constraints and the thing being optimised; a translation that keeps the objective and quietly drops a requirement returns an excellent answer to a different question.
- Don't reach for a general solver when a structural property gives you a direct method. The general target is available for far more problems and pays for that reach in both time and memory.

## Checklist
- What standard problem are you translating into, and does a solver for it exist?
- How large is the instance your conversion produces, as a function of your input?
- Does the conversion carry every constraint, or only the ones that were easy to express?
- What does the returned answer mean in your problem's terms?
- Would a method built for your problem's structure beat the general one?

## Notes
The reason this is worth naming as a move is that it inverts where the effort goes. Ordinarily solving a problem means designing a procedure for it; here it means designing two conversions and borrowing a procedure, and the skill being exercised is recognition rather than construction. That makes it heavily dependent on knowing what the standard problems are — which is the practical argument for being fluent in a modest catalogue of them, since a target you cannot name is one you will never translate into.

The size caveat deserves more weight than it usually gets, because the failure is silent at the point where it is introduced. A translation is validated by checking it is faithful, and faithfulness says nothing about scale; the formulation with one variable per route is exactly as correct as the compact one. The check has to be a separate, deliberate question about how the instance grows, asked before anything is built on the reduction.
