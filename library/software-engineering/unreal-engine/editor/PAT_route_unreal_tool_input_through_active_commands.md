---
object_id: PAT_route_unreal_tool_input_through_active_commands
object_type: pattern
name: Route Unreal Tool Input Through Active Commands
library_path:
- software-engineering
- unreal-engine
- editor
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: none
tags:
- unreal_engine
- commands
- editor_modes
- input
cross_links: []
reference:
  source_title: Extending and Customizing Unreal Engine Editor
  author: Roger Mattsson
confidence: medium
references: []
variants: []
---

# Route Unreal Tool Input Through Active Commands

## Pattern Rule
**IF** an editor-mode tool uses a user-rebindable keyboard-and-pointer gesture
**THEN** register it as a `TCommands` command, read the current primary and secondary bindings when handling input, and consume an event only when the tool intentionally handles it.

## Do
- Define searchable command names and descriptions with `UI_COMMAND`, an appropriate action type and an optional default `FInputChord`.
- Register commands from module startup after their style resources exist; unregister them when the module shuts down.
- Keep the tool's click logic in a separate helper and let the mode delegate to it. If the helper declines the event, call the base mode handler.
- Obtain the clicked actor, component and material slot from the hit proxy; do not substitute the actor's first component or slot zero.
- Validate the hit proxy and component type. Explicitly reject unsupported targets such as volumes where the gesture would be a mistake.
- Check both active chord slots rather than the default key. If bindings can contain modifiers, verify those modifiers too; checking only the key cannot demonstrate the complete configured gesture.

## Don't
- Don't hardcode the initial default as the only accepted key.
- Don't return handled for unrelated input and suppress the editor's normal behavior.
- Don't infer a current engine input-routing defect from a patch demonstrated for another version.

## Checklist
- Do primary and secondary rebindings change the accepted gesture?
- Are the clicked component and slot the ones edited?
- Are unrelated events delegated?
- Does the tool explain an intentionally rejected gesture?

## Notes
A command declaration makes the gesture discoverable and rebindable; hit-proxy handling identifies the actual edit target. These are different responsibilities. A key-only comparison does not establish complete modifier-chord matching. Test combinations beyond a plain key and check any engine routing patch against the installed version.
