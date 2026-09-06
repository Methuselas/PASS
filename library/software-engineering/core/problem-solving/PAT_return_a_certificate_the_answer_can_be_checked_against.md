---
object_id: PAT_return_a_certificate_the_answer_can_be_checked_against
object_type: pattern
name: Return a Certificate the Answer Can Be Checked Against
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
- verification
- optimization
- trust
cross_links:
- rel: related_to
  target_object_id: PAT_prove_a_greedy_rule_safe_before_calling_it_an_algorithm
- rel: related_to
  target_object_id: PAT_reduce_your_problem_to_one_that_is_already_solved
reference:
  source_title: Algorithms
  author: Sanjoy Dasgupta, Christos Papadimitriou, Umesh Vazirani
confidence: high
references: []
variants: []
---

# Return a Certificate the Answer Can Be Checked Against

## Pattern Rule
**IF** you are returning an answer whose correctness or optimality took real work to establish, and a caller has to trust it
**THEN** look for a small companion object that makes the answer checkable by a computation far cheaper than the one that produced it, and return that alongside the answer.

## Do
- Look for the bound that meets the answer from the other side. Routing as much as possible through a network and finding the cheapest place to sever it are different questions with the same numeric answer, so a severing point of that cost proves no routing can do better — and it is checked by adding up a handful of capacities rather than by rerunning any search.
- Accept a witness that is not itself an answer to your question. A set of weights that combines your own constraints into a single statement bounding the objective is not a solution to anything, and it is enough: exhibit the weights, do the arithmetic, and the bound is established by someone who never ran the algorithm.
- Require the check to be independent of the method. A verification that repeats the search has confirmed the code is deterministic and nothing else, and the value here comes precisely from the checker not needing to know how the answer was found.
- Use the failure to check as a signal, not an error to suppress. A certificate that no longer verifies means the answer, the certificate, or the checker is wrong, and all three are worth knowing about immediately rather than at the point where the answer is acted on.

## Don't
- Don't confuse a certificate with a test. A test says the method worked on the inputs someone thought of; this establishes something about the answer in hand, including on inputs nobody anticipated.
- Don't produce one that is as expensive to verify as the problem was to solve. The whole value is the gap between the two costs, and without a gap you have shipped the computation twice.
- Don't expect one to exist for every problem. Some answers admit a cheap witness and some do not, and the useful discipline is asking rather than assuming either way.

## Checklist
- Is there a quantity that bounds your answer from the opposite direction?
- What would a sceptic have to compute to be convinced, and is it cheaper than what you did?
- Does the check depend on how the answer was produced?
- What do you do when a certificate fails to verify?

## Notes
The pattern worth carrying is the pairing: a maximising question and a minimising one that shadow each other, where any answer to one bounds every answer to the other, and the best answers coincide. When that structure exists, the second problem is not a curiosity — it is the checking apparatus for the first, and finding it converts an answer that must be trusted into one that can be verified.

What makes this practical rather than theoretical is that the verifier needs no access to the reasoning. It does not need the algorithm, the intermediate state, or a matching implementation to compare against; it needs the answer, the witness, and arithmetic. That independence is the whole of its value, and it is why whether a cheap witness exists is worth asking at design time, while the answer can still shape what gets returned rather than only what gets computed.
