---
object_id: PAT_parse_untrusted_text_instead_of_evaluating_it
object_type: pattern
name: Parse Untrusted Text Instead of Evaluating It
library_path:
- software-engineering
- languages
- python
- execution
stage_binding: 3 rough
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- python
- security
- eval
- input
cross_links:
- rel: related_to
  target_object_id: PAT_barricade_dirty_data_at_a_named_boundary
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Parse Untrusted Text Instead of Evaluating It

## Pattern Rule
**IF** text that a user, file, network peer, or other program supplied has to become a Python value
**THEN** convert it with a parser that only builds values — `int()`, `float()`, `json.loads()`, `ast.literal_eval()` — never with `eval()` or `exec()`, which run the text as code with your program's privileges
**ELSE** when the input really must be code (a plugin, a configuration script), load it only from a location you control and treat it as part of the program, not as data.

## Do
- Read input with `input()` or from the file, keep it as a string, and convert it explicitly into the type you expect.
- Use `ast.literal_eval()` when the text is written in Python literal syntax (numbers, strings, tuples, lists, dicts, sets, booleans, `None`); it rejects names, calls and operators, so `__import__('os').remove(...)` raises `ValueError` instead of running.
- Decode numbers written in another base with `int(text, base)`: `int(text, 16)` for a known base, or `int(text, 0)` to honour a `0x`, `0o` or `0b` prefix and underscores exactly as Python literals do. Base 0 rejects an ambiguous leading zero such as `'010'` instead of guessing.
- Catch the conversion error (`ValueError`, `json.JSONDecodeError`, `SyntaxError`) at the boundary and report the bad input, rather than letting a parse failure escape as a crash.
- Prefer a data format the other side can produce reliably — JSON for structured data — over asking anyone to hand you Python source.

## Don't
- Don't write `eval(input())` to turn typed text into numbers or lists; typed text can also be a call that deletes files or opens a connection.
- Don't run a file's text with `exec(open(path).read())` when the path or its contents come from outside your control.
- Don't treat `eval` as safe because you passed restricted globals; attribute access through literals can still reach dangerous objects, and the restriction is not a security boundary.

## Checklist
- Does any path from outside input reach `eval`, `exec`, or `compile`?
- Is every conversion done by a function that can only produce data?
- Is a failed conversion caught and reported where the input arrives?

## Notes
`eval` and `exec` exist because Python compiles and runs code at run time — the same machinery that lets a program load modules and customize itself on site. That power is exactly the problem with untrusted text: to the interpreter there is no difference between a string that spells a list and one that spells a system call.

`int()` itself guards one more boundary: since Python 3.11 it refuses decimal strings longer than 4300 digits by default (`sys.set_int_max_str_digits`), because converting a huge digit string takes time that grows quadratically and an attacker can supply one. Raise the limit only for input you trust.

The rule has a long history in Python itself: an early version of the built-in `input()` evaluated what the user typed, and it was replaced by a version that returns the raw string, leaving the choice of conversion to the program.
