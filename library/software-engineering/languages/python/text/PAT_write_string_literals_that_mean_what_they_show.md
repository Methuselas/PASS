---
object_id: PAT_write_string_literals_that_mean_what_they_show
object_type: pattern
name: Write String Literals That Mean What They Show
library_path:
- software-engineering
- languages
- python
- text
stage_binding: 3 rough
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- python
- strings
- escapes
- raw-strings
- paths
cross_links:
- rel: related_to
  target_object_id: PAT_trim_and_split_text_with_the_method_that_matches_the_intent
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Write String Literals That Mean What They Show

## Pattern Rule
**IF** a Python string literal contains backslashes, spans lines, or sits next to another literal
**THEN** write it so the characters in the source are the characters in the string: raw strings (`r'...'`) for regular expressions, `pathlib` or forward slashes for file paths, explicit escapes only for the control characters you mean, and a comma or `+` wherever two literals are meant to stay separate
**ELSE** when a string must end in a single backslash, which a raw string cannot do, write the doubled escape `'\\'` for that character.

## Do
- Write every regular expression as a raw string: `re.compile(r'\d+\.\d+')`.
- Build file paths with `pathlib.Path('C:/new') / 'text.dat'`, or with forward slashes, which Windows accepts; use a raw string only when a native backslash path must appear literally.
- Check a suspicious literal with `len()` or `repr()`: `'C:\new\text.dat'` is 13 characters containing a newline and a tab, not 15.
- Keep comments outside triple-quoted strings; text inside the quotes, including `# notes`, becomes part of the value.
- End each line of a multi-line list of strings with a comma, and check the list's length when it is data.

## Don't
- Don't rely on unrecognised escapes being kept: `"C:\py\code"` still works, but Python 3.12 and later report `SyntaxWarning: "\p" is an invalid escape sequence` and the behaviour is scheduled to become an error.
- Don't write `open('C:\new\text.dat')`; `\n` and `\t` are converted to control characters and the call opens the wrong name or fails.
- Don't leave out a comma between string literals in a list or call: adjacent literals are joined silently, so `['spam' 'eggs', 'ham']` has two items, `'spameggs'` and `'ham'`.
- Don't disable code by wrapping it in a triple-quoted string; it still has to parse, and it is easy to leave behind.

## Checklist
- Does every backslash in the literal produce the character intended?
- Are regular expressions raw strings?
- Are paths built with `pathlib` or forward slashes?
- Is every pair of adjacent string literals meant to be joined?

## Notes
Single and double quotes are interchangeable; pick the one that avoids escaping a quote inside the text. Escapes such as `\n`, `\t`, `\xhh`, `\uhhhh` and `\N{name}` stand for one character each, and `\0` is an ordinary character — Python strings carry their length and are not terminated by a zero. Implicit joining of adjacent literals exists so a long string can be split across lines inside parentheses; the same feature turns a missing comma into a silent data bug.
