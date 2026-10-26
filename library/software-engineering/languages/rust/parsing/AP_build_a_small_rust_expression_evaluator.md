---
object_id: AP_build_a_small_rust_expression_evaluator
object_type: ap
name: Build a Small Rust Expression Evaluator
library_path: [software-engineering, languages, rust, parsing]
stage_binding: 1 skeleton
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags: [rust, parsing, ast, recursion, error_handling, cli]
cross_links:
- rel: supports
  target_object_id: PAT_scan_variable_length_rust_tokens_with_peekable_lookahead
- rel: supports
  target_object_id: PAT_climb_precedence_by_raising_the_minimum_on_the_right
- rel: supports
  target_object_id: PAT_unify_rust_errors_from_multiple_sources_with_from
- rel: related_to
  target_object_id: PAT_insert_rust_indirection_at_a_recursive_edge
- rel: related_to
  target_object_id: AP_build_a_testable_rust_cli_pipeline
reference: {source_title: Practical System Programming for Rust Developers, author: Prabhu Eshwarla}
confidence: medium
references: []
variants: []
---

# Build a Small Rust Expression Evaluator

## Objective
Build an arithmetic evaluator from text to tokens to syntax tree to numeric result so lexical boundaries, precedence, recursive representation, and error propagation remain explicit and independently testable.

## Steps / Flow
1. Define the accepted grammar before coding: numeric literal shape, operators, precedence, associativity, prefix minus, parentheses, whitespace policy, and whether constructs such as implicit multiplication are supported or rejected.
2. Define a token enum for operators, parentheses, numeric values, and end-of-input. Keep precedence as explicit data rather than scattering numeric constants through the parser.
3. Build the lexer around a a `Peekable` character iterator. Skip permitted whitespace without concatenating separated tokens, consume variable-width numeric tokens with lookahead, and reject unsupported characters at the lexical boundary.
4. Define the AST as a recursive enum whose recursive children use indirection such as `Box`, so the node type has a finite size.
5. Build the parser around the lexer and current token. Parse operands (numbers, prefix operators, parenthesized expressions), then combine infix operators with a precedence-climbing routine whose associativity is covered by focused tests.
6. Evaluate the tree recursively. Borrow the tree if callers still need it after evaluation; consume it only when ownership transfer is intentional.
7. Expose one structured pipeline error contract. Preserve whether failure came from lexing, parsing, conversion, or evaluation, and use meaningful `From` conversions only when they preserve the cause that callers still need.
8. Put a thin read-evaluate-print loop around one `evaluate` entry point. Bad user input should report through the error contract and return to the loop rather than panic or collapse every cause into one generic message.
9. Before calling the evaluator complete, run the adversarial Drill for associativity, malformed syntax, unsupported lexical forms, floating-point edge cases, oversized literals, and user-visible error reporting.

## Notes
The source chapter deliberately builds the tokenizer, parser, AST, evaluator, and custom error handling from first principles. That makes the boundaries visible enough to test separately. The durable lesson is not the exact toy grammar; it is the staged pipeline: lexical ownership first, syntax structure second, evaluation third, with one explicit error contract crossing the stages.

Floating-point arithmetic also creates valid-looking results that are not parser failures: division by zero can yield infinities or NaN, and large decimal inputs can overflow to infinity. If the application's contract rejects those values, validate the evaluated result explicitly rather than assuming parsing will reject them.
