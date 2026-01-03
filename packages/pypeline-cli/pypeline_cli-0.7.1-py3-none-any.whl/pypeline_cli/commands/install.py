from pathlib import Path
import subprocess
import platform

import click

from ..core.managers.project_context import ProjectContext


@click.command()
def install():
    """Create .venv if it doesn't exist. Install deps from pyproject.toml"""
    # Verify in pypeline project
    ctx = ProjectContext(start_dir=Path.cwd(), init=False)

    venv_path = ctx.project_root / ".venv"

    # Check if venv already exists
    if venv_path.exists():
        click.echo(f"✓ Virtual environment already exists at {venv_path}")
    else:
        click.echo("📦 Creating virtual environment...")
        # Try to use Python 3.12-3.13 (required by generated projects, compatible with Snowflake)
        python_cmd = None
        for cmd in ["python3.13", "python3.12", "python3", "python"]:
            try:
                result = subprocess.run(
                    [cmd, "--version"],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                # Extract version from output like "Python 3.12.0"
                version_str = result.stdout.strip().split()[1]
                major, minor = map(int, version_str.split(".")[:2])
                # Accept Python 3.12 or 3.13 (Snowflake compatibility)
                if major == 3 and 12 <= minor <= 13:
                    python_cmd = cmd
                    break
            except (subprocess.CalledProcessError, FileNotFoundError, IndexError, ValueError):
                continue

        if not python_cmd:
            raise click.ClickException(
                "Could not find Python 3.12 or 3.13. Please install Python 3.12 or 3.13 and try again.\n"
                "Note: Python 3.14+ is not yet supported by snowflake-snowpark-python."
            )

        click.echo(f"Using {python_cmd} to create virtual environment...")
        subprocess.run(
            [python_cmd, "-m", "venv", ".venv"], cwd=ctx.project_root, check=True
        )
        click.echo(f"✓ Created virtual environment at {venv_path}")

    # Determine Python executable path based on OS
    if platform.system() == "Windows":
        python_exe = venv_path / "Scripts" / "python.exe"
    else:
        python_exe = venv_path / "bin" / "python"

    if not python_exe.exists():
        raise click.ClickException(f"Python executable not found at {python_exe}")

    # Upgrade pip to latest version (required for modern editable installs)
    # Use 'python -m pip' instead of calling pip directly (Windows compatibility)
    click.echo("\n🔄 Upgrading pip to latest version...\n")
    upgrade_result = subprocess.run(
        [str(python_exe), "-m", "pip", "install", "--upgrade", "pip"],
        cwd=ctx.project_root,
    )

    if upgrade_result.returncode != 0:
        click.echo("\n⚠️  Warning: Failed to upgrade pip")
        raise click.ClickException("Failed to upgrade pip")

    click.echo("\n✓ pip upgraded successfully")

    # Install project in editable mode using 'python -m pip' (Windows compatibility)
    click.echo("\n🔧 Installing project dependencies...\n")
    result = subprocess.run(
        [str(python_exe), "-m", "pip", "install", "-e", "."],
        cwd=ctx.project_root,
    )

    if result.returncode != 0:
        click.echo("\n❌ Installation failed")
        raise click.ClickException("Failed to install dependencies")

    click.echo("✅ Successfully installed dependencies!")
    click.echo("\n📂 Next steps:")
    click.echo("  Activate the virtual environment:")
    if platform.system() == "Windows":
        click.echo("    .venv\\Scripts\\activate")
    else:
        click.echo("    source .venv/bin/activate")
