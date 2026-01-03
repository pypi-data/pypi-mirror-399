"""
Create Pipeline Command

Generates a new pipeline folder structure in an existing pypeline project.
"""

import click
from pathlib import Path

from ..core.managers.project_context import ProjectContext
from ..core.managers.pipeline_manager import PipelineManager
from ..utils.valdators import validate_pipeline_name
from ..utils.name_converter import to_pascal_case


@click.command()
@click.option(
    "--name",
    prompt="Please enter the pipeline name",
    help="Name of the pipeline (alphanumeric, hyphens, and underscores allowed)",
)
def create_pipeline(name: str):
    """Create a new pipeline with folder structure in the current pypeline project"""

    click.echo("\n📦 Creating new pipeline...\n")

    # Validate and normalize pipeline name
    is_valid, result = validate_pipeline_name(name)

    if not is_valid:
        # result contains error message
        raise click.BadParameter(result, param_hint="'--name'")

    # result contains normalized name
    normalized_name = result
    class_name = to_pascal_case(normalized_name) + "Pipeline"

    # Find project root
    try:
        ctx = ProjectContext(start_dir=Path.cwd(), init=False)
    except RuntimeError as e:
        raise click.ClickException(str(e))

    # Verify pipelines folder exists
    if not ctx.pipelines_folder_path.exists():
        raise click.ClickException(
            f"Pipelines folder not found at {ctx.pipelines_folder_path}. "
            "Is this a valid pypeline project?"
        )

    # Create pipeline structure
    try:
        click.echo(f"✓ Creating pipeline structure for '{normalized_name}'...\n")
        pipeline_manager = PipelineManager(ctx=ctx)
        pipeline_folder = pipeline_manager.create(
            pipeline_name=normalized_name, class_name=class_name
        )

        click.echo(f"\n✅ Successfully created pipeline '{normalized_name}'!\n")
        click.echo("📂 Created structure:")
        click.echo(f"  • {pipeline_folder}/")
        click.echo(f"    ├── {normalized_name}_runner.py")
        click.echo(f"    ├── config.py")
        click.echo(f"    ├── README.md")
        click.echo(f"    ├── processors/")
        click.echo(f"    │   └── __init__.py")
        click.echo(f"    └── tests/")
        click.echo(f"        └── __init__.py")

        click.echo("\n📝 Next steps:")
        click.echo(f"  1. Review {pipeline_folder}/README.md")
        click.echo(f"  2. Add configuration to {pipeline_folder}/config.py")
        click.echo(
            f"  3. Create processors: pypeline create-processor --name <processor-name> --pipeline {normalized_name}"
        )
        click.echo(f"  4. Update {normalized_name}_runner.py to use your processors")

    except FileExistsError as e:
        raise click.ClickException(str(e))
    except Exception as e:
        raise click.ClickException(f"Failed to create pipeline: {str(e)}")
