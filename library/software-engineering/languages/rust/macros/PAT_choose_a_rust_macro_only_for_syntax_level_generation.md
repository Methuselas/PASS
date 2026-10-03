---
object_id: PAT_choose_a_rust_macro_only_for_syntax_level_generation
object_type: pattern
name: Choose a Rust Macro Only for Syntax-Level Generation
library_path: [software-engineering, languages, rust, macros]
stage_binding: 0 design
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags: [rust, macros, metaprogramming, api_design, code_generation]
cross_links:
- rel: related_to
  target_object_id: PAT_define_your_code_contract_explicitly
- rel: related_to
  target_object_id: PAT_dont_widen_api_for_reuse_or_testing
reference: {source_title: The Rust Programming Language, author: Steve Klabnik and Carol Nichols}
confidence: high
references: []
variants: []
---

# Choose a Rust Macro Only for Syntax-Level Generation

## Pattern Rule
**IF** an abstraction must accept or generate Rust syntax, vary its syntactic arity, or create compile-time items that a function cannot express
**THEN** expose the smallest macro surface that performs that syntax transformation and delegate ordinary runtime behavior to typed functions
**ELSE** use a function, trait, generic, or ordinary type so callers receive the simpler typed interface.

## Do
- State the capability that requires expansion, such as generating implementations, accepting a token-level mini-language, or creating a variable number of syntax elements.
- Define the accepted input grammar, generated items or expression shape, evaluation behavior, name-resolution assumptions, and diagnostics as the macro's public contract.
- Keep expansion thin: parse and validate syntax, emit the needed glue, and call ordinary typed code for runtime work.
- Choose a declarative macro for bounded token patterns and repetition; choose a procedural macro when the transformation needs structured parsing or semantic validation of richer syntax.
- Test successful calls and intentional compile failures at the public invocation boundary.

## Don't
- Don't choose a macro merely to avoid writing a normal function or generic bound.
- Don't hide ordinary business logic inside generated tokens where type signatures, tests, and debuggers cannot expose it directly.
- Don't duplicate or reorder a caller expression unless the public contract makes evaluation count and order explicit.
- Don't assume generated names and paths resolve where the macro was defined; verify the hygiene and lookup rules for the macro kind.

## Checklist
- What can expansion express that a function or trait cannot?
- Is the accepted syntax smaller and clearer than the code it replaces?
- How many times is each caller expression evaluated?
- Which names resolve at the definition site and which at the invocation site?
- What error will a caller see for malformed or unsupported input?
- Can runtime behavior be delegated to an ordinary testable function?

## Notes
Macros trade a conventional typed call boundary for compile-time syntax transformation. That trade is justified when syntax is the actual input or output; otherwise it adds parsing, expansion, hygiene, diagnostic, and tooling costs without buying a capability that ordinary Rust lacks.
