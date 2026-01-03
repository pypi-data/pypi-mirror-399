import re


def validate_project_name(name: str) -> tuple[bool, str]:
    """
    Validate that name is valid for both:
    1. Folder name (cross-platform)
    2. Python package/import name

    Returns: (is_valid, error_message)
    """
    if not name:
        return False, "Project name cannot be empty"

    # Check length
    if len(name) > 255:
        return False, "Project name too long (max 255 characters)"

    # Must be valid Python identifier (package/import name)
    if not name.isidentifier():
        return False, (
            f"'{name}' is not a valid Python identifier. "
            "Must start with letter/underscore, contain only letters, numbers, and underscores"
        )

    # Cannot be a Python keyword
    import keyword

    if keyword.iskeyword(name):
        return False, f"'{name}' is a Python keyword and cannot be used"

    # Check for invalid filesystem characters (cross-platform)
    # Windows forbidden: < > : " / \ | ? *
    # Also avoid spaces for consistency
    invalid_chars = r'[<>:"/\\|?*\s]'
    if re.search(invalid_chars, name):
        return False, f"'{name}' contains invalid characters for folder names"

    # Cannot start with a dot (hidden files/folders)
    if name.startswith("."):
        return False, "Project name cannot start with a dot"

    # Avoid reserved names on Windows
    reserved_names = {
        "CON",
        "PRN",
        "AUX",
        "NUL",
        "COM1",
        "COM2",
        "COM3",
        "COM4",
        "COM5",
        "COM6",
        "COM7",
        "COM8",
        "COM9",
        "LPT1",
        "LPT2",
        "LPT3",
        "LPT4",
        "LPT5",
        "LPT6",
        "LPT7",
        "LPT8",
        "LPT9",
    }
    if name.upper() in reserved_names:
        return False, f"'{name}' is a reserved name on Windows"

    return True, ""


def validate_email(email: str) -> tuple[bool, str]:
    """
    Validate email address format.

    Returns: (is_valid, error_message)
    """
    if not email:
        return False, "Email cannot be empty"

    # Basic email pattern validation
    # Allows letters, numbers, dots, hyphens, underscores before @
    # Domain must have at least one dot and valid TLD
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w{2,}$"

    if not re.match(pattern, email):
        return False, f"'{email}' is not a valid email format"

    # Additional checks
    if email.count("@") != 1:
        return False, "Email must contain exactly one @ symbol"

    local, domain = email.split("@")

    if not local:
        return False, "Email local part (before @) cannot be empty"

    if not domain:
        return False, "Email domain (after @) cannot be empty"

    if len(email) > 254:  # RFC 5321
        return False, "Email address too long (max 254 characters)"

    return True, ""


def validate_license(license: str) -> tuple[bool, str]: ...


def validate_pipeline_name(name: str) -> tuple[bool, str]:
    """
    Validate and normalize pipeline name.

    Accepts alphanumeric characters, hyphens, and underscores.
    Converts to normalized form (lowercase, underscores).

    Returns:
        (is_valid, normalized_name_or_error_message)

    Note:
        Unlike validate_project_name, this returns the normalized name
        on success rather than empty string, as the command needs the normalized value.
    """
    if not name:
        return False, "Pipeline name cannot be empty"

    # Strip whitespace
    name = name.strip()

    # Check length
    if len(name) > 100:  # Reasonable limit for pipeline names
        return False, "Pipeline name too long (max 100 characters)"

    # Allow only alphanumeric, hyphens, and underscores
    if not re.match(r"^[a-zA-Z0-9_-]+$", name):
        return False, (
            f"'{name}' contains invalid characters. "
            "Use only letters, numbers, hyphens, and underscores"
        )

    # Must start with a letter or underscore (Python identifier requirement)
    if not (name[0].isalpha() or name[0] == "_"):
        return False, "Pipeline name must start with a letter or underscore"

    # Normalize the name
    from .name_converter import normalize_name

    normalized = normalize_name(name)

    # Verify normalized name is a valid Python identifier
    if not normalized.isidentifier():
        return False, f"'{name}' cannot be converted to a valid Python identifier"

    # Check for Python keywords
    import keyword

    if keyword.iskeyword(normalized):
        return False, f"'{normalized}' is a Python keyword and cannot be used"

    # Return success with normalized name
    return True, normalized


def validate_processor_name(name: str) -> tuple[bool, str]:
    """
    Validate and normalize processor name.

    Accepts alphanumeric characters, hyphens, and underscores.
    Converts to normalized form (lowercase, underscores).

    Returns:
        (is_valid, normalized_name_or_error_message)

    Note:
        Same validation rules as pipeline names.
    """
    if not name:
        return False, "Processor name cannot be empty"

    # Strip whitespace
    name = name.strip()

    # Check length
    if len(name) > 100:  # Reasonable limit for processor names
        return False, "Processor name too long (max 100 characters)"

    # Allow only alphanumeric, hyphens, and underscores
    if not re.match(r"^[a-zA-Z0-9_-]+$", name):
        return False, (
            f"'{name}' contains invalid characters. "
            "Use only letters, numbers, hyphens, and underscores"
        )

    # Must start with a letter or underscore (Python identifier requirement)
    if not (name[0].isalpha() or name[0] == "_"):
        return False, "Processor name must start with a letter or underscore"

    # Normalize the name
    from .name_converter import normalize_name

    normalized = normalize_name(name)

    # Verify normalized name is a valid Python identifier
    if not normalized.isidentifier():
        return False, f"'{name}' cannot be converted to a valid Python identifier"

    # Check for Python keywords
    import keyword

    if keyword.iskeyword(normalized):
        return False, f"'{normalized}' is a Python keyword and cannot be used"

    # Return success with normalized name
    return True, normalized


# Mapping of parameter names to their validator functions
PARAM_VALIDATORS = {
    "name": validate_project_name,
    "project_name": validate_project_name,
    "author_email": validate_email,
    "email": validate_email,
    "pipeline_name": validate_pipeline_name,
}


def validate_params(**params) -> None:
    """
    Validate multiple parameters based on their names.

    Automatically uses the appropriate validator function based on parameter name.
    Raises click.BadParameter if validation fails.

    Example:
        validate_params(name="my-project", author_email="user@example.com")
    """
    import click

    for param_name, value in params.items():
        validator_func = PARAM_VALIDATORS.get(param_name)
        if validator_func:
            is_valid, error_message = validator_func(value)
            if not is_valid:
                raise click.BadParameter(
                    error_message, param_hint=f"'--{param_name.replace('_', '-')}'"
                )
