import json
import logging
from typing import Optional, List, Any
from pydantic import BaseModel
from PIL import Image
from groq import Groq
from tenacity import retry, stop_after_attempt, retry_if_exception_type, wait_random_exponential

from ..model.model import Model
from ..media.media import Media
from ..media.image_media import ImageMedia
from .platform import Platform

"""
groq platform

groq support LLm and audio2text models
you can find the list of supported models here : https://console.groq.com/docs/models
"""
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class GroqPlatform(Platform):
    def __init__(self, api_key: str, **kwargs: Any) -> None:
        super().__init__('groq', **kwargs)
        self._api_key = api_key


    def _text2text(self, model: Model, prompt: str, media: Optional[List[Media]] = None, response_model: Optional[BaseModel] = None, **kwargs: Any) -> str:
        system_prompt: Optional[str] = kwargs.get("system_prompt", "You are a helpful assistant.")
        client = Groq(api_key=self._api_key)
        chat_completion = client.chat.completions.create(
            model=model.platform_name(),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
        )
        return chat_completion.choices[0].message.content.strip()

    #
    # using structured data may sometime fail, because the result is not a valid JSON
    # if the JSON is not valid, retry 3 times
    #
    @retry(retry=retry_if_exception_type(json.JSONDecodeError), stop=stop_after_attempt(3), wait=wait_random_exponential(multiplier=3))
    def _text2data(self, model: Model, prompt: str, response_model: BaseModel, media: Optional[List[Media]] = None, **kwargs: Any) -> str:
        system_prompt: Optional[str] = kwargs.get("system_prompt", "You are a helpful assistant.")
        client = Groq(api_key=self._api_key)

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
        client = Groq(api_key=self._api_key)
        if len(media) == 0:
            return ""
        else:
            image = media[0]
            base64_image = image.to_base64()

        try:
            chat_completion = client.chat.completions.create(
                model=model.internal_name(),
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}",
                                },
                            },
                        ],
                    }
                ],
                temperature=1,
                max_completion_tokens=1024,
                top_p=1,
                stream=False,
                stop=None,
            )
        except Exception as e:
            logging.error("API call failed", exc_info=True)
            raise

        return chat_completion.choices[0].message.content.strip()


    def _text2image(self, model: Model, prompt: str, **kwargs: Any) -> Image.Image:
        """Not supported"""
        pass


    def _image2image(self, model: Model, prompt: str, image: Image.Image, **kwargs: Any) -> Image.Image:
        """Not supported"""
        pass


