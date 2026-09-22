---
object_id: PAT_use_niagara_namespaces_to_separate_parameter_ownership
object_type: pattern
name: Use Niagara Namespaces to Separate Parameter Ownership
library_path:
- software-engineering
- unreal-engine
- vfx
- niagara
stage_binding: 1 skeleton
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: none
tags:
- unreal_engine
- niagara
- vfx
cross_links: []
reference:
  source_title: Build Stunning Real-time VFX with Unreal Engine 5
  author: Hrishikesh Andurlekar
confidence: high
references: []
variants: []
---

# Use Niagara Namespaces to Separate Parameter Ownership

## Pattern Rule
**IF** Niagara parameters have similar names but belong to different scopes or data owners
**THEN** use their namespaces to distinguish ownership and respect the read/write rules of each namespace.

## Do
- Treat System, Emitter, Particle, Engine, and User as distinct parameter scopes.
- Use Engine namespace values as read-only engine-provided data.
- Create User parameters for externally supplied or arbitrary user-facing values.

## Don't
- Don't assume two parameters with the same base name are the same value across namespaces.
- Don't try to write to read-only Engine namespace values.

## Checklist
- Each parameter reference uses the intended namespace.
- Reads and writes respect the namespace ownership rules.

## Notes
Namespaces qualify parameter names and constrain where data can be read or written.
