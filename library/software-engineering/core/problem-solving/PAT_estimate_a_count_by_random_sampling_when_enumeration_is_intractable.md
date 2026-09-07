---
object_id: PAT_estimate_a_count_by_random_sampling_when_enumeration_is_intractable
object_type: pattern
name: Estimate a Count by Random Sampling When Enumeration Is Intractable
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
- probabilistic
- estimation
- intractability
cross_links:
- rel: related_to
  target_object_id: PAT_state_the_approximation_guarantee_you_actually_have
- rel: related_to
  target_object_id: AP_get_a_usable_answer_to_an_intractable_problem
reference:
  source_title: 'Algorithms in a Nutshell: A Practical Guide'
  author: George T. Heineman, Gary Pollice, Stanley Selkow
confidence: high
references: []
variants: []
---

# Estimate a Count by Random Sampling When Enumeration Is Intractable

## Pattern Rule
**IF** the exact answer requires enumerating or exhaustively counting a space too large to traverse — the size of a set you can only sample from, the number of leaves in a search tree too big to build
**THEN** build an unbiased random estimator instead of attempting the enumeration: repeat a random trial whose result is provably related to the true count, average many independent trials, and report the estimate together with how many trials produced it
**ELSE** where the space is small enough to count directly, or an exact formula already gives the value, sampling only adds variance for no reason.

## Do
- Find a random process whose expected outcome is provably tied to the quantity you want, before writing any code. Repeated sampling until a value recurs ties the expected number of draws to a population's size; a random walk down a tree ties a single path's branching to the tree's total size. The estimator is only as good as this relationship — get the relationship wrong and no amount of averaging fixes it.
- Run many independent trials and average them, and measure how far they spread. A single trial is not the estimate; the estimate is the average. How far that average can be trusted is not settled by the trial count alone — the count says how much you sampled, the spread across those trials says how much the answer actually moves, and only the second tells you whether the number is usable yet. A thousand trials of a wildly varying process can be worth less than fifty of a stable one.
- Report the result as a statistical estimate, not as a bound. Unlike a proved approximation ratio, this carries no guarantee for any single run — only a distribution around the true value that narrows as trials increase.
- Prefer this over exhaustive search specifically when the count is what's needed, not a witness or the enumerated set itself. If you also need to produce every counted element, sampling the count does not get you there.

## Don't
- Don't mistake more trials for more accuracy without first checking the estimator is unbiased. Averaging a biased process converges confidently to the wrong answer, and no number of additional trials corrects a systematic error in the underlying relationship.
- Don't reuse the intuition behind a proved approximation ratio here. A proved ratio holds for every input by construction; a sampling estimate holds only in expectation over many runs, and any single run can be arbitrarily far off with nothing in that run's own output to say so.
- Don't apply this where an exact algorithm already runs fast enough. Sampling trades a real cost — variance, and the need to run enough trials to trust the number — for a real benefit, tractability; where the exact method is already cheap, there is nothing to buy.

## Checklist
- Is exact enumeration actually intractable here, not merely inconvenient to write?
- Does the random process have a provable relationship to the quantity being estimated, stated before trials are run?
- How many independent trials were run, how far apart did their results fall, and does the report carry that spread rather than only the count?
- Is the result presented as a statistical estimate rather than as a computed bound?

## Notes
This is a different concession from the ones an intractable optimization problem offers. Giving up exactness on an optimization problem in favor of a proved ratio (`PAT_state_the_approximation_guarantee_you_actually_have`) still yields a number that is correct-within-a-known-factor on every input, because the proof is about the algorithm's structure, not about the run. A sampling estimate for a count carries no such per-run guarantee — its accuracy is a property of the distribution of many runs, established empirically rather than proved, and it converges toward the truth only in aggregate.

The technique is worth reaching for specifically because the alternative is usually not "a slower exact method" but "no method at all inside the time available" — the exact count may require visiting a space that would take longer than the program, or the programmer, has to give it. Accuracy bought this way is real and improves predictably with trial count, which is what makes it worth using deliberately rather than treating it as a last resort.
