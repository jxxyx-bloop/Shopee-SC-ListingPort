# CLAUDE.md — Project Memory for ShopeeSC

## Critical: Streamlit `unsafe_allow_html=True` — No Blank Lines Inside HTML Blocks

**Problem:** Streamlit's markdown renderer follows the CommonMark specification, which states that an HTML block (any block-level tag like `<div>`, `<p>`, etc.) is **terminated by a blank line**. If your HTML string passed to `st.markdown(..., unsafe_allow_html=True)` contains any blank lines (empty lines or lines with only whitespace) *within* the HTML, the renderer exits "HTML block" mode at that blank line and begins treating subsequent content as escaped plain text. This causes inner HTML tags to appear as raw code on the page.

**Symptom:** The outermost `<div>` wrapper renders correctly (because it appears before the first blank line), but all HTML elements after the first blank line are shown verbatim as `<div class="...">...</div>` text.

**Rule:** When writing HTML strings for `st.markdown(..., unsafe_allow_html=True)`:
- **NEVER** include blank lines (double newlines) within the HTML string.
- Use Python string concatenation (`"..." + f"..."` or parenthesised `(f"..." f"...")`) to build multi-element HTML without blank gaps.
- Single newlines between tags are fine. Only **blank/empty lines** trigger the break.

**Good pattern:**
```python
# Use parenthesised string concatenation — no blank lines anywhere
return (
    f'<div class="outer">'
    f'<div class="inner-a">Content A</div>'
    f'<div class="inner-b">Content B</div>'
    f'</div>'
)
```

**Bad pattern (will break):**
```python
# Triple-quoted f-string with blank lines — inner divs will render as raw text
return f"""
<div class="outer">
    <div class="inner-a">Content A</div>

    <div class="inner-b">Content B</div>
</div>
"""
```

**Reference:** CommonMark spec §4.6 — HTML blocks of type 6 (block-level tags) are terminated by a blank line.
