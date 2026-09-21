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
variants:
- variant_id: VAR_use_a_validated_get_at_the_reference_read
  variant_name: Use a Validated Get at the Reference Read
  variant_basis: method_sequence
  difference_from_foundation: When the possibly-null object reference already comes from a variable Get node, convert that Get to a Validated Get so the value and Is Valid / Is Not Valid execution paths are exposed together. This is the same validity decision as the standalone Is Valid guard, expressed at the read site rather than with a separate guard node.
  when_to_use: Use when a variable Get is already the point where the reference enters the execution chain and combining the read with the validity split keeps the graph clearer.
  when_not_to_use: Do not treat it as categorically superior to a standalone Is Valid check. Use the standalone form when the reference does not come from a variable Get, when the guard is clearer as a separate decision, or when the graph already has the reference value available.
  absorbed_from_object_id: PAT_use_a_validated_get_to_branch_on_a_reference_validity
---

# Guard Object References With Is Valid Before Use

## Pattern Rule
**IF** you are about to call a function or read a property through an object reference variable
**THEN** branch on the Is Valid check first and only use the reference on the valid branch, because an object reference defaults to None and calling through a null reference is a failure.

## Do
- Treat None (null) as the normal starting state of an object reference variable; it references no instance until one is assigned.
- Assign references in the Level Editor for placed instances (the variable must be Instance Editable) or at runtime from a spawn or lookup.
- Run the Is Valid macro before acting on a reference that may not have been assigned yet, and route the not-valid branch to a safe no-op or a setup step. When the reference is being read from a variable Get node, the Validated Get variant can combine that read with the same validity split.

## Don't
- Don't call functions on a reference that might still be None — the Is Valid check exists precisely to avoid calling a function through a null reference.
- Don't skip the check on the assumption that a reference was assigned — a variable that was never assigned is None.

## Checklist
- Every use of a possibly-null reference is behind an Is Valid branch.
- The not-valid branch does nothing harmful (no-op, log, or re-acquisition).
- References assigned in the Level Editor are on Instance Editable variables.

## Notes
Object references are how Blueprints talk to each other: a variable of another class's type holds a pointer to an instance, and its public variables and functions become reachable through it. The default None state is what makes the guard necessary — a freshly created reference variable points at nothing. Variant `VAR_use_a_validated_get_at_the_reference_read` is the alternate method for the same decision when the reference is read from a variable: convert that Get to a Validated Get so the value and validity execution paths are exposed together. Use it when that combination makes the read site clearer; keep a standalone Is Valid guard when the reference is already available or the separate decision reads better.
