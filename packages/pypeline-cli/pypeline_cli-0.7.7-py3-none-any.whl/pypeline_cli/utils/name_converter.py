"""
Name conversion utilities for pypeline-cli.

Handles conversion between different naming conventions:
- Input names (any case, hyphens/underscores)
- Normalized names (lowercase, underscores)
- PascalCase class names
"""


def normalize_name(name: str) -> str:
    """
    Convert input name to normalized form (lowercase, underscores).

    Args:
        name: Input name (e.g., "beneficiary-claims", "BENEFICIARY", "beneficiary_claims")

    Returns:
        Normalized name (e.g., "beneficiary_claims", "beneficiary")

    Examples:
        >>> normalize_name("beneficiary-claims")
        'beneficiary_claims'
        >>> normalize_name("BENEFICIARY")
        'beneficiary'
        >>> normalize_name("my-pipeline-name")
        'my_pipeline_name'
    """
    # Strip whitespace, convert to lowercase, replace hyphens with underscores
    return name.strip().lower().replace("-", "_")


def to_pascal_case(normalized_name: str) -> str:
    """
    Convert normalized name to PascalCase.

    Args:
        normalized_name: Lowercase name with underscores (e.g., "beneficiary_claims")

    Returns:
        PascalCase name (e.g., "BeneficiaryClaims")

    Examples:
        >>> to_pascal_case("beneficiary")
        'Beneficiary'
        >>> to_pascal_case("beneficiary_claims")
        'BeneficiaryClaims'
        >>> to_pascal_case("my_pipeline_name")
        'MyPipelineName'
    """
    # Split on underscores, capitalize each word, join
    return "".join(word.capitalize() for word in normalized_name.split("_"))
