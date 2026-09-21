---
object_id: PAT_define_product_configurations_with_variant_sets_and_the_variant_manager
object_type: pattern
name: Define Product Configurations With Variant Sets and the Variant Manager
library_path:
- software-engineering
- unreal-engine
- blueprints
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: none
tags:
- unreal_engine
- blueprints
- variant_sets
- variant_manager
- product_configurator
cross_links: []
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Define Product Configurations With Variant Sets and the Variant Manager

## Pattern Rule
**IF** you need to let users switch between different options for a product (or any set of configurable parts) and see the changes applied to the level in real time
**THEN** use the Variant Manager panel to define Variants (each a configuration of a part) grouped into Variant Sets, where each Variant modifies the properties of specific Actors in the level, and drop the VariantSet asset into the level to create a Level Variant Sets Actor so the variants can be switched at runtime.

## Do
- Open the Variant Manager panel by double-clicking the Level Variant Sets asset (a VariantSet asset) in the content browser.
- Add a Variant Set with the +Variant Set button and add Variants to it with the + button next to the set name.
- For each Variant, add the level Actors it modifies and set the property values (for example, the Static Mesh on a Static Mesh Actor).
- Drop the VariantSet asset into the level to create a Level Variant Sets Actor, so the variants can be switched at runtime rather than only in the editor.
- Activate a Variant by double-clicking it in the panel; the property changes apply to the level immediately.

## Don't
- Don't edit the level Actors by hand for each configuration — the Variant holds the per-configuration property values and applies them, so the Actors stay shared.
- Don't expect the variants to change at runtime without the Level Variant Sets Actor — the asset alone only applies changes in the editor.

## Checklist
- Each Variant Set groups the configurations of one part, and each Variant modifies the intended Actors.
- Double-clicking a Variant applies its property changes to the level immediately.
- The Level Variant Sets Actor is in the level, so variants can be switched at runtime.

## Notes
The Variant Manager is the editor tool for a Level Variant Sets asset. A Variant is one configuration of a part (for example, a guitar body shape); a Variant Set groups the Variants of one part. Each Variant names the level Actors it modifies and the property values to apply. Dropping the asset into the level creates a Level Variant Sets Actor, which is what makes the variants switchable at runtime — the editor asset alone only applies changes in the editor. Grouping the product's Actors under a root (for example, a GuitarRoot) lets them move together.
