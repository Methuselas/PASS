---
object_id: PAT_predict_cost_from_counted_operations_and_measured_unit_costs
object_type: pattern
name: Predict Cost From Counted Operations and Measured Unit Costs
library_path:
- software-engineering
- core
- performance
stage_binding: 0 design
lane_fit: skill
foundation_role: foundation
routing_class: general
specialization_axis: none
foundation_object_id: none
tags:
- performance_modeling
- algorithm_analysis
- prediction
- measurement
cross_links:
- rel: related_to
  target_object_id: PAT_estimate_the_order_before_you_run_it
- rel: related_to
  target_object_id: PAT_report_the_spread_not_just_the_number
- rel: related_to
  target_object_id: PAT_sample_a_split_point_you_cannot_afford_to_compute
reference:
  source_title: An Introduction to the Analysis of Algorithms
  author: Robert Sedgewick, Philippe Flajolet
confidence: high
references: []
variants: []
---

# Predict Cost From Counted Operations and Measured Unit Costs

## Pattern Rule
**IF** the question needs an actual figure rather than a growth shape — how long a run will take, which of two methods with the same growth is faster, what cutoff or sample size to use — and the method's cost is dominated by a few repeated operations
**THEN** model the cost as those operations' counts, each worked out for a stated model of the input with its leading constant and, where absolute figures matter, its next term; multiply each count by a cost per operation measured on the target machine; and check one prediction against a run before relying on the model
**ELSE** where the only question is how cost grows — whether a tenfold larger input is survivable — the growth estimate alone answers it, and the constants add nothing.

## Do
- Count what the method does, not what the machine does. Compares, exchanges, probes and partition passes are properties of the method and hold on any computer; the time each takes belongs to the machine and has to be measured there. Keeping the two apart lets one analysis serve every machine and lets a machine change be priced by re-measuring a handful of unit costs.
- Keep the constant, and the next term when comparing absolute figures. On random permutations, the leading term alone for a partitioning sort's compares overestimated the measured average by 13% at a thousand elements and 6% at a million; the formula that also carries the linear term came within about 2% at every size.
- Know which question needs the constant. Predicting the same sort's running time at twenty million elements from a run at two million, the full counted model was off by 0.6% and the bare N log N shape by 0.3% — both fine — while assuming linear growth was off by 14%. Ratios across sizes need the shape; absolute figures and comparisons between methods need the constants.
- State the input model, and treat a mismatch between prediction and run as evidence against the model as well as the analysis. A model that assumed distinct keys or random order can be wrong about the input without being wrong about the method.
- Check the spread before promising one run's cost. An average predicts a single run only when the variation is small beside it; for the sort above the standard deviation of compares was about 0.7 times the element count, under 3% of the average at a million elements, so one run lands near the prediction.
- Test a method that halves its input at sizes other than powers of two. Its exact cost oscillates with the binary form of the size: a recurrence that splits into two copies of the rounded-up half matched N log N exactly at 2²⁰ and exceeded it by 3N just above 2¹⁹, while the ordinary floor-and-ceiling split stayed under 0.09N. A fit made only at powers of two cannot see this.

## Don't
- Don't rank two methods of the same growth by their operation counts alone. At ten million elements a merge-based sort made 24% fewer compares than a partitioning sort and took 50% longer, because each of its compares cost 3.6 ns against 1.8 ns.
- Don't state an average as an order of growth and call it a prediction. "Average cost is proportional to N log N" hides exactly the constants that decide which method wins and what the run will cost; use the order notation for error terms far smaller than a leading term that carries its constant.

## Checklist
- Which few operations dominate the cost, and what is each one's count for the stated input model?
- Does each count carry its constant, and a second term where absolute figures are compared?
- Were the unit costs measured on the machine that will run the code?
- Has one prediction been checked against a run?
- Is the spread small enough beside the average to predict a single run?
- If the method halves its input, were sizes other than powers of two measured?

## Notes
The growth estimate and this model answer different questions and fail differently. The estimate says how the cost curve bends and is robust to everything the constants carry; it cannot say which of two N log N methods finishes first or what a run will cost. The counted model can, because it keeps the constants — and it keeps the machine out of the analysis by pushing all of the machine's influence into a few measured unit costs that can be re-measured whenever the hardware changes.

The check against a run is not a formality. When prediction and measurement agree, both the analysis and the implementation gain credibility together; when they disagree, the disagreement is information about one of three things — the counts, the unit costs, or the input model — and finding out which is usually worth more than the prediction was.
