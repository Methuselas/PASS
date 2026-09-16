---
object_id: PAT_report_the_spread_not_just_the_number
object_type: pattern
name: Report the Spread, Not Just the Number
library_path:
- software-engineering
- core
- performance
stage_binding: 4 final
lane_fit: both
foundation_role: foundation
routing_class: general
specialization_axis: none
foundation_object_id: none
tags:
- performance
- measurement
- benchmarking
- reporting
- statistics
cross_links:
- rel: related_to
  target_object_id: PAT_reproduce_the_real_context_before_believing_a_microbenchmark
- rel: related_to
  target_object_id: PAT_make_benchmarked_work_observable
- rel: related_to
  target_object_id: PAT_let_measurement_decide_what_to_tune
- rel: related_to
  target_object_id: PAT_read_a_break_in_the_cost_curve_as_a_change_of_strategy
reference:
  source_title: Algorithms in a Nutshell
  author: George T. Heineman, Gary Pollice, Stanley Selkow
confidence: high
references: []
variants: []
---

# Report the Spread, Not Just the Number

## Pattern Rule
**IF** you are reporting a measured figure that somebody will make a decision on — a timing, a throughput, a memory figure
**THEN** report it with the spread across trials and rounded to the precision your instrument actually resolves, because a single number carried to several digits is a claim about repeatability and accuracy that the measurement usually cannot support
**ELSE** where the difference you are reporting is far larger than the spread, the bare number is safe to quote — and you only know that because you looked at the spread.

## Do
- Keep the distribution of the trials, not only their average. Thirty runs of one identical computation clustering between eight and ten milliseconds with a single result at forty-two are not telling you the average is eleven; they are telling you the machine did something else once, and only the individual results show it.
- Trim by a stated rule, or not at all. Discarding the best and the worst result of each suite and averaging the remainder is a reasonable convention and is reasonable only while it is written down beside the figure; the identical operation left unstated is indistinguishable from having picked a flattering number.
- Put the dispersion next to the average, because the pair is what supports a prediction and the average alone supports none. An average with a standard deviation lets a reader say how often a future run lands inside a given band; an average by itself cannot answer that question at all.
- Round to what the instrument resolves. Quoting four decimal places from a timer that ticks in whole milliseconds asserts an accuracy nothing in the setup delivers, and digits past the instrument's resolution are decoration that reads as evidence.
- Check whether a finer instrument would change a conclusion before adopting one. Running a suite with a nanosecond timer beside a millisecond timer and finding they agree is a positive reason to keep the coarser one — it is more portable across platforms, and it does not invite a reader to believe in precision that was never there.
- Say which summary you used, because the common ones answer different questions. The smallest time across repetitions estimates the best the code can do with no interference; a trimmed mean estimates what a typical run costs. Both are legitimate, they are not interchangeable, and a table that mixes them is not comparing like with like.

## Don't
- Don't smooth away a result that disagrees with the others before you know why it disagrees. Trimming a known-noisy extreme under a stated rule is housekeeping; discarding a disagreement because it is inconvenient discards the finding.
- Don't report a difference smaller than your spread as a difference. Two averages separated by less than the variation within either one have not been shown to differ, and presenting them as a ranking manufactures a result.
- Don't let the precision of the arithmetic set the precision of the report. A computation yielding 16.897986 is not a measurement good to six decimals; the arithmetic is exact and the input to it was not.
- Don't compare figures gathered under different conventions, different trial counts, or different machines. Each of those is a separate experiment, and lining their numbers up in one table asserts a comparability nobody established.

## Checklist
- How many trials were run, and is the distribution available or only the summary?
- What is the spread, and is the difference you are reporting larger than it?
- Does the number as published carry more digits than the instrument resolves?
- Is the summarising convention — trimmed mean, minimum, median — stated beside the figure?
- Would a finer instrument change any conclusion here, and has anyone checked?

## Notes
The habit this replaces is reporting one number because one number is what the question seemed to ask for. "How long does it take?" invites a scalar answer, and the scalar is an average of results that varied, produced on a machine that was doing other things, by a timer with a resolution nobody stated. None of that is visible in the number, and all of it bears on whether the number can carry the decision being made on it.

Precision and accuracy come apart here in a way that is worth keeping straight. A finer timer improves precision — the resolution of what you can distinguish — and does nothing for accuracy, which is limited by the interference the measurement is subject to. Adopting a nanosecond timer on a machine whose scheduler interrupts the measurement produces numbers with nine digits and the same trustworthiness as before, and the extra digits make the result look better founded rather than making it better founded. Choosing the coarser instrument deliberately, having confirmed it loses nothing, is the move that signals the distinction was understood.

There is a boundary worth marking against the neighbouring discipline of deciding whether a benchmark is representative at all. That question is about context — what was compiled, what was cached, which code path ran. This one arrives afterwards and asks a narrower thing: given the numbers you did collect, what may honestly be published about them. A perfectly representative benchmark reported as a single over-precise figure has thrown away most of what it established.
