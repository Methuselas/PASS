---
object_id: PAT_always_pass_an_explicit_encoding_name_to_encode_and_decode
object_type: pattern
name: Always Pass an Explicit Encoding Name to encode() and decode()
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
- encoding
cross_links:
- rel: related_to
  target_object_id: PAT_choose_str_bytes_or_bytearray_by_data_kind_and_mutability
- rel: related_to
  target_object_id: PAT_open_files_in_a_with_block_and_name_the_encoding
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Always Pass an Explicit Encoding Name to encode() and decode()

## Pattern Rule
**IF** text is being converted to bytes or bytes are being converted to text, whether through `str.encode`, `bytes.decode`, or the `bytes(s, encoding)` / `str(b, encoding)` constructor forms
**THEN** name the encoding explicitly every time, rather than relying on whatever the platform's default happens to be
**ELSE** there is no safe default case here; even when a call's encoding argument is technically optional, omitting it means the result depends on the machine running the code rather than on the data itself

## Do
- Pass an explicit encoding name to every `.encode()` and `.decode()` call, and to every `bytes(s, encoding=...)` / `str(b, encoding=...)` conversion.
- Pick the encoding from what the data actually is (the scheme it was written in, or the scheme a receiving system requires), not from whatever happens to run without raising an error on your machine.
- Treat a successful conversion with the wrong encoding name as a real bug, not a non-event; characters can decode to different, equally valid-looking text under the wrong scheme, and nothing will flag the mismatch.

## Don't
- Don't call `bytes(some_str)` expecting a default encoding to kick in; the encoding argument is not optional there, and the call raises `TypeError` rather than silently picking one.
- Don't call `str(some_bytes)` without an encoding and assume it has decoded the bytes to text; without an encoding name, `str()` on a bytes object returns that object's printable representation as a string (its `repr`-like form, including the `b'...'` wrapper and any escapes) — not a text conversion at all.
- Don't assume the platform default encoding is stable across machines, OS versions, or even Python configurations; code that omits the encoding name behaves differently depending on where it runs, which is the opposite of what a library should do.

## Checklist
- Does every `.encode()`, `.decode()`, `bytes(s, ...)`, and `str(b, ...)` call in the code name its encoding explicitly?
- Where `str()` is applied to a `bytes` object, was an encoding supplied — and if not, is the resulting string actually meant to be a debug display rather than converted text?
- Would this code produce the same result on a machine with a different platform default encoding?

## Notes
The platform default exists so simple, ASCII-only scripts can ignore encodings entirely and still work, which is exactly what makes it a trap once anything non-ASCII enters the picture: the code keeps running, produces a result, and gives no indication that the result would differ on another machine. `str()`'s behavior on a bare `bytes` argument is the sharper version of the same trap — it does not fail, it does not decode, and it quietly returns something that looks like it might be the text you wanted while actually being the object's print form.
