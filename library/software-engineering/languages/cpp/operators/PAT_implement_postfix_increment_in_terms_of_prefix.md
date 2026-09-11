---
object_id: PAT_implement_postfix_increment_in_terms_of_prefix
object_type: pattern
name: Implement Postfix Increment in Terms of Prefix
library_path:
- software-engineering
- languages
- cpp
- operators
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- cpp
- operators
- class_design
- consistency
cross_links:
- rel: related_to
  target_object_id: PAT_return_values_without_top_level_const
reference:
  source_title: 'More Effective C++: 35 New Ways to Improve Your Programs and Designs'
  author: Scott Meyers
confidence: high
references: []
variants: []
---

# Implement Postfix Increment in Terms of Prefix

## Pattern Rule
**IF** you are overloading increment or decrement for a class and want both the prefix and the postfix spelling to work
**THEN** write an lvalue-qualified prefix form as the real operation — modify the object and return a reference — then define an lvalue-qualified postfix form by saving the old value, invoking prefix, and returning the saved value.

## Do
- Read the two names C programmers gave these as implementation specifications rather than folklore. Prefix is increment-and-fetch, so it changes the object and hands that object back; postfix is fetch-and-increment, so it keeps what was there, changes the object, and hands back what it kept.
- Leave the disambiguating parameter unnamed. Compilers pass a zero for it and the body has no use for it, so naming it only earns a warning about a parameter that is never read.
- Return the postfix result as an ordinary value so it remains movable. Ref-qualify both mutating overloads with `&`; applying either to the returned prvalue then fails without top-level const.
- Tell clients to reach for the prefix spelling on class types whenever they do not need the previous value, because the postfix form has to construct and destroy an object that the prefix form never creates.

## Don't
- Don't write the two forms independently from the same specification. They are meant to differ only in what they hand back, nothing enforces that, and two people maintaining them separately will eventually make them disagree about what incrementing this type means.
- Don't return a `const` value to block a second increment. That old technique can inhibit moves and other legitimate rvalue use; put the restriction on the mutating operator with an `&` qualifier.

## Checklist
- Does the postfix body state what incrementing means, or does it delegate that entirely?
- Is the postfix return type a value, the prefix return type a reference, and are both mutating overloads `&`-qualified?
- Is the disambiguating parameter left unnamed?
- If a client applied the operator twice in succession on one object, would that be a diagnostic?

## Notes
The asymmetry in return types follows from what each form owes the caller. Prefix can return a reference because it owes the object it just modified. Postfix must return a value because it owes the object's previous state. Modern C++ should keep that value movable and put the lvalue-only restriction on the mutating member itself. This reproduces the useful built-in behavior without const-qualifying a prvalue.

The efficiency point follows from the structure rather than from any implementation choice. Postfix necessarily creates something to hold the previous value, so on user-defined types the two spellings genuinely differ in cost — unlike on built-in integers, where the habit of writing either one was formed and where the difference does not exist.
