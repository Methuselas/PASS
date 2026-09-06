---
object_id: PAT_define_the_subproblems_and_let_their_dependencies_set_the_order
object_type: pattern
name: Define the Subproblems and Let Their Dependencies Set the Order
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
- dynamic_programming
- decomposition
- memory
cross_links:
- rel: related_to
  target_object_id: PAT_decide_whether_the_split_or_the_combine_does_the_work
- rel: related_to
  target_object_id: PAT_fill_the_table_or_memoise_the_recursion_by_what_you_reach
reference:
  source_title: Algorithms
  author: Sanjoy Dasgupta, Christos Papadimitriou, Umesh Vazirani
confidence: high
references: []
variants: []
---

# Define the Subproblems and Let Their Dependencies Set the Order

## Pattern Rule
**IF** a problem has no efficient direct method, and its answer can be assembled from answers to smaller versions of itself that recur across different branches of the work
**THEN** treat naming the set of subproblems as the design act, with an edge from each one to every larger one that consumes it, and read the solving order, the running time, and the memory you must retain off that dependency graph instead of deciding each separately.

## Do
- Pick the subproblem from the handful of shapes that keep recurring, because the shape tells you the count before you write anything. A prefix of one sequence gives a linear number of them; prefixes of two sequences give the product of the two lengths; a contiguous window within one sequence gives a square; a subtree of a rooted tree gives exactly one per node.
- Require that each subproblem is answerable from smaller ones alone. If answering it needs something the same size or larger, the dependencies contain a cycle, there is no order that respects them, and the decomposition has to change rather than the code.
- Read the running time off the edges. The work is visiting each subproblem once, looking at what feeds into it, and usually doing a fixed amount per incoming edge — so the total is the number of edges, and a decomposition with too many dependencies is expensive for a reason you can see before implementing it.
- Retain a value only while something still unsolved depends on it. A layered dependency structure that appears to need a full grid frequently needs two rows, because everything older has already been consumed, and that reduction is available whenever the dependencies reach back a bounded distance.
- Store which choice produced each value, not only the value. Without it you can report what the best answer costs and not what it is, and reconstructing it afterwards means solving the problem again — it is dull bookkeeping and it is the difference between an answer and a number.
- Reach for this after the specialised methods have failed, not before. It applies far more widely than the techniques that exploit a particular structure, and it pays for that generality in both time and memory, so a problem that yields to a structural argument should be solved that way.

## Don't
- Don't start by writing the recurrence. The recurrence is a consequence of the subproblem definition, and starting there means committing to a decomposition before checking whether it has the properties that make it work.
- Don't define the subproblems in terms of the answer you want. A subproblem has to be a question you could ask independently and look up, and one phrased as "the part of the best solution that lies here" cannot be evaluated without already knowing the solution.
- Don't confuse a subproblem count with a running time. The count sets the table size; the running time is the count multiplied by what each one costs, and a decomposition with few subproblems that each scan everything can be the slower of two candidates.
- Don't hold the entire table because it was convenient to allocate. Memory is the usual reason this technique is rejected in practice, and the value that must be retained is often a small frontier rather than the whole history.

## Checklist
- Which of the standard shapes is your subproblem, and how many does that give?
- Can every subproblem be answered from strictly smaller ones?
- How many dependency edges are there, and what work happens per edge?
- Which values can be discarded once the subproblems consuming them are done?
- Do you record the choice as well as the cost, so the answer can be reported?

## Notes
The dependency graph here is never handed to you. It is created by the definition you choose, its nodes are the subproblems you named, and its edges are the places one answer feeds another — which is why the definition is the design and everything after it is consequence. Two people solving the same problem this way can produce structures of completely different sizes, and the difference shows up as the running time.

It is worth noticing how little of the machinery depends on what is being computed. Taking a minimum of sums over the incoming edges solves one problem; taking a maximum solves another; taking a product solves a third — the traversal, the ordering, and the cost analysis are identical in all three. That is the sense in which this is a general technique rather than a family of tricks, and it is also the warning: generality of that kind usually means paying more than a method built for the specific structure would have cost.
