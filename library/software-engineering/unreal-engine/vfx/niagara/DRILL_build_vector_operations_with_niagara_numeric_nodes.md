---
object_id: DRILL_build_vector_operations_with_niagara_numeric_nodes
object_type: drill
name: Build Vector Operations with Niagara Numeric Nodes
library_path:
- software-engineering
- unreal-engine
- vfx
- niagara
stage_binding: 2 block
lane_fit: teach
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
target_skill: Translate vector arithmetic into correctly typed Niagara graph nodes.
---

# Build Vector Operations with Niagara Numeric Nodes

## Practice Task
Translate vector arithmetic into correctly typed Niagara graph nodes.

## Target Skill
Translate vector arithmetic into correctly typed Niagara graph nodes.

## Setup
Use a scratch or test Niagara graph where Add, Subtract, and Multiply nodes can be created without affecting production content.

## Instructions
1. Create Add, Subtract, and Multiply nodes with their default Numeric pins.
2. Convert the pins to a vector type and enter two known vectors.
3. Verify component-wise addition and subtraction.
4. Multiply a vector by a scalar and record the resulting vector.
5. Change one node to an incompatible type, observe the mismatch, then correct it.

## Success Check
- The recorded Add and Subtract results match component-wise arithmetic.
- The scalar multiplication preserves direction while changing magnitude.
- The attempt with an incompatible pin type is named and the observed incompatibility is recorded before it is fixed.

## Common Failures
- Reporting only the expected math without building the Niagara nodes.
- Leaving the pins as generic or mismatched types and treating the graph as complete.

## Notes
The exercise tests both vector arithmetic and Niagara pin specialization rather than mathematical recall alone.
