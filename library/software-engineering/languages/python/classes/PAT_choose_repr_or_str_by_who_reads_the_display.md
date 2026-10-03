---
object_id: PAT_choose_repr_or_str_by_who_reads_the_display
object_type: pattern
name: Choose __repr__ or __str__ by Who Reads the Display
library_path:
- software-engineering
- languages
- python
- classes
stage_binding: 2 block
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- python
- classes
- display
- debugging
cross_links:
- rel: related_to
  target_object_id: PAT_overload_an_operator_only_to_mimic_a_builtin_interface
- rel: related_to
  target_object_id: PAT_pick_the_string_formatting_tool_by_who_writes_the_template
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Choose __repr__ or __str__ by Who Reads the Display

## Pattern Rule
**IF** a class needs a readable display instead of the default class-name-and-address form
**THEN** implement `__repr__` for the developer-facing form — ideally one that looks like the call that would rebuild the object — because it is used everywhere except `print()` and `str()` when a `__str__` exists; add `__str__` only when end users need a different, friendlier string
**ELSE** when the class is a plain record, let `@dataclass` generate `__repr__` from the declared fields so it cannot drift as fields are added

## Do
- Implement `__repr__` first, always. It backs the interactive prompt, the debugger, logging, error messages, and the display of objects nested inside lists and dicts.
- Aim for an unambiguous developer display: the class name plus the state that distinguishes this instance, in a form a reader can match against the constructor.
- Add `__str__` only when there is a genuinely different audience — a message shown to a user, a value written to a report — and let `__repr__` keep serving everything else.
- Return a string from both; any other type raises `TypeError` rather than being converted, so run values through `str()` or formatting first.
- Derive the display from the object's actual state rather than a hardcoded list of fields, so adding a field cannot leave the display quietly out of date.

## Don't
- Don't implement only `__str__` and expect it everywhere. A list of such objects prints the bare default form for each element, because containers display their items with `repr`, and the interactive prompt does the same.
- Don't put secrets, passwords, tokens or full payloads in either display; both end up in logs and tracebacks, which are exactly the places that get copied into bug reports.
- Don't let a display method do real work or raise — it runs in debuggers and error paths, where a failure during display hides the problem you were trying to see.
- Don't build a display that includes another object's display that can lead back to this one; mutually referential displays recurse until the stack runs out.

## Checklist
- Does the class define `__repr__`, not just `__str__`?
- Does printing a list of these objects show something useful?
- Would a reader of a log line be able to tell two different instances apart from the display alone?
- Could the display expose a secret, or fail, in a context where that would mask the real error?

## Notes
The split is by audience, and the fallback runs in only one direction: `print()` and `str()` prefer `__str__` and fall back to `__repr__`, while everything else — `repr()`, interactive echo, containers, debuggers — uses `__repr__` and never consults `__str__`. One consequence is worth remembering on its own: implementing `__repr__` alone gives a single consistent display in every context, while implementing `__str__` alone gives you a nice display in exactly two places and the default everywhere else.
