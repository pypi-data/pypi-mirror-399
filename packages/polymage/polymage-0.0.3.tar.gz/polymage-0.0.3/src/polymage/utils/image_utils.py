import base64
import logging
from io import BytesIO
from PIL import Image, ImageOps
from typing import Optional, Dict, Any, Union


logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

#
# Conversion utils
#
def base64_to_image(base64_string: str) -> Image.Image:
    """
    Convert a base64 encoded string to a PIL Image object.

    This function decodes a base64 string representation of an image and converts it
    into a PIL (Pillow) Image object that can be manipulated or saved.

    Args:
        base64_string (str): Base64 encoded string representing an image

    Returns:
        PIL.Image.Image: A PIL Image object created from the base64 data

    Example:
        # Convert base64 string to image
        image = base64_to_image("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==")

        # Save the image
        image.save('output.png')

    Note:
        The function supports any image format that PIL can handle (PNG, JPEG, etc.)
    """
    # Decode the base64 string to bytes
    image_bytes = base64.b64decode(base64_string)
    # Create a BytesIO object from the decoded bytes
    image_buffer = BytesIO(image_bytes)
    # Open the image using PIL
    image = Image.open(image_buffer)
    # return a PIL Image object
    return image


def bytes_to_image(image_bytes: bytes) -> Image.Image:
    image = Image.open(BytesIO(image_bytes))
    return image


def image_to_base64(image: Image.Image, format='PNG') -> str:
    """
    Convert a PIL Image object to a base64 encoded string.

    This function takes a PIL Image object and converts it to a base64 encoded string
    which can be used for embedding images in HTML, JSON responses, or other text-based formats.

    Args:
        image (PIL.Image.Image): The PIL Image object to convert
        format (str, optional): The image format to use for encoding. Defaults to 'PNG'.
                               Common formats include 'PNG', 'JPEG', 'GIF'.

    Returns:
        str: Base64 encoded string representation of the image

    Example:
        from PIL import Image
        # Load an image
        img = Image.open('example.jpg')
        # Convert to base64
        base64_string = image_to_base64(img, 'JPEG')

    Note:
        The function uses BytesIO for efficient in-memory image handling and
        returns a UTF-8 decoded base64 string ready for use in text-based protocols.
    """
    # Input is a PIL Image object
    buffered = BytesIO()
    image.save(buffered, format=format)
    encoded_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
    return encoded_str

#
# some image2image models enforce some image ratio size (multiple of 128)
#
ASPECT_RATIO_SIZE = {
    "1:1": [1024, 1024],
    "5:4": [1152, 896],
    "4:3": [1024, 768],
    "3:2": [1152, 768],
    "2:1": [1408, 704],
    "16,9": [1024, 576],
    "9,16": [576, 1024],
    "4,5": [896, 1152],
    "3,4": [768, 1024],
    "2,3": [768, 1152],
    "1,2": [704, 1408],
}

#
# for image2image it's better to fit the image size to the nearest aspect ratio
#
def fit_to_nearest_aspect_ratio(image: Image.Image) -> Image.Image:
    """
    Fits the input PIL image to the nearest aspect ratio defined in ASPECT_RATIO_SIZE,
    using ImageOps.fit. Returns the cropped and resized image.
    """
    img_width, img_height = image.size
    img_aspect = img_width / img_height

    min_diff = float('inf')
    best_size = None

    for size in ASPECT_RATIO_SIZE.values():
        w, h = size
        ar = w / h
        diff = abs(img_aspect - ar)
        if diff < min_diff:
            min_diff = diff
            best_size = (w, h)
    # Use ImageOps.fit to crop and resize to the best matching aspect ratio
    fitted_image = ImageOps.fit(image, best_size, method=Image.LANCZOS)
    return fitted_image
