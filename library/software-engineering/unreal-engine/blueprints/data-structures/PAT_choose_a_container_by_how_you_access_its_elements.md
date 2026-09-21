---
object_id: PAT_choose_a_container_by_how_you_access_its_elements
object_type: pattern
name: Choose a Container by How You Access Its Elements
library_path:
- software-engineering
- unreal-engine
- blueprints
- data-structures
stage_binding: 0 design
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: framework
foundation_object_id: none
tags:
- unreal_engine
- blueprints
- data_structures
- containers
- arrays
- sets
- maps
cross_links:
- rel: related_to
  target_object_id: PAT_choose_blueprint_variable_type_by_value_kind
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Choose a Container by How You Access Its Elements

## Pattern Rule
**IF** you need to store multiple values of the same type in a single Blueprint variable and must choose which container to use
**THEN** pick the container from how you will access the elements: an array when you need ordered, indexed access (position matters), a set when you need unique membership and do not care about order or position, or a map when you look values up by a key.
**ELSE** where the values are few and each has a distinct meaning, separate single variables are clearer than a container.

## Do
- Use an array when elements have a meaningful order or position and you will read or write them by index (for example, one slot per weapon type).
- Use a set when you only need to know whether an element is present and duplicates must not accumulate (for example, the names of players who have won at least one round, without counting how many).
- Use a map when each element is a key-value pair and you look values up by key (for example, a price table keyed by product name).
- Remember the access shape of each: an array is ordered and indexed from 0; a set is unordered, has no index, and allows no duplicates; a map is unordered, searched by key, allows no duplicate keys but does allow duplicate values.

## Don't
- Don't use an array when you only need membership and uniqueness — a set gives you the uniqueness for free, and an array will accumulate duplicates.
- Don't use a set when you need order or position — a set has no index and no GET node, so you cannot address an element by position.
- Don't use a map when the key is just a position — an array's index is the cheaper key.
- Don't reach for a container when two or three single variables would be clearer.

## Checklist
- Do you need order or position? (array)
- Do you need uniqueness without order or count? (set)
- Do you look values up by a key? (map)
- Are the values few and individually meaningful enough that separate variables are clearer?

## Notes
The three containers differ on one axis: how an element is found. An array is found by position, a set by the value itself, and a map by a key. The choice is made once at variable creation — the container type is fixed — so pick from the access pattern you actually need, not from habit. A set has no GET node, so iterating one means copying it to an array first (TO ARRAY), which is a very costly operation for a whole array of large objects; that is another reason to choose a set only when you truly need membership rather than iteration.
