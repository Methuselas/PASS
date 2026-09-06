---
object_id: PAT_fill_the_table_or_memoise_the_recursion_by_what_you_reach
object_type: pattern
name: Fill the Table or Memoise the Recursion, by What You Actually Reach
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
- memoization
- dynamic_programming
- performance
cross_links:
- rel: related_to
  target_object_id: PAT_define_the_subproblems_and_let_their_dependencies_set_the_order
- rel: related_to
  target_object_id: PAT_choose_lazy_or_eager_by_how_often_the_result_is_needed
reference:
  source_title: Algorithms
  author: Sanjoy Dasgupta, Christos Papadimitriou, Umesh Vazirani
confidence: high
references: []
variants: []
---

# Fill the Table or Memoise the Recursion, by What You Actually Reach

## Pattern Rule
**IF** you have a set of subproblems and a rule that builds each from smaller ones, and you are deciding how to evaluate them
**THEN** choose by what fraction of the set any single run actually reaches: work upward through a table when nearly all of them are needed, and cache the results of a recursive function when the ones reached are a sparse subset of the ones definable.

## Do
- Ask what makes an entry unreachable before assuming they all are reachable. When every quantity in the input is a multiple of some step, every position not on that step is definable, never requested, and pure waste to compute — and the sparsity is a property of the input rather than of the algorithm, so it can be checked.
- Take the loop when the set is dense. Working upward has no call overhead, no lookups, and touches memory in address order, so it beats the recursive form by a constant factor that is often large even though the two do the same amount of asymptotic work.
- Take the cached recursion when the set is sparse, and accept the overhead as the price of not computing the rest. Two calls, a hash lookup, and a stack frame per subproblem is a poor exchange when it saves nothing and an excellent one when it skips most of the table.
- Make the cache key the whole identity of the subproblem. Every quantity the answer depends on belongs in the key, and one omitted is not a slow program but a wrong one that returns a neighbour's answer.
- Prefer the loop when memory is the binding constraint. Working upward in a known order is what lets you discard values whose consumers are finished; a recursion that may revisit anything has to keep everything it has seen.

## Don't
- Don't treat equal asymptotic cost as equal cost. Both forms visit each needed subproblem once and the constant between them can be several-fold, which is exactly the range where a measured choice beats a reasoned one.
- Don't reach for the cached recursion because it reads more naturally. It usually does — the rule and the code look alike — and readability is a real argument that should be made on its own terms rather than smuggled in as a performance claim.
- Don't cache a function whose answer depends on anything outside its arguments. Time, a global counter, a mutable structure it consults: any of them makes the stored answer a fact about the moment it was computed, and the failure surfaces far from the cause.

## Checklist
- What fraction of definable subproblems does a typical run request?
- Is there a property of the input that makes most of them unreachable?
- Does the cache key contain every quantity the answer depends on?
- Is the function's answer determined entirely by its arguments?
- Which form does your memory budget allow?

## Notes
The distinction that makes the choice is not about recursion or iteration as styles. Working upward solves every subproblem that could conceivably be needed; caching a recursion solves those that are actually asked for. When those two sets coincide the loop wins on constants; the further they diverge, the more the recursion's overhead is bought back by the entries it never touches. So the question to ask is about the input, not about the code.

The sparse case is easy to miss because the table is usually described by its dimensions, and dimensions suggest density. A quantity indexed by every value up to some limit, where the inputs only ever combine into multiples of a hundred, has a table that is ninety-nine percent unreachable and looks completely full when written down. Noticing that requires reading what the recurrence can construct rather than what the index permits.
