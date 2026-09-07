---
object_id: AP_get_a_usable_answer_to_an_intractable_problem
object_type: ap
name: Get a Usable Answer to an Intractable Problem
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
- intractability
- approximation
- search
cross_links:
- rel: supports
  target_object_id: PAT_find_the_real_constraints_before_calling_it_impossible
- rel: supports
  target_object_id: PAT_check_whether_the_problem_is_a_known_hard_one_in_disguise
- rel: supports
  target_object_id: PAT_check_whether_a_new_constraint_crosses_the_tractability_line
- rel: supports
  target_object_id: PAT_reduce_your_problem_to_one_that_is_already_solved
- rel: supports
  target_object_id: PAT_define_the_subproblems_and_let_their_dependencies_set_the_order
- rel: supports
  target_object_id: PAT_prune_a_partial_candidate_before_you_finish_building_it
- rel: supports
  target_object_id: PAT_prove_a_greedy_rule_safe_before_calling_it_an_algorithm
- rel: supports
  target_object_id: PAT_state_the_approximation_guarantee_you_actually_have
- rel: supports
  target_object_id: PAT_return_a_certificate_the_answer_can_be_checked_against
reference:
  source_title: Algorithms
  author: Sanjoy Dasgupta, Christos Papadimitriou, Umesh Vazirani
confidence: high
references: []
variants: []
---

# Get a Usable Answer to an Intractable Problem

## Objective
Deliver a working answer to a problem that has no efficient exact method, together with an explicit statement of what was given up to get it. The action is complete when something ships and the guarantee attached to it is stated in terms a caller can build on. It is not complete when the search has merely been abandoned, and it is not complete when an answer is produced whose limits nobody has written down.

## Steps / Flow

**Entry state.** A problem resists solution, effort is being spent looking for a method, and nobody has yet established whether one exists.

**1. Audit the boundary before concluding anything about the problem.** Sort the constraints genuinely imposed from the ones assumed, as `PAT_find_the_real_constraints_before_calling_it_impossible` directs. **Gate:** do not proceed until the boundary is established rather than inherited. Most problems that look impossible are being solved inside too small a one, and everything below is wasted effort if that is the case here.

**2. Establish hardness by construction rather than by fatigue.** Attempt the mapping in the hardness direction under `PAT_check_whether_the_problem_is_a_known_hard_one_in_disguise`. **Branch:** if the mapping cannot be built, this protocol does not apply — the problem is unsolved rather than shown hard, and the work returns to ordinary algorithm design. **Gate:** a successful mapping, not an exhausted search.

**3. Name what may be given up, and have it priced by whoever owns the requirement.** The remaining steps each surrender something different — the generality of the inputs, the worst-case running time, exactness, or the guarantee itself — and which of those is acceptable is not an engineering decision. Use `PAT_check_whether_a_new_constraint_crosses_the_tractability_line` in reverse: the constraint that pushed this problem across the line is the one whose removal would bring it back. **Branch:** where a requirement turns out to be negotiable, the problem may leave this protocol entirely.

**4. Give up generality first, because it costs the least.** Ask whether the instances you actually receive carry structure the general problem lacks — a restricted shape, a bounded parameter, a form that arises from how the input is generated. Where they do, an exact efficient method may already exist for that restriction: route through `PAT_reduce_your_problem_to_one_that_is_already_solved` when the restricted case maps onto a solved problem, and `PAT_define_the_subproblems_and_let_their_dependencies_set_the_order` when the structure itself supplies an ordering. **Gate:** you can characterise the instances you receive, *and* the restriction is known to preserve tractability. **Branch:** many restrictions preserve the hardness instead, and a restriction you cannot characterise is not one you can rely on — either failure sends you to step 5.

**5. Give up worst-case running time next, keeping exactness.** Search by building candidates and killing them early, under `PAT_prune_a_partial_candidate_before_you_finish_building_it`. **Invariant:** the answer returned is still exactly the best one; only the time to find it is unbounded. **Gate:** a time limit and a defined result when it expires, because an unbounded search inside a bounded system is a failure mode rather than a method. **Branch:** where the limit is hit routinely on real inputs, treat that as this step having failed and continue to 6.

**6. Give up exactness, keeping a proof.** Build a method that is fast and provably close, using `PAT_prove_a_greedy_rule_safe_before_calling_it_an_algorithm` to establish what its choice rule does and does not guarantee. **Gate:** a ratio proved over every input, recorded under `PAT_state_the_approximation_guarantee_you_actually_have`. Check whether a better ratio is attainable at all before spending effort on one, because for some problems the factor you already have is the best any efficient method will reach.

**7. Give up the proof last.** A method with no bound on time or quality is legitimate and common, and it is the step taken when 4 through 6 are unavailable. It carries one obligation, which `PAT_state_the_approximation_guarantee_you_actually_have` owns: it is measured rather than argued, and described in the vocabulary of measurement rather than of proof. **Branch:** where the quantity wanted is a count rather than an optimum, this step has its own method — an unbiased random estimator under `PAT_estimate_a_count_by_random_sampling_when_enumeration_is_intractable`, whose accuracy is a property of the distribution over many runs rather than of any single one. It sits here rather than at step 6 because it has no per-run bound to prove, and the obligation to describe it in the vocabulary of measurement is the same.

**8. Attach what can be checked, wherever you stopped.** Whatever guarantee survives, ask under `PAT_return_a_certificate_the_answer_can_be_checked_against` whether the answer can carry a cheap witness — a bound met from the other side, a structure whose validity is verifiable by arithmetic. This is available at every step above and matters most at the weakest ones, where the answer is least trustworthy on its own.

**Completion.** An answer ships, and one sentence records which of generality, worst-case time, exactness, or guarantee was surrendered, along with what remains provable about the result. If that sentence cannot be written, the action is not finished regardless of what the code returns.

## Notes
The order is by cost of the concession rather than by difficulty of implementation, and each step is entered only when the one above it is genuinely unavailable. Restricting the inputs costs the least because it surrenders nothing about the answers you do return; abandoning the guarantee costs the most because it removes the caller's ability to reason about the result at all. A team that starts at the last step because it is the easiest to build has usually skipped a restriction that would have made the problem exactly solvable on the only instances it will ever see.

Two of the steps fail in ways that look like success. A restriction nobody can characterise precisely will appear to work until an uncharacterised instance arrives; a bounded search will appear fast until an input that prunes badly arrives. Both surface in production rather than in development, which is the argument for the gates being explicit rather than assumed.

This protocol says nothing about which technique is best for a given problem, and it should not. It orders the concessions, and the methods that implement each one are owned by their own decisions and change far more often than the ordering does.
