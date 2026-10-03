---
object_id: PAT_use_a_rust_raw_identifier_only_for_a_name_you_must_preserve
object_type: pattern
name: Use a Rust Raw Identifier Only for a Name You Must Preserve
library_path: [software-engineering, languages, rust, bindings]
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags: [rust, identifiers, keywords, editions, interoperability]
cross_links:
- rel: related_to
  target_object_id: PAT_choose_rust_paths_by_the_relationship_to_the_target
- rel: related_to
  target_object_id: PAT_import_rust_names_at_the_level_that_preserves_context
reference: {source_title: The Rust Programming Language, author: Steve Klabnik and Carol Nichols}
confidence: high
references: []
variants: []
---

# Use a Rust Raw Identifier Only for a Name You Must Preserve

## Pattern Rule
**IF** a Rust boundary must preserve an externally fixed name that is a keyword in the active edition
**THEN** spell that identifier with the `r#` prefix at every Rust use site and contain the spelling at the boundary
**ELSE** choose an ordinary non-keyword name that communicates the domain meaning directly.

## Do
- Check the crate's edition before diagnosing the collision; keyword status can change across editions.
- Prefix the required name with `r#` in definitions and references. Treat the prefix as Rust syntax, not as part of the identifier's underlying name.
- Use raw identifiers for genuine compatibility boundaries, such as calling an older-edition API, binding an external schema, or preserving a generated interface.
- Alias an imported raw identifier to a clear ordinary name when the external spelling does not need to spread through internal code.
- During an edition migration, run the edition compatibility tooling and review every automatic raw-identifier rewrite, especially inside macro input.

## Don't
- Don't use a raw identifier merely to keep a vague or misleading local name when renaming is under your control.
- Don't assume every keyword has a legal raw form; `_`, `crate`, `self`, `Self`, and `super` remain reserved in raw-identifier position.
- Don't rewrite strings, protocol fields, or foreign symbols with `r#`; the prefix belongs to Rust source syntax only.
- Don't infer that the prefix creates a different exported or linked name. It preserves an identifier that Rust's parser would otherwise reject.

## Checklist
- Which edition parses this crate?
- Is the colliding name fixed by an external or compatibility contract?
- Where can the raw spelling be contained or aliased?
- Are all Rust references to the preserved identifier spelled consistently?
- Did edition-migration tooling change macro input or generated-code expectations?

## Notes
Raw identifiers are an escape hatch for naming compatibility, not a general naming style. They are especially useful when a newer edition reserves a word that an older crate exposed as an item name: the newer caller can preserve the same underlying name while making the token unambiguous to its parser.
