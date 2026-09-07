---
object_id: PAT_prune_a_partial_candidate_before_you_finish_building_it
object_type: pattern
name: Prune a Partial Candidate Before You Finish Building It
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
- pruning
- intractability
cross_links:
- rel: related_to
  target_object_id: PAT_make_only_forced_moves_so_failure_proves_there_was_no_solution
- rel: related_to
  target_object_id: PAT_check_whether_the_problem_is_a_known_hard_one_in_disguise
- rel: related_to
  target_object_id: PAT_order_the_search_by_an_admissible_cost_estimate
reference:
  source_title: Algorithms
  author: Sanjoy Dasgupta, Christos Papadimitriou, Umesh Vazirani
confidence: high
references: []
variants: []
---

# Prune a Partial Candidate Before You Finish Building It

## Pattern Rule
**IF** you must search a space too large to enumerate, and candidates are assembled piece by piece
**THEN** test each partial candidate as soon as enough of it exists to fail — against the constraints when you need any valid answer, and against a cheap optimistic estimate of the best it could still become when you need the best one — because rejecting a partial discards every candidate that would have been built on it, and that is the only source of efficiency the method has.

## Do
- Test at the earliest point a failure can be detected rather than at the end. Two choices that already contradict a requirement condemn every completion beneath them, and rejecting that pair removes a quarter of the space when the pair was the first two decisions taken.
- Keep the best complete answer found so far, and reject any partial whose most optimistic possible outcome is already worse than it. That comparison is what converts a search for any answer into a search for the best one, without enumerating the rest.
- Keep the estimate cheap and keep it optimistic, because those two properties are what make it usable and correct respectively. An expensive estimate costs more than the pruning it buys; an estimate that can overstate what a partial could achieve will discard the answer you were looking for, silently and without any symptom.
- Expand where the outcome is still uncertain, and treat which candidate to expand next as a free choice you are making rather than one the structure forces. The order in which pieces are decided changes how early contradictions surface.
- Design for the instances you actually receive and expect the worst case to stay exponential. The method's value is entirely in how much it prunes on real inputs, so a change that prunes better on your data is a real improvement even though the worst case is untouched.

## Don't
- Don't present this as having made the problem tractable. It remains exponential in the worst case, and an input that prunes badly will run until it is stopped.
- Don't prune against an estimate you have not established is optimistic. It is the one error here that produces a confident wrong answer rather than a slow one, and nothing in the output distinguishes the two.
- Don't test only complete candidates because it is simpler to write. That is enumeration wearing the shape of a search, and the whole technique is the early test.

## Checklist
- At what point in building a candidate can the first failure be detected?
- For an optimisation, what is your estimate of the best a partial could still reach, and have you shown it never understates it?
- What does the estimate cost per candidate, against how much it prunes?
- Which decision, taken first, constrains the most of what follows?
- What happens when an input prunes badly and the search does not finish?

## Notes
Both forms are the same idea applied to different questions. Where any valid answer will do, a partial dies when it already breaks a constraint. Where the best answer is wanted, it dies when even the most favourable completion could not beat something already in hand. In both cases the saving is not the one candidate rejected but the entire subtree beneath it, which is why the test being early matters more than the test being clever.

The optimistic estimate deserves care disproportionate to its size in the code. It is consulted once per node and therefore dominates the running time, and it is also the correctness-critical part: too weak and nothing gets pruned, too aggressive and the search quietly returns a suboptimal answer with no indication anything went wrong. The usual construction is to solve a relaxed version of the remaining problem — one where some requirement is dropped — because the answer to an easier problem cannot be worse than the answer to the real one.
