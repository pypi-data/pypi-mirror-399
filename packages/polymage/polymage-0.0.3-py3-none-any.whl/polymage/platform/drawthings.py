import logging
import requests
from typing import List, Any
from pydantic import BaseModel
from PIL import Image

from .platform import Platform
from ..model.model import Model
from ..utils.image_utils import fit_to_nearest_aspect_ratio
from ..media.image_media import ImageMedia

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class DrawThingsPlatform(Platform):
    def __init__(self, host: str = "127.0.0.1:7860", **kwargs: Any) -> None:
        super().__init__('drawthings', **kwargs)
        self.host = host


    def _text2image(self, model: Model, prompt: str, **kwargs: Any) -> ImageMedia:
        payload = model.default_params()
        payload["model"] = model.internal_name()
        payload["prompt"] = prompt
        try:
            response = requests.post(f"http://{self.host}/sdapi/v1/txt2img", json=payload)
            response.raise_for_status()
            json_data = response.json()
            base64_string = json_data["images"][0]
            return ImageMedia(base64_string, {'Software': f"{self.platform_name()}/{model.name()}", 'Description': prompt})
        except Exception:
            logging.error("API call failed", exc_info=True)
            raise


    def _image2image(self, model: Model, prompt: str, media: ImageMedia, **kwargs: Any) -> ImageMedia:
        payload = model.default_params()
        payload["model"] = model.internal_name()
        payload["prompt"] = prompt
        # for image2image it's better to fit the to the nearest aspect ratio
        media._image = fit_to_nearest_aspect_ratio(media._image)
        # and we need to pass the image size
        width, height = media._image.size
        payload["width"] = width
        payload["height"]  = height
        # convert the image to base64
        base64_image = media.to_base64()
        payload["init_images"] = [base64_image]

        try:
            response = requests.post(f"http://{self.host}/sdapi/v1/img2img", json=payload)
            response.raise_for_status()
            json_data = response.json()
            base64_string = json_data["images"][0]
            return ImageMedia(base64_string, {'Software': f"{self.platform_name()}/{model.name()}"})
        except Exception:
            logging.error("API call failed", exc_info=True)
            raise


    def _text2text(self, model: Model, prompt: str, **kwargs: Any) -> Any:
        """Not supported"""
        pass

    def _text2data(self, model: Model, response_model: BaseModel, prompt: str, **kwargs: Any) -> Any:
        """Not supported"""
        pass

    def _image2text(self, model: Model, prompt: str, image: Image.Image, **kwargs: Any) -> str:
        """Not supported"""
        pass

    def _image2data(self, model: Model, response_model: BaseModel, prompt: str, image: Image.Image, **kwargs: Any) -> Any:
        """Not supported"""
        pass
