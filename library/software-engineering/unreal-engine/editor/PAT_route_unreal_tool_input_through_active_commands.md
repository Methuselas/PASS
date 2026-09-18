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
**IF** an Unreal editor tool uses user-rebindable command input
**THEN** register it as a `TCommands` command, match the current bindings through deliberate polling or a scoped command-list callback, and consume only the input the active tool intentionally handles.

## Do
- Define searchable command names and descriptions with `UI_COMMAND`, an appropriate action type and an optional default `FInputChord`.
- Register commands from module startup after their style resources exist; unregister them when the module shuts down.
- For a callback, map the command to an `FExecuteAction` with `FUICommandList::MapAction`. Let the command list match current bindings and modifiers rather than copying the default chord into another comparison.
- Own the command list in the scope where the action should be active: a mode for mode-local input, or a module for a deliberately persistent action. When accepting a weak command-list pointer, pin it into a local shared pointer and check that pointer before mapping an action.
- Ensure a callback cannot outlive its receiver. A lambda capturing raw `this` requires the receiver to survive every retained command-list mapping; unmap the action or release every retaining owner before destroying the receiver.
- Filter input phases deliberately. Route an intended key press once; reject release events and permit repeats only when the action is designed for them. Pass the actual repeat policy to `ProcessCommandBindings` instead of treating every event as a fresh press.
- Decide whether a matched but currently invalid action should consume the gesture and report its rejection. A false can-execute predicate may let another command sharing the chord run; use validation inside the callback when that fallthrough would violate the intended behavior.
- Keep frequently polled can-execute predicates cheap. Read and validate changing external input again when the action executes; avoid repeatedly parsing the clipboard just to paint button availability, and justify caching or additional polling work with measurements and an invalidation policy.
- For polled viewport gestures, check both active chord slots and their modifiers. Obtain the clicked actor, component and material slot from the hit proxy; do not substitute the actor's first component or slot zero.
- Validate the hit proxy and component type for pointer gestures. Explicitly reject unsupported targets such as volumes where the gesture would be a mistake.
- Let unrelated input continue through the installed mode's input chain. If a delegated helper declines an event, use the appropriate base handler or command-list result for that engine hook.

## Don't
- Don't hardcode the initial default as the only accepted key.
- Don't return handled for unrelated input and suppress the editor's normal behavior.
- Don't dereference an expired weak command list or leave a callback mapped to a destroyed helper.
- Don't invoke the action again on key release merely because the input hook also receives release events.
- Don't infer a current engine input-routing defect from a patch demonstrated for another version.

## Checklist
- Do primary and secondary rebindings change the accepted gesture?
- Are modifiers, press/release phases and repeats tested with an observable callback count?
- Can mode exit or module shutdown leave a callable mapping to a destroyed receiver?
- For pointer gestures, are the clicked component and slot the ones edited?
- Are unrelated events delegated?
- Does an intentionally rejected gesture explain its failure without accidentally triggering a competing command?

## Notes
A command declaration makes input discoverable and rebindable. Target resolution, callback lifetime and event consumption are separate responsibilities. A key-only comparison does not establish complete modifier-chord matching, and a registered command does not prove its callback is safely routed. Test the actual input path and check any engine routing patch against the installed version.
