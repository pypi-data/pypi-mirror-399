"""
Excel Pixel Art - Convert images to Excel pixel art and back.

Tools:
  - image2xlsx: Convert an image to an Excel file with coloured cells
  - xlsx2image: Reconstruct an image from an Excel file (with QA tools)
"""

from .image_to_excel import image_to_excel, rgb_to_argb
from .excel_to_image import excel_to_image, compare_images

__version__ = "1.0.0"
__all__ = ["image_to_excel", "excel_to_image", "compare_images", "rgb_to_argb"]
