---
object_id: PAT_capture_a_loop_variable_with_a_default_argument
object_type: pattern
name: Capture a Loop Variable with a Default Argument
library_path:
- software-engineering
- languages
- python
- functions
stage_binding: 3 rough
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- python
- functions
- closures
- gotcha
cross_links:
- rel: related_to
  target_object_id: PAT_retain_per_call_state_in_a_closure_declaring_nonlocal_to_change_it
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Capture a Loop Variable with a Default Argument

## Pattern Rule
**IF** creating functions inside a loop — callback handlers, `lambda` expressions, generated actions — where each one needs the loop variable's value from its own iteration
**THEN** capture that value in a default argument in the generated function's own header, because defaults are evaluated when the function is created rather than when it is later called
**ELSE** when the generated function needs no per-iteration value, or the loop produces exactly one function, an ordinary enclosing-scope reference is fine

## Do
- Bind the value at creation time by adding a parameter whose default is the loop variable, so each produced function carries its own copy from the iteration that made it.
- Give that captured parameter the same name as the loop variable when it reads clearly, and place it after the parameters real callers are expected to pass.
- Suspect this bug the moment every generated handler behaves identically — all of them reflecting the loop's final value — rather than one per item.
- Check generated callbacks built in a loop over widgets, rows, or menu items specifically; this is where the mistake shows up in working programs rather than in exercises.

## Don't
- Don't rely on enclosing-scope capture for a loop variable: the nested function looks the name up when it is called, and by then the loop has finished, so every function produced sees the last value the variable held.
- Don't try to fix it by renaming or copying the loop variable inside the loop body but outside the generated function; the generated function still looks up whatever that name holds at call time.
- Don't take a passing test with a single-iteration loop as evidence that the capture works; the defect only appears once the loop runs more than once.

## Checklist
- Does each function produced in this loop return a result derived from its own iteration rather than the last one?
- Is the per-iteration value bound in the generated function's header rather than referenced from the enclosing scope?
- Would this still be correct if the loop ran one more time after the functions were created?

## Notes
This is the one place where a default argument remains the right way to carry a value into a nested function, even though enclosing-scope lookup covers every other case. The difference is timing: a default is evaluated once, while the function is being built, so it freezes the value then; an enclosing-scope reference is resolved on each call, so it reports whatever the name holds by then. A loop rebinds one name repeatedly, which is exactly the situation where those two timings disagree.
