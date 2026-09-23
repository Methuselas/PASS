---
object_id: PAT_expose_niagara_controls_through_an_actor_blueprint
object_type: pattern
name: Expose Niagara Controls through an Actor Blueprint
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
- construction_script
- artist_control
cross_links: []
confidence: high
references: []
variants: []
---

# Expose Niagara Controls through an Actor Blueprint

## Pattern Rule
**IF** designers should adjust Niagara properties from an Actor instance without opening Niagara,  
**THEN** expose those values as Niagara User parameters and mirror them with public Blueprint variables wired through typed Set Niagara Variable nodes.  
**ELSE** keep values internal when they are implementation details rather than intended controls.

## Do
**Target result.** An Actor Blueprint exposes selected VFX controls in its Details panel and pushes those values into its Niagara component, including while editing when the Construction Script is used.

**Construction-Script User Controls setup.**
- Create the Niagara System and identify which properties should become public controls.
- For each property, create a matching **User** parameter in Niagara with the appropriate data type.
- Bind each target Niagara property to its corresponding User parameter.

**Construction-Script User Controls build.**
1. Create an **Actor Blueprint**.
2. Add a **Niagara Particle System Component** and assign the target Niagara System.
3. Create public Blueprint variables matching the controls you want to expose.
4. Use the **Construction Script** when the effect should update in the editor as those properties are changed.
5. For each public variable, drag from the Niagara component and add the **Set Niagara Variable** node whose type matches the Niagara User parameter.
6. Enter the exact User parameter name in **In Variable Name**, including the `User.` namespace.
7. Connect the public Blueprint variable to **In Value**.
8. Repeat for every exposed control.
9. Compile the Blueprint, place an instance in the level, and change its public properties in Details to verify live propagation.

**Construction-Script User Controls tuning.**
- Expose only parameters that represent meaningful artistic/gameplay controls.
- Good candidates include spawn density, color, texture/mask selection, size multipliers, and effect intensity.
- Keep stable names once other Blueprints/tools depend on them.

## Don't
- Don't expose every low-level Niagara setting simply because it can be exposed; the Blueprint should present a clean control surface.
- Don't use Set Niagara Variable (Float) for a LinearColor, Vector3, or other mismatched parameter type.
- Don't omit `User.` from the Niagara variable name.

## Checklist
- Editing a public Blueprint variable changes the intended Niagara property.
- Multiple exposed variables change their own targets without cross-talk.
- Construction Script controls update while editing the Actor, not only during Play, when that behavior is desired.

## Notes
Recipe catalog metadata: family `vfx.control.blueprint-user-controls`; local variant 01 (`construction-script` — Construction-Script User Controls); visual style `style_agnostic`; implementation Unreal Engine Niagara; authored-against baseline 5.1.1; later engine versions remain unverified until tested.

- **Symptom:** public variable changes but Niagara does not.  
  **Likely cause:** User parameter is not bound to the target property or setter name/type is wrong.  
  **Correction:** verify Niagara binding first, then the Blueprint's exact variable name and typed setter.

Treat the Blueprint as the effect's public interface and Niagara as the implementation behind it. This keeps high-level controls accessible without widening every internal parameter.
