# 06 Questions Round 1 - PDF Rendering Fixes

Please answer each question below (select one or more options, or add your own notes). Feel free to add additional context under any question.

## 1. Logo Transparency

What format are your logo files typically in?

- [X] (A) PNG with transparent background
- [ ] (B) PNG with solid background
- [ ] (C) JPEG (no transparency support)
- [ ] (D) SVG
- [ ] (E) Mix of formats

## 2. Text Overflow Behavior

When text is too long to fit in a square even at minimum font size, what should happen?

- [ ] (A) Truncate with ellipsis (...) - cut off text that doesn't fit
- [X] (B) Allow smaller font sizes (below current minimum of 6pt)
- [ ] (C) Allow text to extend slightly outside square (current behavior)
- [ ] (D) Wrap to more lines, accepting tighter vertical spacing
- [ ] (E) Other (describe)

## 3. Font Size Range

The current font size range is 6-12pt. Should this change?

- [ ] (A) Keep current range (6-12pt)
- [X] (B) Allow smaller minimum (e.g., 5pt or 4pt)
- [ ] (C) Increase maximum for short text (e.g., 14pt)
- [ ] (D) Other range (specify)

## 4. Specific Problem Text

Can you provide examples of square text that is currently bleeding outside the squares? This will help with testing.

- Uses OpenTelemetry in prod
- Has an open source project
- Repeat DevOpsDays attendee

## 5. Proof Artifacts

What would demonstrate these fixes are working correctly?

- [ ] (A) Generated PDF with transparent logo visible (no white box around logo)
- [ ] (B) Generated PDF showing long text properly contained in squares
- [ ] (C) Unit tests verifying font sizing calculations
- [ ] (D) Before/after screenshot comparison
- [X] (E) All of the above
