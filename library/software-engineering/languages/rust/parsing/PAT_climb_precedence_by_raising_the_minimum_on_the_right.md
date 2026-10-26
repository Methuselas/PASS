---
object_id: PAT_climb_precedence_by_raising_the_minimum_on_the_right
object_type: pattern
name: Climb Precedence by Raising the Minimum on the Right-Hand Parse
library_path: [software-engineering, languages, rust, parsing]
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags: [rust, parsing, recursive_descent, precedence_climbing, associativity]
cross_links:
- rel: related_to
  target_object_id: PAT_scan_variable_length_rust_tokens_with_peekable_lookahead
reference: {source_title: Practical System Programming for Rust Developers, author: Prabhu Eshwarla}
confidence: medium
references: []
variants: []
---

# Climb Precedence by Raising the Minimum on the Right-Hand Parse

## Pattern Rule
**IF** a Rust parser must turn infix operators with several precedence levels into a tree
**THEN** use one precedence-climbing routine parameterized by the minimum precedence the caller will accept, and make associativity an explicit choice in the threshold passed to the right-hand parse.

## Do
- Parse one operand first, then keep consuming infix operators while the current operator binds more tightly than the caller's minimum.
- Give each operator an explicit precedence value. An ordered fieldless enum can work well when declaration order exactly matches semantic precedence.
- Derive the right-hand threshold from associativity. With a strict-greater loop such as the source uses, parsing the right side at the current operator's precedence yields left association; allowing the right side to admit an equal-precedence operator yields right association.
- Parse prefix operators and parenthesized expressions in the operand step so the infix loop only combines complete operands.
- Test associativity independently from precedence with chains such as `8/4/2`, `2-2-2`, and `2^3^2`.

## Don't
- Don't infer associativity from comments or intended mathematics; derive it from the loop comparison and the threshold passed into recursion.
- Don't change `<` to `<=`, or change the recursive threshold, without re-running isolated associativity tests; those two choices jointly determine grouping.
- Don't duplicate one recursive function per precedence level when a single minimum-precedence parameter expresses the same grammar more clearly.

## Checklist
- Does each operator have a documented precedence and associativity?
- Does an isolated same-operator chain produce the intended tree shape?
- Are parentheses and prefix operators handled before the infix loop combines operands?
- Would changing one precedence value fail a focused test rather than silently alter results?

## Notes
The source evaluator uses a single recursive `generate_ast` function whose loop continues while the current operator outranks the supplied precedence. That compact shape correctly captures precedence, but its exponent path also demonstrates the trap: the golden expression can pass while a same-operator chain groups in the wrong direction. Test precedence and associativity separately.
