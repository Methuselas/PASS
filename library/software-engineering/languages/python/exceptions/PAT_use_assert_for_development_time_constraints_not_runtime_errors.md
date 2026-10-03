---
object_id: PAT_use_assert_for_development_time_constraints_not_runtime_errors
object_type: pattern
name: Use assert for Development-Time Constraints, Not Runtime Error Handling
library_path:
- software-engineering
- languages
- python
- exceptions
stage_binding: 2 block
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- python
- exceptions
- assert
- contracts
cross_links:
- rel: related_to
  target_object_id: PAT_enforce_contracts_at_runtime_with_checks
- rel: related_to
  target_object_id: PAT_declare_a_required_subclass_method_with_abstractmethod
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Use assert for Development-Time Constraints, Not Runtime Error Handling

## Pattern Rule
**IF** a condition is a constraint you are checking during development — an assumption about your own code that should never be false if the program is correct
**THEN** express it with `assert`, accepting that assert statements can be stripped from a program run in optimized mode and so provide no protection once that happens
**ELSE** when the condition reflects something that can legitimately go wrong at runtime — bad input, a failed operation, a resource that may be unavailable — handle it with ordinary exception handling instead, because that code must run regardless of how the program is launched

## Do
- Reach for `assert` to flag violations of your own code's internal assumptions, the kind a passing test suite should never actually trigger.
- Let Python's own runtime checks catch ordinary errors — out-of-range indexing, division by zero, missing keys — instead of duplicating them in an `assert`; the built-in check already raises on the same condition.
- Use `assert`'s optional message argument to say what was assumed, so a tripped assertion explains the broken assumption rather than just the failing expression.

## Don't
- Don't use `assert` to validate data your program cannot control, such as user input or a value read from a file or network; stripping asserts in optimized mode would silently remove that validation.
- Don't write an `assert` whose condition duplicates a check the language already performs automatically, since the automatic check fires regardless of optimization mode and the assert adds nothing.
- Don't put an `assert` condition where evaluating it has a side effect the surrounding code depends on; a stripped assert then changes program behavior, not just its error checking.

## Checklist
- Is this `assert` checking an assumption about the code's own correctness, rather than about data the program received from outside?
- Would removing every `assert` in this module, as optimized mode does, remove any check this program still needs to run?
- Does the assert's condition have any side effect the rest of the code relies on?

## Notes
`assert` is syntactic sugar for a conditional raise guarded by a flag the interpreter sets, which is why it can vanish under an optimization switch in a way an ordinary `raise` cannot: the flag that would have triggered it is simply false, and the whole statement compiles away. That mechanism is exactly what makes `assert` the right tool for internal, development-time assumptions and the wrong one for anything the shipped program still needs to check — a validation that disappears under one command-line flag was never actually enforcing anything in production.
