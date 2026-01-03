import logging
from typing import Any, Optional, List

from .agent import Agent
from ..media.media import Media

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

"""
an image captioner agent
"""

class ImageCaptionerAgent(Agent):
	"""
	"""
	def __init__(self, **kwargs):
		super().__init__(**kwargs)

	def run(self, prompt: str, media: Optional[List[Media]] = None, **kwargs: Any) -> Any:
		"""
		Execute the image captioning process.

		Args:
			prompt (str): The prompt or instruction for image description generation.
			media (Optional[List[Media]]): List of media objects to process.
										  Defaults to None.
			**kwargs: Additional keyword arguments passed to the platform's
					 image2text method.

		Returns:
			Any: The result from the platform's image-to-text conversion, typically
				 a string or structured data containing the generated caption or
				 description.
		"""
		platform=self.platform
		model=self.model
		system_prompt=self.system_prompt

		return platform.image2text(model=model, prompt=prompt, media=media, **kwargs)
