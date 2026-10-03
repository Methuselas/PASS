---
object_id: PAT_open_files_in_a_with_block_and_name_the_encoding
object_type: pattern
name: Open Files in a with Block and Name the Encoding
library_path:
- software-engineering
- languages
- python
- files
stage_binding: 3 rough
lane_fit: skill
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- python
- files
- encoding
- resources
- context-managers
cross_links:
- rel: related_to
  target_object_id: PAT_write_string_literals_that_mean_what_they_show
reference:
  source_title: Learning Python, 5th Edition
  author: Mark Lutz
confidence: high
references: []
variants: []
---

# Open Files in a with Block and Name the Encoding

## Pattern Rule
**IF** Python code opens a file
**THEN** open it in a `with` statement so it is closed and flushed at a known point even when an exception escapes, choose text mode (`'r'`, `'w'`, `'a'`) with an explicit `encoding=` for text or binary mode (`'rb'`, `'wb'`) for bytes, and read text line by line by iterating over the file object
**ELSE** when the file must stay open beyond one block (a log kept by a long-lived object), give the owning object a `close()` method, make it a context manager itself, and close it deterministically.

## Do
- Write `with open(path, encoding='utf-8') as f:` for text, and name the encoding on every text open, read or write.
- Use `'rb'`/`'wb'` for images, archives, packed records and anything else that is not text; binary reads return `bytes` and perform no newline translation or decoding.
- Loop over lines with `for line in f:`; it reads one line at a time instead of loading the whole file.
- Create a file only if it does not exist with mode `'x'`, which raises `FileExistsError` instead of silently truncating.
- Call `f.flush()` when another process must see written data before the file is closed.
- Run tests with `python -X warn_default_encoding` to find opens that rely on the platform default.
- Call `.readlines()` deliberately when something downstream needs a real sequence rather than a lazy iterator — `reversed(f.readlines())` to print a file's lines back to front, for instance, since `reversed()` requires a real sequence and a file's own line-at-a-time iteration doesn't qualify.

## Don't
- Don't rely on garbage collection to close files; closing on collection is a CPython implementation detail, it does not happen at a predictable point in other implementations, and unflushed output can be lost.
- Don't open text without `encoding=`; the default comes from the platform (on many Windows systems it is `cp1252`), so a UTF-8 file can decode into wrong characters without any error.
- Don't open binary data in text mode; decoding can fail or corrupt bytes, and newline translation alters `\r\n` sequences.
- Don't write non-strings to a text file; `write` does not convert, so format or `str()` values first and add the `\n` yourself.

## Checklist
- Is every `open` inside a `with` block or owned by an object that closes it?
- Does every text-mode open name its encoding?
- Is binary data opened in binary mode?
- Are large files read by iteration rather than all at once?

## Notes
The file object buffers output, so data written is not guaranteed to be on disk until `flush()` or `close()`. The `with` statement calls `close()` when the block exits by any route, which also flushes. Since Python 3.10, omitting the encoding can be reported with an `EncodingWarning` when warnings are enabled with `-X warn_default_encoding`; a later Python version is planned to make UTF-8 the default, and until then the explicit argument is what keeps behaviour identical across platforms. The `open` modes combine: `'+'` adds updating, and `seek` moves the position for random access.
