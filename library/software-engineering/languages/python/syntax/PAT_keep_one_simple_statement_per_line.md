---
object_id: PAT_keep_one_simple_statement_per_line
object_type: pattern
name: Keep One Simple Statement per Line
library_path:
- software-engineering
- languages
- python
- syntax
stage_binding: 2 block
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- python
- syntax
- readability
- style
cross_links: []
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Keep One Simple Statement per Line

## Pattern Rule
**IF** deciding how many statements to place on a single physical line of Python code
**THEN** write exactly one statement per line, with every nested block on its own indented line, reserving the semicolon-separated chain and the single-line `header: body` form for a header followed by one trivial simple statement
**ELSE** when the body is or contains a compound statement — another `if`, `while`, `for`, `try`, `def`, and so on — it cannot be collapsed onto the header line or chained with semicolons; it needs its own indented line no matter how short it is

## Do
- Use the single-line form, as in `if reply == 'stop': break`, only when what follows the colon is one simple statement — an assignment, a call, or similar.
- Reserve the semicolon chain, as in `a = 1; b = 2; print(a + b)`, for the rare case where stacking genuinely independent, non-compound statements on one line is worth the tradeoff; this is the one place Python requires a semicolon at all, as a separator between statements rather than a terminator after one.
- Default to a fresh line and the loop's or branch's own indentation level for every statement, even where the language would accept something more compressed.

## Don't
- Don't put a compound statement after a colon or inside a semicolon chain; the grammar does not allow a header-and-block construct to serve as the body of a one-liner or as one link in a chain.
- Don't collapse an `elif`, `else`, `except`, or `finally` clause onto the line above it; each remaining clause of a compound statement still needs its own header line ending in a colon.
- Don't pick a compressed form for anything beyond genuinely trivial code: some coverage and profiling tools cannot tell several statements squeezed onto one line apart from a single statement, which quietly degrades what those tools report.

## Checklist
- Is everything after a one-liner's colon, or between its semicolons, a simple, non-compound statement?
- Does every `elif`/`else`/`except`/`finally` clause sit on its own line, aligned with the header it belongs to?
- Would a coverage or profiling tool reading this file still attribute results to one statement at a time?

## Notes
Both compressed forms are legal and both are meant to be used sparingly: the interpreter accepts them, but a file that keeps one statement per line has its vertical layout match its logical structure one-for-one, which is what lets a reader trust what the indentation already tells them without separately checking for statements hidden on the same line.
