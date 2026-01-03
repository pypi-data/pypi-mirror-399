import click

from pathlib import Path

from ..core.managers.project_context import ProjectContext
from ..core.managers.dependencies_manager import DependenciesManager
from ..core.managers.toml_manager import TOMLManager


@click.command
def sync_deps():
    """Sync dependencies from dependencies.py to pyproject.toml"""

    click.echo("🔄 Syncing dependencies...")

    # Find project root
    ctx = ProjectContext(start_dir=Path.cwd(), init=False)
    click.echo(f"📁 Project root: {ctx.project_root}")

    dependencies_manager = DependenciesManager(ctx=ctx)
    toml_manager = TOMLManager(ctx=ctx)

    # Read dependencies file
    click.echo(f"📖 Reading dependencies from: {ctx.dependencies_path}")
    dependencies = dependencies_manager.read_user_dependencies()

    if not dependencies:
        click.echo("⚠️  No dependencies found in dependencies.py")
        return

    click.echo(f"✓ Found {len(dependencies)} dependencies")

    # Write changes to toml
    toml_manager.update_dependencies(
        key="project.dependencies", updated_data=dependencies
    )

    click.echo(
        f"✅ Successfully synced {len(dependencies)} dependencies to pyproject.toml"
    )
    click.echo("\n📦 Dependencies:")
    for dep in dependencies:
        click.echo(f"  • {dep}")
