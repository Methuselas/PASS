---
object_id: PAT_choose_the_bom_aware_encoding_name_for_a_text_files_byte_order_marker
object_type: pattern
name: Choose the BOM-Aware Encoding Name for a Text File's Byte Order Marker
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
- encoding
- files
cross_links:
- rel: related_to
  target_object_id: PAT_open_files_in_a_with_block_and_name_the_encoding
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Choose the BOM-Aware Encoding Name for a Text File's Byte Order Marker

## Pattern Rule
**IF** a text file may carry, or must be written with, a byte order marker (BOM) — as UTF-16 and UTF-32 files require, and UTF-8 files sometimes optionally do
**THEN** choose the specific encoding name that matches what you need done with that marker, rather than assuming the general encoding name handles it the way you expect
**ELSE** for encodings that have no BOM concept at all (ASCII, Latin-1, and most single-byte encodings), this choice does not apply

## Do
- Use `"utf-16"` or `"utf-32"` when you want the BOM read automatically on input (to detect byte order) and written automatically on output; these general names always expect and produce a BOM for that scheme.
- Use `"utf-8-sig"` when you specifically want a UTF-8 BOM skipped on read or written on write; plain `"utf-8"` does neither — it leaves a BOM's bytes decoded as a literal `\ufeff` character at the start of the text instead of stripping them.
- Use an explicit endianness name (`"utf-16-le"`, `"utf-16-be"`) when you need to force a specific byte order without the automatic BOM handling the general name performs; expect these forms to require you to handle any BOM yourself.
- Reach for `"utf-8-sig"` on input whenever you are not sure if a UTF-8 source has a BOM; it correctly reads data both with and without one, unlike plain `"utf-8"`, which only reads cleanly when no BOM is present.

## Don't
- Don't open a UTF-8 file that might have a BOM with plain `"utf-8"` and expect the marker to disappear; it will decode into a real, visible `\ufeff` character at the front of your string instead.
- Don't assume `"utf-16"` and `"utf-16-le"`/`"utf-16-be"` are interchangeable; the general name both expects a BOM to be present on input and writes one on output, while the specific endianness names do neither.
- Don't guess an encoding name's BOM behavior from its general family; verify whether the exact name you are using reads, writes, both, or neither, since the differences are easy to get backward.

## Checklist
- For a file that might carry a BOM, does the chosen encoding name match the intended BOM behavior (skip it, write it, or ignore the question entirely)?
- Where byte order must be forced explicitly, is an endianness-specific name used, with the resulting lack of automatic BOM handling accounted for?
- Has reading a sample of the actual target file (or a file saved by the actual tool that will produce it) confirmed whether a BOM is present, rather than assuming based on the encoding family alone?

## Notes
A BOM is just a few bytes at the start of a file that declare byte order or encoding identity, and Python's encoding names split into those that treat the BOM as part of their contract (general "utf-16"/"utf-32", and the specific "utf-8-sig") and those that leave it as ordinary data to be handled by hand (plain "utf-8", and the endianness-specific UTF-16/32 names). The failure mode in both directions is silent: reading a BOM as data leaves a stray character at the front of a string, and failing to write one when a consumer expects it leaves that consumer unable to detect the encoding at all — neither failure raises an exception, so the encoding name is the only thing standing between a file and a nearly invisible bug.
