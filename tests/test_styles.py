"""Unit tests for the styles.py helper functions."""
from unittest.mock import MagicMock, call, patch

import pytest

from shopee_transfer.web.styles import (
    CSS_CUSTOM_STYLES,
    badge,
    card,
    progress_indicator,
    status_text,
    step_badge,
)


class TestBadge:
    def test_success_badge_has_correct_class(self):
        result = badge("OK", "success")
        assert 'class="shopee-badge shopee-badge-success"' in result
        assert "OK" in result

    def test_error_badge_has_correct_class(self):
        result = badge("Fail", "error")
        assert 'class="shopee-badge shopee-badge-error"' in result

    def test_warning_badge_has_correct_class(self):
        result = badge("Warn", "warning")
        assert 'class="shopee-badge shopee-badge-warning"' in result

    def test_info_badge_has_correct_class(self):
        result = badge("Info", "info")
        assert 'class="shopee-badge shopee-badge-info"' in result

    def test_pending_badge_has_correct_class(self):
        result = badge("Pending", "pending")
        assert 'class="shopee-badge shopee-badge-pending"' in result

    def test_default_badge_has_correct_class(self):
        result = badge("Default", "default")
        assert 'class="shopee-badge shopee-badge-default"' in result

    def test_unknown_status_falls_back_to_default(self):
        result = badge("X", "nonexistent")
        assert "shopee-badge-default" in result

    def test_text_is_included_in_output(self):
        result = badge("My Label", "info")
        assert "My Label" in result

    def test_returns_span_element(self):
        result = badge("Test", "success")
        assert result.startswith("<span")
        assert result.endswith("</span>")


class TestStepBadge:
    def test_default_total_steps_is_4(self):
        result = step_badge(1)
        assert "Step 1/4" in result

    def test_custom_total_steps(self):
        result = step_badge(2, 6)
        assert "Step 2/6" in result

    def test_returns_div_element(self):
        result = step_badge(3)
        assert 'class="shopee-step-badge"' in result
        assert "<div" in result

    def test_last_step(self):
        result = step_badge(4, 4)
        assert "Step 4/4" in result


class TestProgressIndicator:
    def test_percentage_calculation(self):
        result = progress_indicator(3, 5)
        assert "60.0%" in result

    def test_full_progress(self):
        result = progress_indicator(5, 5)
        assert "100.0%" in result

    def test_zero_total_returns_zero_percent(self):
        result = progress_indicator(0, 0)
        assert "width: 0%" in result

    def test_zero_current(self):
        result = progress_indicator(0, 10)
        assert "width: 0.0%" in result

    def test_custom_label_appears(self):
        result = progress_indicator(2, 4, label="Export Files")
        assert "Export Files" in result

    def test_default_label_is_progress(self):
        result = progress_indicator(1, 4)
        assert "Progress" in result

    def test_current_and_total_displayed(self):
        result = progress_indicator(3, 5)
        assert "3/5" in result


class TestCard:
    def test_renders_title(self):
        result = card("My Title", "Some content")
        assert "My Title" in result
        assert 'class="shopee-card-title"' in result

    def test_renders_content(self):
        result = card("T", "My Content")
        assert "My Content" in result
        assert 'class="shopee-card-content"' in result

    def test_subtitle_included_when_provided(self):
        result = card("T", "C", subtitle="My Sub")
        assert "My Sub" in result
        assert 'class="shopee-card-subtitle"' in result

    def test_no_subtitle_html_when_omitted(self):
        result = card("T", "C")
        assert "shopee-card-subtitle" not in result

    def test_wrapped_in_card_div(self):
        result = card("T", "C")
        assert 'class="shopee-card"' in result


class TestStatusText:
    def test_text_is_included(self):
        result = status_text("All good", "success")
        assert "All good" in result

    def test_includes_badge_for_status(self):
        result = status_text("All good", "success")
        assert "shopee-badge-success" in result

    def test_badge_label_is_uppercased_status(self):
        result = status_text("msg", "info")
        assert "INFO" in result


class TestInjectStyles:
    @patch("shopee_transfer.web.styles.st")
    def test_calls_markdown_with_unsafe_html(self, mock_st):
        from shopee_transfer.web.styles import inject_styles
        inject_styles()
        mock_st.markdown.assert_called_once_with(CSS_CUSTOM_STYLES, unsafe_allow_html=True)


class TestRenderSummaryBox:
    def _make_mock_st(self, mock_st):
        """Configure a patched st mock with unpacking-safe columns."""
        mock_col = MagicMock()
        mock_st.columns.return_value = [mock_col, mock_col]
        mock_st.container.return_value.__enter__ = MagicMock(return_value=MagicMock())
        mock_st.container.return_value.__exit__ = MagicMock(return_value=False)
        return mock_col

    @patch("shopee_transfer.web.styles.st")
    def test_renders_title_via_markdown(self, mock_st):
        from shopee_transfer.web.styles import render_summary_box

        self._make_mock_st(mock_st)
        render_summary_box("My Title", {"Key": "Value"})
        mock_st.markdown.assert_called_with("**My Title**")

    @patch("shopee_transfer.web.styles.st")
    def test_renders_one_row_per_item(self, mock_st):
        from shopee_transfer.web.styles import render_summary_box

        self._make_mock_st(mock_st)
        items = {"From": "MY (MYR)", "To": "SG (SGD)", "Rate": "0.2900"}
        render_summary_box("Config", items)
        assert mock_st.columns.call_count == len(items)

    @patch("shopee_transfer.web.styles.st")
    def test_container_opened_with_border(self, mock_st):
        from shopee_transfer.web.styles import render_summary_box

        self._make_mock_st(mock_st)
        render_summary_box("T", {"k": "v"})
        mock_st.container.assert_called_once_with(border=True)
