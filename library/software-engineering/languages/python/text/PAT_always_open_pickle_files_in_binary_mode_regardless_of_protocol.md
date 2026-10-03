---
object_id: PAT_always_open_pickle_files_in_binary_mode_regardless_of_protocol
object_type: pattern
name: Always Open pickle Files in Binary Mode, Regardless of Protocol
library_path:
- software-engineering
- languages
- python
- text
stage_binding: 2 block
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- python
- text
- bytes
- pickle
cross_links:
- rel: related_to
  target_object_id: PAT_open_files_in_a_with_block_and_name_the_encoding
- rel: related_to
  target_object_id: PAT_choose_str_bytes_or_bytearray_by_data_kind_and_mutability
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Always Open pickle Files in Binary Mode, Regardless of Protocol

## Pattern Rule
**IF** a file will be used to store or load data with the `pickle` module
**THEN** open it in binary mode (`'rb'` / `'wb'`) unconditionally
**ELSE** there is no protocol choice or data shape that makes a text-mode pickle file safe; `pickle.dumps` always returns `bytes`, no matter which protocol is selected

## Do
- Open every file that `pickle.dump`/`pickle.load` will use with `'wb'` or `'rb'`, with no exceptions based on which protocol number is in use.
- Treat `pickle.dump(obj, file)` as requiring a binary file object as firmly as it requires `obj` to be picklable; both are preconditions, not options.
- Remember this rule covers tools built on `pickle` as well, such as `shelve`, which stores pickled data under the hood.

## Don't
- Don't open a pickle file in text mode because an older or lower-numbered protocol looks like it produces readable ASCII-ish output; `pickle.dumps` returns `bytes` under every protocol, including protocol 0.
- Don't treat a text-mode pickle write or read that happens not to raise an error as evidence it is safe; pickled bytes that happen to be valid under the platform's default text encoding will decode by coincidence, not because the combination is actually supported.
- Don't special-case protocol selection as a way to make text mode work; the protocol controls the data format pickle produces, not the type of object that format is returned as.

## Checklist
- Is every file used with `pickle.dump`/`pickle.load` (or a tool built on `pickle`, like `shelve`) opened in binary mode?
- Does any code path open a pickle file in text mode under the assumption that a particular protocol makes it safe?
- Where a text-mode pickle operation currently appears to work, has it been verified that this is not accidental platform-specific luck?

## Notes
`pickle.dumps` returning `bytes` regardless of protocol is a statement about what pickled data fundamentally is: a serialized byte stream, not text, whatever characters its bytes happen to look like when printed. A text-mode file can only accept and return `str`, so pairing one with pickle data is a type mismatch waiting to surface — sometimes immediately as a `TypeError`, and sometimes not until the specific bytes involved fail to decode under whatever encoding the text mode is using, which can make the failure look data-dependent rather than structural.
