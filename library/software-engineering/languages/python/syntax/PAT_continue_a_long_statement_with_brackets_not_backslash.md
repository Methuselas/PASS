---
object_id: PAT_continue_a_long_statement_with_brackets_not_backslash
object_type: pattern
name: Continue a Long Statement with Brackets, Not a Backslash
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
- line-continuation
- readability
cross_links: []
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Continue a Long Statement with Brackets, Not a Backslash

## Pattern Rule
**IF** a single Python statement — a list/dict/set literal, a function call, an assignment's expression, or a compound statement's test — does not fit comfortably on one physical line
**THEN** wrap the part that needs to continue in an enclosing `()`, `[]`, or `{}` pair and drop to the next line inside it, so Python keeps reading the same statement until it reaches the matching close
**ELSE** when no bracket is already open and introducing one would be awkward, a trailing backslash still works, but treat it as a fallback rather than a first choice

## Do
- Reach for a bare pair of parentheses when nothing is already bracketing the expression — any expression can be wrapped in `( )` purely to enable continuation, even one with no function call in it, as in `X = (A + B + C + D)`.
- Let the bracket a literal or call already needs double as its own continuation device: a list's `[ ]`, a dict or set's `{ }`, and a call's `( )` all allow dropping to the next line with no extra wrapping.
- Continue a compound statement's test the same way: wrapping a long `if` condition in parentheses lets the condition span several lines while the header still carries exactly one colon, on its last physical line.
- Align continuation lines so a human reader can see where the statement resumes, even though Python itself does not require any particular indentation inside the brackets.
- Wrap adjacent string literals that are meant to concatenate in parentheses to let them span multiple lines, using the same open-pairs mechanism as any other continuation: `('aaaa' 'bbbb' 'cccc')` reads as one concatenated string, not three separate statements.

## Don't
- Don't leave anything — not even a trailing space — after a continuation backslash; the continuation is void if anything follows it on that line, and the mistake stays silent until the next line misbehaves.
- Don't reach for backslash continuation out of habit carried over from C `#define` macros; an open bracket is easy to spot on a skim, while a missing or misplaced backslash is not, and omitting one by accident ends the statement a line early without any error.
- Don't trust a backslash continuation to fail loudly if dropped: `x = 1 + 2 + 3 \` followed by `+4` on the next line assigns `10` as intended, but drop the backslash and `+4` becomes its own valid expression statement — `x` silently ends up `6` instead, with no error raised anywhere.
- Don't use a semicolon to try to join a statement across lines; a semicolon separates statements that share one line, it does not connect a statement split across two.

## Checklist
- Is the continuation anchored by a bracket that stays open across the line break?
- If a backslash was used instead, is there genuinely no bracket available for the job, and does nothing follow the backslash on its line?
- Does the header line of a continued compound statement still end in exactly one colon, on its last physical line?

## Notes
Parentheses are the general-purpose device here because, unlike `[ ]` or `{ }`, they wrap any expression at all rather than only a literal or a call — which is why a plain arithmetic continuation needs nothing more than an added pair of parentheses to span lines.
