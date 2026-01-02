# politechie_core/validations/age_validator.py

from politechie_core.utils.base import Validator


class AgeValidator(Validator):
    MIN_AGE = 1
    MAX_AGE = 149

    def validate(self, value):
        if not isinstance(value, int):
            raise ValueError(
                f"Invalid age: '{value}'. Age must be a positive integer."
            )
        if value < self.MIN_AGE or value > self.MAX_AGE:
            raise ValueError(
                f"Invalid age: {value}. Age must be between {self.MIN_AGE} and {self.MAX_AGE}."
            )
        return True

