# Politechie Core

Utilities for validating common pieces of user data such as ages, dates of birth, phone numbers, genders, and email addresses. The package ships with a simple `Validator` base class plus a collection of concrete validators under `politechie_core.validations`.

## Installation

```bash
pip install politechie-core
```

Or install from source inside this repository:

```bash
pip install .
```

## Usage

```python
from politechie_core.validations import (
    AgeValidator,
    DobValidator,
    EmailValidator,
    GenderValidator,
    PhoneNumberValidator,
)

age_validator = AgeValidator()
email_validator = EmailValidator()

age_validator.validate(32)           # returns True
email_validator.validate("user@example.com")

# Invalid input raises ValueError
try:
    age_validator.validate(-1)
except ValueError as exc:
    print(exc)
```

### Available validators

- `AgeValidator` – ensures ages fall between 1 and 149
- `DobValidator` – parses YYYY-MM-DD dates and rejects future dates
- `EmailValidator` – wraps a regex (see `politechie_core.utils.constants.EMAIL_PATTERN`)
- `GenderValidator` – checks membership in `{"M", "F", "O"}`
- `PhoneNumberValidator` – enforces basic E.164-style formatting

Each validator inherits from the abstract `Validator` class defined in `politechie_core.utils.base`. Validators return `True` on success and raise a `ValueError` when the input is invalid.

## Local development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest
```

## Deploying to PyPI

1. **Bump the version** inside `setup.py`.
2. **Install build tooling** (one time):
   ```bash
   pip install --upgrade build twine
   ```
3. **Remove old artifacts**:
   ```bash
   rm -rf build dist *.egg-info
   ```
4. **Create the sdist and wheel**:
   ```bash
   python setup.py sdist bdist_wheel
   ```
5. **Upload to TestPyPI (optional but recommended)**:
   ```bash
   twine upload --repository testpypi dist/*
   ```
6. **Upload to PyPI**:
   ```bash
   twine upload dist/*
   ```

Provide your PyPI credentials when prompted or export `TWINE_USERNAME` and `TWINE_PASSWORD` before running the upload command. After publishing, verify installation with `pip install politechie-core==<version>` in a clean environment.

