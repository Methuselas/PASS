---
object_id: PAT_expect_none_from_a_function_with_no_explicit_return
object_type: pattern
name: Expect None from a Function with No Explicit Return
library_path:
- software-engineering
- languages
- python
- functions
stage_binding: 2 block
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- python
- functions
- return-values
- none
cross_links:
- rel: related_to
  target_object_id: PAT_avoid_unexpected_side_effects
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Expect None from a Function with No Explicit Return

## Pattern Rule
**IF** a function body can fall off its end without running a `return`, or you are about to use the result of a call whose job is to act on an object in place
**THEN** expect that call to hand back `None`, and never assign, chain, or print that result as if it were the object the function acted on
**ELSE** where the function's documentation states a real return value, depending on that value is safe

## Do
- Read "no return statement" as "returns `None`," not as "returns nothing, which is an error." Python always hands a caller some value; absent a `return`, that value is `None`.
- Check a standard-library method's documentation before assigning its result. Many container methods mutate in place and report nothing about the result — `list.append`, `list.sort`, `list.extend`, `dict.update` — while others, like `str.upper` or `sorted`, build and return a new object instead of mutating.
- Call a known in-place mutator as its own statement, on its own line, and keep using the original name afterward to refer to the (now-changed) object.
- Treat a function that mixes "does a side effect" with "returns a value" as two jobs bolted together, and prefer splitting it so each call site is unambiguous about which it is getting.

## Don't
- Don't write `x = x.append(y)` or any equivalent reassignment through an in-place method; the right-hand side is `None`, and the statement replaces the only reference to the object just mutated with nothing.
- Don't assume a method name without a verb like "get" or "to" returns a fresh value; many mutators are verbs too (`append`, `sort`, `update`), and verb phrasing alone does not tell you which family a method belongs to.
- Don't rely on a function "obviously" returning its argument back just because that would be convenient at the call site; an author who intended a procedure has no obligation to return anything useful.

## Checklist
- Does this function's body guarantee a `return` on every path, or can control fall off the end?
- Is the method being called here documented as mutating in place, or as building and returning a new object?
- Is any call's result being assigned, chained, or printed before confirming it isn't `None`?

## Notes
A function without an explicit `return` (or with a bare `return`) is Python's equivalent of what other languages call a procedure or void function: it is invoked for its side effect, and the `None` it technically returns is meant to be thrown away. The standard library is not uniform about which style a given method uses, so the only reliable check is to look, not to guess from the method's name or from habits formed in another language.
