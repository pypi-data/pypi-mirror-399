import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
from pydantic import BaseModel

from polymage.registry import ModelRegistry
from polymage.model.model import Model
from polymage.media.media import Media
from polymage.media.image_media import ImageMedia

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class Platform(ABC):
	def __init__(self, name: str, **kwargs: Any) -> None:
		self._name = name.lower()


	def platform_name(self) -> str:
		return self._name


	def text2text(self, model: str, prompt: str, media: Optional[List[Media]] = None,
				  response_model: Optional[str] = None, **kwargs: Any) -> Any:
		"""
        Convert text to text with optional structured output.

        Args:
            model: The model identifier to use
            prompt: The input text prompt
            media: Optional list of media objects
            response_model: Optional Pydantic model for structured output
            **kwargs: Additional platform-specific arguments

        Returns:
            Any: Text response or structured data
        """
		# get the model object for this platform
		platform_model = ModelRegistry.getModelByName(model, self._name)
		if response_model is None:
			return self._text2text(platform_model, prompt, media=media, response_model=response_model, **kwargs)
		# structured data output
		else:
			return self._text2data(platform_model, prompt, media=media, response_model=response_model, **kwargs)

	@abstractmethod
	def _text2text(self, model: Model, prompt: str, media: Optional[List[Media]] = None,
				   response_model: Optional[BaseModel] = None, **kwargs: Any) -> Any:
		"""Platform-specific execution interface for text-to-text conversion"""
		pass

	@abstractmethod
	def _text2data(self, model: Model, prompt: str, response_model: str, media: Optional[List[Media]] = None, **kwargs: Any) -> Dict[str, Any]:
		"""Platform-specific execution interface for text-to-structured data conversion"""
		pass


	def text2image(self, model: str, prompt: str, **kwargs: Any) -> ImageMedia:
		"""
        Convert text to image.

        Args:
            model: The model identifier to use
            prompt: The input text prompt
            **kwargs: Additional platform-specific arguments

        Returns:
            ImageMedia: Generated image media object
        """
		platform_model = ModelRegistry.getModelByName(model, self._name)
		return self._text2image(platform_model, prompt, **kwargs)

	@abstractmethod
	def _text2image(self, model: Model, prompt: str, **kwargs: Any) -> ImageMedia:
		"""Platform-specific execution interface for text-to-image conversion"""
		pass

	def image2text(self, model: str, prompt: str, media: List[ImageMedia], **kwargs: Any) -> str:
		"""
        Convert image to text.

        Args:
            model: The model identifier to use
            prompt: The input text prompt guiding the image analysis
            media: List of ImageMedia objects to process
            **kwargs: Additional platform-specific arguments

        Returns:
            str: Text description or caption of the image(s)

        Raises:
            ValueError: If media list is empty
        """
		platform_model = ModelRegistry.getModelByName(model, self._name)
		if not media:
			raise ValueError("Media list cannot be empty")
		return self._image2text(platform_model, prompt, media=media, **kwargs)

	@abstractmethod
	def _image2text(self, model: Model, prompt: str, media: List[ImageMedia], **kwargs: Any) -> str:
		"""Platform-specific execution interface for image-to-text conversion"""
		pass


	def image2image(self, model: str, prompt: str, media: List[ImageMedia], **kwargs: Any) -> ImageMedia:
		"""
        Convert image to image (image editing/transformations).

        Args:
            model: The model identifier to use
            prompt: The input text prompt guiding the transformation
            media: List of ImageMedia objects to process
            **kwargs: Additional platform-specific arguments

        Returns:
            ImageMedia: Transformed image media object
        """
		platform_model = ModelRegistry.getModelByName(model, self._name)
		if media is not None:
			image = media[0]
			return self._image2image(platform_model, prompt, media=image, **kwargs)

	@abstractmethod
	def _image2image(self, model: Model, prompt: str, media: ImageMedia, **kwargs: Any) -> ImageMedia:
		"""Platform-specific execution interface for image-to-image conversion"""
		pass
