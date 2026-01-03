from abc import ABC, abstractmethod
from pathlib import Path
from typing import Union, BinaryIO


class Media(ABC):
    """
    Abstract base class representing a multimedia object.
    Provides multiple constructors and conversion methods.
    """
