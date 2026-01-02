# politechie_core/validations/gender_validator.py

from politechie_core.utils.base import Validator
from politechie_core.utils.constants import VALID_GENDER_OPTIONS

class GenderValidator(Validator):
    def validate(self, value):
        if value not in VALID_GENDER_OPTIONS:
            raise ValueError(
                f"Invalid gender: '{value}'. Valid options are: {', '.join(VALID_GENDER_OPTIONS)}"
            )
        return True

    def get_valid_options(self):
        """Return the set of valid gender options."""
        return VALID_GENDER_OPTIONS