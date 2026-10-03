---
object_id: PAT_choose_a_rust_collection_by_access_and_update_semantics
object_type: pattern
name: Choose a Rust Collection by Access and Update Semantics
library_path: [software-engineering, languages, rust, collections]
stage_binding: 0 design
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags: [rust, collections, vec, string, hashmap]
cross_links:
- rel: related_to
  target_object_id: PAT_choose_the_data_structure_for_the_dominant_access_pattern
reference: {source_title: The Rust Programming Language, author: Steve Klabnik and Carol Nichols}
confidence: medium
references: []
variants: []
---

# Choose a Rust Collection by Access and Update Semantics

## Pattern Rule
**IF** Rust data is a homogeneous ordered sequence addressed by position
**THEN** use a vector, using an owned string instead when the sequence is specifically mutable UTF-8 text
**ELSE** use a hash map when values are retrieved and updated by unique keys rather than positions.

## Do
- Use a vector for growable contiguous elements of one type and iterate instead of manually managing indexes when processing all elements.
- Use an owned string for growable UTF-8 text and a string slice for a borrowed text view.
- Use a hash map when key lookup expresses the domain better than numeric position.
- Encode a known closed set of heterogeneous payloads in an enum before storing them in one vector.

## Don't
- Don't use a map when stable sequence order or positional access is the actual requirement.
- Don't treat a string as an arbitrary byte vector when operations mean human text.
- Don't erase element types merely to place a known closed set in one vector.

## Checklist
- Is lookup by position, text boundary, or key?
- Must ordering be preserved?
- Is the element set homogeneous or a closed enum of alternatives?
- Who should own the stored values?

## Notes
Collection choice fixes lookup, ordering, ownership, and update behavior together. Choose from the operations the domain needs, then use the collection API that expresses those operations directly.
