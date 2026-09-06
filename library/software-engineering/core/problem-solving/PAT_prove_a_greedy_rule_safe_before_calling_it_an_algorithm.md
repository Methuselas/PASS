---
object_id: PAT_prove_a_greedy_rule_safe_before_calling_it_an_algorithm
object_type: pattern
name: Prove a Greedy Rule Safe Before Calling It an Algorithm
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
- greedy
- correctness
- optimization
cross_links:
- rel: related_to
  target_object_id: PAT_decide_whether_the_split_or_the_combine_does_the_work
- rel: related_to
  target_object_id: PAT_make_only_forced_moves_so_failure_proves_there_was_no_solution
reference:
  source_title: Algorithms
  author: Sanjoy Dasgupta, Christos Papadimitriou, Umesh Vazirani
confidence: high
references: []
variants: []
---

# Prove a Greedy Rule Safe Before Calling It an Algorithm

## Pattern Rule
**IF** you are building a solution piece by piece, each time taking whatever looks best at that moment and never reconsidering it
**THEN** show that a choice made by your rule always leaves at least one best solution reachable, and where you cannot show it, describe what you have as a heuristic rather than as an algorithm that returns the best answer.

## Do
- Argue it by exchange, which is the shape that works. Assume a best solution that does not contain the piece your rule just picked. Add that piece to it, which must create a conflict — a cycle, an overlap, a violated capacity — because otherwise the solution was not maximal. Remove a conflicting piece. Then show what remains is still a valid solution and costs no more than the one you started with.
- State the safety condition over a boundary rather than over a step, because that is what makes it reusable. Phrasing it as "the cheapest link joining any group of nodes to everything outside that group is always safe to take" says nothing about the order pieces are considered in, and so covers every procedure that respects it.
- Notice that a proved condition hands you a family rather than one procedure. Growing a single connected region outward and sorting all links by weight and taking each one that does not close a cycle look like different algorithms, and are the same schema with different rules for choosing the boundary; both are correct the moment the condition is, and neither needs its own proof.
- Keep the counterexample when the argument fails. Choosing the site that covers the most uncovered towns is a rule that feels unarguable and returns four schools on a map that three would serve — a concrete failing input is worth more than a vague suspicion, and it is what stops the rule being quietly promoted back to optimal later.
- Say which of the two you are shipping. A rule that is fast, reasonable and unproved is often the right thing to deploy; describing it as the one that finds the best answer is what causes the damage downstream, where somebody builds on a guarantee nobody made.

## Don't
- Don't accept agreement with a brute-force check on small inputs as proof. It is a useful way to find a counterexample and no evidence at all that none exists, and the inputs where a plausible rule fails are frequently larger than the ones anybody enumerated.
- Don't argue from the rule feeling unarguable. The strongest intuition in this family — take the biggest immediate gain — is exactly the one with a standing counterexample, and the feeling of obviousness is a property of the rule rather than of the problem.
- Don't quietly extend a proved rule to a variant problem. The condition was proved about a specific structure and a specific cost, and adding a capacity limit, a second objective, or a precedence constraint can invalidate it without changing a line of the code.
- Don't discard an unproved rule as worthless. For a great many problems no efficient procedure returns the best answer at all, and the piece-by-piece rule is then the practical answer; it just needs to be labelled and measured rather than trusted.

## Checklist
- Can you state, in one sentence, the condition that makes each choice safe?
- Does the exchange argument close — insert your choice, remove the conflict, and the result is still valid and no worse?
- Is the condition phrased over a boundary or structure, so more than one procedure satisfies it?
- If the argument does not close, do you have the failing input written down?
- Does the code, the interface, or the documentation claim optimality you have not shown?

## Notes
The reason this needs saying is that the rules in this family are unusually persuasive. Repeatedly taking the cheapest available link really does produce the cheapest possible network; repeatedly taking the site that covers the most uncovered towns really does not produce the smallest set of sites, and no amount of staring at the two rules distinguishes them. The proof is the only discriminator, which makes attempting it a design step rather than a formality — and attempting it is cheap, because the exchange argument either closes in a few lines or fails in a way that hands you the counterexample.

There is a second payoff that is easy to miss. Because the proof is about a condition rather than about a procedure, it covers everything that respects the condition — including procedures nobody has written yet. That turns one argument into a licence to choose an implementation on other grounds entirely, such as which data structure the surrounding system already maintains, without reopening the correctness question each time.
