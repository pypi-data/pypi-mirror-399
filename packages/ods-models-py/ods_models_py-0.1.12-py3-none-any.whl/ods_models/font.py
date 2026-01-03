"""
ODS Models - Font
Font-related models including font types, weights, styles, and font families.
Python equivalent of font models from ods-models TypeScript package.
"""

from typing import Dict, List, Any
from enum import IntEnum
from pydantic import BaseModel, Field
from ods_models.base import FontMimeType


class FontType(BaseModel):
    """Font type classification for typography hierarchy"""
    HEADING = "heading"
    SUBHEADING = "subheading"
    BODY = "body"


class FontWeight(IntEnum):
    """Font weight values following CSS standard"""
    THIN = 100
    EXTRA_LIGHT = 200
    LIGHT = 300
    REGULAR = 400
    MEDIUM = 500
    SEMI_BOLD = 600
    BOLD = 700
    EXTRA_BOLD = 800
    BLACK = 900


class FontStyle(BaseModel):
    """Font style variants"""
    NORMAL = "normal"
    ITALIC = "italic"
    OBLIQUE = "oblique"


class Font(BaseModel):
    """Font definition with metadata and S3 storage location"""
    id: str
    name: str
    description: str
    mime_type: FontMimeType
    s3Location: Dict[str, Any]
    type: FontType
    weights: List[FontWeight]
    styles: List[FontStyle]

