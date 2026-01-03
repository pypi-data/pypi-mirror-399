import yaml
from abc import ABC, abstractmethod
from typing import Dict, List, Any

class Model(ABC):
    _name: str
    _internal_name: str
    _capabilities: List[str]
    _default_params: Dict[str, Any]
    _platform_params: Dict[str, Any]

    def __init__(self, name: str="", internal_name: str="", capabilities: List[str]=[], default_params: Dict[str, Any]={}, platform_params: Dict[str, Any]={} ) -> None:
        self._name = name
        self._internal_name = internal_name
        self._capabilities = capabilities
        self._default_params = default_params
        # some platforms (for example cloudfare) use some specific parameters
        self._platform_params = platform_params

    #
    # getters
    #
    def name(self) -> str:
        return self._name

    def internal_name(self) -> str:
        return self._internal_name

    def capabilities(self) -> List[str]:
        return self._capabilities

    def default_params(self) -> Dict[str, Any]:
        return self._default_params

    def platform_params(self) -> Dict[str, Any]:
        return self._platform_params

    #
    # setters
    #
    def set_name(self, name: str) -> None:
        self._name = name.lower()

    def set_internal_name(self, internal_name: str) -> None:
        self._internal_name = internal_name.lower()

    def set_capabilities(self, capabilities: List[str]) -> None:
        self._capabilities = capabilities

    def set_default_params(self, default_params: Dict[str, Any]) -> None:
        self._default_params = default_params

    def set_platform_params(self, platform_params: Dict[str, Any]) -> None:
        self._platform_params = platform_params

    @classmethod
    def from_dict(cls, dict: Dict[str, Any]):
        model_name = dict["name"]
        model_internal_name = dict["internal_name"]
        model_capabilities = dict["capabilities"]
        model_default_params = dict["default_params"]
        # platform_params is optional
        if "platform_params" in dict:
            model_platform_params = dict["platform_params"]
        else:
            model_platform_params = {}

        model = cls(model_name, model_internal_name, model_capabilities, model_default_params, model_platform_params)
        return model

