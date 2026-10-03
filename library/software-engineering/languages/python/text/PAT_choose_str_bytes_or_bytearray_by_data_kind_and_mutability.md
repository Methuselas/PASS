---
object_id: PAT_choose_str_bytes_or_bytearray_by_data_kind_and_mutability
object_type: pattern
name: Choose str, bytes, or bytearray by Data Kind and Mutability
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
- unicode
cross_links:
- rel: related_to
  target_object_id: PAT_open_files_in_a_with_block_and_name_the_encoding
- rel: related_to
  target_object_id: PAT_always_pass_an_explicit_encoding_name_to_encode_and_decode
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Choose str, bytes, or bytearray by Data Kind and Mutability

## Pattern Rule
**IF** a piece of data in your program is text — characters meant to be read, matched, or displayed, in any language or character set
**THEN** represent it with `str`, never `bytes` or `bytearray`
**ELSE** when the data is binary — image content, packed records, network payloads, anything that is not characters — represent it with `bytes` if it is read-only, or `bytearray` if it must be changed in place without copying

## Do
- Decide text-or-binary first, before reaching for a type; `str` is Unicode characters (code points), while `bytes` and `bytearray` are sequences of small integers (0–255) that happen to print as ASCII when possible.
- Default to `bytes` for binary data, and upgrade to `bytearray` only once in-place mutation is actually needed — appending, extending, or assigning to an index without rebuilding the whole object.
- Let the tool that hands you the data make the choice for you where it already does: a binary-mode file read, a `struct.pack` call, and most networking APIs hand back `bytes` already; a text-mode file read hands back `str`.
- Keep a value in the type it started as unless a specific operation genuinely requires the other; indexing a `str` yields a one-character `str`, while indexing `bytes` or `bytearray` yields a plain integer.

## Don't
- Don't mix `str` with `bytes` or `bytearray` in the same expression or call — concatenation, comparison, and pattern-matching functions like `re.match` all raise a `TypeError` when given mismatched types, rather than silently converting one for you.
- Don't reach for `bytearray` by default "in case something needs to mutate it"; most binary data is read, transformed into a new object, and discarded, which `bytes` already handles without the extra mutability no one uses.
- Don't assume a `bytes` or `bytearray` object represents text just because it prints as letters; `b'97'` and the integer sequence `[57, 55]` are the same object viewed two ways, and nothing about it is a character until it is decoded.
- Don't call a method that exists on `bytes`/`bytearray` but not `str` (or vice versa) and expect it to coerce; check which type you actually have before reaching for format strings (`str`-only) or `decode`/`fromhex` (`bytes`/`bytearray`-only).

## Checklist
- For each variable holding string-like data, is it unambiguous whether it represents text or binary content?
- Where binary data is held in `bytearray`, is there an actual in-place mutation happening, rather than habit?
- Does any expression or call mix `str` with `bytes`/`bytearray` without an explicit `.encode()`/`.decode()` between them?
- Does a tool's own return type (file read, `struct.pack`, a parser) already dictate the type here, rather than a type chosen independently?

## Notes
All three types share most of their operation set — slicing, concatenation, `find`, `split`, and more work the same way across them — which is exactly why mixing them is easy to attempt and immediately rejected: the language draws a hard line between decoded text and raw bytes precisely because the two answer different questions ("what characters are these" versus "what byte values are these") that happen to look similar in code. `bytearray` adds nothing to that distinction; it only adds the ability to change a binary sequence's contents without allocating a new object, the same tradeoff a list makes against a tuple.
