---
object_id: PAT_pick_a_serialization_format_by_who_reads_it_back
object_type: pattern
name: Pick a Serialization Format by Who Reads It Back
library_path:
- software-engineering
- languages
- python
- files
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- python
- serialization
- json
- pickle
- security
cross_links:
- rel: related_to
  target_object_id: PAT_parse_untrusted_text_instead_of_evaluating_it
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Pick a Serialization Format by Who Reads It Back

## Pattern Rule
**IF** Python objects must be saved to a file or sent to another process
**THEN** choose the format by who will read the data and whether they can trust it: `json` for data read by other programs, other languages or people; `csv` for tables exchanged with spreadsheets and databases; `struct` for fixed binary layouts defined by a C program, file format or protocol; `pickle` only for data your own trusted code wrote and will read back
**ELSE** when the data may come from anyone else — a download, an upload, a shared directory — never load it with `pickle`; use `json` or another format whose loader only builds data.

## Do
- Write and read JSON with `json.dump(obj, f, indent=2)` and `json.load(f)` on text files opened with `encoding='utf-8'`.
- Convert types JSON lacks at the edges: tuples come back as lists, dictionary keys become strings (`{1: 'a'}` reloads as `{'1': 'a'}`), and tuple keys are refused, so map them to strings or nested structures deliberately.
- Open pickle files in binary mode (`'wb'`, `'rb'`); pickle produces bytes.
- Describe binary layouts once in a `struct` format string with an explicit byte order, such as `'>i4sh'`, and use the same string to `pack` and `unpack`.
- Read and write tabular text with `csv.reader` and `csv.writer`, opened with `newline=''` as the `csv` documentation requires.

## Don't
- Don't `pickle.load` data from a source you do not control; unpickling can call arbitrary functions — a crafted pickle runs code the moment it is loaded.
- Don't store objects by writing `str(obj)` and read them back with `eval`; use `json` or `ast.literal_eval`.
- Don't use pickle for data that must outlive the program's code or be read by another language; pickles name your classes and modules, and renaming them breaks old files.

## Checklist
- Who reads this data back, and can they trust whoever wrote it?
- Does any `pickle.load` or `eval` read data that crossed a trust boundary?
- Do the types that JSON cannot represent survive the round trip as intended?
- Is every binary format opened in binary mode with an explicit byte order?

## Notes
Files and sockets carry strings or bytes, never Python objects, so every save is a conversion. `pickle` is the most convenient converter because it handles almost any object graph, and that generality is exactly what makes it unsafe: the format can instruct the loader to call functions. `json` covers dictionaries, lists, strings, numbers, booleans and `None`, maps almost one-to-one onto Python literals, and is readable everywhere. `shelve` stores pickled objects by key in a file and inherits pickle's trust requirement.
