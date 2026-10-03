---
object_id: PAT_control_prints_separator_ending_and_destination_with_keyword_arguments
object_type: pattern
name: Control Print's Separator, Ending, and Destination with Keyword Arguments
library_path:
- software-engineering
- languages
- python
- io
stage_binding: 2 block
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- python
- print
- io
- formatting
cross_links:
- rel: prerequisite_for
  target_object_id: PAT_redirect_print_output_through_a_write_interface
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Control Print's Separator, Ending, and Destination with Keyword Arguments

## Pattern Rule
**IF** a `print()` call needs a different separator between values, a different (or no) line ending, or a different output destination than the defaults
**THEN** pass `sep=`, `end=`, or `file=` as keyword arguments directly to that call, rather than pre-building a formatted string by hand or reassigning `sys.stdout` for the whole program
**ELSE** when the formatting need is more specific than a separator and a terminator — column widths, decimal places, thousands separators — build the string first with the string-formatting tools and print the finished string in one call

## Do
- Pass `sep=''` or `sep=', '` to control what goes between the printed values, instead of concatenating them into one string first.
- Pass `end=''` to keep the cursor on the same output line for a later print, or `end='...\n'` to customize the line terminator, instead of calling `sys.stdout.write` directly.
- Pass `file=` an already-open file or stream object for a single call that should go elsewhere, leaving every other `print()` in the program going to its normal destination.
- Pass `flush=True` when output must reach its destination immediately rather than waiting in a buffer — useful for progress text interleaved with another process's output.

## Don't
- Don't pass a filename string to `file=`; it must be an open file or file-like object with a `write` method, not a path — open the file first.
- Don't try to suppress the space between printed items by editing the values themselves; that changes the values, not just how they display. Use `sep=''`.
- Don't reach for manual `sys.stdout.write` calls to avoid the default space-and-newline formatting; the keyword arguments cover that without giving up `print`'s automatic string conversion of each argument.

## Checklist
- Could a one-off formatting need here be satisfied by `sep=`/`end=`/`file=` instead of hand-built strings?
- Is `file=` being passed an open stream, not a filename?
- Does the call still get the automatic string conversion of each argument, rather than losing it to a manual `.write()`?

## Notes
`print` is a thin, ergonomic layer over calling `write` on a stream: every argument is converted to its display text, joined with `sep`, followed by `end`, then handed to `file`'s `write` method (`sys.stdout` by default). Reaching for the keyword arguments keeps that convenience; dropping to manual `sys.stdout.write` calls gives it up for no benefit when the only need was a different separator or terminator.
