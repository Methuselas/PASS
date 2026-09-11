---
object_id: PAT_use_traits_classes_for_type_info
object_type: pattern
name: Use Traits Classes for Compile-Time Type Information
library_path:
- software-engineering
- languages
- cpp
- traits
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- cpp
- traits
- templates
- compile_time
cross_links:
- rel: related_to
  target_object_id: PAT_use_template_metaprogramming
reference:
  source_title: 'Effective C++, Third Edition: 55 Specific Ways to Improve Your Programs and Designs'
  author: Scott Meyers
confidence: high
references: []
variants:
- variant_id: VAR_branch_inside_one_function_with_if_constexpr
  variant_name: Branch Inside One Function With a Compile-Time If
  variant_basis: method_sequence
  difference_from_foundation: The foundation obtains its compile-time if/else by splitting the work across overloaded workers and letting overload resolution choose between them, with a trait supplying the tag that selects one. This variant keeps the work in a single function and writes the if/else literally, with the condition being a compile-time boolean rather than a tag. The mechanism that makes it safe is that the branch not taken is not instantiated, so a branch may contain an expression that would be ill-formed for the types that do not reach it — dereferencing the parameter in the branch selected only for pointers is the standard case. That is the same property the overload set was buying, obtained without the indirection — no tag type, no worker overloads, and no master function whose only job is to pass the trait along. The trade is that the whole decision now sits inside one body, which reads well for a two-way branch on one property and poorly once the conditions multiply or the branches diverge in length.
  when_to_use: Use where the variation is a small number of alternatives selected by a property expressible as a compile-time boolean, and where the alternative bodies are short enough to read together. It is the better choice when the overload set would exist only to carry the dispatch and each worker would be called from exactly one place, since that indirection is pure ceremony. It also keeps a function's logic legible in one place for a reader who would otherwise have to assemble it from several overloads and a tag hierarchy.
  when_not_to_use: Do not use it where the trait must compute a type rather than answer a question — selecting how a parameter is taken or naming a container's element type is not a branch and has no if/else form. Prefer the foundation where the alternatives are numerous, where they are long enough that one function stops being readable, or where the workers are genuinely reusable and called from more than one master. It is also unavailable where the variation must be extensible by other authors, since an overload set can be added to from outside while a chain of compile-time branches inside one function cannot.
  absorbed_from_object_id: none
---

# Use Traits Classes for Compile-Time Type Information

## Pattern Rule
**IF** generic code needs an associated type or a compile-time property that is not naturally expressed as an operation
**THEN** expose it through a trait with a conservative primary template and supported specializations, then consume it with a C++20 constraint, `if constexpr`, or overload dispatch according to the shape of the decision.

## Do
- Reuse standard traits and concepts before inventing one. For iterators, `std::iterator_traits` supplies associated types for class iterators and pointers, while C++20 iterator concepts usually express an operation requirement more directly than inspecting a category tag.
- Use a trait when the output is itself a type, when a library must expose a user-specializable property, or when adapting a protocol whose associated information already lives in traits.
- Choose the consumer deliberately. A named concept or `requires` clause states whether an operation is available; `if constexpr` keeps a short closed choice local; overload or tag dispatch remains useful for compatibility protocols and extensible implementation sets.
- Use a trait to compute a *type* as well as to answer a question. Selecting how a parameter should be taken, stripping a qualifier, or picking a container's element type are all decisions generic code cannot make by hand, because the category of the type is exactly what it does not know.

## Don't
- Don't branch on a compile-time type property at runtime. It adds runtime machinery and an ordinary `if` still requires both branches to be well-formed.
- Don't require a nested member from every participating type when non-class types or third-party types must work. Put the adapter in a trait or use a concept defined in terms of valid expressions.
- Don't inspect a legacy category tag when a C++20 concept states the real requirement. Category dispatch is appropriate when interoperating with the classic iterator protocol, not as a substitute for constraints.

## Checklist
- Does a standard trait or concept already express the information?
- Is this genuinely associated information, or would a `requires` expression state the needed operation more directly?
- Does the design work for non-class and third-party types as well as user-defined class types?
- Is the consumer a constraint, `if constexpr`, or overload dispatch for a stated reason?
- Where the trait yields a type rather than a flag, does that type stay legal for every argument the template accepts, including one that is already a reference or already qualified?

## Notes
Classic `advance` demonstrates the compatibility form: `std::iterator_traits` exposes an iterator category for class iterators and pointers, and overloaded workers selected by category tags choose only operations valid for that category. C++20 code can often state the same boundary more directly with iterator concepts and use `if constexpr` for the small closed implementation choice. The trait remains valuable for associated types and for protocols whose customization surface is intentionally a specialization.

`VAR_branch_inside_one_function_with_if_constexpr` reaches the same compile-time if/else by writing it as an if/else. Where the foundation splits the work into tagged workers and lets overload resolution pick one, the variant keeps a single function and branches on a compile-time boolean, relying on the fact that the untaken branch is never instantiated — which is what permits a branch to dereference a parameter when it is only selected for pointers. Note what that does to this card's second Don't: the objection to a runtime `typeid` if/else was partly that it forces code invalid for some types to be compiled, and the compile-time branch supplies the readable if/else shape without reintroducing that problem. Use it for a small number of short alternatives selected by one property, where an overload set would exist purely to carry the dispatch. Keep the foundation where the trait computes a type rather than answering a question, where the alternatives are many or long, or where other authors must be able to extend the set — an overload set is open to additions from outside and a chain of branches inside one function is not.

The same mechanism computes types, and that use is easy to miss because it does not look like a decision. Standard transformation traits remove qualifiers, add references under defined rules, and select between candidate types. Prefer those vocabulary operations to home-grown cost heuristics such as assuming every scalar should be passed by value and every class by reference; parameter passing depends on semantics and measured cost, not merely on the type category.
