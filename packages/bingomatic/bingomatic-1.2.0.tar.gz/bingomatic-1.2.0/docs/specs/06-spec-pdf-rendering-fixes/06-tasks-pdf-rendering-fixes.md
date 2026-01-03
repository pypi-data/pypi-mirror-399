# Tasks: Spec 06 - PDF Rendering Fixes

## Spec Reference

- **Spec:** `./spec.md`
- **Feature:** Fix logo transparency and text overflow in PDF generation

## Tasks

### [x] 1.0 Fix Logo Transparency

Add support for preserving PNG alpha channel transparency when rendering logos in the center square of bingo cards.

#### 1.0 Proof Artifact(s)

- Screenshot: Before/after comparison showing logo renders without white box
- File: Generated PDF with transparent logo in center square
- CLI: `bingomatic generate` completes successfully with transparent PNG logo

#### 1.0 Tasks

- [x] 1.1 Capture "before" screenshot of current logo rendering with transparent PNG
- [x] 1.2 Add `mask='auto'` parameter to `canvas.drawImage()` in `_draw_logo()` function
- [x] 1.3 Test logo rendering with transparent PNG logo
- [x] 1.4 Verify transparency is preserved in generated PDF

---

### [x] 2.0 Fix Text Fitting Algorithm

Modify the text fitting algorithm to validate both horizontal and vertical fit, ensuring all text stays within square boundaries.

#### 2.0 Proof Artifact(s)

- Screenshot: Before/after comparison showing "Uses OpenTelemetry in prod" contained in square
- File: Generated PDF with long text properly contained
- CLI: `bingomatic generate` produces cards with no text overflow

#### 2.0 Tasks

- [x] 2.1 Capture "before" screenshot showing text overflow with problematic phrases
- [x] 2.2 Update `MIN_FONT_SIZE` constant from 6 to 4
- [x] 2.3 Modify `_fit_text_in_square()` to validate line widths fit within `max_width`
- [x] 2.4 Add width check: verify each wrapped line width <= max_width before accepting font size
- [x] 2.5 Test with problematic phrases: "Uses OpenTelemetry in prod", "Has an open source project", "Repeat DevOpsDays attendee"
- [x] 2.6 Verify all text is contained within square boundaries

---

### [x] 3.0 Add Unit Tests

Create unit tests for the logo transparency and text fitting functionality to prevent regressions.

#### 3.0 Proof Artifact(s)

- CLI: `uv run pytest tests/test_pdf.py -v` passes all new tests
- File: `tests/test_pdf.py` contains tests for transparency and text fitting
- Test: Specific test cases for "Uses OpenTelemetry in prod", "Has an open source project", "Repeat DevOpsDays attendee"

#### 3.0 Tasks

- [x] 3.1 Add test for `_fit_text_in_square()` with long single word ("OpenTelemetry")
- [x] 3.2 Add test for `_fit_text_in_square()` with long phrase ("Repeat DevOpsDays attendee")
- [x] 3.3 Add test verifying font size reduces appropriately for long text
- [x] 3.4 Add test verifying all wrapped lines fit within max_width
- [x] 3.5 Run full test suite: `uv run pytest tests/ -v`

---

### [x] 4.0 Visual Verification and Documentation

Generate test PDF with problematic content, capture before/after screenshots, and update proof artifacts.

#### 4.0 Proof Artifact(s)

- Screenshot: Side-by-side before/after comparison of logo transparency
- Screenshot: Side-by-side before/after comparison of text containment
- File: Final generated PDF with all fixes applied
- File: Proof artifacts document in `./06-proofs/`

#### 4.0 Tasks

- [x] 4.1 Generate final PDF with user's config (includes problematic phrases)
- [x] 4.2 Capture "after" screenshots showing fixes
- [x] 4.3 Create `./06-proofs/` directory
- [x] 4.4 Create proof artifacts document with before/after comparisons
- [x] 4.5 Commit all changes with appropriate message

---

## Relevant Files

| File | Action | Description |
|------|--------|-------------|
| `src/bingomatic/pdf.py` | Modify | Add `mask='auto'`, fix `_fit_text_in_square()`, update `MIN_FONT_SIZE` |
| `tests/test_pdf.py` | Modify | Add tests for text fitting with long phrases |
| `docs/specs/06-spec-pdf-rendering-fixes/06-proofs/` | Create | Proof artifacts directory |

## Spec Coverage Matrix

| Spec Requirement | Task Coverage |
|------------------|---------------|
| FR-1: PNG Transparency | Task 1.0 |
| FR-2: Text Fitting | Task 2.0 |
| FR-3: Min Font Size | Task 2.0 |
| US-1: Logo Transparency | Task 1.0, 4.0 |
| US-2: Text Containment | Task 2.0, 4.0 |
| DU-1: Logo Demo | Task 1.0, 4.0 |
| DU-2: Text Demo | Task 2.0, 4.0 |
