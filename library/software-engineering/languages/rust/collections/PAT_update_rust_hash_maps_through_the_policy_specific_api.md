---
object_id: PAT_update_rust_hash_maps_through_the_policy_specific_api
object_type: pattern
name: Update Rust Hash Maps Through the Policy-Specific API
library_path: [software-engineering, languages, rust, collections]
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags: [rust, hashmap, entry, updates, ownership]
cross_links:
- rel: related_to
  target_object_id: PAT_choose_the_data_structure_for_the_dominant_access_pattern
reference: {source_title: The Rust Programming Language, author: Steve Klabnik and Carol Nichols}
confidence: medium
references: []
variants: []
---

# Update Rust Hash Maps Through the Policy-Specific API

## Pattern Rule
**IF** inserting a Rust hash-map key should unconditionally replace any old value
**THEN** use `insert`
**ELSE** use the entry API when the update depends on whether the key is vacant or occupied.

## Do
- Decide explicitly whether duplicate keys replace, preserve, initialize, or combine values.
- Use entry insertion helpers for defaults that should run only when vacant.
- Mutate the reference returned by an entry operation when combining with the existing value.
- Remember that owned keys and values move into the map unless copied or borrowed intentionally.

## Don't
- Don't perform a separate contains check followed by lookup or insertion when one entry operation expresses the transition.
- Don't ignore the previous-value result from `insert` when replacement itself must be observed.
- Don't insert borrowed data without ensuring its owners outlive the map.

## Checklist
- What should happen when the key already exists?
- Is default construction needed only for a vacant entry?
- Must the previous value be observed?
- Should the map own the key and value?

## Notes
Hash-map updates are state transitions. Rust's insert and entry APIs encode distinct duplicate-key policies while avoiding redundant lookup and borrow conflicts.
