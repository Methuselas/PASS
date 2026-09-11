---
object_id: PAT_hand_container_data_to_a_c_api_as_a_pointer_and_a_count
object_type: pattern
name: Hand Container Data to a C API as a Pointer and a Count
library_path:
- software-engineering
- languages
- cpp
- containers
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- cpp
- containers
- language_interop
- legacy_code
- undefined_behavior
cross_links:
- rel: related_to
  target_object_id: PAT_cross_a_c_boundary_with_only_what_c_can_express
- rel: related_to
  target_object_id: PAT_reserve_capacity_up_front_and_release_it_deliberately
- rel: related_to
  target_object_id: PAT_choose_a_container_on_more_than_algorithmic_complexity
- rel: related_to
  target_object_id: AP_settle_a_containers_contract_before_filling_it
reference:
  source_title: 'Effective STL: 50 Specific Ways to Improve Your Use of the Standard Template Library'
  author: Scott Meyers
confidence: high
references: []
variants: []
---

# Hand Container Data to a C API as a Pointer and a Count

## Pattern Rule
**IF** you need to pass the contents of a container to an interface that takes a pointer and a length, or fill a container from one
**THEN** use contiguous storage such as `std::vector`, `std::array`, or `std::basic_string` and pass `.data()` with the correct element count, adapting other containers through contiguous storage when necessary
**ELSE** where the C++ interface is under your control, accept `std::span` (or `std::string_view` for read-only character data) so pointer and extent travel together.

## Do
- Use `.data()` instead of `&container[0]`. Calling `.data()` on an empty standard contiguous container is valid; whether a C API accepts that pointer with a zero count is part of that API's contract and may still require an adapter.
- Use `.c_str()` when the C function requires a null-terminated read-only string, and `.data()` with an explicit size when embedded nulls or binary character data are allowed. Since C++17, non-const string `.data()` exposes writable contiguous storage for existing characters.
- Pass a pointer to const unless the call is documented to write.
- Before a C routine writes into a vector or string, resize it to the number of actual element objects the routine may write and pass `.size()`, not merely `.capacity()`. Afterward, shrink to the reported count after validating that count does not exceed the supplied size.
- Bridge in both directions through a growable array. To fill some other container from such an interface, let it fill one of these and then construct the real container from the resulting range; to send some other container's contents out, copy them into one first and pass that.
- Read the non-owning view in the ELSE above as carrying the extent, not as checking it. Taking one is what stops a sequence parameter from decaying to a bare pointer and losing its length, so the callee can size what it was given instead of being told separately or guessing — that is the whole of what it buys. Indexing past the end of such a view is undefined exactly as it is for the pointer it replaced. It removes the class of bug where the length is wrong because it travelled separately from the data; it does not remove the class where the index is wrong.

## Don't
- Don't use the beginning iterator where a pointer is wanted. Its type is an iterator, and although implementations often make that a pointer for this container, nothing requires it — so code relying on the equivalence works until it is moved to an implementation where it does not.
- Don't let a C routine grow the data. Writing into unused capacity leaves the container's element count disagreeing with its contents, and writing past the capacity is worse than that.
- Don't forget what an embedded null does at the boundary. The string object is content to hold one; the interface receiving it will treat it as the end, so the data crossing is truncated without complaint from either side.
- Don't hand out a container carrying an invariant to something that may reorder it. A sequence kept sorted so it can be searched is still sorted only if the routine you passed it to left it that way, and re-establishing that is your problem after the call returns.

## Checklist
- Does the C API define what pointer it accepts when the count is zero?
- Is the parameter a pointer to const, and if not, what justifies the write?
- If the routine writes, are elements alive for the whole writable range, and is the reported count validated before resizing?
- Could the data contain an embedded null, and does the receiving side care?
- Does the container carry an invariant that the call might break?

## Notes
The whole technique rests on one guarantee — that this container's elements occupy contiguous memory, exactly as an array's do — which is why every other container has to be routed through one. That guarantee is what makes the container the interoperability point for the whole library rather than merely one option among several.

Two of Meyers's cautions have since been resolved and are worth not carrying forward. Strings are guaranteed contiguous, and standard contiguous containers expose `.data()`, which avoids the undefined `&v[0]` expression on an empty vector. Empty still belongs in the boundary contract: a valid zero-length C call may accept the returned pointer, require null, or require a non-null sentinel.

Where you control the C++ side, `std::span` carries a pointer and extent as one object; `std::string_view` does the same for read-only character sequences. Neither owns storage or makes indexing checked, so the source lifetime and bounds remain obligations. The raw pointer-and-count advice is for ABI boundaries that C must be able to express.
