# politechie_core/validations/email_validator.py

import re

from politechie_core.utils.base import Validator
from politechie_core.utils.constants import EMAIL_PATTERN

class EmailValidator(Validator):
    def validate(self, value):
        if not re.fullmatch(EMAIL_PATTERN, value):
            raise ValueError(
                f"Invalid email: '{value}'. Format must be like 'user@example.com'."
            )
        return True

    def get_pattern(self):
        """Returns the email regex pattern used for validation."""
        return EMAIL_PATTERN