import copy
import yaml
from pathlib import Path
from importlib import resources
from typing import Dict, Any, Type, Optional
from .model.model import Model


class ModelRegistry:
	"""Centralized store for model configurations and platform mappings."""
	_models: [Dict] = {}

	@classmethod
	def register(cls, logical_name: str, platform_name: str, model: Model):
		"""
		register a model class and its platform-specific params.
		Usage: ModelRegistry.register("llama3", "ollama", ollama_model())
		"""
		model.set_name(logical_name)
		# if model not register yet
		if logical_name.lower() not in cls._models:
			# init the dictionary
			cls._models[logical_name.lower()] = { platform_name : model }
		else:
			cls._models[logical_name.lower()][platform_name] = model

	@classmethod
	def get_all_models(cls) -> Dict[Any, Any]:
		return cls._models


	@classmethod
	def getModelByName(cls, logical_name: str, platform_name: str) -> Model:
		"""Retrieves the provider-specific string for a logical model name."""
		if logical_name.lower() not in cls._models:
			raise ValueError(f"Model '{logical_name}' is not registered.")

		platform_dict = cls._models[logical_name.lower()]
		if platform_name not in platform_dict:
			raise ValueError(f"Platform '{platform_name}' not supported for model '{logical_name}'.")

		model = platform_dict[platform_name]
		# return a copy of the model, because we may overide some params
		return copy.deepcopy(model)


	@classmethod
	def load_all_models(cls):
		pkg_path = resources.files('polymage.data.models')
		for entry in pkg_path.iterdir():
			if entry.is_file() and entry.suffix in ('.yaml', '.yml'):
				with entry.open('r', encoding="utf-8") as f:
					# Load the data for the yaml file
					model_list = yaml.safe_load(f)
					for model_name, model_properties in model_list.items():
						# capabilities is a property of the model
						model_capabilities = model_properties['capabilities']
						for platform_name, model_dict in model_properties['platforms'].items():
							model_dict['name'] = model_name
							model_dict['capabilities'] = model_capabilities
							model = Model.from_dict(model_dict)
							# register the model
							ModelRegistry.register(logical_name=model_name, platform_name=platform_name, model=model)






