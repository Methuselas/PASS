---
object_id: PAT_state_the_approximation_guarantee_you_actually_have
object_type: pattern
name: State the Approximation Guarantee You Actually Have
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
- approximation
- heuristics
- honesty
cross_links:
- rel: related_to
  target_object_id: PAT_prove_a_greedy_rule_safe_before_calling_it_an_algorithm
- rel: related_to
  target_object_id: PAT_check_whether_the_problem_is_a_known_hard_one_in_disguise
- rel: related_to
  target_object_id: PAT_estimate_a_count_by_random_sampling_when_enumeration_is_intractable
reference:
  source_title: Algorithms
  author: Sanjoy Dasgupta, Christos Papadimitriou, Umesh Vazirani
confidence: high
references: []
variants: []
---

# State the Approximation Guarantee You Actually Have

## Pattern Rule
**IF** you are shipping a method that does not return the best answer
**THEN** say which of three things you have — a proved ratio bounding how far from the best it can ever fall, a figure observed on the inputs you tested, or nothing at all — because callers can build very different things on the three, and the words for them are not interchangeable.

## Do
- Define a proved ratio over the worst input, not the typical one. Repeatedly covering the most uncovered elements returns a selection no larger than the smallest possible one multiplied by the natural logarithm of the number of elements, on every input including the ones nobody has tried, and that is a different kind of statement from any average.
- Check whether a better ratio is even attainable before spending effort chasing one. For some problems the achievable factor is itself bounded, so an apparently disappointing guarantee can be the best that any efficient method will ever offer, and the effort belongs elsewhere.
- Say heuristic when there is no bound on either the running time or the quality, and let the word do its work. A method built on a plausible analogy and refined by experiment is a legitimate thing to ship and an illegitimate thing to describe as approximate within a factor.
- Measure a heuristic rather than reasoning about it, because reasoning is exactly what it does not come with. Methods that improve a solution by repeatedly making small changes and keeping the ones that help carry no guarantee whatsoever and are, as an empirical matter, among the strongest performers available on many problems.
- Name what the guarantee is about. A bound on cost says nothing about running time, a bound on running time says nothing about quality, and a method can be excellent on one while unbounded on the other.

## Don't
- Don't report a ratio measured on a test set as though it were proved. The measured figure describes the inputs you had; the proved one describes every input, and the gap between those two claims is where a caller's assumption gets built on sand.
- Don't let an unbounded method inherit the vocabulary of a bounded one. Approximate within a factor is a specific claim with a proof behind it, and using it loosely removes the only word available for the case where the proof exists.
- Don't treat the absence of a guarantee as a reason to reject a method. It is a reason to measure it and to say what you measured, not to prefer a worse method that happens to come with a bound.

## Checklist
- Which of the three do you have: a proof, a measurement, or neither?
- If a proof, over what inputs, and against which quantity?
- Is the achievable factor for this problem already known to be limited?
- If a measurement, on which inputs, and how do they relate to production traffic?
- Does the interface or the documentation claim more than the answer to those questions?

## Notes
The three cases are not points on one scale. A proved bound is a statement about every possible input and survives whatever arrives next year; a measured figure is a statement about a sample and expires as the traffic changes; nothing at all is a statement about the method having been useful when someone tried it. Each supports real decisions, and the failure mode is not shipping the weaker one but describing it in the stronger one's language, because the caller then builds on a promise that was never made.

There is a related trap in the direction of ambition. The instinct on seeing a loose guarantee is to look for a tighter method, and for some problems that search is provably futile — the factor is not an artifact of the method but a property of the problem, and no efficient method will beat it. Establishing which case you are in before chasing an improvement is the same discipline as establishing hardness before chasing an exact method, applied one level further along.
