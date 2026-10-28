---
object_id: PAT_redirect_after_successful_state_changing_form_posts
object_type: pattern
name: Redirect After Successful State-Changing Form Posts
library_path:
- software-engineering
- core
- control-flow
stage_binding: 2 block
lane_fit: skill
foundation_role: foundation
routing_class: general
specialization_axis: none
foundation_object_id: none
tags:
- http
- forms
- redirect
- post
- control-flow
cross_links: []
reference:
  source_title: 'Practical Rust Web Projects: Building Cloud and Web-Based Applications'
  author: Shing Lyu
confidence: high
references: []
variants: []
---

# Redirect After Successful State-Changing Form Posts

## Pattern Rule
**IF** a browser form POST successfully changes server state and the next user-visible view can be retrieved separately
**THEN** respond with a redirect to a GET resource, using 303 See Other when the method must change to GET, so the displayed page is not the POST response itself

## Do
- Commit the state change first, then return a Location that identifies the page or resource the user should view next.
- Use a redirect status whose method semantics match the intent; 303 explicitly tells the client to follow with GET after POST or PUT.
- Make the redirected GET independently render the committed result so refreshes operate on a read path.

## Don't
- Don't leave the browser displaying the successful POST response when a refresh would invite the client to resubmit the state-changing request.
- Don't use a method-preserving redirect such as 307 when the intent is specifically to turn the follow-up into a GET.

## Checklist
- Has the state-changing operation completed before the redirect is sent?
- Does the chosen redirect status produce the intended follow-up method?
- Can the redirected GET reconstruct the success view without replaying the POST body?
- What happens if the user refreshes or bookmarks the destination?

## Notes
The redirect separates mutation from representation. After the POST succeeds, the browser moves onto a retrieval URL whose refresh semantics are naturally safe for ordinary page viewing. This is a control-flow decision, not a guarantee that the original mutation is itself idempotent.
