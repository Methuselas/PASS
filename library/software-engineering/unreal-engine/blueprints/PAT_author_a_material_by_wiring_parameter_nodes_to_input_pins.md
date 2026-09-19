---
object_id: PAT_author_a_material_by_wiring_parameter_nodes_to_input_pins
object_type: pattern
name: Author a Material by Wiring Parameter Nodes to the Result Node's Input Pins
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
- materials
cross_links:
- rel: related_to
  target_object_id: PAT_model_an_actors_surface_look_as_a_swappable_material_asset
reference:
  source_title: Blueprints Visual Scripting for Unreal Engine 5 - Unleash the true power of Blueprints to create
  author: Marcos Romero and Brenden Sewell
confidence: medium
references: []
variants: []
---

# Author a Material by Wiring Parameter Nodes to the Result Node's Input Pins

## Pattern Rule
**IF** you are defining a Material's look in the Material Editor
**THEN** build a node graph in which parameter nodes feed the result node's input pins — a VectorParameter for a color wired to Base Color, and a ScalarParameter for a single float wired to Metallic or Roughness.

## Do
- Open the Material by double-clicking it; the node in the center of the graph, labeled with the Material's name, is the result node whose input pins define the Material's properties.
- Add a parameter node by right-clicking in the graph and using the context-sensitive search box (typing the node name filters the list), then rename the node to say what it holds.
- Set a VectorParameter's value by double-clicking its swatch to open the color picker; set a ScalarParameter's value in its Details panel.
- Connect nodes by dragging from an output pin (right side of a node) to an input pin (left side), the same convention as Blueprints.

## Don't
- Don't leave the result node's input pins unconnected — an unconnected pin means the Material has no value for that property.
- Don't try to set the look on the mesh or the Actor directly; the look is defined by the node graph feeding the result node.

## Checklist
- Each property you want the Material to have (Base Color, Metallic, Roughness) has a parameter node wired to its input pin on the result node.
- The Material's appearance matches the parameter values you set.
- The node graph is fully connected with no dangling pins on the properties you intend to use.

## Notes
The Material Editor shares the node-graph conventions of Blueprints: a central graph, nodes with input pins on the left and output pins on the right, and a context-sensitive search to find nodes. The result node is the single node labeled with the Material's name; every other node feeds one of its input pins to define a property.
