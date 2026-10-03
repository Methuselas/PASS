---
object_id: PAT_choose_a_record_type_by_how_its_fields_are_used
object_type: pattern
name: Choose a Record Type by How Its Fields Are Used
library_path:
- software-engineering
- languages
- python
- collections
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- python
- records
- tuples
- namedtuple
- dataclasses
cross_links:
- rel: related_to
  target_object_id: PAT_use_dedicated_types_over_general_ones
- rel: related_to
  target_object_id: PAT_make_immutability_deep
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Choose a Record Type by How Its Fields Are Used

## Pattern Rule
**IF** Python code groups a few related values into one record — a point, an employee, a parsed row
**THEN** choose the type by how the fields are used: a plain tuple for a short, fixed group that is unpacked immediately or used as a dictionary key; a `typing.NamedTuple` when the same fixed group travels through the program and fields should be read by name; a `dataclass` when the record has defaults, validation, methods, or fields that change; a `dict` when the set of keys is open-ended or comes from outside, as with JSON
**ELSE** when a list is being used as a record (`rec[0]` is a name, `rec[1]` an age), replace it; lists are for collections of like items that grow and shrink.

## Do
- Return several values from a function as a tuple and unpack them at the call: `name, age = parse(line)`.
- Use tuples, not lists, as dictionary keys and set members for compound values such as coordinates and dates.
- Declare named tuples with types: `class Point(NamedTuple): x: float; y: float`, which gives attribute access, positional unpacking and a readable repr.
- Make a record immutable and hashable with `@dataclass(frozen=True)` when it is a value that should not change after construction.
- Pass tuples where a callee must not change the collection; the object itself cannot be altered through any reference.

## Don't
- Don't treat a tuple as deeply immutable: `(1, [2, 3])` still lets the inner list change, and such a tuple is unhashable. Keep only immutable values inside when integrity or hashing matters.
- Don't forget the comma of a one-item tuple: `(40)` is an integer, `(40,)` is a tuple.
- Don't index a record by position (`bob[2]`) when a name would say what the field is.
- Don't reach for a dict when every record has the same known fields; typos in keys become silent new entries instead of errors.

## Checklist
- Are the record's fields fixed and known, or open-ended?
- Is the record used as a key or set member, and is everything inside it hashable?
- Does any code read fields by numeric position where a name would be clearer?
- Should the record change after construction, and does its type allow or prevent that?

## Notes
Tuples are immutable sequences: they support indexing, slicing, concatenation and iteration but no in-place changes, and they have only `index` and `count` methods. Immutability is one level deep — it protects which objects the tuple holds, not the state of those objects. `collections.namedtuple` and `typing.NamedTuple` generate tuple subclasses whose fields are also attributes; `_asdict()` returns a plain `dict`. Data classes generate `__init__`, `__repr__` and `__eq__` from annotated class attributes and are the usual choice once a record needs behaviour.
