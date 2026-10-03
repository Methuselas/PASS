---
object_id: PAT_write_a_compound_statement_as_header_colon_and_indented_block
object_type: pattern
name: Write a Compound Statement as Header, Colon, and Indented Block
library_path:
- software-engineering
- languages
- python
- syntax
stage_binding: 1 skeleton
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- python
- syntax
- indentation
- blocks
cross_links:
- rel: prerequisite_for
  target_object_id: PAT_continue_a_long_statement_with_brackets_not_backslash
- rel: prerequisite_for
  target_object_id: PAT_keep_one_simple_statement_per_line
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Write a Compound Statement as Header, Colon, and Indented Block

## Pattern Rule
**IF** coding any Python statement that nests another block of statements inside it — an `if`, `while`, `for`, `def`, `class`, `try`, or `with`
**THEN** end the header line with a colon and indent every statement of the nested block the same distance to the right, using indentation alone — never braces, `then`/`endif`, or `begin`/`end` — to mark where the block starts and stops
**ELSE** for a simple statement that nests nothing (an assignment, a bare call, a `return` by itself), skip the colon and indentation entirely; the line ends the statement on its own

## Do
- Start every top-level, unnested statement in column 1; only a statement nested inside some header line may be indented at all.
- Indent every line of one nested block by the identical whitespace — the same number of spaces, or the same number of tabs — though the exact amount is free to differ from one block to the next in the same file; reaching `PAT_continue_a_long_statement_with_brackets_not_backslash` and `PAT_keep_one_simple_statement_per_line` assumes this base layout is already settled.
- Put the colon at the true end of the header line, even when the test or expression before it spans several physical lines; the block does not start until that colon is reached.
- Drop the C-style parentheses around an `if`/`while` test and the braces around the nested block entirely; Python tolerates parentheses around a test without complaint, but including them reads as an unconverted C habit rather than Python style.
- Let an `elif` or `else` clause pair with whichever header shares its indentation column, never with whichever header is visually nearest on the page.

## Don't
- Don't indent a statement that isn't nested inside anything — an indented first line of a file, or a line indented further than its header actually opened, is a syntax error, not a tolerated style choice.
- Don't mix tabs and spaces within one nested block; the running interpreter raises `TabError: inconsistent use of tabs and spaces in indentation` instead of guessing which one you meant.
- Don't assume a block's indent width is fixed for the whole file — one nested block may use four spaces while a different block elsewhere uses two, as long as each block is internally consistent.
- Don't add a semicolon to close the header or the block; the colon and the indentation already do that job, and a stray semicolon only matters as a statement separator on a single line.

## Checklist
- Does every header line that opens a nested block end in a colon, on its last physical line?
- Are all statements in one nested block indented by identical whitespace, with no tabs/spaces mixing?
- If two clauses should be read as part of the same compound statement — an `if` and its `else`, a `try` and its `except` — do they share the same indentation column?

## Notes
Python promotes this from a style preference to syntax: because the way the code looks is the way it runs, a reader's visual read of the nesting and the interpreter's structural read can never diverge the way they can in a brace-delimited language. The practical payoff Lutz points to is concrete rather than aesthetic — the classic C pitfall where an `else` silently binds to the wrong `if` cannot occur here, because the `else` that lines up with a given `if` is, by construction, the one it belongs to.
