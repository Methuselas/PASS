---
object_id: PAT_choose_the_map_update_call_that_does_not_construct_twice
object_type: pattern
name: Choose the Map Update Call That Does Not Construct Twice
library_path:
- software-engineering
- languages
- cpp
- containers
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- cpp
- containers
- efficiency
- api_design
- lookup
cross_links:
- rel: related_to
  target_object_id: PAT_tell_equality_from_equivalence_when_looking_up
- rel: related_to
  target_object_id: PAT_consider_emplacement_where_it_can_actually_help
- rel: related_to
  target_object_id: PAT_dont_add_a_default_constructor_a_class_cannot_honor
reference:
  source_title: 'Effective STL: 50 Specific Ways to Improve Your Use of the Standard Template Library'
  author: Scott Meyers
confidence: high
references: []
variants: []
---

# Choose the Map Update Call That Does Not Construct Twice

## Pattern Rule
**IF** you are putting a value into a keyed associative container and the mapped type is not trivially cheap to build
**THEN** name the intended operation directly: `try_emplace` for insert-only construction, `insert_or_assign` for add-or-replace, `at` for update-only checked access, and `find` or `contains` for presence without mutation
**ELSE** where the mapped type is a built-in or a small aggregate, both cost essentially nothing and subscripting is the clearer spelling.

## Do
- Read subscripting on these containers for what it is, which is unrelated to subscripting anything else. It means add-or-update: it returns a reference to the mapped value for that key, and where no such key exists it first creates one by default-constructing the mapped value.
- Follow that definition to the cost. Adding a new entry by subscripting and assigning builds a default object, assigns to it, and destroys the temporary that was assigned from — three calls that adding by insertion does not make, because insertion builds the value once, in place, from what you supplied.
- Follow it to the reverse cost too. Updating an existing entry by insertion requires constructing the pair to pass as the argument, which constructs a mapped value that is then thrown away because the key was already present; subscripting constructs nothing.
- Use `try_emplace` when an absent key should construct the mapped value and a present key should leave both the existing value and constructor arguments unused. Use `insert_or_assign` when either inserting or replacing is intended.
- Use `contains` for a boolean membership question in C++20, `find` when the iterator or mapped value is needed, and `at` when absence is an error rather than an insertion request.
- Supply a placement hint when you already know where the entry belongs — from a preceding bound search, for instance — which makes the insertion constant rather than logarithmic.

## Don't
- Don't reach for subscripting to test whether a key is present. It inserts a default-constructed entry as a side effect of asking, so the question changes the answer, and the container quietly accumulates entries nobody put there.
- Don't assume the mapped type can be default-constructed at all. Subscripting requires it, so a mapped type that has no sensible argument-free construction cannot be used with subscripting even where it would be efficient.
- Don't hand-write the efficient add-or-update helper any more. It was worth writing when the library offered only the two calls above; the library now offers both behaviors directly, and a hand-rolled version is a maintenance liability that duplicates them.

## Checklist
- Is this call adding an entry, updating one, or genuinely either?
- Is subscripting being used anywhere merely to check for presence?
- Does the mapped type have a default constructor, and does it cost anything?
- Is a call available that constructs the mapped value only when it is actually needed?
- Does the chosen name distinguish membership, update-only, insert-only, and add-or-replace?
- Is a position already known from a previous search that could serve as a hint?

## Notes
The trap is the reasonable assumption that subscripting a container is a lookup. On the keyed associative containers it is not — it is an insertion that returns a reference — and the entries it silently creates are the failure people meet before they ever meet the performance question. A read-only-looking expression that modifies the container is unusual enough to be worth flagging on its own.

Meyers works up to a helper function that gets the best of both by locating the position with a bound search, testing equivalence there, and either assigning or inserting with that position as a hint. The reasoning is worth following because it shows what "efficient" actually requires: one traversal rather than two, and no constructed value that goes unused.

The library now supplies the durable operations directly. `try_emplace` and `insert_or_assign` arrived before the C++20 floor, and `contains` supplies the non-mutating boolean query. The old cost model still explains why `operator[]` can default-construct and overwrite, but it no longer justifies hand-writing an add-or-update helper.
