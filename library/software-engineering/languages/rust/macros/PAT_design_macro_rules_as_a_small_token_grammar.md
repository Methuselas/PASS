---
object_id: PAT_design_macro_rules_as_a_small_token_grammar
object_type: pattern
name: Design macro_rules as a Small Token Grammar
library_path: [software-engineering, languages, rust, macros]
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags: [rust, macro_rules, declarative_macros, grammar, hygiene]
cross_links:
- rel: related_to
  target_object_id: PAT_choose_a_rust_macro_only_for_syntax_level_generation
reference: {source_title: The Rust Programming Language, author: Steve Klabnik and Carol Nichols}
confidence: high
references: []
variants: []
---

# Design macro_rules as a Small Token Grammar

## Pattern Rule
**IF** a Rust syntax abstraction can be expressed as a bounded set of token patterns and repetitions
**THEN** define each `macro_rules!` arm as a narrow grammar production, transcribe captures at matching repetition depth, and make hygiene and evaluation behavior explicit
**ELSE** use a procedural macro or an ordinary typed API instead of stretching token matching into an implicit parser.

## Do
- Give each arm one recognizable input form and use the narrowest fragment specifier that represents it.
- Put separators and repetition operators in the matcher deliberately, including whether zero, one, or many elements and a trailing separator are accepted.
- Use captured fragments at compatible repetition nesting in the transcriber so every generated element has an unambiguous source.
- Wrap expression expansions in a block when the macro needs private temporary bindings, and bind a caller expression once when repeated evaluation would be surprising.
- Start paths to support-crate items with `$crate` and a fully qualified module path; remember that visibility rules still apply.
- Compile-test accepted forms, boundary arities, nested calls, name collisions, and malformed invocations with expected diagnostics.

## Don't
- Don't treat macro matchers as value patterns; they match token structure and fragment categories before ordinary type checking.
- Don't use a broad token-tree capture when a narrower expression, type, path, item, or identifier contract is intended.
- Don't emit unqualified helper names and assume the invocation site imported them.
- Don't make a declarative macro parse an open-ended language through increasingly opaque token munching when structured procedural parsing would be clearer.
- Don't assume a fragment specifier means exactly the same syntax across editions.

## Checklist
- What grammar production does each arm accept?
- Which separator and repetition cardinality are part of the public syntax?
- Do matcher and transcriber repetitions nest compatibly?
- Can any input expression be evaluated more than once?
- Are helper paths rooted with `$crate` and publicly reachable?
- Which edition defines the fragment semantics?

## Notes
A declarative macro is easier to maintain when read as a grammar rather than as compressed code. Narrow productions improve both ambiguity handling and error locality. The expansion should remain small enough that a caller can predict the generated shape without mentally executing a parser.
