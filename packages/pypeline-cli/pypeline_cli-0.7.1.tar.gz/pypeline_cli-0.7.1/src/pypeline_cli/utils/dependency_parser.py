import re
from typing import NamedTuple


class Dependency(NamedTuple):
    """Represents a parsed dependency with name and version specifier."""

    name: str
    version_spec: str

    def __str__(self) -> str:
        """Return dependency in standard format: name>=version or name==version"""
        return f"{self.name}{self.version_spec}"


def parse_dependency(dep_string: str) -> Dependency:
    """
    Parse a dependency string into name and version specifier.

    Supports formats:
        - "package>=1.0.0"
        - "package==1.0.0"
        - "package~=1.0"
        - "package>1.0,<2.0"
        - "package"  (no version -> empty spec)

    Args:
        dep_string: Dependency string to parse

    Returns:
        Dependency namedtuple with name and version_spec

    Examples:
        >>> parse_dependency("requests>=2.28.0")
        Dependency(name='requests', version_spec='>=2.28.0')

        >>> parse_dependency("numpy==1.24.0")
        Dependency(name='numpy', version_spec='==1.24.0')

        >>> parse_dependency("pandas")
        Dependency(name='pandas', version_spec='')
    """
    # Regex to split package name from version specifier
    # Matches: package-name followed by optional version operators
    pattern = r"^([a-zA-Z0-9_\-\.]+)(.*)$"

    match = re.match(pattern, dep_string.strip())
    if not match:
        raise ValueError(f"Invalid dependency format: {dep_string}")

    name = match.group(1)
    version_spec = match.group(2).strip()

    return Dependency(name=name, version_spec=version_spec)


def parse_dependencies(dep_list: list[str]) -> list[Dependency]:
    """
    Parse a list of dependency strings.

    Args:
        dep_list: List of dependency strings

    Returns:
        List of Dependency namedtuples

    Example:
        >>> parse_dependencies(["requests>=2.28.0", "numpy==1.24.0", "pandas"])
        [Dependency(name='requests', version_spec='>=2.28.0'),
         Dependency(name='numpy', version_spec='==1.24.0'),
         Dependency(name='pandas', version_spec='')]
    """
    return [parse_dependency(dep) for dep in dep_list]


def format_dependency(name: str, version_spec: str = "") -> str:
    """
    Format a dependency name and version into a standard string.

    Args:
        name: Package name
        version_spec: Version specifier (e.g., ">=1.0.0", "==1.0.0")

    Returns:
        Formatted dependency string

    Example:
        >>> format_dependency("requests", ">=2.28.0")
        'requests>=2.28.0'

        >>> format_dependency("pandas")
        'pandas'
    """
    return f"{name}{version_spec}"
