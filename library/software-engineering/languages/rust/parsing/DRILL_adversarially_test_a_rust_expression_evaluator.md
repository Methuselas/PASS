---
object_id: DRILL_adversarially_test_a_rust_expression_evaluator
object_type: drill
name: Adversarially Test a Rust Expression Evaluator
library_path: [software-engineering, languages, rust, parsing]
stage_binding: 2 block
lane_fit: teach
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags: [rust, testing, parsing, floating_point, practice]
cross_links:
- rel: teaches
  target_object_id: AP_build_a_small_rust_expression_evaluator
- rel: teaches
  target_object_id: PAT_climb_precedence_by_raising_the_minimum_on_the_right
reference: {source_title: Practical System Programming for Rust Developers, author: Prabhu Eshwarla}
confidence: medium
references: []
variants: []
target_skill: AP_build_a_small_rust_expression_evaluator
---

# Adversarially Test a Rust Expression Evaluator

## Practice Task
Run a fixed adversarial battery against a small infix expression evaluator, record every surprising result, and turn each surprise into an explicit language or error-handling policy before changing the implementation.

## Target Skill
AP_build_a_small_rust_expression_evaluator

## Setup
Use a working evaluator that accepts one expression string and returns either a numeric result or a structured error. Keep the implementation unchanged for the first pass so the battery reveals the behavior that already exists.

## Instructions
1. Verify a golden mixed-precedence expression from the source, `1+2*3.2+(4/2-3/2)-2.11+2^4`, which should evaluate to 21.79 under the source grammar.
2. Probe associativity separately from precedence: `8/4/2`, `2-2-2`, and `2^3^2`. Record the actual grouping and compare it with the grammar you intended.
3. Try mismatched parentheses, a trailing operator, an empty expression, and unsupported characters. Confirm each failure is reported by the stage that owns it rather than by a later generic error.
4. Probe lexical-policy edges such as `.5`, exponent notation, digit separators, adjacent parenthesized expressions, and whitespace between numeric fragments. Classify each as accepted syntax or a deliberate error.
5. Probe numeric edges: division by zero, `0/0`, an extremely long decimal literal, and a value beyond exact integer representation in `f64`. Record whether the evaluator returns an error, infinity/NaN, or a rounded value.
6. Try non-ASCII digit-like characters and mixed ASCII/non-ASCII numeric input. The result must follow the lexer policy without panicking.
7. Inspect every user-visible failure. Confirm the concrete error cause survives to the boundary and that formatting the error does not itself panic or collapse every cause into one sentence.
8. For each surprise, write a one-line policy: accept, reject with a typed error, or document as an inherent numeric limitation. Apply the fixes, then rerun the entire battery.

## Success Check
- Every input terminates without an unplanned panic.
- Each operator's associativity and precedence match a written requirement.
- Unsupported lexical forms fail at the lexical or parse boundary with a specific error.
- Floating-point infinities, NaN, overflow, and precision loss each have an explicit policy.
- The final rerun preserves the source's golden result and all newly declared policies.

## Common Failures
- Testing `1+2*3` and assuming precedence coverage also proves associativity.
- Treating any returned error as sufficient without checking which stage produced it.
- Letting `unwrap` in numeric conversion turn unusual input into a process abort.
- Mistaking floating-point representation behavior for a parser bug.

## Notes
The source evaluator's happy-path example is not enough to establish the grammar. Same-operator chains and malformed lexical input exercise different contracts than mixed precedence. The purpose of the battery is to force those contracts into the open before more syntax is added.
