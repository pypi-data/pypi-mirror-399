from importlib import resources
from .registry import ModelRegistry
#
# load all pre-defined models in the ModelRegistry
#
ModelRegistry.load_all_models()
