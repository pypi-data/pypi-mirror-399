import logging
from typing import Any, Optional, List
from pydantic import BaseModel

from .agent import Agent
from ..media.media import Media

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

class InstructAgent(Agent):
	"""
	"""

	def __init__(self, **kwargs: Any) -> None:
		super().__init__(**kwargs)

	def run(self, prompt: str, media: Optional[List[Media]] = None, **kwargs: Any) -> Any:
		"""
		Execute a text-to-text transformation using the configured platform.

		This method processes a prompt through the platform's text2text capability,
		optionally incorporating a system prompt if one was provided during initialization.

		Args:
			prompt (str): The input text prompt to process
			media (Optional[List[Media]]): Optional list of media objects to include
										  in the processing (e.g., images, files)
			**kwargs: Additional keyword arguments to pass to the platform's text2text method

		Returns:
			Any: The result from the platform's text2text processing, typically
				 a string or structured data based on response_model parameter

		Note:
			If system_prompt was provided during initialization, it will be merged
			with any additional kwargs, where the system prompt takes precedence
			in case of key conflicts.
		"""

		if self.system_prompt is not None:
			kwargs['system_prompt'] = self.system_prompt

		return self.platform.text2text(
			model=self.model,
			prompt=prompt,
			media=media,
			response_model=self.response_model,
			**kwargs
		)
