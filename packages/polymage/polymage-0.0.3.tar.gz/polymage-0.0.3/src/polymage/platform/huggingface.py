import json
import logging
from typing import Optional, List, Any
from pydantic import BaseModel
from PIL import Image
from huggingface_hub import InferenceClient
from tenacity import retry, stop_after_attempt, retry_if_exception_type, wait_random_exponential

from polymage.model.model import Model
from polymage.media.media import Media
from polymage.media.image_media import ImageMedia
from polymage.platform.platform import Platform

"""
Huggingface platform
"""
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


flux_1_schnell = Model(
	name="flux-1-schnell",
	internal_name="black-forest-labs/FLUX.1-schnell",
	capabilities=["text2image"],
	default_params={
	},
)

stable_diffusion_3_medium = Model(
    name="stable-diffusion-3-medium",
    internal_name="stabilityai/stable-diffusion-3-medium-diffusers",
    capabilities=["text2image"],
    default_params={
    },
)


class HuggingFacePlatform(Platform):
    def __init__(self, api_key: str, **kwargs: Any) -> None:
        super().__init__('huggingface', **kwargs)
        self._api_key = api_key


    def _text2text(self, model: Model, prompt: str, media: Optional[List[Media]] = None, response_model: Optional[BaseModel] = None, **kwargs: Any) -> str:
        system_prompt: Optional[str] = kwargs.get("system_prompt", "You are a helpful assistant.")
        client = InferenceClient(api_key=self._api_key)

        try:
            chat_completion = client.chat.completions.create(
                model=model.internal_name(),
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
            )
        except:
            logging.error("API call failed", exc_info=True)
            raise

        return chat_completion.choices[0].message.content.strip()

    #
    # using structured data may sometime fail, because the result is not a valid JSON
    # if the JSON is not valid, retry 3 times
    #
    @retry(retry=retry_if_exception_type(json.JSONDecodeError), stop=stop_after_attempt(3), wait=wait_random_exponential(multiplier=3))
    def _text2data(self, model: Model, prompt: str, response_model: BaseModel, media: Optional[List[Media]] = None, **kwargs: Any) -> str:
        system_prompt: Optional[str] = kwargs.get("system_prompt", "You are a helpful assistant.")
        client = InferenceClient(api_key=self._api_key)

        json_schema = response_model.model_json_schema()
        json_schema_name = json_schema['title']

        try:
            chat_completion = client.chat.completions.create(
                model=model.internal_name(),
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": json_schema_name,
                        "schema": json_schema,
                    },
                },
                temperature=0.8,
            )
        except:
            logging.error("API call failed", exc_info=True)
            raise

        json_string = chat_completion.choices[0].message.content.strip()
        # return a python Dict
        return json.loads(json_string)


    def _image2text(self, model: Model, prompt: str, media: List[ImageMedia], **kwargs: Any) -> str:
        """Not supported"""
        pass


    def _text2image(self, model: Model, prompt: str, **kwargs: Any) -> Image.Image:
        client = InferenceClient(provider="hf-inference", api_key=self._api_key)

        # output is a PIL.Image object
        try:
            image = client.text_to_image(
                prompt,
                model=model.internal_name(),
            )
        except:
            logging.error("API call failed", exc_info=True)
            raise

        return ImageMedia(image, {'Software': f"{self.platform_name()}/{model.name()}"})


    def _image2image(self, model: Model, prompt: str, image: Image.Image, **kwargs: Any) -> Image.Image:
        """Not supported"""
        pass


