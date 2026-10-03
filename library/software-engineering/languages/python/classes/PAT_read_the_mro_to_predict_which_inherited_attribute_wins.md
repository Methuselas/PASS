---
object_id: PAT_read_the_mro_to_predict_which_inherited_attribute_wins
object_type: pattern
name: Read the MRO to Predict Which Inherited Attribute Wins
library_path:
- software-engineering
- languages
- python
- classes
stage_binding: 2 block
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- python
- classes
- multiple-inheritance
- mro
cross_links:
- rel: related_to
  target_object_id: PAT_extend_a_superclass_method_by_calling_it_through_super
- rel: related_to
  target_object_id: PAT_package_reusable_behavior_as_a_mixin_class
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Read the MRO to Predict Which Inherited Attribute Wins

## Pattern Rule
**IF** a class has more than one base and the same attribute name exists in more than one place above it
**THEN** settle which one wins by reading `TheClass.__mro__` — the single ordered list Python searches — rather than reasoning about the tree shape, and when the winner is not the one you want, name it explicitly at the point the classes are combined
**ELSE** in a single-inheritance chain there is nothing to predict: the search runs straight up, and the lowest definition wins

## Do
- Print `[c.__name__ for c in Cls.__mro__]` when a multiple-inheritance tree surprises you; the order shown is exactly the order attribute lookup uses, for methods and data alike.
- Expect the order to go across before up where two bases share an ancestor: a class to the right is searched before the common ancestor above, so a lower class can override an attribute regardless of which branch it sits in.
- Expect every class to appear exactly once, no matter how many paths lead to it, and `object` to come last.
- Break a tie explicitly when the default is not what you want, by assigning the version you mean at the combining class (`method = Left.method`) or by calling the specific implementation (`Left.method(self)`) from an override.
- Remember that listing bases left to right in the header is the lever you control; where no shared ancestor is involved, the leftmost base still wins.

## Don't
- Don't reason about multiple inheritance as "depth first, all the way up". That is not the order used, and predicting from the picture rather than the computed list is where the mistakes come from.
- Don't assume a mix-in's method will be found just because it is listed as a base; if another base defines the same name further left, that one wins and the mix-in silently does nothing.
- Don't treat `super()` as independent of this: it continues along the same ordered list from the current class, which is why what it reaches can be a sibling branch rather than a parent.
- Don't build deep diamonds to express a design. The ordering rules are well defined but hard to hold in your head, and the resulting coupling is rarely worth it.

## Checklist
- For each class with multiple bases, has `__mro__` been checked against what the code assumes?
- Does any name appear in more than one base, and is the winner the intended one?
- Where a non-default choice is needed, is it made explicitly rather than by reordering bases and hoping?
- Could the design avoid the diamond altogether?

## Notes
The resolution order is computed once per class, when the class is created, by linearizing the whole tree into a list in which every class precedes its own parents and the order of each header's bases is preserved. Attribute lookup then just walks that list and stops at the first hit — so all of inheritance, including what `super()` reaches, reduces to one sequence you can print. That also means the shared root every class has makes a diamond out of every multiple-inheritance tree, which is exactly why the ordering had to guarantee that your classes are visited before the defaults they override.
