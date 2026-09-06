---
object_id: PAT_make_only_forced_moves_so_failure_proves_there_was_no_solution
object_type: pattern
name: Make Only Forced Moves, So Failure Proves There Was No Solution
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
- constraints
- invariant
- search
cross_links:
- rel: related_to
  target_object_id: PAT_prove_a_greedy_rule_safe_before_calling_it_an_algorithm
- rel: related_to
  target_object_id: PAT_find_the_real_constraints_before_calling_it_impossible
reference:
  source_title: Algorithms
  author: Sanjoy Dasgupta, Christos Papadimitriou, Umesh Vazirani
confidence: high
references: []
variants: []
---

# Make Only Forced Moves, So Failure Proves There Was No Solution

## Pattern Rule
**IF** you are looking for an assignment, schedule, or configuration that satisfies a set of constraints, and some constraints compel a value while others forbid one
**THEN** start from the most conservative state and change something only where a constraint leaves you no alternative, repeating until nothing further is compelled — the state you reach is contained in every valid solution, so if it breaks a remaining constraint there is no valid solution to find.
**ELSE** where the next step is a genuine choice rather than a compulsion, this technique has done all it can, and the remainder needs search with the ability to take a decision back.

## Do
- Pick the conservative starting state deliberately, meaning the one that satisfies the forbidding constraints for free. Setting every value to false costs nothing against constraints that demand something be false, which is what leaves the compelling constraints as the only reason to move.
- Move only under compulsion, and record why. A rule saying that if these three things hold then this fourth must too is a reason; a rule saying this value would be convenient is not, and admitting the second kind is what destroys the guarantee.
- Keep the invariant stated where the code can be read against it: everything changed so far is changed the same way in every valid solution. That single sentence is the whole correctness argument, and it is worth a comment because nothing in the loop body implies it.
- Test the forbidding constraints only after propagation has finished. Checking them early can reject a state that later compulsions would have moved past, and the order is load-bearing rather than stylistic.
- Recognise the shape when it appears under another name. Deducing types from usage, deriving what must be true from a set of implications, and simplifying a formula by repeatedly applying the clauses that leave one option are all the same procedure, and they share both the guarantee and its limit.

## Don't
- Don't take a move because it appears safe or symmetric. Safe means every solution makes it, and a move made for any weaker reason breaks the invariant silently — the run still produces an answer, and the answer no longer proves anything about the cases it rejects.
- Don't report unsatisfiable from a run that guessed anywhere. Once a free choice enters, a failure is evidence about that branch and not about the problem, and the two conclusions are easy to confuse because the code path is identical.
- Don't expect it to finish the job in general. It resolves what the constraints determine, and where the constraints leave real freedom it stops with the problem partly solved — which is a correct result and not a bug to work around.
- Don't discard the partial state when it stops. Everything it established still holds in every solution, so a search that follows it starts from a smaller problem rather than from the beginning.

## Checklist
- Which state satisfies the forbidding constraints before anything moves?
- For each move the loop makes, which constraint compels it?
- Can you state the invariant in one sentence, and does the code read as though it holds?
- Are the forbidding constraints checked only after nothing further is compelled?
- If the run reports no solution, did it make any choice that was not forced?

## Notes
What earns this a place is the strength of the negative result, which is unusual. Most procedures that fail to find something have shown only that they did not find it; this one shows that nothing was there. The strength comes entirely from the invariant, and the invariant survives only while every step is compelled — which is why the discipline about what counts as compulsion is not pedantry but the thing being paid for.

The limit is worth being equally clear about, because the technique tends to be oversold once it has worked a few times. It exhausts what the constraints determine and then stops. A problem whose constraints determine everything is solved outright; a problem whose constraints determine nothing gets no benefit; the common case is in between, where this reduces the problem before search begins and the reduction is often large enough to change what is feasible. Ordering matters here in a way that is easy to get wrong from the outside: the compelling constraints are run to exhaustion first, and only then are the forbidding ones consulted, because a state that looks doomed partway through propagation may be nothing of the kind.
