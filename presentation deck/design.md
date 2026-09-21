# Presentation design profile

Cooper AI · Sales Engineer take-home · Internal engineering and sales review

## 1. Design direction

Create a warm, editorial presentation that feels visually consistent with Cooper's website while making the candidate's reasoning, working product, and evidence easy to assess.

**Visual character:** calm, precise, spacious, human, and understated.

**Core formula:** ivory canvas + espresso text + regular-weight serif headlines + restrained orange accents + clear product evidence.

The audience should quickly understand the customer problem, the scope decision, how the system works, and what has actually been demonstrated. Visual polish supports that understanding.

## 2. Source and confidence

Reference: [Cooper homepage](https://www.askcooper.ai/), inspected September 20, 2026.

The audit included desktop screenshots of the hero, role cards, impact section, product demonstrations, integration diagram, and footer, plus read-only inspection of computed page styles.

- **Verified website tokens:** the four core colors and three font families below.
- **Observed patterns:** warm photography, large serif headings, uppercase labels, spacious grids, fine borders, restrained shadows, and dashed diagram connectors.
- **Deck adaptations:** slide dimensions, type sizes, spacing, layout proportions, chart rules, and accessibility guidance in this document. These are recommendations, not Cooper's official brand guidelines.

## 3. Color system

| Token | Value | Role |
|---|---|---|
| Canvas / ivory | `#FFFCF1` | Default slide background; text on dark slides |
| Surface / parchment | `#EDE7D9` | Grouped content, comparison panels, screenshot surrounds |
| Ink / espresso | `#1E1A15` | Primary text, diagram lines, dark slide backgrounds |
| Accent / burnt orange | `#D95611` | Section labels, emphasis, selected steps, key markers |

### Application rules

- Keep roughly 75–85% of the deck on light backgrounds. Reserve dark or photographic slides for the cover, a major transition, and the close.
- Use orange sparingly: one primary point of emphasis per slide. Avoid full orange backgrounds.
- Use espresso at approximately 75% opacity for secondary copy and 15–20% for decorative rules on ivory. Export with the intended background so transparency remains predictable.
- Use solid espresso for small text, table values, and essential annotations. Do not copy the website's faint secondary text into projected slides.
- Orange on ivory is suitable for larger labels and non-text emphasis; verify contrast before using it for small text. Use espresso labels with an orange marker when necessary.
- Always pair status colors with text or symbols. “Verified,” “Assumption,” and “Proposed” must remain distinguishable in grayscale.

## 4. Typography

| Role | Font | Weight | Recommended slide size |
|---|---|---|---|
| Cover headline | BIZ UDPMincho | Regular / 400 | 48–60 pt |
| Slide headline | BIZ UDPMincho | Regular / 400 | 36–44 pt |
| Large result / metric | BIZ UDPMincho | Regular / 400 | 48–64 pt |
| Body and table text | Inter | Regular / 400 | 20–24 pt |
| Emphasis within body | Inter | Semibold / 600 | Match surrounding text |
| Diagram labels | Inter | Regular or medium | 16–20 pt |
| Eyebrow / section label | Space Grotesk | Medium / 500 | 12–14 pt |
| Source / footer | Inter | Regular / 400 | 10–12 pt |

### Typesetting

- Use sentence case for headlines. Keep them to one or two lines with intentional line breaks.
- Use uppercase only for short eyebrows, section labels, and compact status tags. Add approximately 0.08–0.10 em tracking.
- Keep serif headlines regular weight. Create hierarchy through scale and spacing.
- Set body leading around 1.25–1.4× and headline leading around 1.1–1.2×. Check actual font rendering in the authoring tool.
- Left-align explanatory text. Center only short cover statements or a simple group of metrics.
- Aim for 45–65 characters per body line; use shorter lines beside diagrams.
- Do not shrink body copy to rescue an overcrowded slide. Edit or split the content.

**Fallbacks:** Georgia for BIZ UDPMincho; Arial for Inter; Arial with uppercase tracking for Space Grotesk. Verify font availability and embedding permissions before export. Inspect the exported deck for substitution and changed line breaks.

## 5. Canvas, grid, and spacing

- **Format:** 16:9 widescreen, 13.333 × 7.5 inches.
- **Safe margins:** 0.6–0.7 inches horizontally; 0.45–0.55 inches vertically.
- **Grid:** 12 columns within the safe area, with approximately 0.2-inch gutters.
- **Common layouts:** equal halves for comparisons; 5/7 columns for explanation and evidence; full width for architecture or a large demo image.
- **Spacing rhythm:** multiples of 8 pt, typically 16, 24, 32, and 48 pt.
- Keep the eyebrow, title, content start, and footer in consistent positions across related slides.
- Leave generous unoccupied space. A slide should have one focal point and one clear reading sequence.
- Keep essential content away from the footer and slide edges; allow room for projection cropping.

## 6. Content hierarchy

Each slide should answer one audience question.

1. **Eyebrow:** the section or context, such as `DISCOVERY` or `PILOT MEASUREMENT`.
2. **Headline:** the takeaway or decision, expressed in plain language.
3. **Evidence:** one diagram, screenshot, comparison, or small group of facts.
4. **Supporting explanation:** only the text needed to interpret the evidence.
5. **Source or qualification:** a concise reference and any material limitation.

Prefer 30–60 words of explanatory copy on a normal slide. Detailed assumptions, field mappings, test inventories, and implementation notes belong in the appendix or speaker notes.

## 7. Reusable slide layouts

| Layout | Composition | Best use |
|---|---|---|
| Cover | Warm image or espresso background; large ivory title; small presenter and assignment line | Introduce the customer outcome |
| Context | Ivory; large left-aligned headline; short narrative beside a simple workflow | Customer problem and current process |
| Discovery | Two columns separated by a fine rule; question or uncertainty paired with build assumption | Show how discovery influenced scope |
| Scope | Parchment panel with clear included/deferred columns; orange emphasis on the chosen slice | Explain prioritization and cuts |
| Architecture | Full-width diagram on ivory; faint grid optional; five or fewer primary stages | Explain extraction through output |
| Demo evidence | Large, tightly cropped product screenshot; short headline; two or three numbered annotations | Show working behavior |
| Exception handling | Two source snippets and the reviewed outcome, with a visible human decision step | Explain disagreement, missing data, and correction |
| Results | Two or three large figures; explicit labels, units, sample, and qualification | Present verified measurements |
| Pilot plan | Three sequential stages with owners, acceptance criteria, and decision points | Explain customer deployment and next steps |
| Close | Espresso background; one ivory conclusion and one next decision | End with a concrete recommendation |
| Appendix | Ivory; compact but readable tables, diagrams, or code excerpts | Support technical questions |

These layouts define the visual system; they do not prescribe the final table of contents or slide count.

## 8. Components and visual language

### Panels and tables

- Use ivory or parchment fills with 0.5–1 pt rules.
- Prefer square corners or a subtle 4–6 pt radius. Avoid heavily rounded cards around every paragraph.
- Use 20–28 pt internal padding where space allows.
- Reserve a soft shadow for elevated product screenshots or a featured demonstration panel. Keep ordinary information panels flat.
- Use tables for actual comparison. Prefer row separators over a dense boxed grid, and keep numeric columns aligned.

### Diagrams

- Use thin espresso connectors and an orange focal stage or decision marker.
- Use dashed lines only when they convey a defined meaning, such as a proposed integration. Provide a legend when mixing line styles.
- Keep arrows directional, labels short, and the primary flow left to right.
- Separate input sources, processing, reviewer decisions, and outputs visually.
- Represent planned capabilities with explicit “Proposed” labels. Visual styling must not imply that an integration is already implemented.
- A faint grid may sit behind technical diagrams, but must remain subordinate to labels and connectors.

### Screenshots

- Use current screenshots of the actual build. Preserve product text and values.
- Crop to the relevant task, remove irrelevant browser chrome, and avoid shrinking an entire interface until labels become unreadable.
- Prefer one large screenshot or two closely related crops per slide.
- Use small orange numbered markers outside critical UI text, with matching espresso annotations.
- Show source evidence and final output where the argument depends on correctness.
- Keep screenshots as evidence; do not recolor the application to imply a different shipped interface.

### Photography and brand assets

- Match the site's warm daylight, amber, wood, glass, and human workplace imagery.
- Use photography primarily on the cover or section transitions. Keep technical slides visually quiet.
- Add a consistent dark overlay when placing ivory text on an image; verify contrast across the entire text area.
- Use authorized images and an authentic logo asset if available. Do not redraw or approximate Cooper's wordmark.
- Identify the presentation as a candidate take-home; visual alignment should not imply an official Cooper publication.

### Icons

- Use one consistent outline icon family with similar stroke widths.
- Prefer simple document, table, review, arrow, and output symbols.
- Pair icons with labels when their meaning is not immediately obvious. Avoid decorative icons that add no information.

## 9. Evidence and data presentation

- Explicitly distinguish **verified result**, **build assumption**, and **proposed target** wherever confusion is possible.
- Include units, sample size, and measurement scope beside reported figures.
- Keep automated processing time separate from end-to-end human handling time.
- Never present Cooper's website marketing metrics as results achieved by this MVP.
- Avoid borrowing the website's large-stat treatment for unmeasured benefits. Use a labeled measurement plan instead.
- Use direct chart labels, minimal gridlines, and a single orange series or highlight. Use espresso and parchment for context.
- Avoid 3D charts, decorative gauges, and precision unsupported by the data.
- Cite the relevant artifact or source in a small footer; expand methodology in the appendix.

## 10. Motion and presentation behavior

- Use no transition or a restrained 150–250 ms fade.
- Reveal diagram stages only when sequencing helps the explanation.
- Avoid animated counters, autoplay backgrounds, parallax, and rotating copy in the deck.
- Keep a static screenshot fallback for the live demo.
- Ensure the PDF export tells the complete story without animations or speaker interaction.

## 11. Accessibility and export review

- Check normal text against a 4.5:1 contrast target and large text against 3:1; verify actual foreground/background combinations.
- Make status understandable through words and symbols as well as color.
- Give meaningful images alt text in the editable deck and preserve a logical reading order when supported.
- Keep essential explanations out of tiny footnotes. Footnotes are for attribution and supplementary detail.
- Inspect slides at presentation size and in slide-sorter view for legibility, rhythm, and consistency.
- Check font substitution, line breaks, clipping, image sharpness, and table alignment in both the editable file and exported PDF.
- Confirm all screenshot annotations point to the intended UI state and all figures retain their qualifications.

## 12. Design acceptance checklist

- [ ] Core colors and typography match this profile.
- [ ] Each slide communicates one clear takeaway.
- [ ] Headlines, margins, and footer placement are consistent.
- [ ] Orange highlights the central point rather than decorating everything.
- [ ] Product screenshots are legible and reflect the actual build.
- [ ] Diagrams separate implemented behavior from proposed extensions.
- [ ] Results, assumptions, and targets are labeled accurately.
- [ ] No unsupported time savings, accuracy, customer, or integration claim appears.
- [ ] The deck remains readable in grayscale and as a static PDF.
- [ ] Final export has no substituted fonts, overflow, or missing assets.

**Design north star:** make the work feel at home in Cooper's visual world while keeping the customer's workflow and the candidate's evidence at the center.
