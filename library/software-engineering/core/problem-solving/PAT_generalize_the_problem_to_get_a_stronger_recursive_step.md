---
object_id: PAT_generalize_the_problem_to_get_a_stronger_recursive_step
object_type: pattern
name: Generalise the Problem to Get a Stronger Recursive Step
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
- recursion
- algorithm_design
- problem_framing
cross_links:
- rel: related_to
  target_object_id: PAT_reduce_the_problem_until_you_can_already_solve_it
- rel: related_to
  target_object_id: PAT_decide_whether_the_split_or_the_combine_does_the_work
reference:
  source_title: Algorithms
  author: Sanjoy Dasgupta, Christos Papadimitriou, Umesh Vazirani
confidence: high
references: []
variants: []
---

# Generalise the Problem to Get a Stronger Recursive Step

## Pattern Rule
**IF** a problem resists a recursive solution because the smaller instances you would recurse on are not the same question as the one you were asked
**THEN** look for a more general problem that contains the asked question as one case, and recurse on that instead, accepting a harder-looking statement in exchange for a step that can actually call itself.

## Do
- Check whether the recursive call would need to ask something the original statement cannot express. Finding the middle value of a list gives a recursive call nothing to say: after partitioning, the answer you want from one part is no longer its middle value but some other position within it, and the original question has no way to name that position.
- Add the parameter the recursion needs. Asking instead for the kth smallest value carries a position that each call can adjust, so the same routine answers the general question at every level and the middle value is simply one choice of that parameter.
- Expect the general version to be no harder to solve. The extra parameter usually costs nothing in the body of the routine, which is what makes the trade favourable; the work of the algorithm is unchanged and only the interface widened.
- Ship the general version. It is the working algorithm rather than a stepping stone, and the specific question is answered by calling it with one argument fixed.

## Don't
- Don't confuse this with weakening a problem to get unstuck. Suspending a real requirement to reach something you can already write is a different move with a different purpose, and its product is discarded once it has taught you what was missing. This one strengthens the statement and keeps the result.
- Don't generalise past what the recursion needs. The point is to supply the parameter the recursive call must vary, not to build the most abstract routine available; every dimension added beyond that is surface nobody calls.
- Don't take the wider signature as licence to widen the contract. A routine that answers a more general question still promises exactly what it computes, and a parameter added for the recursion's benefit is as much a part of the interface as any other.

## Checklist
- Can the recursive call state its subproblem using only the original question's terms?
- If not, what quantity does it need to vary that the original statement cannot name?
- Does adding that parameter change the body of the routine, or only its signature?
- Is the asked question recoverable by fixing that parameter to one value?

## Notes
The move is counterintuitive, which is why it is worth writing down: the instinct when a recursion will not close is to look for a smaller or simpler question, and here the route out is a larger one. The reason it works is that recursion needs a step that can call itself with different arguments, and a question with no parameters offers nothing to change. Widening the question supplies the variation, and the strengthened statement is what makes the induction go through.

There is a family resemblance to strengthening an induction hypothesis in a proof, where a statement that resists direct proof becomes provable once it is made stronger, because the stronger form is what the inductive step has to work with. The engineering version has the same shape and the same surprise, and the same practical test: the generalisation is the right one when the recursive call can finally be written down without inventing new vocabulary at each level.
