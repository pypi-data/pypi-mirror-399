# politechie_core/utils/base.py

from abc import ABC, abstractmethod

class Validator(ABC):
    @abstractmethod
    def validate(self, value):
        """Return True/False or raise exception if invalid."""
        pass
