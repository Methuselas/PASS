---
object_id: DRILL_verify_unreal_toolmenu_ownership
object_type: drill
name: Verify Unreal ToolMenu Ownership
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
- toolmenus
cross_links:
- rel: teaches
  target_object_id: AP_publish_a_persistent_unreal_toolbar_action
reference:
  source_title: Extending and Customizing Unreal Engine Editor
  author: Roger Mattsson
confidence: medium
references: []
variants: []
target_skill: Verify Unreal ToolMenu Ownership
---

# Verify Unreal ToolMenu Ownership

## Practice Task
Produce a deferred ToolMenus toolbar fixture and verify two registration/teardown cycles alongside an unrelated owner's entry.

## Target Skill
Practise `AP_publish_a_persistent_unreal_toolbar_action` with observable routing and ownership.

## Setup
An Unreal editor C++ project, a plugin-owned action and a separate unrelated menu owner.

## Instructions
1. State the selected menu, action scope and owners with reasons.
2. Build the fixture and run deferred registration; record entries, owner identities and the mapped command list.
3. Invoke the registered action route and record its callback count and result.
4. Retain a command-list reference, tear down the fixture and record entries, mappings and callback behavior afterward.
5. Repeat registration and teardown; record duplicate counts and whether the unrelated owner's entry survives.
6. Record whether startup timing, native menu construction and visible toolbar input were exercised; retain fixture and run evidence.

## Success Check
- A built fixture executes registration and teardown twice; a proposed registration sequence does not pass.
- The command route invokes the intended action with the observed count/result.
- No duplicates or callable dead receivers remain, and unrelated owner entries survive both cycles.
- Menu/scope choices have reasons, and deferred timing or visible UI claims are supported by their actual interface rather than native construction alone.

## Common Failures
- Registering entries before menus are ready.
- Omitting the entry's command list.
- Removing a button but retaining a raw receiver callback.

## Notes
A commandlet may construct menu objects without running the real editor startup callback or showing a toolbar.
