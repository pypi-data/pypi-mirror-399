from pathlib import Path
import click


def resolve_path(destination: str, action: str, name: str) -> Path:
    """
    Resolve and validate a destination path for project creation.

    Args:
        destination: Target directory path. Empty string or "." uses current directory.
        action: Description of the action for confirmation prompts (e.g., "creating project")
        name: Project/subdirectory name to append to destination

    Returns:
        Resolved Path object (destination/name)

    Raises:
        click.Abort: If user cancels confirmation prompt
        click.ClickException: If destination points to an existing file

    Examples:
        >>> resolve_path(
        ...     "", "creating project", "my_pkg"
        ... )  # Prompts, returns cwd/my_pkg
        >>> resolve_path(".", "creating project", "my_pkg")  # Returns cwd/my_pkg
        >>> resolve_path(
        ...     "/home/user/projects", "creating project", "my_pkg"
        ... )  # Returns /home/user/projects/my_pkg
    """
    current_dir = Path.cwd()

    # Handle empty destination with confirmation
    if not destination:
        if not click.confirm(
            f"Destination path not provided. Proceed with {action} in {current_dir}?",
            default=True,
        ):
            raise click.Abort()
        base_path = current_dir
    # Handle explicit current directory or custom path
    elif destination == ".":
        base_path = current_dir
    else:
        base_path = Path(destination)

    dest_path = base_path / name

    # Validate not pointing to an existing file
    if dest_path.exists() and dest_path.is_file():
        raise click.ClickException(f"{dest_path} is a file, not a directory")

    return dest_path
