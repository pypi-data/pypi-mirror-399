import subprocess
import click

from pathlib import Path


def create_git_repo(path: Path):
    """
    Initialize a git repository with proper configuration and initial commit.

    Args:
        path: Path to the project directory

    Raises:
        click.ClickException: If git initialization fails
    """
    try:
        click.echo("\n🔧 Initializing git repository...")

        # Initialize git repository
        subprocess.run(["git", "init"], cwd=path, check=True, capture_output=True)
        click.echo("✓ Git initialized")

        # Configure line endings (prevents CRLF warnings on Windows)
        subprocess.run(
            ["git", "config", "core.autocrlf", "input"], cwd=path, check=True
        )

        # Create .gitattributes for consistent line endings
        gitattributes_content = """# Ensure line endings are consistent
* text=auto
*.py text eol=lf
*.toml text eol=lf
*.txt text eol=lf
*.md text eol=lf
*.yaml text eol=lf
*.yml text eol=lf
"""
        (path / ".gitattributes").write_text(gitattributes_content.strip())

        # Stage all files
        subprocess.run(["git", "add", "."], cwd=path, check=True, capture_output=True)
        click.echo("✓ Files staged")

        # Create initial commit
        subprocess.run(
            ["git", "commit", "-m", "Initial commit from pypeline init"],
            cwd=path,
            check=True,
            capture_output=True,
        )
        click.echo("✓ Initial commit created")

        # Verify commit exists (for debugging)
        result = subprocess.run(
            ["git", "log", "--oneline", "-1"],
            cwd=path,
            capture_output=True,
            text=True,
            check=True,
        )
        click.echo(f"✓ Git repository ready: {result.stdout.strip()}")

    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.decode() if e.stderr else str(e)
        click.echo(f"\n⚠️  Git initialization failed: {error_msg}")
        raise click.ClickException("Failed to initialize git repository")
