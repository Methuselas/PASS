---
object_id: PAT_measure_rust_elapsed_time_with_monotonic_instant
object_type: pattern
name: Measure Rust Elapsed Time With a Monotonic Instant
library_path:
- software-engineering
- languages
- rust
- time
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- rust
- time
- instant
- duration
- elapsed
- monotonic
cross_links: []
reference:
  source_title: Practical System Programming for Rust Developers
  author: Prabhu Eshwarla
confidence: medium
references: []
variants: []
---

# Measure Rust Elapsed Time With a Monotonic Instant

## Pattern Rule
**IF** Rust code needs the duration of an operation rather than a civil or externally meaningful timestamp
**THEN** take the start point with `Instant::now()` and compute a `Duration` from that monotonic clock
**ELSE** use `SystemTime` when the value must represent wall-clock time that can be compared or communicated outside the process

## Do
- Capture an `Instant` immediately before the interval being measured and use `elapsed` or another `Instant` comparison after the work completes.
- Keep the result as `Duration` until a presentation or policy boundary needs a particular unit.
- Use `SystemTime` for timestamps such as when an event occurred, not as the default stopwatch for operation latency.
- Treat suspend behavior and exact clock steadiness as platform properties when measurements cross long pauses or require unusual precision guarantees.

## Don't
- Don't subtract wall-clock timestamps to measure routine operation latency when clock adjustment can change the apparent time.
- Don't convert elapsed time to an integer unit earlier than needed and silently lose precision required by later comparisons.
- Don't treat `Instant` as a calendar timestamp; it is opaque and meaningful only relative to other instants and durations.

## Checklist
- Is the required value an elapsed duration or an externally meaningful point in time?
- Is the measured interval bounded by `Instant` values rather than wall-clock timestamps?
- Does downstream code preserve enough `Duration` precision for its decision?
- Does platform-dependent suspend behavior matter for this measurement?

## Notes
Rust separates the stopwatch and wall-clock concepts. `Instant` is monotonically nondecreasing and intended for elapsed-time measurement, while `SystemTime` represents the system clock used to communicate time with the outside world. The distinction prevents ordinary duration calculations from inheriting wall-clock adjustments as application behavior.
