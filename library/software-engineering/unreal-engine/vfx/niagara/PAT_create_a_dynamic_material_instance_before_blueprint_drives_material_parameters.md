---
object_id: PAT_create_a_dynamic_material_instance_before_blueprint_drives_material_parameters
object_type: pattern
name: Create a Dynamic Material Instance before Blueprint Drives Material Parameters
library_path:
- software-engineering
- unreal-engine
- vfx
- niagara
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: none
tags:
- unreal_engine
- niagara
- vfx
cross_links: []
reference:
  source_title: Build Stunning Real-time VFX with Unreal Engine 5
  author: Hrishikesh Andurlekar
confidence: high
references: []
variants: []
---

# Create a Dynamic Material Instance before Blueprint Drives Material Parameters

## Pattern Rule
**IF** a Blueprint instance must change parameterized material values without modifying the shared base material
**THEN** create a Dynamic Material Instance for the component and set parameters on that instance.

## Do
- Parameterize the material inputs that Blueprint must control.
- Create the Dynamic Material Instance before setting texture/vector/scalar parameters.
- Apply updates to the dynamic instance owned by the component.

## Don't
- Do not modify the shared base material asset to implement one actor's per-instance state.

## Checklist
- Different actor instances can hold different material parameter values.

## Notes
The logo-fire Blueprint uses a dynamic material on its Plane component.
