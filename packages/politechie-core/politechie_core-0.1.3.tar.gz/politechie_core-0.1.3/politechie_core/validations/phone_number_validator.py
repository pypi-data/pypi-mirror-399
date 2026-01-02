# politechie_core/validations/phone_validator.py

from politechie_core.utils.base import Validator

class PhoneNumberValidator(Validator):
    def clean(self, phone):
        phone_str = str(phone).replace(" ", "")

        # Remove everything after '.'
        if "." in phone_str:
            phone_str = phone_str.split(".")[0] 

        try:
            phone_int = int(phone_str)
            return str(phone_int)
        except ValueError:
            return None

    def validate(self, phone):
        if any(char.isalpha() for char in str(phone)):
            raise ValueError("Phone number must not contain alphabetic characters.")

        cleaned = self.clean(phone)
        if cleaned is None:
            raise ValueError(f"Invalid phone number: '{phone}'. Not numeric.")

        if len(cleaned) != 10:
            raise ValueError(f"Invalid phone number: '{cleaned}'. Must be 10 digits.")

        if cleaned[0] in "01234":
            raise ValueError(f"Invalid phone number: '{cleaned}'. Must not start with 0–4.")

        return True
