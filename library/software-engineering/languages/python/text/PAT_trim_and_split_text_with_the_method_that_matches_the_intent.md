---
object_id: PAT_trim_and_split_text_with_the_method_that_matches_the_intent
object_type: pattern
name: Trim and Split Text with the Method That Matches the Intent
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
- parsing
- split
- strip
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

# Trim and Split Text with the Method That Matches the Intent

## Pattern Rule
**IF** Python code removes a known piece from the end of a string or breaks a line into fields
**THEN** use the method whose behaviour matches what you mean — `removeprefix`/`removesuffix` for one exact piece, `strip`/`rstrip` for any run of certain characters, `split()` for whitespace-separated words, `split(sep)` for exact delimiters, `partition` for one split point, and the `csv` module for quoted or escaped fields
**ELSE** when the layout is fixed-width columns, slice at known offsets and validate the line length first.

## Do
- Remove a line ending with `line.rstrip('\n')` (or `rstrip()` to drop trailing whitespace too); it leaves a last line that has no newline untouched.
- Remove an exact prefix or suffix with `name.removesuffix('.txt')` and `url.removeprefix('www.')` (Python 3.9+).
- Split on runs of whitespace with `split()`, which also drops leading and trailing whitespace; split on an exact delimiter with `split(',')`, which keeps empty fields: `'a,,b'.split(',')` is `['a', '', 'b']`.
- Split once with `key, sep, value = line.partition('=')`; `sep` is empty when the delimiter is missing, so the check is explicit.
- Read comma- or tab-separated data with `csv.reader`, which handles quoted fields such as `a,"b,c",d`.
- Put strings back together with the delimiter's `join`: `','.join(fields)`.

## Don't
- Don't use `strip`, `lstrip` or `rstrip` to remove a word: their argument is a set of characters, not a substring. `'report.txt'.rstrip('.txt')` is `'repor'`, and `'www.wikipedia.org'.lstrip('w.')` is `'ikipedia.org'`.
- Don't cut a newline with `line[:-1]`; it deletes a real character from a final line that has no newline.
- Don't use `split(' ')` for words; two spaces produce an empty field.
- Don't hand-split CSV with `split(',')` once any field can contain a comma or a quote.

## Checklist
- Does each strip call mean "these characters", not "this text"?
- Does the split keep or drop empty fields, and which does the data need?
- Can a field contain the delimiter, and if so is `csv` doing the parsing?
- Does the code handle a last line without a newline?

## Notes
Python strings are immutable sequences, so every one of these methods returns a new string and indexing and slicing work as on any sequence: offsets start at 0, negative offsets count from the end, and a slice `S[i:j]` includes `i` and excludes `j`. String methods do plain text matching; pattern matching lives in the `re` module, and plain methods are usually faster when they suffice.
