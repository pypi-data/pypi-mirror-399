# Spec 06 Proof Artifacts - PDF Rendering Fixes

## Task 1.0: Fix Logo Transparency

### Code Change

Added `mask='auto'` parameter to `canvas.drawImage()` in `_draw_logo()` function:

```python
# src/bingomatic/pdf.py lines 397-407
canvas.drawImage(
    str(logo_path),
    logo_x,
    logo_y,
    width=logo_size,
    height=logo_size,
    preserveAspectRatio=True,
    anchor="c",
    mask="auto",  # Added to preserve PNG transparency
)
```

### Test Results

```bash
$ uv run pytest tests/test_pdf.py -v -k logo
tests/test_pdf.py::TestGeneratePdf::test_generates_pdf_with_logo PASSED
tests/test_pdf.py::TestGeneratePdf::test_raises_error_for_missing_logo PASSED
```

---

## Task 2.0: Fix Text Fitting Algorithm

### Code Changes

1. **Updated MIN_FONT_SIZE from 6 to 4:**

```python
# src/bingomatic/pdf.py line 50
MIN_FONT_SIZE = 4
```

2. **Added width validation to `_fit_text_in_square()`:**

```python
# src/bingomatic/pdf.py lines 121-127
# Check both height constraint AND that all lines fit within width
all_lines_fit_width = all(
    pdfmetrics.stringWidth(line, font_name, font_size) <= max_width
    for line in lines
)

if total_height <= max_height and all_lines_fit_width:
    return lines, font_size
```

---

## Task 3.0: Unit Tests

### New Tests Added

```python
class TestTextFitting:
    def test_min_font_size_is_4(self)
    def test_max_font_size_is_12(self)
    def test_fit_short_text_uses_max_font(self)
    def test_fit_long_text_reduces_font(self)
    def test_fit_long_word_reduces_font(self)
    def test_all_lines_fit_within_width(self)
    def test_wrap_text_splits_on_words(self)
```

### Test Results

```bash
$ uv run pytest tests/test_pdf.py::TestTextFitting -v
tests/test_pdf.py::TestTextFitting::test_min_font_size_is_4 PASSED
tests/test_pdf.py::TestTextFitting::test_max_font_size_is_12 PASSED
tests/test_pdf.py::TestTextFitting::test_fit_short_text_uses_max_font PASSED
tests/test_pdf.py::TestTextFitting::test_fit_long_text_reduces_font PASSED
tests/test_pdf.py::TestTextFitting::test_fit_long_word_reduces_font PASSED
tests/test_pdf.py::TestTextFitting::test_all_lines_fit_within_width PASSED
tests/test_pdf.py::TestTextFitting::test_wrap_text_splits_on_words PASSED
7 passed
```

### Full Test Suite

```bash
$ uv run pytest tests/ -v
69 passed
```

---

## Task 4.0: Visual Verification

### Before PDF (Reference)

- Location: `/Users/richardboydii/Documents/bingomatic/output/bingo-cards-2026-01-01.pdf`
- Issues: Logo had white background, text overflowed squares

### After PDF

Generate new PDF with fixes:

```bash
$ uv run bingomatic generate
```

### Verification Checklist

- [x] PNG logos with transparent backgrounds render correctly (no white box)
- [x] All text fits within square boundaries (no overflow)
- [x] Font size reduces appropriately for longer text
- [x] Minimum font size is 4pt
- [x] Unit tests pass for new functionality (69 passed)

---

## Summary

| Requirement | Status | Evidence |
|-------------|--------|----------|
| FR-1: PNG Transparency | ✅ Complete | `mask='auto'` added |
| FR-2: Text Fitting | ✅ Complete | Width validation added |
| FR-3: Min Font Size | ✅ Complete | MIN_FONT_SIZE = 4 |
| Unit Tests | ✅ Complete | 7 new tests, 69 total passing |
