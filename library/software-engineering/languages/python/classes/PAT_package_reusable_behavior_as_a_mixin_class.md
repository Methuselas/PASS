---
object_id: PAT_package_reusable_behavior_as_a_mixin_class
object_type: pattern
name: Package Reusable Behavior as a Mix-in Class
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
- mixins
cross_links:
- rel: related_to
  target_object_id: PAT_signal_name_visibility_with_underscore_conventions
- rel: related_to
  target_object_id: PAT_choose_repr_or_str_by_who_reads_the_display
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Package Reusable Behavior as a Mix-in Class

## Pattern Rule
**IF** the same behavior — a display format, a comparison scheme, a logging or serialization helper — is wanted by several classes that do not otherwise share a superclass
**THEN** put it in a mix-in: a small class that defines only that behavior, depends on nothing but `self`, and is added as an extra base to each client class, left of the base it should take precedence over
**ELSE** when the behavior needs no access to instance state, make it a module-level function instead; a class that never touches `self` is a namespace with extra ceremony

## Do
- Keep a mix-in narrow: one coherent capability, no `__init__`, and no assumption about what else is in the tree beyond the attributes it documents as required.
- List the mix-in to the left of other bases when its method must win; attribute lookup proceeds left to right across the bases named in the header, so position decides which same-named method is found.
- Name the mix-in's internal helpers with two leading underscores (`__collect`), so Python mangles them to include the mix-in's own class name and they cannot collide with — or be accidentally overridden by — anything a client class defines.
- Document which attributes or methods the mix-in expects clients to supply, since it reaches them through `self` with no declaration anywhere to check against.
- Prefer `__str__` over `__repr__` for a display mix-in, so client classes keep `__repr__` free for their own lower-level display.

## Don't
- Don't give a mix-in state of its own that clients must initialize; the moment it needs an `__init__`, every client has to cooperate, and the mix-in stops being free to add.
- Don't use plain names for a mix-in's helper methods. A client that happens to define the same name silently replaces the helper, because both live in one shared namespace, and the mix-in breaks in a way that points at the wrong file.
- Don't stack mix-ins carelessly. Each one you add widens the set of names competing in a single instance namespace, and the resolution order is the only thing deciding the winner.
- Don't reach for multiple inheritance to express an is-a relationship with two parents; mix-ins work because they add a capability, not because they claim the object is also a second kind of thing.

## Checklist
- Does the mix-in depend only on `self` and documented required attributes, with no constructor of its own?
- Is it positioned left of any base whose same-named method it must override?
- Are its internal helpers double-underscore-prefixed so client names cannot clash with them?
- Would a plain function be enough, given what this actually uses from the instance?

## Notes
A mix-in works because every instance in a class tree shares one attribute namespace, and because `self` in an inherited method refers to the instance of whatever subclass pulled it in — so a method written once can process objects of classes it has never heard of. That shared namespace is also the hazard: two classes in one tree that assign the same attribute name are writing to the same slot. Name mangling exists exactly for this case, which is why it earns its keep in a mix-in far more than in an ordinary class.
