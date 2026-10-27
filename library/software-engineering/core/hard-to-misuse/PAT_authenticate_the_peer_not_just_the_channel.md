---
object_id: PAT_authenticate_the_peer_not_just_the_channel
object_type: pattern
name: Authenticate the Peer, Not Just the Channel
library_path:
- software-engineering
- core
- hard-to-misuse
stage_binding: 0 design
lane_fit: both
foundation_role: foundation
routing_class: general
specialization_axis: none
foundation_object_id: none
tags:
- security
- authentication
- tls
- key-agreement
- identity
cross_links:
- rel: related_to
  target_object_id: PAT_specify_the_application_protocol_above_the_transport
- rel: related_to
  target_object_id: PAT_barricade_dirty_data_at_a_named_boundary
reference:
  source_title: Network Programming with Rust
  author: Abhishek Chanda
confidence: high
references: []
variants: []
---

# Authenticate the Peer, Not Just the Channel

## Pattern Rule
**IF** the security contract depends on which peer is at the other end of a protected connection
**THEN** use an authenticated channel or authenticated key exchange that validates the peer against an independently established expected identity and binds that identity to the negotiated session keys
**ELSE** if the threat model intentionally permits an anonymous encrypted channel, name that weaker property explicitly and do not treat successful key agreement or encryption as peer authentication

## Do
- Define the expected peer identity independently of whatever identity the peer presents during the handshake.
- Validate the credential or authentication proof under the protocol policy, including the intended identity match and relevant validity or usage constraints.
- Choose the trust-anchor source deliberately. A platform trust store follows administrator and operating-system policy; a bundled root set makes trust behavior part of the application release. Either way, the selected roots are part of the security boundary.
- Use a protocol that cryptographically binds authentication to the key-establishment transcript or session so an active intermediary cannot substitute its own key unnoticed.
- Fail closed when the required peer identity cannot be established instead of silently downgrading to an unauthenticated session.

## Don't
- Don't treat possession of a Diffie-Hellman shared secret by itself as proof of who the peer is.
- Don't treat a chain to a trusted certificate authority as sufficient when the presented service identity does not match the identity the client intended to reach.
- Don't disable certificate or peer verification in ordinary operation merely to make a connection succeed.
- Don't treat an arbitrary self-signed certificate as authenticated merely because it is self-signed; trust it only when that exact credential or key is an independently configured expected identity.

## Checklist
- What peer identity is the caller or protocol expecting, and where does that expectation come from?
- Which credential or authentication proof binds that identity to the peer key?
- Which trust anchors are accepted, where do they come from, and who can change them?
- Is the authentication proof cryptographically bound to the session/key exchange?
- What happens when validation, identity matching, or authentication fails?

## Notes
Encryption and integrity protection can protect an exchange, and key agreement can establish shared secret material; none of those properties alone says who the peer is. An active attacker can establish separate unauthenticated protected sessions with both sides unless the protocol binds the negotiated keys to an identity each side is prepared to trust.
