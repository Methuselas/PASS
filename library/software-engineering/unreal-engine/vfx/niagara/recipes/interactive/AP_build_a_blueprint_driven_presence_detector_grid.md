---
object_id: AP_build_a_blueprint_driven_presence_detector_grid
object_type: ap
name: Build a Blueprint-Driven Presence Detector Grid
library_path:
- software-engineering
- unreal-engine
- vfx
- niagara
- recipes
- interactive
stage_binding: 3 rough
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
- family_interactive_grid
- variant_01
- style_stylized
- ue_5_1_1_baseline
- grid
- custom_module
- blueprint
- distance_field
- interaction
cross_links: []
confidence: high
references: []
variants: []
---

# Build a Blueprint-Driven Presence Detector Grid

## Objective
Build a ground-plane particle grid that reacts to a moving player: particles near the player shrink and change from red toward white/cyan, and the response region follows the player's world position.

## Steps / Flow
**Final effect structure.**
- **Grid emitter:** spawns a flat, regularly spaced particle grid.
- **Presence Detector module:** transforms each particle into world space, measures distance to the player, converts that distance into SpriteSize and Color, and exposes an artist multiplier.
- **User parameter:** `User.PlayerPosition` carries the gameplay position into Niagara.
- **Actor Blueprint:** updates `User.PlayerPosition` from the player every frame or on a timer.

**Entry state.**
- Enable Niagara.
- Create a Niagara System and an emitter suitable for sprite particles.
- Create a Niagara Module Script named **Presence Detector**.
- Create an Actor Blueprint that will own the Niagara component.

1. **Create the module inputs.** In the Presence Detector module's Map Get, add:
   - `Particles.Position`
   - an Input Vector named `PlayerPosition`
   - `Engine.Owner.Position`
   - `Engine.Owner.Rotation`
   - `Engine.Owner.Scale`
   - an Input Float named `SpriteSizeMultiplier` with default `1.0`
2. **Transform particle position to the player's space.** Add **Apply Local Transform**. Feed `Particles.Position` to InputVector. Feed Owner Position, Rotation, and Scale into Translate, Rotate, and Scale.
3. **Measure player distance.** Subtract the transformed particle position from PlayerPosition: `PlayerPosition - TransformedVector`. Feed the result to **Length**.
4. **Clamp influence.** Feed Length into **Clamp** with Min `0` and Max `700.0`.
5. **Convert distance to sprite size.** Feed the clamped scalar into **Make Vector**, using the same scalar for X, Y, and Z. Convert that Vector to **Vector2D**. Multiply the Vector2D by `SpriteSizeMultiplier`. Write the result to `Particles.SpriteSize` in Map Set.
6. **Create distance-based color.** Branch from the clamped distance into **Remap Range**: Input Min `0`, Input Max `700`, Output Min `0`, Output Max `1`, Clamp Results enabled.
7. Feed the Remap output directly to **R** of **Make Linear Color**.
8. Subtract the Remap output from `1.0`. Feed that result to both **G** and **B**. Set Alpha to `1.0`.
9. Write Make Linear Color output to `Particles.Color` in Map Set.
10. **Create the grid.** In the emitter, add **Spawn Particles in Grid** to Emitter Update.
11. If Niagara reports an unmet dependency, use **Fix Issue** to add **Grid Location** to Particle Spawn.
12. In Grid Location, set XYZ Dimensions to `X=100`, `Y=100`, `Z=1` for a flat ground-plane distribution.
13. In Spawn Particles in Grid, set X Count `50`, Y Count `50`, and use Z Count `1` for a 50x50 ground grid.
14. Add the **Presence Detector** module to Particle Update. For a local test, set PlayerPosition `(0,0,0)` and SpriteSizeMultiplier `1.0`.
15. **Expose gameplay position.** Create a User Vector parameter named `User.PlayerPosition` and bind the Presence Detector module's PlayerPosition input to it.
16. **Build the Blueprint driver.** Create an Actor Blueprint, add a Niagara Particle System Component, and assign this Niagara System.
17. In the Blueprint Event Graph, get the player's world location. Use **Set Niagara Variable (Vector3)** on the Niagara component, variable name exactly `User.PlayerPosition`, and feed the player location into In Value.
18. Update each frame with Event Tick, or use a timer if a lower update rate is acceptable.
19. Place the Blueprint in the level. If you have not added additional relative-position math, place the effect at world origin for the baseline test.
20. Play and move the player through the grid.

**Integration rules.**
- PlayerPosition entering the custom module must be world space.
- Particle position must be transformed using the owning system's position/rotation/scale before distance is measured.
- The same clamped distance drives both size and color so both visual responses travel together.
- `SpriteSizeMultiplier` must default to `1.0`; a default of `0` makes a correctly wired system appear empty.

**Tuning.**
- **Clamp Max 700** is the interaction radius. Increase it for a broader response region.
- **SpriteSizeMultiplier** scales the size response without changing the distance calculation.
- **Grid spacing/dimensions** control physical spacing; **X/Y Count** control density.
- The Remap/Make Linear Color construction can be replaced with another palette while retaining the same distance signal.
- Use a timer rather than Tick when the effect does not need frame-perfect tracking.

**Avoid.**
- Don't subtract local-space particle positions directly from world-space player positions.
- Don't manually guess missing grid prerequisites when Niagara's **Fix Issue** can add Grid Location correctly.
- Don't leave SpriteSizeMultiplier at `0`.
- Don't omit the `User.` namespace in the Blueprint setter.

**Completion check.**
- Before Blueprint integration, changing `User.PlayerPosition` X/Y in Niagara moves the reaction region across the grid.
- With PlayerPosition at the grid center, nearby particles are smaller than distant particles.
- Distant particles read redder; nearby particles move toward white/cyan.
- During Play, the size/color response follows the player's movement.
- **Near-miss excluded:** a response centered at the world origin regardless of actor transform indicates the particle position was not transformed correctly.

## Notes
Recipe catalog metadata: family `vfx.interactive.presence-grid`; local variant 01 (`distance-size-color` — Distance-Driven Size and Color Grid); visual style `stylized`; implementation Unreal Engine Niagara; authored-against baseline 5.1.1; later engine versions remain unverified until tested. Style descriptors: interactive, abstract, reactive, grid.

- **Symptom:** Spawn Particles in Grid has a red error dot.  
  **Likely cause:** Grid Location dependency is missing.  
  **Correction:** select the module and use **Fix Issue** to add Grid Location.
- **Symptom:** no particles are visible.  
  **Likely cause:** SpriteSizeMultiplier is `0`.  
  **Correction:** set its default and current value to `1.0`.
- **Symptom:** the response moves incorrectly when the Niagara actor is moved/rotated/scaled.  
  **Likely cause:** local particle coordinates are being compared directly with world-space PlayerPosition.  
  **Correction:** restore the Apply Local Transform step using Engine.Owner transform values.
- **Symptom:** manual User parameter changes work but gameplay movement does not.  
  **Likely cause:** Blueprint setter name/type/cadence is wrong.  
  **Correction:** use Set Niagara Variable (Vector3), exact name `User.PlayerPosition`, and verify execution.

This composite intentionally embeds the full Niagara module, grid setup, User parameter, and Blueprint driver. It does not require any other recipe card to execute.
