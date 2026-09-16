---
object_id: PAT_measure_how_much_your_index_actually_prunes
object_type: pattern
name: Measure How Much Your Index Actually Prunes
library_path:
- software-engineering
- core
- performance
stage_binding: 4 final
lane_fit: skill
foundation_role: foundation
routing_class: general
specialization_axis: none
foundation_object_id: none
tags:
- performance
- indexing
- measurement
- data_shape
- dimensionality
cross_links:
- rel: related_to
  target_object_id: PAT_pin_the_relationship_between_input_sizes_before_ranking_two_costs
- rel: related_to
  target_object_id: PAT_choose_lazy_or_eager_by_how_often_the_result_is_needed
- rel: related_to
  target_object_id: PAT_estimate_the_order_before_you_run_it
- rel: related_to
  target_object_id: PAT_detect_a_degrading_run_and_switch_to_a_bounded_method
reference:
  source_title: Algorithms in a Nutshell
  author: George T. Heineman, Gary Pollice, Stanley Selkow
confidence: high
references: []
variants: []
---

# Measure How Much Your Index Actually Prunes

## Pattern Rule
**IF** you have built a structure whose whole purpose is to let a query skip most of the data — a spatial tree, a search index, any partition that answers by descending instead of scanning
**THEN** measure what fraction of the data it actually eliminates on the data you really hold, rather than the fraction its complexity promises, because a structure that eliminates nothing still returns exactly the right answers
**ELSE** where the query has to return most of the data anyway, no partition was ever going to help and a plain scan is the honest implementation.

## Do
- Instrument the decision that does the pruning rather than the clock. The useful counter is how often the test that should have excluded a branch failed to exclude it and forced both sides to be searched; that number rising toward one per node is the structure telling you it has stopped partitioning anything, and it says so long before a timing difference would.
- Watch the parameter that erodes discrimination. Dimensionality is the standard one: a tree over points in two dimensions discards roughly half the remaining candidates at every step, while the same tree over ten-dimensional points is forced to descend both sides of nearly every split, and past roughly a dozen dimensions scanning every point outright is measurably faster.
- Count the comparison itself as growing. Comparing two points across d dimensions is work proportional to d, so the per-item constant you had been treating as fixed is inflating under the same parameter that is destroying the pruning — the two effects arrive together and compound.
- Test the distributions that defeat the partition, not only the uniform ones. Points arranged around a circle can multiply the both-sides descents two-hundredfold at two dimensions, where dimensionality is not the problem at all; points clustered into one corner collapse a fixed quadrant partition into something close to a chain. Uniform random data is the case these structures are designed for and the case least likely to reveal their failure.
- Re-measure when the data changes shape rather than when it changes size. Several of these structures are built once from the median outward and cannot be rebalanced or deleted from cheaply, so a structure that discriminated well on the data it was built from can degrade without anything in the code changing.

## Don't
- Don't read correct results as evidence the structure is earning its place. This is the entire trap: the degraded case and the healthy case are indistinguishable from the output, and the only difference is how much work happened underneath.
- Don't accept the complexity expression as the measurement. A bound whose exponent contains the dimension is honest and approaches linear as that dimension rises, so quoting it says nothing about whether you are in the regime where it helps — the expression describes a curve, and which point of the curve you occupy is the question.
- Don't keep a structure that has stopped discriminating because removing it would feel like a regression. It costs memory, build time, and a body of code to maintain, and where it prunes nothing it buys nothing; deleting it and scanning is a simplification rather than a concession.
- Don't amortize the build cost over queries you have not counted. The structure pays for itself across many searches and is pure overhead for a handful, and the number of searches is usually knowable in advance.

## Checklist
- What fraction of the data does a typical query actually eliminate, measured rather than assumed?
- How often does the pruning test fail to exclude either side?
- Which parameter erodes the discrimination here, and what is its value in production?
- Has this been tested on clustered, aligned, or degenerate data, or only on uniform random data?
- How many queries will this structure serve before it is rebuilt, and does that number repay building it?

## Notes
The failure mode is worth naming precisely because it is invisible from every direction that usually reveals problems. The structure is correct. The tests pass. The complexity written in the comment is accurate. The only symptom is that a query costs about what scanning would have cost, which nobody notices because nobody has the scanning version to compare against — it was deleted when the structure was introduced.

Two forces run together as the eroding parameter grows, and separating them explains why the crossover arrives sooner than people expect. The pruning weakens, so more of the data is visited; and the per-comparison cost rises, because comparing richer items is more work. Either alone would move the crossover; together they move it a long way, which is why a structure that is overwhelmingly worthwhile in two dimensions can lose to brute force in eleven rather than in some comfortably remote number.

The distribution case deserves as much attention as the dimensional one and usually gets less. A partition discriminates by separating things; data that is genuinely spread out separates well, and data arranged along a curve, clustered in a corner, or duplicated heavily does not. Those arrangements are not pathological inputs invented by an adversary — they are what measurements, sensor readings, and spatial data from the real world routinely look like, and the uniform random data used to validate the structure is the one distribution that guarantees the problem will not appear.
