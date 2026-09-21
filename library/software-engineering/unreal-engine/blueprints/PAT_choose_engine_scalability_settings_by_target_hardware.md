---
object_id: PAT_choose_engine_scalability_settings_by_target_hardware
object_type: pattern
name: Choose Engine Scalability Settings by Target Hardware
library_path:
- software-engineering
- unreal-engine
- blueprints
stage_binding: 4 final
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: none
tags:
- unreal_engine
- blueprints
- graphics
- performance
cross_links: []
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Choose Engine Scalability Settings by Target Hardware

## Pattern Rule
**IF** you are setting graphics quality before building a game for particular target machines
**THEN** set the Engine Scalability Settings to match those machines: pick one of the Low-to-Epic presets as your broad performance-versus-quality target, use Auto when the targets are roughly equivalent to the machine you develop on (it detects that hardware and balances performance against quality), and reserve Cinematic for rendering cinematics rather than gameplay.

## Do
- Open Engine Scalability Settings from the Settings button in the Level Editor toolbar; the preset buttons along the top set every quality setting at once, so a preset is the fast way to move the whole game between performance tiers.
- Tweak individual settings only when you need finer control: Resolution Scale renders below target resolution and upscales (faster but fuzzier), View Distance stops rendering beyond a camera distance (shorter is faster but objects pop into view), Anti-Aliasing softens jagged edges, Post Processing sets baseline quality for filters like motion blur and bloom, Shadows bundles shadow-quality settings with a big performance impact, Textures controls how the engine manages texture memory (lower it to avoid running out of graphics memory), Effects covers material reflections and translucency, and Foliage and Shading set foliage and material quality.
- Define workable defaults for simple games: when assets are simple and level size is constrained, a fixed preset can stand in for player-facing graphics menus.

## Don't
- Don't ship a Cinematic-quality build for gameplay — that setting exists for rendering cinematics and is not intended for runtime play.
- Don't assume the settings your editor machine picked suit your players' machines; Auto only helps when you target hardware roughly equivalent to the development machine.
- Don't chase maximum visual quality at the expense of frame rate: games that struggle with low frame rates feel bad from a gameplay perspective even when the mechanics are solid.

## Checklist
- The chosen preset matches the performance tier of the machines your players will run the game on.
- No Cinematic setting is active in a playable build.
- Any individually tweaked setting was changed for a reason you can state (for example, lowering Textures to protect graphics memory).

## Notes
Unreal Engine 5 exposes its graphics quality as Engine Scalability Settings: one interface of settings, each determining the final visual quality of one element of the game. Every choice trades frame rate against visual fidelity, so the decision belongs to the target hardware, not to taste. Many games on variable PC and macOS hardware give players their own graphics menus; a simple game with constrained content can instead commit to workable defaults before it is packaged.
