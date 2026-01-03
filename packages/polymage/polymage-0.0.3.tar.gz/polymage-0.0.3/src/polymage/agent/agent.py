from abc import ABC, abstractmethod
from typing import Any, Optional, List
from pydantic import BaseModel

from ..media.media import Media
from ..platform.platform import Platform


class Agent(ABC):
	"""
	Abstract base class for creating intelligent agents that interact with platforms.

	This class serves as a blueprint for implementing various types of agents (e.g., chatbots,
	code assistants, content generators) that can process prompts and generate responses
	using different AI models.

	Attributes:
		platform (Platform): The platform instance this agent operates on
		model (str): The AI model identifier (e.g., 'gpt-4', 'llama3') used for generating responses
		response_model (Optional[BaseModel]): Pydantic model defining the structure of expected responses,
			or None if free-form text responses are acceptable
		system_prompt (Optional[str]): System-level instructions that define the agent's behavior and role

	Example:
		class ChatAgent(Agent):
			def run(self, prompt: str, media: Optional[List[Media]] = None, **kwargs) -> Any:
				# Implementation here
				pass
	"""

	def __init__(
			self,
			platform: Platform,
			model: str,
			response_model: Optional[BaseModel] = None,
			system_prompt: Optional[str] = None,
	):
		self.platform = platform
		self.model = model
		self.response_model = response_model
		self.system_prompt = system_prompt


	@abstractmethod
	def run(self, prompt: str, media: Optional[List[Media]] = None, **kwargs: Any) -> Any:
		"""
		Execute the agent with a given prompt and optional media.

		This abstract method must be implemented by subclasses to define how the agent
		processes input and generates responses.

		Args:
			prompt (str): The user's input or instruction for the agent
			media (Optional[List[Media]]): List of media objects (images, files) to process,
				or None if no media is provided
			**kwargs: Additional keyword arguments for flexible input handling

		Returns:
			Any: The result of the agent's processing, typically a response or generated content

		Raises:
			NotImplementedError: If subclass doesn't implement this method
		"""
		pass
