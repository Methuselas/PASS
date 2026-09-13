---
object_id: PAT_implement_the_standalone_operator_from_the_compound
object_type: pattern
name: Implement the Standalone Operator From Its Compound Assignment
library_path:
- software-engineering
- languages
- cpp
- operators
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- cpp
- operators
- class_design
- efficiency
- consistency
cross_links:
- rel: related_to
  target_object_id: PAT_make_operator_nonmember_for_conversions
- rel: related_to
  target_object_id: PAT_return_by_value_when_returning_new_object
reference:
  source_title: 'More Effective C++: 35 New Ways to Improve Your Programs and Designs'
  author: Scott Meyers
confidence: high
references: []
variants: []
---

# Implement the Standalone Operator From Its Compound Assignment

## Pattern Rule
**IF** your class offers an arithmetic-style operator and clients will reasonably expect both the standalone spelling and its compound-assignment counterpart to exist and agree
**THEN** write the compound-assignment version as the real implementation and define the standalone version by calling it, and ship both
**ELSE** where only one of the pair makes sense for the type — an operation with no meaningful in-place form, or no meaningful value form — ship the one that does and leave the other undeclared rather than faked.

## Do
- Start from the fact that the language relates none of these to each other. Nothing connects the standalone operator, plain assignment, and the compound form, so any consistency between them is consistency you wrote and are maintaining. This is a statement about the arithmetic-style operators, and it is worth holding as such rather than as a general fact about operator families: the comparison operators are related by the language, where one three-way operator generates the relational spellings and a defaulted one generates equality too. Carrying the arithmetic expectation across to comparisons produces six hand-written overloads where one line would have done. See `PAT_define_one_three_way_comparison_and_let_the_language_derive_the_rest`.
- Name the result: copy the left operand into a local, apply the compound operator to it, and return the local. The shorter spelling that returns a copy of the left operand with the compound operator applied in the same expression looks like a temporary and is not one — compound assignment returns a reference, so that expression is an lvalue and returning it copies. Measured, it made two copies where the named local made one.
- Ship both spellings so callers can choose. Chained standalone expressions read better and are easier to debug; the sequence of compound assignments avoids constructing a temporary at each step, and clients under performance pressure can switch between them knowing the semantics are identical because one is written in terms of the other.
- Keep the compound versions in the public interface, which also removes any need for the standalone ones to be friends of the class.

## Don't
- Don't maintain two independent implementations of the same arithmetic. When the meaning of the operation changes, only one of them will be updated, and the version that falls behind will be the one used in the expression form that reads most naturally.
- Don't assume the standalone spelling is merely a convenience wrapper with equivalent cost. It has to produce a new object to hand back, which the compound form never does, because the compound form writes into an operand that already exists.

## Checklist
- For each arithmetic-style operator on this class, does the compound counterpart exist?
- Does exactly one of the two contain the actual arithmetic?
- Does the standalone version return a named local, rather than the result of the compound expression, which is an lvalue and forces a copy?
- If the operation's definition changed, how many places would need editing?

## Notes
The consistency argument is the durable half of this and the efficiency argument is the contingent half. Clients will assume a relationship between the two spellings whether or not you established one, so the reason to derive one from the other is that the assumption then holds by construction instead of by discipline.

The efficiency half has reversed since Meyers wrote it. Guaranteed elision applies to a returned prvalue, and the compound expression is not one: compound assignment returns a reference, so returning its result copies from that reference every time. A named local is eligible for elision and is at worst moved, which makes it the cheaper of the two forms rather than the riskier one.

Where all the standalone operators can live at namespace scope, a template can generate them from the compound versions, so that any type supplying the compound form gets the standalone one without a line being written for it.
