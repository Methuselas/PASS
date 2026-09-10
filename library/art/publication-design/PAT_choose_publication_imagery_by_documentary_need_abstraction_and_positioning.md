---
object_id: PAT_choose_publication_imagery_by_documentary_need_abstraction_and_positioning
object_type: pattern
name: Choose Publication Imagery by Documentary Need, Abstraction, and Positioning
library_path:
- art
- publication-design
stage_binding: 0 design
lane_fit: both
foundation_role: foundation
routing_class: general
specialization_axis: none
foundation_object_id: none
tags:
- publication_design
- imagery
- photography
- illustration
- abstraction
- audience
- positioning
cross_links:
- rel: related_to
  target_object_id: PAT_frame_publication_concept_from_subject_audience_and_positioning
- rel: related_to
  target_object_id: PAT_define_image_story_job_before_visualizing
- rel: related_to
  target_object_id: PAT_choose_rendering_technique_from_visual_intent_subject_and_constraints
- rel: related_to
  target_object_id: PAT_crop_decisively_to_reshape_figure_ground_relationships
reference:
  source_title: 'Publication Design Workbook: A Real-World Guide to Designing Magazines, Newspapers, and Newsletters'
  author: Timothy Samara
confidence: high
references: []
variants:
- variant_id: VAR_samara_use_one_coherent_low_cost_image_language_instead_of_mixed_stock
  variant_name: Use One Coherent Low-Cost Image Language Instead of Mixed Stock
  variant_basis: constraint
  difference_from_foundation: >-
    Specializes imagery selection for a publication that needs a recurring image voice but lacks the budget or resources for a custom image
    program. Replace a heterogeneous mix of convenient stock with one affordable, legally usable source family or treatment that can support
    multiple content-specific metaphors while preserving a recognizable visual character across the publication.
  when_to_use: >-
    Use when a recurring newsletter, magazine, brochure family, or similar publication needs several images and image budget, commissioning
    time, or available original artwork is constrained, but a coherent source language can still serve the subject and positioning.
  when_not_to_use: >-
    Do not force one source family onto content it cannot represent honestly, use imagery whose rights or reproduction quality are uncertain,
    or keep repeating a stylistic device after it has become a gimmick that weakens the information.
  absorbed_from_object_id: none
- variant_id: VAR_samara_translate_abstract_values_into_specific_object_metaphors
  variant_name: Translate Abstract Values into Specific Object Metaphors
  variant_basis: context
  difference_from_foundation: >-
    Specializes publication imagery for intangible values, attitudes, or institutional qualities that cannot be documented directly. Translate each
    abstract term into a concrete object or situation whose association is specific enough to carry meaning, favoring associations supplied or
    validated by the people whose values are being represented rather than generic symbolic shorthand.
  when_to_use: >-
    Use when a publication must make abstract organizational values, culture, philosophy, or comparable intangible ideas visually present and
    the stakeholders or source material can supply concrete associations that can be photographed or illustrated coherently.
  when_not_to_use: >-
    Do not invent arbitrary symbolism that has no defensible relationship to the stated value, use a metaphor where direct documentary evidence
    is required, or choose an object only because it is visually surprising.
  absorbed_from_object_id: none
---

# Choose Publication Imagery by Documentary Need, Abstraction, and Positioning

## Pattern Rule
**IF** a publication's imagery must be selected or visually treated
**THEN** decide whether each image is primary content or supporting content, choose its representational-to-abstract balance from the subject's documentary need and the audience or positioning work it must also perform, and select photography, illustration, hybrid treatment, and image handling to serve that communication.

## Do
- Identify what the image contributes beyond the writing: direct documentation, rapid clarification, experiential connection, interpretive meaning, audience resonance, positioning, or some deliberate combination of these jobs.
- Treat representation and abstraction as a continuum rather than a binary. Move toward representation when documentary clarity or direct subject recognition dominates; move toward abstraction when interpretation, association, or positioning must carry more of the message.
- Allow one image to do both kinds of work. A recognizable subject can still carry symbolic, emotional, or lifestyle meaning through context and treatment.
- Choose photography, drawing or painting, manipulated photography, or a hybrid by the communication need rather than by habit. Consider how much documentary evidence the subject requires and how the intended audience and publisher point of view should shape the image.
- Treat image handling as content. Selective focus, what enters or leaves the frame, relative scale, lighting, color treatment, cropping, mark character, and medium can change emphasis, mood, and interpretation even when the depicted subject stays the same.
- Use imagery to condense complex, abstract, or process-oriented information when a visual form can make the relationship understandable more quickly than prose alone.
- Judge image choices against the publication concept and surrounding text so informational clarity and interpretive character reinforce rather than contradict each other.

## Don't
- Do not treat imagery as decoration that can be chosen independently of the publication's subject, audience, and positioning.
- Do not assume a photograph is automatically objective or an illustration automatically interpretive; framing, lighting, selection, composition, and treatment can make either carry layered meaning.
- Do not push abstraction so far that a subject that must be documented or recognized becomes unclear.
- Do not choose a medium, crop, effect, or degree of stylization merely because it looks contemporary, dramatic, or personally interesting.
- Do not let branding or audience resonance erase the informational job the image must still perform.
- Do not judge only what an image shows; judge how the chosen treatment changes what viewers are likely to understand or feel about it.

## Checklist
- Each important image has a clear role as primary content, support, or both.
- The chosen level of representation or abstraction fits the balance between documentary clarity and interpretive work.
- The photography, illustration, hybrid, or manipulated-image route has a communication reason beyond preference.
- Framing, focus, lighting, scale, crop, color treatment, and medium have been checked for the meaning they add.
- Required subject information remains clear enough for the publication's purpose.
- The image treatment resonates with the intended audience and positioning without contradicting the core subject.
- Imagery and writing divide the communication work intentionally rather than repeating or obscuring each other.

## Notes
Images are content because their meaning comes from both subject and treatment. A representational image tends to carry more direct documentary information, while a more abstract image tends to carry more interpretive, associative, or positioning work, but every image can mix both functions. Photography, illustration, and hybrid imagery are therefore not neutral containers. The choice among them, and choices inside them such as focus, lighting, framing, crop, relative scale, and mark or medium character, shape the message. In publication work, select those variables from the subject first, then filter them through audience need and any deliberate positioning rather than treating image style as an independent decorative layer.

`VAR_samara_use_one_coherent_low_cost_image_language_instead_of_mixed_stock` is the constrained-resource branch. When commissioning or original-image resources are too limited for a publication that still needs a recurring pictorial voice, choose one affordable and legally usable source family or treatment that can carry several content-specific metaphors. The point is not to imitate a particular historical style; it is to replace a visual grab bag with a coherent image language whose tone and metaphorical range still support the subject. Reject the branch when the source cannot represent the material honestly, reproduction quality is inadequate, rights are unclear, or repetition has become a distracting conceit.

`VAR_samara_translate_abstract_values_into_specific_object_metaphors` is the abstract-values branch. When a publication must visualize an intangible quality, start with a concrete association that comes from or is validated by the people or source material being represented, then render that object or situation consistently enough that the series reads as one visual argument. The point is not generic symbolism; it is to make an otherwise abstract value visible through a specific association that remains defensible in context. Reject the branch when the object is merely odd, when its connection to the value cannot be explained, or when the communication job requires direct documentary evidence instead.
