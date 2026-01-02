# politechie_core/validations/dob_validator.py

from datetime import datetime

from politechie_core.utils.base import Validator
from politechie_core.utils.constants import DOB_FORMAT

class DobValidator(Validator):
    def validate(self, value):
        try:
            datetime.strptime(value, DOB_FORMAT)
        except ValueError:
            raise ValueError(
                f"Invalid date of birth: '{value}'. Format must be YYYY-MM-DD (e.g., 1990-01-31)."
            )
        return True

    def get_format(self):
        """Returns the required date string format."""
        return DOB_FORMAT
