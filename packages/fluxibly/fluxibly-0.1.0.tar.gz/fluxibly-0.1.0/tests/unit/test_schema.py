"""Unit tests for schema module."""

from fluxibly.schema.input import ContentFormat, ContentItem, UnifiedInput


def test_content_item_creation() -> None:
    """Test ContentItem model creation."""
    item = ContentItem(
        item_id="test_1",
        format=ContentFormat.IMAGE,
        mime_type="image/png",
        content_base64="base64data",
    )
    assert item.item_id == "test_1"
    assert item.format == ContentFormat.IMAGE


def test_unified_input_creation() -> None:
    """Test UnifiedInput model creation."""
    item = ContentItem(
        item_id="test_1",
        format=ContentFormat.TEXT,
        mime_type="text/plain",
        content_text="Hello World",
    )
    unified_input = UnifiedInput(
        submission_id="sub_001",
        source_system="test_system",
        items=[item],
    )
    assert unified_input.submission_id == "sub_001"
    assert len(unified_input.items) == 1
