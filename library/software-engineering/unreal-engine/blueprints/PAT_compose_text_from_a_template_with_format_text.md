---
object_id: PAT_compose_text_from_a_template_with_format_text
object_type: pattern
name: Compose Text From a Template With Format Text
library_path:
- software-engineering
- unreal-engine
- blueprints
stage_binding: 1 skeleton
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: none
tags:
- unreal_engine
- blueprints
- text
- format
cross_links: []
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Compose Text From a Template With Format Text

## Pattern Rule
**IF** you need to build a text string from a template and named values
**THEN** use the Format Text node, which builds text based on a template and the parameters specified in it.

## Do
- Write the template in the Format input parameter, marking each value with {} delimiters (for example, `{Name} wins the round with {Score} points`).
- Wire each named parameter to its input pin — an input parameter is created for each {} delimiter found in the Format parameter.
- Use the Result as the composed text.

## Don't
- Don't build the string by concatenating values with separate nodes when a template with named parameters is clearer.

## Checklist
- The template uses {} delimiters for each value.
- Each {} has a corresponding wired input parameter.
- The Result is the composed text.

## Notes
Example: the template `{Name} wins the round with {Score} points` with Name = Sarena and Score = 17 produces "Sarena wins the round with 17 points".
