---
object_id: PAT_declare_who_may_read_and_write_blueprint_state
object_type: pattern
name: Declare Who May Read and Write Blueprint State
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
cross_links: []
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Declare Who May Read and Write Blueprint State

## Pattern Rule
**IF** you are creating a variable in a Blueprint and must decide who may read or change it
**THEN** set the variable's attributes to declare the access contract explicitly — per-instance versus shared, writable versus read-only, and visible to child Blueprints versus private.

## Do
- Check Instance Editable when each placed copy of the Blueprint should hold its own value; leave it unchecked when all copies share one initial value.
- Check Blueprint Read Only when no node in the graph should be able to change the variable.
- Check Private when child Blueprints must not be able to modify the variable.
- Check Expose on Spawn when the value should be settable at the moment the Blueprint is spawned.
- Use Value Range to clamp the variable to a minimum and maximum.

## Don't
- Don't leave the default attributes in place without deciding — the default is shared, writable, and visible to children, which is rarely the intent.
- Don't use Instance Editable to share a value across instances; it does the opposite, giving each instance its own copy.
- Don't rely on a variable being read-only or private by convention; the attribute is the only thing that enforces it.

## Checklist
- Each variable has an explicit per-instance versus shared decision (Instance Editable).
- Variables that must not change have Blueprint Read Only set.
- Variables that must not be modified by child Blueprints have Private set.
- Values that are set at spawn time have Expose on Spawn set, and clamped values have a Value Range.

## Notes
A variable's attributes are its access contract. Instance Editable controls whether each placed copy holds its own value or all copies share one initial value. Blueprint Read Only prevents nodes in the graph from changing the variable. Private prevents child Blueprints from modifying it. Expose on Spawn makes the value settable when the Blueprint is spawned. Value Range clamps the allowed values to a minimum and maximum. The default (all unchecked) is shared, writable, and visible to children, so the contract should be declared rather than inherited.
