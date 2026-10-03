---
object_id: AP_harden_an_interactive_input_loop_with_try_except
object_type: ap
name: Harden an Interactive Input Loop with Try/Except
library_path:
- software-engineering
- languages
- python
- control-flow
stage_binding: 2 block
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- python
- loops
- exceptions
- input-validation
- eafp
cross_links:
- rel: supports
  target_object_id: PAT_write_a_compound_statement_as_header_colon_and_indented_block
- rel: supports
  target_object_id: PAT_parse_untrusted_text_instead_of_evaluating_it
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Harden an Interactive Input Loop with Try/Except

## Objective
Turn a bare read-input/act/repeat loop into one that exits cleanly on a sentinel value and never crashes on bad input, by routing each reply through a single `try`/`except`/`else` instead of hand-validating it before use.

## Steps / Flow
1. **Build the bare skeleton first.** Write `while True:` reading one reply with `input()`, an `if reply == 'stop': break` to exit on a chosen exit word, and the happy-path action on the next line — nothing else. Get this running correctly for good input before adding any error handling at all; a loop that is not yet right for valid input cannot be meaningfully hardened against invalid input. `PAT_write_a_compound_statement_as_header_colon_and_indented_block` owns the header/colon/indent shape of the `while` and of the one-line `if`.
2. **Identify what can actually fail.** Find the one operation in the happy-path action that raises on bad input — typically a conversion such as `int(reply)` or `float(reply)` — before deciding how to guard it. Do not wrap code that cannot fail.
3. **Wrap only the failing part in `try`, and put what depends on its success in the paired `else`.** Code that assumes the conversion worked belongs in `else`, not after the `try` block — this keeps a bug in the "success" code from ever being caught and hidden by the conversion's own `except`.
4. **Prefer catching the exception over pre-validating the string.** Attempting the conversion and reacting in `except` is shorter than a method like `.isdigit()`, and it generalizes for free to formats a hand-written check would miss — floating-point and scientific-notation text, for instance, have no single string method that confirms them in advance.
5. **Keep the sentinel check outside and ahead of the `try`.** The exit test (`if reply == 'stop': break`) belongs before the `try`, never inside it — exiting the loop on purpose is not the failure case the `try` exists to catch.
6. **Place whatever runs once the loop ends outside the `while`, at the loop's own indentation.** A closing message or summary that depends on the loop being over must sit back at that level so it runs exactly once, regardless of which iteration triggered the exit.
7. **Confirm completion before calling the loop hardened.** The sentinel exit never passes through the `try`; a bad conversion reaches the `except` branch without crashing the loop; a good conversion still reaches its action, by way of `else`; and the line placed after the loop runs exactly once no matter which iteration exited. Only once all four hold has the loop actually been hardened, rather than merely rewritten.

## Notes
The order matters because a `try`/`except` written around code that does not yet work correctly conflates two separate problems — getting the logic right, and deciding what to do when it legitimately fails — into one debugging session. A bare `except:` is the right width for a short script expecting exactly one kind of failure, such as a bad conversion; a loop that needs to tell several failure kinds apart needs a named exception type on the `except` clause, which this protocol does not itself adjudicate. The `try`'s `else` and the sentinel `if`'s absence of one are unrelated: which statement an `else` belongs to is decided purely by which header shares its indentation, never by proximity on the page.

If a later version of this loop swaps `int`/`float` for `eval` to accept arbitrary expressions, that is a separate decision with its own trust boundary, not a mechanical extension of this protocol: `PAT_parse_untrusted_text_instead_of_evaluating_it` owns whether such a swap is safe for a given input source.
