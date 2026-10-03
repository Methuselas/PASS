---
object_id: PAT_confine_rust_unsafe_to_a_documented_safe_abstraction
object_type: pattern
name: Confine Rust Unsafe to a Documented Safe Abstraction
library_path: [software-engineering, languages, rust, unsafe]
stage_binding: 0 design
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: PAT_barricade_dirty_data_at_a_named_boundary
tags: [rust, unsafe, safety_invariants, abstraction, contracts]
cross_links:
- rel: related_to
  target_object_id: PAT_define_your_code_contract_explicitly
- rel: related_to
  target_object_id: PAT_end_conflicting_rust_borrows_before_mutation
reference: {source_title: The Rust Programming Language, author: Steve Klabnik and Carol Nichols}
confidence: high
references: []
variants: []
---

# Confine Rust Unsafe to a Documented Safe Abstraction

## Pattern Rule
**IF** a Rust implementation needs an operation whose safety the compiler cannot prove
**THEN** establish the operation's invariant in safe code, perform the smallest auditable unsafe operation with a local `SAFETY` justification, and expose a safe API only when every safe input preserves that invariant
**ELSE** keep the implementation entirely in safe Rust and let its types and borrow rules carry the proof.

## Do
- State the unchecked obligation before writing the unsafe block: which pointers are valid, which aliases may exist, which values are initialized, and which state transitions must be atomic or exclusive.
- Keep each unsafe block narrow enough that its `SAFETY` comment can connect the nearby checks and state directly to the operation's documented preconditions.
- Use module privacy and private fields to stop safe callers from constructing states that would invalidate the unsafe implementation.
- Mark a function `unsafe` only when its caller must uphold a safety precondition that the function cannot establish for itself; document that precondition under a `# Safety` section.
- Put explicit unsafe blocks around unsafe operations even inside an `unsafe fn`; the function declaration assigns obligations to callers, while each block records where the implementation discharges another obligation.
- Mark a trait unsafe only when an incorrect implementation could make otherwise safe code unsound, and document the invariant that every `unsafe impl` must uphold.
- Prefer safe synchronization or single-owner state over `static mut`; unsafe access does not provide the synchronization or alias control that mutable global state requires.

## Don't
- Don't treat `unsafe` as disabling Rust's ordinary checks or as permission to bypass a borrow-checker error without proving the equivalent aliasing and lifetime rules yourself.
- Don't make an entire function or module unsafe merely for convenience; a broad scope hides which operation required the proof.
- Don't publish a safe wrapper whose soundness depends on callers following an undocumented convention.
- Don't let public safe code mutate fields or invoke callbacks in ways that can invalidate an invariant trusted by unsafe code.

## Checklist
- What exact safety condition can the compiler not verify?
- Can safe checks, ownership, or privacy establish it before the unsafe operation?
- Does every unsafe block have one local, reviewable justification?
- If the public API is safe, can any safe input or safe callback cause undefined behavior?
- If the API is unsafe, is the caller's complete obligation documented?

## Notes
The `unsafe` keyword separates two different acts. An unsafe function or trait declares a contract that Rust cannot check; an unsafe block or implementation asserts that the relevant contract has been satisfied. Neither form turns off the borrow checker or makes undefined behavior acceptable.

A safe abstraction may contain unsafe operations, but soundness means that safe clients cannot drive it into undefined behavior. The real boundary is therefore not just the braces around an unsafe block. It includes every safe check, private field, and state transition on which that block relies. Keep that trusted surface small enough to audit as a unit.
