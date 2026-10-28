---
object_id: PAT_preserve_rust_usb_device_identity_across_enumeration_and_open
object_type: pattern
name: Preserve Rust USB Device Identity Across Enumeration and Open
library_path:
- software-engineering
- languages
- rust
- io
stage_binding: 2 block
lane_fit: both
foundation_role: specialization
routing_class: specialized
specialization_axis: language
foundation_object_id: none
tags:
- rust
- usb
- io
- devices
- enumeration
- identity
- errors
cross_links:
- rel: related_to
  target_object_id: PAT_keep_rust_failures_as_result_until_recovery_context_exists
- rel: related_to
  target_object_id: PAT_unify_rust_errors_from_multiple_sources_with_from
- rel: related_to
  target_object_id: PAT_program_rust_io_against_read_and_write_traits
reference:
  source_title: Practical System Programming for Rust Developers
  author: Prabhu Eshwarla
confidence: medium
references: []
variants: []
---

# Preserve Rust USB Device Identity Across Enumeration and Open

## Pattern Rule
**IF** Rust code enumerates USB devices and then opens one of those devices for descriptors or transfers
**THEN** open the exact enumerated device object and keep later observations bound to that identity, using VID/PID as filtering metadata rather than as a unique lookup key
**ELSE** use a convenience VID/PID lookup only when selecting the first matching device is actually the intended contract

## Do
- Open the Device or DeviceInfo selected during enumeration so bus/address/path metadata and the live handle refer to the same enumerated instance.
- Treat opening, descriptor reads, supported-language discovery, and optional string descriptors as separate fallible steps because permissions, disconnects, unsupported descriptors, and device state can differ per device.
- Define whether the inventory must be complete or may be best-effort, and preserve per-device failures when they affect the result's meaning.
- Handle an empty supported-language list and unavailable manufacturer, product, or serial strings without indexing or unwrapping them as invariants.
- Use VID/PID to filter candidate devices, then preserve a stronger instance identity such as the enumerated object, bus/address/path, or another backend-provided stable selector when multiple matching devices can exist.

## Don't
- Don't enumerate one device and then reopen globally by VID/PID while assuming the handle necessarily refers to that same instance.
- Don't assume every enumerated USB device can be opened by the current process or remains connected long enough for all descriptor reads.
- Don't abort a best-effort inventory merely because one device is inaccessible or only partially describable.
- Don't assume every USB device exposes at least one readable string language or all manufacturer, product, and serial descriptors.

## Checklist
- Can two attached devices share the same VID/PID, and would this code still open the device it just enumerated?
- What happens if permissions deny opening a device or it disappears after enumeration?
- Which descriptors are mandatory for the result, and which may be absent or unreadable?
- Does the caller require a complete inventory, or a best-effort inventory with per-device errors?
- Are identity fields reported from the same device instance whose handle produced the detailed observations?

## Notes
USB discovery and USB access are separate capability boundaries. Enumerating a device proves that the backend observed it, not that the process can open it or read every optional descriptor.

libusb-style Rust APIs expose an open operation on the enumerated device itself. Convenience VID/PID lookup is useful for simple first-match selection, but current rusb documentation explicitly describes that helper as a prototype convenience that returns the first matching device, so it should not be used to recover the identity of a device that was already enumerated.
