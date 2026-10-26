---
object_id: PAT_start_with_portable_interfaces_then_isolate_platform_extensions
object_type: pattern
name: Start With Portable Interfaces Then Isolate Platform Extensions
library_path:
- software-engineering
- core
- design
stage_binding: 0 design
lane_fit: both
foundation_role: foundation
routing_class: general
specialization_axis: none
foundation_object_id: none
tags:
- portability
- platform
- interfaces
- operating_system
- abstraction
cross_links:
- rel: related_to
  target_object_id: PAT_decompose_into_layers_of_abstraction
- rel: related_to
  target_object_id: PAT_design_modular_interfaces
reference:
  source_title: Practical System Programming for Rust Developers
  author: Prabhu Eshwarla
confidence: medium
references: []
variants: []
---

# Start With Portable Interfaces Then Isolate Platform Extensions

## Pattern Rule
**IF** a system operation has both a portable interface and platform-specific extensions
**THEN** express the common behavior through the portable interface first and isolate platform-specific code behind the smallest boundary that genuinely needs it

## Do
- State the behavior the application needs before selecting an operating-system-specific mechanism.
- Use the portable layer for behavior whose contract is shared across supported platforms.
- Put unavoidable platform-specific operations behind a narrow module or adapter so the rest of the system does not inherit that dependency.
- Test the portable contract separately from platform-specific capability or integration tests.

## Don't
- Don't reach for a platform extension merely because it exposes more detail than the application requires.
- Don't scatter conditional platform branches through business logic when one boundary can contain them.
- Don't promise portability beyond the platforms and semantics the portable layer actually supports.

## Checklist
- Which required behavior is portable and which is truly platform-specific?
- Can the platform-specific dependency be confined to one boundary?
- Does the common code depend only on the portable contract?
- Are platform-specific assumptions tested on the platforms that own them?

## Notes
A standard or cross-platform library can hide operating-system differences without eliminating them. The engineering advantage comes from keeping the portable contract dominant and making exceptions visible at a boundary instead of allowing platform details to become ambient assumptions.
