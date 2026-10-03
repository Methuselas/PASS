---
object_id: PAT_choose_rust_closure_bounds_by_capture_and_call_needs
object_type: pattern
name: Choose Rust Closure Bounds by Capture and Call Needs
library_path: [software-engineering, languages, rust, closures]
stage_binding: 1 skeleton
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: PAT_use_anonymous_functions_only_when_small
tags: [rust, closures, fn_traits, ownership, api_design]
cross_links:
- rel: related_to
  target_object_id: PAT_encode_rust_ownership_intent_in_function_signatures
reference: {source_title: The Rust Programming Language, author: Steve Klabnik and Carol Nichols}
confidence: high
references: []
variants: []
---

# Choose Rust Closure Bounds by Capture and Call Needs

## Pattern Rule
**IF** a Rust API accepts callable behavior
**THEN** require the least restrictive call trait the API's invocation pattern needs: `FnOnce` for one possible call, `FnMut` for repeated calls that may mutate captured state, and `Fn` only when repeated calls need no mutable access to captures.

## Do
- Start from how the API calls the value, not from whether the caller wrote a closure or a named function.
- Accept `FnOnce` when the API invokes the callable at most once; this admits every closure and function item that matches the arguments and result.
- Raise the requirement to `FnMut` when the API may call repeatedly, while allowing captured state to change.
- Require `Fn` when the API may call repeatedly through shared access, including cases that need simultaneous or concurrent invocation under additional thread-safety bounds.
- Add `move` when the closure must own captured values, then separately check whether its body moves any captured value out and therefore limits invocation to once.

## Don't
- Don't require `Fn` by reflex; an unnecessarily strong bound rejects useful stateful or consuming closures.
- Don't infer the call trait from the `move` keyword alone. Capture ownership and what the body does with that capture are separate decisions.
- Don't assume identical-looking closures have the same concrete type; use a generic bound, trait object, or function pointer according to the storage and dispatch requirement.
- Don't hide a long or domain-significant algorithm inside the closure merely because the type boundary accepts one.

## Checklist
- How many times can this API call the callable?
- Must the callable mutate or consume captured state?
- Does the closure need to outlive its defining scope or cross a thread boundary?
- Is static generic dispatch, dynamic dispatch, or a plain function pointer the intended storage model?
- Is the inline behavior still small and self-explanatory?

## Notes
Every closure implements `FnOnce`; closures that do not move captured values out also implement `FnMut`, and those that do not mutate or move captures also implement `Fn`. Ordinary safe functions using Rust's ABI implement all three call traits; unsafe functions, functions with target features, and functions using another ABI are exceptions. The API should therefore state only the invocation capability it actually uses, preserving the widest set of valid callers.
