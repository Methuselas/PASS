---
object_id: PAT_decide_with_a_random_test_whose_error_shrinks_with_each_trial
object_type: pattern
name: Decide With a Random Test Whose Error Shrinks With Each Trial
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
- randomized_algorithms
- probability
- verification
- algorithm_choice
cross_links:
- rel: related_to
  target_object_id: PAT_return_a_certificate_the_answer_can_be_checked_against
- rel: related_to
  target_object_id: PAT_prescreen_with_a_bounded_false_positive_filter
- rel: related_to
  target_object_id: PAT_sample_a_split_point_you_cannot_afford_to_compute
reference:
  source_title: Introduction to Algorithms
  author: Thomas H. Cormen, Charles E. Leiserson, Ronald L. Rivest, Clifford Stein
confidence: high
references: []
variants: []
---

# Decide With a Random Test Whose Error Shrinks With Each Trial

## Pattern Rule
**IF** a yes-or-no question about an input is too expensive to settle exactly, and a cheap check exists that either finds a witness proving one answer or fails to find one
**THEN** use a randomized version of the check whose chance of missing a witness is bounded for every input, report the proved answer with its witness, repeat independent trials until the chance of a wrong unproved answer is small enough for what depends on it, and interpret that answer against how common each answer is to begin with
**ELSE** where inputs are drawn at random and nobody chooses them, a fixed check that is wrong only on rare specific inputs can be enough; once an input can be chosen, it cannot.

## Do
- Separate the answer the test proves from the one it only fails to disprove. A primality test that finds a witness has proved the number composite, and the witness is the proof; a test that finds none has only failed to find one. Run over every odd number below 100,000 with five random trials each, every prime was reported prime and no composite was.
- Prefer a check whose errors come from its own random choices rather than from the input. Testing a single fixed base is wrong on 22 odd composites below 10,000, starting with 341, and wrong on each of them every time it is asked; some composites fool that kind of check for every base that shares no factor with them — all 320 such bases for 561. The strengthened check that also looks for a nontrivial square root of one has, for every odd composite, at least half of all bases as witnesses: across the odd composites below 20,000 the largest share of bases that failed to expose one was a quarter, and for 561 it was 10 bases out of 560.
- Repeat independent trials to shrink the error. If every trial has at least an even chance of finding a witness, s trials all miss with probability at most one in 2ˢ. Measured over every odd composite below 100,000, three runs each: one trial per run called a composite prime 124 times in 121,224 runs, two trials 7 times, five trials never.
- Find an object by testing random candidates when enough candidates qualify. The expected number of draws is one over the fraction that qualifies: about one in every 710 numbers near 2¹⁰²⁴ is prime, half that among odd numbers, and drawing random odd 64-bit numbers until one passed took 22.5 draws on average against a predicted 22.2.

## Don't
- Don't read the per-trial bound as the chance that a reported answer is wrong. When most candidates have the other answer, a "probably prime" must first overcome that prior: for a random 1024-bit number, the guaranteed probability that a reported prime really is prime is 0.003 after one trial, 0.59 after ten and 0.9993 after twenty. The guarantee passes one half only once the trials exceed the base-2 logarithm of the prior odds, and a fixed number of trials does not mean a fixed confidence across input sizes.
- Don't rely on a check that is wrong on specific inputs where the inputs can be chosen. The fixed-base test calls 341 prime every time it sees it, so a caller who supplies 341 defeats it with certainty; a randomized check has no such input, and its error stays bounded whoever picks the number.

## Checklist
- Which answer does the test prove, and does that answer carry its witness?
- Is the chance of missing a witness bounded for every input, or only for typical ones?
- How many independent trials are run, and what bound does that give?
- Has the reported confidence been adjusted for how common each answer is among the inputs?
- Can anyone choose the inputs this check will see?

## Notes
Two different uses of randomness meet here and are easy to confuse. Randomizing to protect running time leaves every answer correct and spreads the cost; randomizing a decision leaves the cost fixed and allows a bounded chance of a wrong answer. The second is acceptable because the error is one-sided and repeatable: the proved answer is never wrong, and the unproved one gets exponentially more reliable with each trial for a linear increase in work.

The fixed-base test is a useful warning about what "rarely wrong" means. Its errors are genuinely rare among random inputs and it is good enough for picking random primes, yet its failures are a fixed set that anyone can look up. The randomized test is not merely less often wrong on average; it has no inputs on which it is reliably wrong, and that is the property that survives an adversary.
