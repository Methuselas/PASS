---
object_id: PAT_separate_parsing_stages_by_representation_boundary
object_type: pattern
name: Separate Parsing Stages by Representation Boundary
library_path:
- software-engineering
- core
- design
stage_binding: 0 design
lane_fit: both
foundation_role: foundation
routing_class: general
specialization_axis: none
foundation_object_id: none
tags:
- parsing
- tokenization
- ast
- representation
- pipeline
cross_links:
- rel: related_to
  target_object_id: PAT_choose_a_problem_representation_before_solving
- rel: related_to
  target_object_id: PAT_design_modular_interfaces
reference:
  source_title: Practical System Programming for Rust Developers
  author: Prabhu Eshwarla
confidence: medium
references: []
variants: []
---

# Separate Parsing Stages by Representation Boundary

## Pattern Rule
**IF** free-form input must pass through lexical rules, structural rules, and domain evaluation
**THEN** separate those responsibilities at representation boundaries so each stage consumes one explicit representation and produces the next

## Do
- Turn raw input into tokens before applying structural precedence or nesting rules when lexical recognition and grammar are distinct concerns.
- Build an explicit structural representation, such as an AST, before evaluation when later behavior depends on hierarchy rather than source order.
- Give each stage a narrow contract: text to tokens, tokens to structure, structure to result.
- Test malformed input at the stage that can name the failure most precisely instead of waiting for a downstream generic failure.

## Don't
- Don't mix character scanning, precedence handling, and evaluation in one state machine when they obey different invariants.
- Don't discard an intermediate representation merely to save a type if later stages need information it made explicit.
- Don't let a downstream evaluator reinterpret raw syntax that the parser was supposed to settle.

## Checklist
- What representation enters and leaves each stage?
- Which stage owns lexical validity, structural validity, and domain validity?
- Can each stage be tested without driving the whole application?
- Does the intermediate structure preserve the ordering or nesting facts evaluation needs?

## Notes
The useful boundary is not specific to compilers. Configuration languages, query parsers, template engines, protocol decoders, and expression evaluators all become easier to reason about when representation changes are explicit rather than hidden inside one monolithic routine.
