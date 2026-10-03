---
object_id: PAT_choose_rust_smart_pointer_by_ownership_contract
object_type: pattern
name: Choose a Rust Smart Pointer by Its Ownership Contract
library_path: [software-engineering, languages, rust, ownership]
stage_binding: 0 design
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: PAT_give_every_acquired_resource_one_named_owner
tags: [rust, ownership, smart_pointers, box, rc, refcell]
cross_links:
- rel: related_to
  target_object_id: PAT_end_conflicting_rust_borrows_before_mutation
- rel: related_to
  target_object_id: PAT_break_rust_reference_cycles_with_weak_edges
reference: {source_title: The Rust Programming Language, author: Steve Klabnik and Carol Nichols}
confidence: high
references: []
variants: []
---

# Choose a Rust Smart Pointer by Its Ownership Contract

## Pattern Rule
**IF** Rust data needs heap indirection, shared lifetime, or mutation through a shared access path
**THEN** state the number of owners, the mutation rule, and the thread boundary first, then add only the smart-pointer capabilities that enforce that contract: `Box&lt;T&gt;` for one owner with indirection, `Rc&lt;T&gt;` for multiple owners in one thread, and `RefCell&lt;T&gt;` for borrow checking deferred to runtime
**ELSE** keep the value directly owned and let ordinary references express temporary access.

## Do
- Start from one named owner and ordinary borrows; shared ownership must identify a real second owner whose lifetime cannot nest under the first.
- Use `Box&lt;T&gt;` when the required capability is a stable-size pointer to heap data, including an indirection that makes a recursive type finite.
- Use `Rc&lt;T&gt;` when multiple single-threaded owners must keep the same allocation alive, and write `Rc::clone(&value)` where the count increase should be visible as an ownership event.
- Use `RefCell&lt;T&gt;` only when mutation must occur through a shared reference and the program can uphold the ordinary many-readers-or-one-writer rule at runtime.
- Compose wrappers by responsibility: `Rc&lt;RefCell&lt;T&gt;&gt;` means shared ownership outside and runtime-checked mutable access inside; neither layer supplies the other's guarantee.
- Keep `Rc&lt;T&gt;` within one thread, and do not share a `RefCell&lt;T&gt;` across threads because it is not `Sync`. Reopen the design when ownership or access crosses a thread boundary rather than assuming either type supplies synchronization.

## Don't
- Don't choose reference counting merely to postpone deciding who owns the value.
- Don't treat `RefCell&lt;T&gt;` as an escape from the borrow rules; conflicting `borrow` and `borrow_mut` guards panic at runtime instead of failing compilation.
- Don't add `Box&lt;T&gt;` to a small, directly owned value without a need for indirection, stable address, trait erasure, or movement cost.
- Don't infer mutability from ownership count: `Rc&lt;T&gt;` shares lifetime but exposes shared access, while `RefCell&lt;T&gt;` changes where borrowing is checked.

## Checklist
- How many independent owners must keep the allocation alive?
- Is mutation compile-time checked or deliberately deferred to runtime?
- Will ownership or access be shared across threads?
- What capability does each wrapper layer add?
- Could direct ownership plus ordinary borrowing express the same lifetime more clearly?

## Notes
The types are composable because they answer different questions. `Box&lt;T&gt;` chooses indirection with one owner, `Rc&lt;T&gt;` chooses shared lifetime, and `RefCell&lt;T&gt;` chooses runtime enforcement of exclusive mutation. Naming those questions before naming the type prevents a nested pointer expression from becoming the ownership design.
