---
object_id: PAT_choose_development_or_shipping_build_configuration_by_audience
object_type: pattern
name: Choose Development or Shipping Build Configuration by Audience
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
- packaging
- build_configuration
cross_links: []
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Choose Development or Shipping Build Configuration by Audience

## Pattern Rule
**IF** you are choosing the Build Configuration when packaging a Blueprint-only project
**THEN** build Development while you are still finding errors — it contains debug information that helps you locate them — and Shipping for the final version you distribute, which strips that debug information.

## Do
- Set the Build Configuration on the Project - Packaging page (Platforms submenu → Packaging Settings in the Level Editor).
- Point the Staging Directory at the folder where you want the packaged build stored.
- Enable For Distribution when submitting to a store such as the App Store or Google Play, which requires it.

## Don't
- Don't hand players a Development build — the debug information is for your error-finding, not their experience.
- Don't look for a third configuration: Blueprint-only projects offer only Development and Shipping.

## Checklist
- The build you distribute is configured as Shipping.
- Debug work was done against a Development build.
- Store submissions have For Distribution enabled.

## Notes
Packaging takes all the code and assets of the game and sets them up in the proper format to perform on the selected platform; the Build Configuration decides how that build is made. Development keeps the information you need while errors are still being found, and Shipping produces the cleaner artifact that goes out to players. The same page carries other packaging options — some platform-specific — worth studying for your target platform before release.
