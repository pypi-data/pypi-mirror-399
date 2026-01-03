import json
import logging
from typing import Optional, List, Any
from openai import OpenAI
from pydantic import BaseModel
from PIL import Image
from tenacity import retry, stop_after_attempt, retry_if_exception_type

from polymage.model.model import Model
from polymage.media.media import Media
from polymage.media.image_media import ImageMedia
from polymage.platform.platform import Platform


logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class LMStudioPlatform(Platform):
	def __init__(self, host: str = "127.0.0.1:1234", **kwargs: Any) -> None:
		super().__init__('lmstudio', **kwargs)
		self._host = host
		self._api_key = "lm-studio"  # Dummy key (LM Studio doesn't require real keys)


	def _text2text(self, model: Model, prompt: str, media: Optional[List[Media]] = None, response_model: Optional[BaseModel] = None, **kwargs: Any) -> str:
		system_prompt: Optional[str] = kwargs.get("system_prompt", "")
		client = OpenAI(
				base_url=f"http://{self._host}/v1",  # LM Studio's default endpoint
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
				base_url=f"http://{self._host}/v1",  # LM Studio's default endpoint
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
			base_url="http://localhost:1234/v1",  # LM Studio's default endpoint
			api_key="lm-studio"  # Dummy key (LM Studio doesn't require real keys)
		)
		if len(media) == 0:
			return ""
		else:
			image = media[0]
			base64_image = image.to_base64()

		response = client.responses.create(
			model=model.internal_name(),
			input=[
				{
					"role": "user",
					"content": [
						{"type": "input_text", "text": prompt},
						{"type": "input_image", "image_url": f"data:image/png;base64,{base64_image}"},
					],
				}
			],
		)
		return response.output[0].content[0].text




	def _text2image(self, model: str, prompt: str, **kwargs: Any) -> Image.Image:
		"""Not supported"""
		pass

	def _image2image(self, model: str, prompt: str, image: Image.Image, **kwargs: Any) -> Image.Image:
		"""Not supported"""
		pass

