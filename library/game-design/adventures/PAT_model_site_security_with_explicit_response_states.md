---
object_id: PAT_model_site_security_with_explicit_response_states
object_type: pattern
name: Model Site Security with Explicit Response States
library_path:
- game-design
- adventures
stage_binding: 0 design
lane_fit: both
foundation_role: foundation
routing_class: general
specialization_axis: none
foundation_object_id: none
tags:
- adventures
- infiltration
- security
- detection
- dynamic-state
cross_links:
- rel: related_to
  target_object_id: PAT_design_occupied_sites_around_inhabitant_operations
- rel: related_to
  target_object_id: PAT_separate_mobile_actors_from_fixed_location_state
- rel: related_to
  target_object_id: PAT_layer_dynamic_events_over_static_location_state
- rel: related_to
  target_object_id: PAT_express_faction_power_as_deployable_response_capacity
- rel: related_to
  target_object_id: PAT_preserve_stable_challenge_conditions_against_reactive_difficulty_protection
confidence: high
references: []
variants: []
---

# Model Site Security with Explicit Response States

## Pattern Rule
**IF** intrusion, detection, alarm, or suspicion should change how a site operates across multiple locations or encounters
**THEN** model security as a small set of explicit response states with causal triggers, observable consequences, bounded responder capacity, and defined escalation or recovery transitions
**ELSE** resolve isolated guards, traps, or sensors locally when no persistent site-wide change needs to survive the encounter.

## Do
- Define a baseline posture and only as many heightened or degraded states as create different player decisions.
- Give each transition a causal trigger such as a missed check-in, witnessed intrusion, damaged sensor, discovered body, forged authorization failure, communication loss, or confirmed attack.
- State what each response state changes in concrete operational terms: patrol routes, access control, checkpoints, communications, searches, civilian behavior, transport, lighting, locks, surveillance attention, reinforcement deployment, or escape conditions as appropriate to the site.
- Expose cues that let players infer the posture through changed routines, visible barriers, radio traffic, personnel movement, interrupted services, warnings, or other fictional evidence.
- Bound the response by the site's actual people, tools, communications, jurisdiction, travel time, and organizational capacity. Responders must come from somewhere and take time when distance matters.
- Let preparation and sabotage alter specific triggers or capabilities when players meaningfully interfere with sensors, communications, credentials, power, transport, command, or responder access.
- Track mobile responders separately from the static location key when their current position matters.
- Define how a state can stabilize, recover, decay, or escalate further so one ambiguous suspicion does not automatically become permanent maximum response.
- Preserve consequences once triggered unless the fiction supplies a reason they change; do not silently reset the site between encounters.

## Don't
- Increase opposition simply because players are succeeding while claiming the site is reacting to them.
- Teleport reinforcements, restore destroyed sensors, or close routes without a capability and causal path that exists in the established state.
- Make every detection jump immediately to the strongest possible response when intermediate states would create useful decisions.
- Hide all evidence of changing security and then punish players for failing to respond to a posture they had no way to perceive.
- Track a detailed state machine when one local guard response is all the adventure will ever query.
- Put exact mobile positions into static room descriptions when responders can move across the site.

## Checklist
- Each security state changes at least one operational condition players can care about.
- Every transition has a recognizable fictional cause rather than a difficulty-balancing trigger.
- Players can obtain some evidence of the current posture before or while making decisions affected by it.
- Responders, surveillance, access control, and other capabilities are limited by established resources and travel or communication constraints.
- Preparation, deception, sabotage, delay, or withdrawal can alter at least one part of the response when the scenario promises those approaches.
- The facilitator knows what causes escalation, what persists, and what permits recovery or de-escalation.
- Static site keys remain valid while mobile or global security state is tracked separately where necessary.

## Notes
Security becomes playable when detection changes state instead of merely summoning more opposition. A persistent response model lets players reason about what the site knows, what it can do next, which capabilities can be disrupted, and how much time remains before conditions worsen. Explicit states also protect fairness: escalation follows visible causes and bounded resources rather than retrospective difficulty correction.

This Pattern owns the **site-wide security posture and its transitions**. Site operations own the architecture and routines being protected; mobile-actor tracking owns current responder positions; faction-capacity design owns organization-scale resources; and reactive-difficulty protection owns the broader rule against countering player success without causal support.
