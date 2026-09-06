---
object_id: PAT_check_whether_the_problem_is_a_known_hard_one_in_disguise
object_type: pattern
name: Check Whether the Problem Is a Known Hard One in Disguise
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
- intractability
- reduction
- estimation
cross_links:
- rel: related_to
  target_object_id: PAT_reduce_your_problem_to_one_that_is_already_solved
- rel: related_to
  target_object_id: PAT_find_the_real_constraints_before_calling_it_impossible
reference:
  source_title: Algorithms
  author: Sanjoy Dasgupta, Christos Papadimitriou, Umesh Vazirani
confidence: high
references: []
variants: []
---

# Check Whether the Problem Is a Known Hard One in Disguise

## Pattern Rule
**IF** you are about to spend real effort searching for an efficient exact method for a problem you cannot yet solve
**THEN** first try to recognise it as one of the standard hard problems in different vocabulary, and attempt the mapping in the hardness direction — a known-hard problem into yours — because if that mapping works, no efficient exact method is coming and the effort belongs on what to do instead.

## Do
- Mind the direction, because reversing it proves nothing and is the common error. Mapping your problem onto a solved one borrows that solution; mapping a known-hard one onto yours inherits its difficulty. Difficulty travels along the arrow and efficient methods travel against it.
- Learn a small catalogue rather than a large one, because recognition is cheaper here than it looks. The tractable problems are tractable for many unrelated reasons and have to be learned individually; the hard ones are all the same problem in different costumes, mutually convertible, so recognising any of them is most of the skill.
- Check first that you could verify a proposed answer quickly, given one. A problem where even checking is expensive is in worse shape than the hard family, and the techniques for coping with hardness assume a cheap check.
- Read a failed mapping as inconclusive, not as good news. Failing to construct it means you did not find one, which is the same evidence you had before starting, and it is a much weaker statement than the successful mapping would have been.
- Stop the search for an exact efficient method once the mapping succeeds, and say so explicitly to whoever is waiting. That sentence is the deliverable: it converts an open-ended search into a decision about what to relax.

## Don't
- Don't reach for this before auditing what you assumed. Most problems that look impossible are being solved inside a boundary smaller than the real one, and that audit is the first move; this one applies when the boundary is genuinely established and the problem still resists.
- Don't infer difficulty from your own failure to find a method. Not having found one is a fact about the search, and the whole value of the mapping is that it replaces that with a fact about the problem.
- Don't treat the verdict as a reason to abandon the problem. It rules out one thing — an exact method fast on every input — and leaves approximate answers, restricted inputs, and methods that are fast on the inputs you actually get.
- Don't extend the verdict to a neighbouring problem without redoing the work. Difficulty is not a property of the subject area, and problems that read almost identically sit on opposite sides of the line.

## Checklist
- Which standard hard problem does yours resemble, once the domain vocabulary is stripped out?
- Which direction does your mapping run, and does that direction establish what you want?
- Could you check a proposed answer cheaply if somebody handed you one?
- Have you audited your assumed constraints first?
- If the mapping succeeded, who is still waiting to be told that the exact search is over?

## Notes
The asymmetry underneath this is what makes the recognition practical. Problems that submit to an efficient method do so for scattered and unrelated reasons — one yields to a growth-by-safe-choices argument, another to an ordering of subproblems, another to a flow formulation — so knowing one tells you little about the next. The hard ones are not like that: they are interconvertible, which means they are one problem viewed from many angles, and the catalogue you have to carry is correspondingly small.

Attempting the mapping is itself cheap, which is the argument for doing it before the search rather than after it has failed for a while. A successful one converts an open-ended engineering search into a bounded decision about which requirement to relax, and that is a different kind of question with a different kind of answer.
