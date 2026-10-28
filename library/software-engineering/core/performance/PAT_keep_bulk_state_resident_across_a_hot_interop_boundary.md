---
object_id: PAT_keep_bulk_state_resident_across_a_hot_interop_boundary
object_type: pattern
name: Keep Bulk State Resident Across a Hot Interop Boundary
library_path:
- software-engineering
- core
- performance
stage_binding: 0 design
lane_fit: both
foundation_role: specialization
routing_class: general
specialization_axis: none
foundation_object_id: PAT_generate_interop_marshalling_at_a_rich_foreign_boundary
tags:
- performance
- interop
- marshalling
- data_movement
- ffi
cross_links:
- rel: related_to
  target_object_id: PAT_let_measurement_decide_what_to_tune
- rel: related_to
  target_object_id: PAT_price_communication_by_transfer_count_and_volume_separately
confidence: medium
references: []
variants: []
---

# Keep Bulk State Resident Across a Hot Interop Boundary

## Pattern Rule
**IF** profiling shows that repeatedly copying or serializing a large, long-lived value across a foreign-runtime boundary is a meaningful part of the cost
**THEN** keep that bulk state resident on one side of the boundary, expose a small stable handle or view, perform transformations where the state lives, and return only the results that actually need to cross
**ELSE** when the boundary cost is not material or the value is small and short-lived, prefer the simpler value-copying interface

## Do
- Measure the boundary before redesigning it; separate call overhead from bytes copied or serialized.
- Choose one side to own the large state for the interval in which repeated operations use it, and make the lifetime of the handle explicit.
- Move operations to the state when that avoids round-tripping the full representation; return small results or bounded views when possible.
- Keep the typed application contract separate from the raw handle or memory representation used by the interop layer.
- Release resident state and invalidate handles deterministically when the owning session or object ends.

## Don't
- Copy or serialize the entire data structure on every cross-boundary call merely because the binding tool makes that easy.
- Replace a clear value interface with opaque handles unless measurement shows the transfer cost matters.
- Let a handle outlive the state it names or silently turn it into permanent leaked state.
- Expose raw memory layout to unrelated application code just to save a copy.

## Checklist
- How many crossings occur, and how many bytes are copied or serialized per crossing?
- Which side can own the bulk state for the whole sequence of operations?
- Can callers send operations or small parameters instead of round-tripping the complete value?
- What invalidates the handle and releases the resident state?
- Did the redesigned boundary improve the measured end-to-end metric?

## Notes
Foreign-runtime bindings can make rich values look local while still copying, encoding, allocating, or serializing behind the interface. When that hidden transfer dominates a measured hot path, keeping the large state resident and crossing with small handles changes the cost model. The optimization is not universal: for small or infrequent values, copying often buys a simpler and safer contract at negligible cost.
