---
object_id: PAT_guard_object_references_with_is_valid
object_type: pattern
name: Guard Object References With Is Valid Before Use
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
- object_reference
- null_safety
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

# Guard Object References With Is Valid Before Use

## Pattern Rule
**IF** you are about to call a function or read a property through an object reference variable
**THEN** branch on the Is Valid check first and only use the reference on the valid branch, because an object reference defaults to None and calling through a null reference is a failure.

## Do
- Treat None (null) as the normal starting state of an object reference variable; it references no instance until one is assigned.
- Assign references in the Level Editor for placed instances (the variable must be Instance Editable) or at runtime from a spawn or lookup.
- Run the Is Valid macro before acting on a reference that may not have been assigned yet, and route the not-valid branch to a safe no-op or a setup step.

## Don't
- Don't call functions on a reference that might still be None — the Is Valid check exists precisely to avoid calling a function through a null reference.
- Don't skip the check on the assumption that a reference was assigned — a variable that was never assigned is None.

## Checklist
- Every use of a possibly-null reference is behind an Is Valid branch.
- The not-valid branch does nothing harmful (no-op, log, or re-acquisition).
- References assigned in the Level Editor are on Instance Editable variables.

## Notes
Object references are how Blueprints talk to each other: a variable of another class's type holds a pointer to an instance, and its public variables and functions become reachable through it. The default None state is what makes the guard necessary — a freshly created reference variable points at nothing.
