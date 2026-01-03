# Spec 06: PDF Rendering Fixes

## Overview

Fix two PDF rendering issues in Bingomatic bingo card generation:
1. **Logo transparency**: Preserve transparent backgrounds when rendering PNG logos
2. **Text overflow**: Fix font sizing algorithm to properly contain text within squares

## User Stories

### US-1: Logo Transparency
**As a** bingo card creator  
**I want** my logo's transparent background preserved in the PDF  
**So that** the logo blends seamlessly with the bingo card without a white box

### US-2: Text Containment
**As a** bingo card creator  
**I want** all square text to fit within the square boundaries  
**So that** the cards look professional and text is readable

## Functional Requirements

### FR-1: Preserve PNG Transparency

**Current Behavior:** Logos with transparent backgrounds render with a white/opaque background in the PDF.

**Required Behavior:** PNG images with alpha channel transparency must preserve their transparent areas when rendered in the center square.

**Implementation:** Add `mask='auto'` parameter to the `canvas.drawImage()` call in `_draw_logo()`.

### FR-2: Fix Text Fitting Algorithm

**Current Behavior:** The `_fit_text_in_square()` function only validates vertical fit (total text height), not horizontal fit. Long words like "OpenTelemetry" or "CloudFormation" can exceed square width.

**Required Behavior:** The fitting algorithm must ensure:
1. Each wrapped line fits within the square width
2. Total text height fits within the square height
3. Font size is reduced until both constraints are satisfied

**Implementation:** Modify `_fit_text_in_square()` to validate that all wrapped lines fit within `max_width` before accepting a font size.

### FR-3: Reduce Minimum Font Size

**Current Behavior:** Minimum font size is 6pt, which may be too large for longer phrases.

**Required Behavior:** Reduce minimum font size to 4pt to accommodate longer text strings.

**Implementation:** Change `MIN_FONT_SIZE` constant from 6 to 4.

## Technical Considerations

### Files to Modify

| File | Changes |
|------|---------|
| `src/bingomatic/pdf.py` | Fix `_draw_logo()`, `_fit_text_in_square()`, update `MIN_FONT_SIZE` |
| `tests/test_pdf.py` | Add tests for transparency and text fitting |

### Key Code Locations

- **Logo rendering:** `_draw_logo()` function (lines 367-406)
- **Text fitting:** `_fit_text_in_square()` function (lines 102-126)
- **Text wrapping:** `_wrap_text()` function (lines 68-99)
- **Constants:** `MIN_FONT_SIZE`, `MAX_FONT_SIZE` (lines 50-51)

### Dependencies

- ReportLab library (already installed)
- No new dependencies required

### Testing Considerations

Test cases for text fitting should include:
- "Uses OpenTelemetry in prod" (long word)
- "Has an open source project" (multiple words)
- "Repeat DevOpsDays attendee" (long phrase)

## Out of Scope

- SVG logo support
- Dynamic font size maximum based on text length
- Text truncation with ellipsis
- Custom font selection per square

## Demoable Units

### DU-1: Logo Transparency Fix
Demonstrate a PNG logo with transparent background renders without a white box in the generated PDF.

### DU-2: Text Containment Fix
Demonstrate that problematic text strings ("Uses OpenTelemetry in prod", etc.) are fully contained within their squares.

## Definition of Done

- [ ] PNG logos with transparent backgrounds render correctly (no white box)
- [ ] All text fits within square boundaries (no overflow)
- [ ] Font size reduces appropriately for longer text
- [ ] Minimum font size is 4pt
- [ ] Unit tests pass for new functionality
- [ ] Generated PDF visually verified with test data

## Proof Artifacts

1. **Generated PDF** with transparent logo visible (no white box around logo)
2. **Generated PDF** showing long text ("Uses OpenTelemetry in prod") properly contained
3. **Unit tests** verifying font sizing calculations
4. **Before/after screenshot comparison** showing the fixes

## References

- Questions: `./questions-round-1.md`
- Example problematic PDF: `/Users/richardboydii/Documents/bingomatic/output/bingo-cards-2026-01-01.pdf`
- Config with test data: `~/.bingomatic/config.yaml`
