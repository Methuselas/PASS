---
object_id: PAT_drive_a_niagara_vector3_user_parameter_from_blueprint
object_type: pattern
name: Drive a Niagara Vector3 User Parameter from Blueprint
library_path:
- software-engineering
- unreal-engine
- vfx
- niagara
- recipes
- techniques
- blueprint
stage_binding: 2 block
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: none
tags:
- unreal_engine
- niagara
- vfx
- recipe
- family_control
- variant_01
- style_style_agnostic
- ue_5_1_1_baseline
- blueprint
- user_parameter
- vector3
- runtime_control
cross_links: []
confidence: high
references: []
variants: []
---

# Drive a Niagara Vector3 User Parameter from Blueprint

## Pattern Rule
**IF** Niagara behavior must react to a world-space Vector3 value owned or calculated by gameplay code,  
**THEN** expose a Niagara User Vector parameter and set it from an Actor Blueprint through the matching typed **Set Niagara Variable (Vector3)** node.  
**ELSE** keep the value local to Niagara when gameplay does not need to control it.

## Do
**Target result.** A Blueprint updates a Niagara Vector3 user parameter at runtime so particle behavior can follow a player, target, impact point, or other moving position.

**Vector3 Blueprint Binding setup.**
- Create a Niagara System containing the effect to control.
- Add a **User** parameter of type Vector3, for example `User.PlayerPosition`.
- Bind the effect's internal Vector3 input to that User parameter.

**Vector3 Blueprint Binding build.**
1. Create an **Actor Blueprint**.
2. Add a **Niagara Particle System Component**.
3. Assign the target Niagara System to that component.
4. In the Event Graph, decide how often the Vector3 should update. **Event Tick** gives per-frame updates; a timer can reduce update frequency when perfect tracking is unnecessary.
5. Obtain the world-space location to send. For a player character, get the Player Character and then read a suitable component's world location; the Capsule Component is a common choice.
6. Drag the Niagara component into the graph.
7. From it, add **Set Niagara Variable (Vector3)**.
8. Set **In Variable Name** to the exact User parameter name, including namespace, e.g. `User.PlayerPosition`.
9. Connect the world-space position into **In Value**.
10. Connect execution so the update runs at the chosen frequency.

**Vector3 Blueprint Binding tuning.**
- Use Event Tick for the tightest following behavior.
- Use **Set Timer By Event** for less frequent updates when performance matters more than frame-perfect tracking.
- Replace player position with any other Vector3 gameplay value without changing the Niagara-side control pattern.

## Don't
- Don't omit the `User.` namespace from the variable name.
- Don't choose a Set Niagara Variable node with the wrong data type.
- Don't update every frame by default when the effect can tolerate a slower cadence.

## Checklist
- Changing the Blueprint-provided world position changes the Niagara User parameter at runtime.
- Moving the controlled actor causes the particle behavior to follow without manually editing Niagara.
- **Near-miss excluded:** a Blueprint graph that executes correctly but produces no Niagara response usually indicates the variable name/type does not exactly match the Niagara User parameter.

## Notes
Recipe catalog metadata: family `vfx.control.blueprint-user-parameter`; local variant 01 (`vector3-event-tick` — Vector3 Blueprint Binding); visual style `style_agnostic`; implementation Unreal Engine Niagara; authored-against baseline 5.1.1; later engine versions remain unverified until tested.

- **Symptom:** Set Niagara Variable executes but the effect never changes.  
  **Likely cause:** wrong variable name, missing `User.` namespace, or wrong typed setter.  
  **Correction:** copy/use the exact Niagara User parameter name and match the setter type.
- **Symptom:** effect lags behind a fast-moving target.  
  **Likely cause:** update cadence is too slow.  
  **Correction:** increase timer frequency or update on Tick.

This is a control recipe rather than a visual style recipe. Keep the Blueprint-facing parameter name stable once gameplay begins depending on it.
