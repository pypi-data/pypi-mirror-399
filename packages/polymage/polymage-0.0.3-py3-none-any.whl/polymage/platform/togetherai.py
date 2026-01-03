import json
import logging
from typing import Optional, List, Any
from openai import OpenAI
from pydantic import BaseModel
from PIL import Image
from tenacity import retry, stop_after_attempt, retry_if_exception_type

from ..model.model import Model
from ..media.media import Media
from ..media.image_media import ImageMedia
from ..platform.platform import Platform


logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

TOGETHEAI_BASE_URL = "https://api.together.xyz/v1/"


class TogetherAiPlatform(Platform):
	"""
	    Integration platform for Together AI services using the OpenAI-compatible API.

	    This class provides a concrete implementation of the `Platform` interface,
	    allowing interaction with Together AI models for text generation, structured
	    data extraction, and vision-to-text tasks. It leverages the `openai` Python
	    library to communicate with Together AI's inference endpoints.

	    Attributes:
	        api_key (str): The API key used for authenticating requests to Together AI.
	        models (List[Model]): A list containing the supported models for this platform,
	            defaulting to `gpt-oss-20b`.

	    Methods:
	        _text2text: Sends a text prompt to a model and returns a string response.
	        _text2data: Sends a text prompt and returns structured data validated
	            against a Pydantic model with automatic retry logic on JSON failure.
	        _image2text: Analyzes an image alongside a text prompt (Vision).
	        _text2image: (Not supported) Placeholder for future implementation.
	        _image2image: (Not supported) Placeholder for future implementation.

	    Note:
	        The `_text2data` method currently references `self._host` and an LM Studio
	        style URL in its implementation, which may require adjustment to align
	        with Together AI's standard production endpoints.
	"""
	def __init__(self, api_key: str, **kwargs: Any) -> None:
		super().__init__('togetherai', **kwargs)
		self._api_key = api_key


	def _text2text(self, model: Model, prompt: str, media: Optional[List[Media]] = None, response_model: Optional[BaseModel] = None, **kwargs: Any) -> str:
		system_prompt: Optional[str] = kwargs.get("system_prompt", "")
		client = OpenAI(
				base_url=TOGETHEAI_BASE_URL,  # TogetherAi's default endpoint
				api_key=self._api_key
			)
		response = client.chat.completions.create(
			model=model.internal_name(),
			messages=[
				{"role": "system", "content": system_prompt},
				{"role": "user", "content": prompt}
			],
			temperature=0.8
		)
		return response.choices[0].message.content.strip()


	#
	# using structured data may sometime fail, because the result is not a valid JSON
	# if the JSON is not valid, retry 3 times
	#
	@retry(retry=retry_if_exception_type(json.JSONDecodeError), stop=stop_after_attempt(3))
	def _text2data(self, model: Model, prompt: str, response_model: BaseModel, media: Optional[List[Media]] = None, **kwargs: Any) -> str:
		system_prompt: Optional[str] = kwargs.get("system_prompt", "")
		client = OpenAI(
				base_url=TOGETHEAI_BASE_URL,  # TogetherAi's default endpoint
				api_key=self._api_key
		)

		json_schema = response_model.model_json_schema()
		json_schema_name = json_schema['title']

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
		json_string = chat_completion.choices[0].message.content.strip()
		# return a python Dict
		return json.loads(json_string)


	def _image2text(self, model: Model, prompt: str, media: List[ImageMedia], **kwargs: Any) -> str:
		client = OpenAI(
			base_url=TOGETHEAI_BASE_URL,
			api_key=self._api_key,
		)
		if len(media) == 0:
			return ""
		else:
			image = media[0]
			base64_image = image.to_base64()

		response = client.chat.completions.create(
		    model="meta-llama/Llama-4-Scout-17B-16E-Instruct",
			messages=[
        		{
            		"role": "user",
            		"content": [
                		{"type": "text", "text": prompt},
                		{
                    		"type": "image_url",
                    		"image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                		},
            		],
        		}
    		],
    		stream=False,
    	)
		return response.choices[0].message.content.strip()


	def _text2image(self, model: str, prompt: str, **kwargs: Any) -> Image.Image:
		"""Not supported"""
		pass
		

	def _image2image(self, model: str, prompt: str, image: Image.Image, **kwargs: Any) -> Image.Image:
		"""Not supported"""
		pass

