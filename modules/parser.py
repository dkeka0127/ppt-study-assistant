"""
PPT Parser Module
- Extract text, images, and tables from PowerPoint files
- Convert images to base64 for Claude Vision API
"""

import io
import base64
from typing import List, Dict, Any, Optional
from pptx import Presentation
from pptx.util import Inches
from pptx.enum.shapes import MSO_SHAPE_TYPE
from PIL import Image


def extract_slide_content(uploaded_file) -> List[Dict[str, Any]]:
    """
    Extract all content from PPT slides.

    Returns:
        List of slide data with texts, images, and metadata
    """
    prs = Presentation(uploaded_file)
    slides_data = []

    for slide_num, slide in enumerate(prs.slides, start=1):
        slide_content = {
            "slide_num": slide_num,
            "texts": [],
            "images": [],
            "tables": [],
            "has_chart": False,
            "has_diagram": False
        }

        for shape in slide.shapes:
            # Extract text
            if hasattr(shape, "text") and shape.text.strip():
                slide_content["texts"].append(shape.text.strip())

            # Extract images
            if shape.shape_type == MSO_SHAPE_TYPE.PICTURE:
                image_data = extract_image(shape)
                if image_data:
                    slide_content["images"].append(image_data)

            # Extract tables
            if shape.has_table:
                table_data = extract_table(shape.table)
                slide_content["tables"].append(table_data)

            # Check for charts
            if shape.has_chart:
                slide_content["has_chart"] = True

            # Check for grouped shapes (diagrams)
            if shape.shape_type == MSO_SHAPE_TYPE.GROUP:
                slide_content["has_diagram"] = True

        slides_data.append(slide_content)

    return slides_data


def extract_image(shape) -> Optional[Dict[str, Any]]:
    """
    Extract image from shape and convert to base64.
    """
    try:
        image = shape.image
        image_bytes = image.blob
        image_ext = image.ext

        # Convert to base64
        base64_image = base64.b64encode(image_bytes).decode('utf-8')

        # Get image dimensions if possible
        width = shape.width.inches if hasattr(shape, 'width') else None
        height = shape.height.inches if hasattr(shape, 'height') else None

        return {
            "base64": base64_image,
            "format": image_ext,
            "width": width,
            "height": height,
            "media_type": get_media_type(image_ext)
        }
    except Exception as e:
        print(f"Error extracting image: {e}")
        return None


def extract_table(table) -> List[List[str]]:
    """
    Extract table content as 2D list.
    """
    table_data = []
    for row in table.rows:
        row_data = []
        for cell in row.cells:
            row_data.append(cell.text.strip())
        table_data.append(row_data)
    return table_data


def get_media_type(ext: str) -> str:
    """
    Get MIME type from file extension.
    """
    media_types = {
        "png": "image/png",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "gif": "image/gif",
        "webp": "image/webp",
        "bmp": "image/bmp"
    }
    return media_types.get(ext.lower(), "image/png")


def get_slide_text_combined(slide_data: Dict[str, Any]) -> str:
    """
    Combine all text content from a slide into a single string.
    """
    texts = slide_data.get("texts", [])
    tables = slide_data.get("tables", [])

    combined = "\n".join(texts)

    # Add table content
    for table in tables:
        table_text = "\n".join([" | ".join(row) for row in table])
        combined += f"\n[표]\n{table_text}"

    return combined


def get_all_text_content(slides_data: List[Dict[str, Any]]) -> str:
    """
    Get all text content from all slides as a single string.
    """
    all_text = []
    for slide in slides_data:
        slide_text = get_slide_text_combined(slide)
        if slide_text.strip():
            all_text.append(f"[슬라이드 {slide['slide_num']}]\n{slide_text}")

    return "\n\n".join(all_text)


def get_slides_with_images(slides_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Filter slides that contain images for Vision API processing.
    """
    return [slide for slide in slides_data if slide.get("images")]


def prepare_vision_content(slide_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Prepare content list for Claude Vision API.
    Returns list of content blocks (text and images).
    """
    content = []

    # Add text context
    text_content = get_slide_text_combined(slide_data)
    if text_content:
        content.append({
            "type": "text",
            "text": f"슬라이드 {slide_data['slide_num']}의 텍스트 내용:\n{text_content}"
        })

    # Add images
    for img in slide_data.get("images", []):
        content.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": img["media_type"],
                "data": img["base64"]
            }
        })

    return content
