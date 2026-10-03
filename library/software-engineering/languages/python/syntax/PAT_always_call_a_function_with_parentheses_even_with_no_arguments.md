---
object_id: PAT_always_call_a_function_with_parentheses_even_with_no_arguments
object_type: pattern
name: Always Call a Function with Parentheses, Even with No Arguments
library_path:
- software-engineering
- languages
- python
- syntax
stage_binding: 1 skeleton
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- python
- syntax
- function-calls
- gotcha
cross_links: []
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Always Call a Function with Parentheses, Even with No Arguments

## Pattern Rule
**IF** intending to invoke a function, method, or other callable
**THEN** write the call with parentheses, `name()`, even when it takes no arguments
**ELSE** when the intent is genuinely to reference the callable object itself — to pass it as a value, store it, or compare it — write the bare name with no parentheses; that is the one case where omitting them is correct

## Do
- Add parentheses after every function or method call, including zero-argument ones like `file.close()`; the parentheses are what actually trigger the call.
- Use the bare name, with no parentheses, specifically when passing a function as a value — as a dict's value for dispatch, or as an argument to another function — since that is a deliberate reference, not a forgotten call.
- Double check any line where a callable's result was expected but nothing seems to have happened; a missing pair of parentheses fails silently rather than raising an error.

## Don't
- Don't write `file.close` expecting it to close the file; that expression only retrieves the bound method object and does nothing on its own — only `file.close()` calls it.
- Don't assume a missing `()` will be caught as a mistake; referencing a callable without calling it is completely legal Python, so the code runs without error while silently not doing what was intended.
- Don't confuse "callable with no required arguments" with "doesn't need parentheses"; every call needs the parentheses regardless of how many arguments it takes, including none.

## Checklist
- Does every place a function or method is meant to run actually include its call parentheses?
- Where a bare, unparenthesized name appears, is that deliberately a reference to the callable itself, not an accidentally omitted call?
- For an action that silently seems to do nothing (a file that isn't closing, a procedure that isn't running), has a missing `()` been ruled out?

## Notes
This fails silently because referencing a function and calling it are both completely ordinary, legal expressions in Python — the language has no way to know which one was intended, so it does exactly what was written. The classic version of this mistake is `file.close` in place of `file.close()`: the file stays open, and nothing about the running program signals that anything went wrong.
