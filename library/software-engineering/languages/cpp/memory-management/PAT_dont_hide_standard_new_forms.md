---
object_id: PAT_dont_hide_standard_new_forms
object_type: pattern
name: Don't Let Class-Specific new Hide the Standard Forms
library_path:
- software-engineering
- languages
- cpp
- memory-management
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- cpp
- memory_management
- name_hiding
- placement_new
cross_links:
- rel: related_to
  target_object_id: PAT_unhide_inherited_names_with_using
- rel: related_to
  target_object_id: AP_replace_new_and_delete_for_a_named_reason
reference:
  source_title: 'Effective C++, Third Edition: 55 Specific Ways to Improve Your Programs and Designs'
  author: Scott Meyers
confidence: high
references: []
variants: []
---

# Don't Let Class-Specific new Hide the Standard Forms

## Pattern Rule
**IF** you declare any operator new in a class
**THEN** treat the class allocation functions as an overload family: declare and test every normal, nothrow, placement, aligned, sized, and array form the class intentionally supports, with a matching deallocation path for each allocation path.

## Do
- Keep the overload family beside the class or in a deliberately reviewed allocation base, and forward uncustomized forms to the matching global function.
- Include `std::align_val_t` forms when over-aligned instances may reach the class allocator, and include matching sized/aligned delete overloads required by the supported toolchains and calling forms.
- Pair each placement form's extra parameter list with the corresponding placement delete so constructor failure can release the storage.

## Don't
- Don't declare one class operator new and assume global overloads remain candidates; class-scope allocation lookup hides them.
- Don't copy the old three-form recipe unchanged. Alignment-aware allocation added another dimension to the overload family.

## Checklist
- Does declaring a class operator new hide standard forms clients still expect?
- Are normal, nothrow, placement, alignment-aware, sized, and array cases either supported or intentionally rejected?
- Does each re-exposed or custom operator new have a matching operator delete?

## Notes
Member names hide same-named names in enclosing scopes, so one class allocation declaration changes lookup for the whole family. The historical recipe counted normal, placement, and nothrow forms. Modern code must also account for alignment-aware and sized deallocation signatures, plus arrays if the class permits them. The safest default is not to replace class allocation at all; when a measured requirement justifies it, make the supported family explicit and test each new-expression form rather than relying on a memorized list.
