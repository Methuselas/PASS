---
object_id: PAT_prefer_pass_by_reference_to_const
object_type: pattern
name: Choose Read-Only Parameter Passing by Cost and Semantics
library_path:
- software-engineering
- languages
- cpp
- parameter-passing
stage_binding: 3 rough
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- cpp
- parameter_passing
- efficiency
- slicing
cross_links:
- rel: related_to
  target_object_id: PAT_adapt_rules_to_active_cpp_sublanguage
- rel: related_to
  target_object_id: PAT_return_by_value_when_returning_new_object
- rel: related_to
  target_object_id: PAT_pass_by_value_only_when_all_four_conditions_hold
reference:
  source_title: 'Effective C++, Third Edition: 55 Specific Ways to Improve Your Programs and Designs'
  author: Scott Meyers
confidence: high
references: []
variants: []
---

# Choose Read-Only Parameter Passing by Cost and Semantics

## Pattern Rule
**IF** you are deciding how a function that only reads its argument should take a parameter
**THEN** pass by value when the type is deliberately cheap, small, and value-like; pass by reference-to-const when copying is material, identity matters, or a base parameter must preserve dynamic type
**ELSE** where the function's job is to keep a copy of what it is given, passing by value can be right for reasons this rule does not cover; `PAT_pass_by_value_only_when_all_four_conditions_hold` owns that decision.

## Do
- Pass scalar types and intentionally lightweight vocabulary types by value, so the callee receives an independent value without an indirection or aliasing concern.
- Pass a larger or expensive-to-copy object by reference to const when the call only observes it.
- Use a reference when the parameter type is a polymorphic base and derived behavior must survive; passing the base by value slices.
- Judge iterators, views, and function objects by their actual type contract and size. Many are cheap values, but custom ones are not guaranteed to be pointer-sized merely because they model the same concept.

## Don't
- Don't classify a type from "built-in" versus "user-defined" alone. A user-defined span-like view may be an ideal value parameter, while a custom iterator or callable may own substantial state.
- Don't pass a derived object by value through a base-type parameter — the base copy constructor slices off the derived part and later virtual calls resolve to the base.
- Don't take a built-in by reference-to-const on the reasoning that a reference is always the cheaper way to pass something. A reference is the size of a pointer or larger, so nothing is saved on a type that fits in a register; the callee has to load through it, and to reload wherever an intervening write might alias the referent — measured, a loop with no such write loaded it once, the same as the by-value version, and adding a write through another pointer reloaded it every iteration; and because the reference is to const it binds to a temporary whenever the argument's type does not match exactly, so an index arriving as a different integer type materialises one on every call. This is the mirror image of the mistake the rule above prevents, and it is easy to reach by applying that rule past the types it was written for.

## Checklist
- Is this type intentionally cheap and value-like, or is its copy cost or identity material?
- Would a reference introduce aliasing and indirection without avoiding meaningful work?
- Could passing by value slice a derived argument here?
- If this is an iterator, view, or callable, what does its concrete type actually store?

## Notes
Passing a large object by value may invoke every base and member copy constructor; reference-to-const avoids that work. It also prevents slicing when a derived object arrives through a base parameter. The old rule split built-ins from user-defined types and assumed iterators and function objects were always pointer-like. Modern code has cheap user-defined vocabulary values and potentially heavy custom models, so the decision belongs to the concrete type's value semantics and cost.

The rule above answers the case where the function only reads its argument, which is the
common one. Where the function's job is to *keep* a copy — a constructor storing a member, or
a function that consumes its argument destructively — passing by value stops being the
inefficiency it looks like, because one signature then serves lvalues and rvalues without a
second overload taking an rvalue reference. That is a decision with four qualifying conditions
and two ways to go wrong, and it has its own card rather than living here as a footnote.

One consequence of the const on that reference is worth knowing, because it is where a
surprising share of unnoticed temporaries come from. When the argument's type does not match
the parameter's, a const reference parameter will happily bind to a temporary conjured up to
make the call work, so passing a character array where a string is expected constructs and
destroys a string on every call. A reference to non-const will not do this — the language forbids
it, because modifying such a temporary would change something the caller never sees — which
means the same mismatch that compiles silently in the const case is a diagnostic in the other.
The two places temporaries arise are exactly this and returning an object by value; learning to
notice both is more useful than any individual fix for them.
