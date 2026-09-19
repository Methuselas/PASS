---
object_id: PAT_investigate_an_external_asset_before_relying_on_it
object_type: pattern
name: Investigate an External Asset Before Relying on It
library_path:
- software-engineering
- unreal-engine
- blueprints
stage_binding: 0 design
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: none
tags:
- unreal_engine
- blueprints
- external_assets
- maintenance
cross_links: []
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Investigate an External Asset Before Relying on It

## Pattern Rule
**IF** you are bringing an existing asset into a project — a template Blueprint, a starter-content object, a third-party asset — and plan to rely on it
**THEN** spend time investigating how it works before you depend on it, so you can repair it when it breaks and extend it when your needs exceed what it does.

## Do
- Open the asset and break it down section by section to see how each part contributes to its behavior.
- Identify the parts you will modify and the parts you will leave alone.
- Keep the investigation as the basis for your modifications, so a change is an extension of understood behavior rather than a guess.

## Don't
- Don't use an asset that works without learning how it accomplishes its functionality — the shortcut buys you a dependency you cannot repair or extend.
- Don't modify an asset you have not investigated; a change to behavior you do not understand is a guess that breaks silently.

## Checklist
- You can explain how the asset accomplishes its behavior before you modify it.
- Your modification extends behavior you investigated, not behavior you assumed.

## Notes
A template's player character looks complex, but breaking it down section by section shows how each part contributes to the player's experience. Using an existing asset is quick and easy, but the time spent investigating it is what makes it repairable and extendable. The investigation is not optional diligence; it is the precondition for modifying the asset at all.
