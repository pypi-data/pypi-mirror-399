"""Unified Input Schema for the framework.

This module defines the standard input format for handling heterogeneous content types.
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ContentFormat(str, Enum):
    """Supported content formats."""

    IMAGE = "image"
    DOCUMENT = "document"
    VIDEO = "video"
    AUDIO = "audio"
    TEXT = "text"
    CODE = "code"
    PRESENTATION = "presentation"


class ContentItem(BaseModel):
    """Individual content item within a submission.

    Attributes:
        item_id: Unique identifier within submission
        format: Content type (image, document, video, etc.)
        mime_type: MIME type (e.g., application/pdf, image/png)
        content_base64: Base64-encoded content (for files < 10MB)
        content_url: URL to content (for larger files)
        content_text: Plain text content (for text/code)
        filename: Original filename
        size_bytes: File size in bytes
        metadata: Format-specific metadata
        parent_item_id: Reference to parent item for hierarchical content
        order: Sequence number within parent
    """

    item_id: str = Field(..., description="Unique identifier within submission")
    format: ContentFormat = Field(..., description="Content type")
    mime_type: str = Field(..., description="MIME type")

    # Content delivery (use ONE of these)
    content_base64: str | None = Field(None, description="Base64-encoded content")
    content_url: str | None = Field(None, description="URL to content")
    content_text: str | None = Field(None, description="Plain text content")

    # Item metadata
    filename: str | None = Field(None, description="Original filename")
    size_bytes: int | None = Field(None, description="File size in bytes")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Format-specific metadata")

    # Hierarchical relationships
    parent_item_id: str | None = Field(None, description="Parent item reference")
    order: int = Field(0, description="Sequence within parent")


class UnifiedInput(BaseModel):
    """Top-level input envelope for the framework.

    Attributes:
        submission_id: Unique identifier for tracking and correlation
        timestamp: Submission time
        source_system: Origin system identifier
        items: List of content items (supports multiple items)
        context: Task-specific context data
        priority: Processing priority (low, normal, high)
        callback_url: URL for async response callbacks
    """

    submission_id: str = Field(..., description="Unique identifier for tracking")
    timestamp: datetime = Field(default_factory=datetime.now, description="Submission time")
    source_system: str = Field(..., description="Origin system identifier")

    items: list[ContentItem] = Field(..., description="Content items (one or more)")

    context: dict[str, Any] = Field(default_factory=dict, description="Task-specific context")
    priority: str = Field("normal", description="Processing priority")
    callback_url: str | None = Field(None, description="Callback URL for async responses")
