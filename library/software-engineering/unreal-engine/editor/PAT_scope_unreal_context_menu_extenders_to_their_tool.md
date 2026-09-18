---
object_id: PAT_scope_unreal_context_menu_extenders_to_their_tool
object_type: pattern
name: Scope Unreal Context Menu Extenders to Their Tool
library_path:
- software-engineering
- unreal-engine
- editor
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: PAT_give_every_acquired_resource_one_named_owner
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

# Scope Unreal Context Menu Extenders to Their Tool

## Pattern Rule
**IF** an Unreal tool adds actor-specific context-menu actions
**THEN** register its extender in the tool's active scope, expose it only for relevant targets, and remove its exact delegate before the tool's receiver is destroyed.

## Do
- Inspect selected actors before adding type-specific menu entries.
- Choose the installed engine's appropriate extension hook and position.
- Supply the command list that owns the entries' callbacks; append it to the mode list when keyboard rebindings should reach the same actions.
- Retain the delegate handle and remove only that registration on exit.
- Account for retained command lists and open menu callbacks when ending the receiver lifetime.
- During shutdown, check module availability rather than loading a module just to unregister.

## Don't
- Don't remove other tools' extenders or leave raw callbacks mapped to a dead helper.
- Don't assume menu-construction targets remain current at action execution.

## Checklist
- Are entries absent for unrelated actor types?
- Do the actions resolve and validate the intended current targets?
- Can repeated enter/exit cycles leave stale delegates or callback mappings?

## Notes
This specializes `PAT_give_every_acquired_resource_one_named_owner`: registrations and their borrowed receivers need an explicit teardown owner.
