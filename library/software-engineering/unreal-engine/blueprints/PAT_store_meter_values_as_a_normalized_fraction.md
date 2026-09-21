---
object_id: PAT_store_meter_values_as_a_normalized_fraction
object_type: pattern
name: Store Meter Values as a Normalized Fraction
library_path:
- software-engineering
- unreal-engine
- blueprints
stage_binding: 0 design
lane_fit: both
foundation_role: foundation
routing_class: general
specialization_axis: none
foundation_object_id: none
tags:
- unreal_engine
- blueprints
- umg
- ui
- meter
- data_representation
cross_links:
- rel: related_to
  target_object_id: PAT_bind_a_widget_property_to_the_value_it_displays
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Store Meter Values as a Normalized Fraction

## Pattern Rule
**IF** a progress bar or meter should display how full a quantity is — health, stamina, a charge
**THEN** store the quantity as a normalized fraction from 0.0 (empty) to 1.0 (full) and bind the bar's Percent to it directly, so the stored value is the fill position.

## Do
- Store the meter's value as a Float in the 0.0–1.0 range, with 1.0 meaning full.
- Bind the progress bar's Percent property to that value so the fill position is the stored value.
- Change the value within the 0.0–1.0 range to change the fill; the bar reflects it directly.

## Don't
- Don't store the quantity in raw units (100 health points) and expect the bar to scale it — the Percent is a 0.0–1.0 fraction, so a raw value above 1.0 overfills or is meaningless.
- Don't keep a separate "full" constant in the widget and divide there when the value can be stored normalized already.

## Checklist
- The meter's value is stored as a 0.0–1.0 fraction.
- The progress bar's Percent is bound to that value.
- Changing the value within range changes the fill directly.

## Notes
A progress bar's Percent property is a fraction from 0.0 (empty) to 1.0 (full) that sets the fill position. Storing the underlying quantity normalized to that same 0.0–1.0 range means the bar's Percent can be bound to the value directly, with no scaling in between. This keeps the meter's data representation aligned with the widget's fill representation: the value you store is the fill you see.
