# image_media.py
import base64
import logging
from io import BytesIO
from PIL import Image
from PIL.PngImagePlugin import PngInfo
from typing import Optional, Dict, Any, Union
from .media import Media
from ..utils.image_utils import base64_to_image, bytes_to_image

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class ImageMedia(Media):
    """
    Image media class using Pillow as internal representation.

    This class provides a wrapper around PIL (Pillow) Image objects to handle image media
    with additional functionality for base64 encoding and metadata management.

    Attributes:
        _image (PIL.Image.Image): Internal PIL Image object
        _metadata (Optional[dict]): Metadata associated with the image

    Example:
        from PIL import Image
        pil_img = Image.open('image.jpg')
        image_media = ImageMedia(pil_img, {'author': 'John Doe'})

        # Convert to base64
        base64_data = image_media.to_base64()

        # Save with metadata
        image_media.save_to_file('output.png')
    """

    def __init__(self, image_data: Union[str, bytes, Image.Image], metadata: Optional[Dict[str, Any]] = None, **kwargs: Any) -> None:
        self._metadata = metadata
        # Auto-detect based on type
        if isinstance(image_data, str):
            self._image = base64_to_image(image_data)
        elif isinstance(image_data, bytes):
            self._image = bytes_to_image(image_data)
        elif isinstance(image_data, Image.Image):
            self._image = image_data
        else:
            raise TypeError("image_data must be either a Pillow Image or base64-encoded string or raw bytes.")


    def to_base64(self, format='PNG') -> str:
        """
        Convert the image to a base64 encoded string.

        Args:
            format (str): Image format for encoding (default: 'PNG')

        Returns:
            str: Base64 encoded string representation of the image

        Example:
            base64_str = image_media.to_base64('JPEG')
        """
        # Create an in-memory bytes buffer
        buffer = BytesIO()
        # Save the image to the buffer in the specified format
        self._image.save(buffer, format=format)
        # Get the bytes from the buffer
        image_bytes = buffer.getvalue()
        # Encode the bytes as base64 and decode to a string
        base64_str = base64.b64encode(image_bytes).decode('utf-8')
        return base64_str


    def save_to_file(self, filepath: str) -> None:
        """
        Save the image to a file with metadata support.

        Args:
            filepath (str): Path where the image should be saved

        Example:
            image_media.save_to_file('output.png')
        """
        metadata = self._metadata
        self._image.load()  # Ensures image is fully loaded
        file_metameta = PngInfo()
        if metadata is not None:
            for key, value in metadata.items():
                file_metameta.add_text(key, value)
        # save to file
        self._image.save(filepath, pnginfo=file_metameta)
