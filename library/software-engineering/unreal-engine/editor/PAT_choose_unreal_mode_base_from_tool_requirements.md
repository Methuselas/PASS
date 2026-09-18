---
object_id: PAT_choose_unreal_mode_base_from_tool_requirements
object_type: pattern
name: Choose Unreal Mode Base from Tool Requirements
library_path:
- software-engineering
- unreal-engine
- editor
stage_binding: 1 skeleton
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: none
tags:
- unreal_engine
- editor_tools
cross_links: []
reference:
  source_title: Extending and Customizing Unreal Engine Editor
  author: Roger Mattsson
confidence: medium
references: []
variants: []
---

# Choose Unreal Mode Base from Tool Requirements

## Pattern Rule
**IF** choosing the base for a new Unreal editor mode
**THEN** compare the actual input, UI and reflection requirements before choosing FEdMode's direct hooks or UEdMode's reflected framework.

## Do
- Consider FEdMode for direct viewport hooks and a collection of helper tools with explicit Slate presentation.
- Consider UEdMode when reflected properties and its tool framework justify the additional setup.
- Inspect installed examples and declarations for the required callbacks and lifecycle.
- Prototype the input and presentation path that motivates the choice before expanding the tool.

## Don't
- Don't turn one author's preference into a universal quality ranking.
- Don't infer that similar names imply interchangeable lifecycle or setup.

## Checklist
- Does the chosen base satisfy the stated reflection and input needs?
- Is the setup cost justified by the tool's purpose?
- Was the required path exercised rather than assumed?

## Notes
Both bases can support substantial editor tools. This decision does not supply a complete UEdMode setup procedure or predict future engine deprecations.
