---
object_id: PAT_amortize_a_sequence_instead_of_bounding_one_operation
object_type: pattern
name: Amortize a Sequence Instead of Bounding One Operation
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
- performance
- algorithms
- amortized_analysis
- data_structures
cross_links:
- rel: related_to
  target_object_id: PAT_estimate_the_order_before_you_run_it
- rel: related_to
  target_object_id: PAT_name_the_allocation_pattern_before_choosing_a_strategy
reference:
  source_title: 'Introduction to Algorithms, 3rd Edition'
  author: Thomas H. Cormen, Charles E. Leiserson, Ronald L. Rivest, Clifford Stein
confidence: high
references: []
variants: []
---

# Amortize a Sequence Instead of Bounding One Operation

## Pattern Rule
**IF** a data structure's operations vary wildly in individual cost — most are cheap, but a rare one is expensive — and multiplying the worst-case cost of one operation by the number of operations gives a bound far worse than what actually happens
**THEN** bound the total cost of the whole sequence directly, using one of three lenses (charge each operation the sequence average; give cheap operations a fixed charge and bank the surplus as credit against later expensive ones; or track a potential function of the structure's state whose rise pays for the fall an expensive operation causes) rather than multiplying a per-operation worst case by the operation count
**ELSE** where every operation genuinely costs about the same regardless of history, ordinary per-operation analysis already gives the tight answer and there is nothing this buys.

## Do
- Reach for the plainest lens first. Summing the true total cost of any sequence of n operations and dividing by n (aggregate analysis) is enough whenever every operation type ends up with the same amortized cost — a stack of push, pop, and a multi-pop that only ever removes objects some earlier push placed there is the model case: bound the pops by the pushes that could have supplied them, not by the size of the structure.
- Reach for a credit scheme (the accounting method) when different operation types should carry different amortized costs. Overcharge the operations that create the conditions for an expensive one — charge an insertion enough to prepay for both its own cost and its eventual share of being copied during a resize — and never let the running total of unspent credit go negative; a negative balance means the amortized costs charged so far no longer bound the actual costs incurred so far.
- Reach for a potential function when the credit needs to live on the structure as a whole rather than on identifiable pieces of it. Define a function of the structure's current state that is zero at the start, never negative, and rises exactly as fast as the slack that an expensive operation will consume — a dynamic table's fullness relative to its ideal load factor is this kind of function, rising toward the size of the table as it fills and dropping to zero the moment a resize pays it out.
- State which quantity is being amortized over. All three lenses answer "cost per operation, worst case, over a sequence" — none of them involve probability, and none of them are an average-case claim about typical input.

## Don't
- Don't build a resize-both-directions structure with symmetric thresholds. Doubling on full and halving on half-empty looks safe but has no slack: an adversarial insert-delete-delete-insert-delete-delete sequence straddling the halfway point triggers a full resize on nearly every operation, driving the amortized cost from constant to linear. The fix is asymmetric thresholds — grow at full, shrink only once usage drops to a quarter, say — so a resize in either direction leaves enough slack that the opposite resize can't be triggered again until real work has paid for it.
- Don't let charges assigned during the analysis leak into the code. A credit balance or a potential function is bookkeeping for the proof; a data structure that starts tracking its own amortized-cost ledger at runtime has confused the analysis with the implementation.
- Don't mistake an amortized bound for a per-operation guarantee. It bounds the sequence, not any single call — a caller relying on one particular expensive operation completing quickly, such as inside a real-time deadline, is exposed exactly where the bound is silent.

## Checklist
- Does the true cost of one operation depend on the sequence's history (how full a structure is, how much slack has accumulated) rather than being fixed?
- Has the total cost of an arbitrary sequence of n operations been bounded directly, rather than assumed to be n times the worst single operation?
- If a credit scheme is used, is there a check that the running balance never goes negative for any sequence?
- If a potential function is used, is it zero at the start and never negative afterward?
- If the structure resizes in two directions, is there real slack between the grow and shrink thresholds, or could an alternating sequence retrigger both on every step?

## Notes
The three lenses prove the same kind of claim from different angles and are not competing techniques to pick the "best" one from in general — aggregate analysis is the easiest to reach for and the least flexible, since it forces one amortized cost onto every operation type; the accounting method is the most intuitive because the credit has a physical story (a dollar taped to an object); the potential method is the most general because it doesn't require the credit to be attachable to any single object, at the cost of needing a function to be invented and verified. A structure with one operation type that occasionally does a lot of cleanup work is often provable by any of the three; a structure whose operations naturally have different amortized weights usually needs accounting or potential.

The resize-threshold trap is worth carrying on its own, separate from the proof techniques, because it is a design mistake this analysis exposes rather than a mistake in the analysis itself: the symmetric-threshold version is genuinely wrong at runtime, not merely harder to prove a bound for, and the amortized analysis is what makes the difference visible before it shows up as a production stall.
