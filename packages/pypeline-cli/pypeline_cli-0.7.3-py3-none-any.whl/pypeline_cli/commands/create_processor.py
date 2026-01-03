"""
Create Processor Command

Generates a new processor class within an existing pipeline.
"""

import click
from pathlib import Path

from ..core.managers.project_context import ProjectContext
from ..core.managers.processor_manager import ProcessorManager
from ..utils.valdators import validate_pipeline_name, validate_processor_name
from ..utils.name_converter import to_pascal_case


@click.command()
@click.option(
    "--name",
    prompt="Please enter the processor name",
    help="Name of the processor (alphanumeric, hyphens, and underscores allowed)",
)
@click.option(
    "--pipeline",
    prompt="Please enter the pipeline name",
    help="Name of the pipeline where this processor will be created",
)
def create_processor(name: str, pipeline: str):
    """Create a new processor class within an existing pipeline"""

    click.echo("\n🔧 Creating new processor...\n")

    # 1. Find project root
    try:
        ctx = ProjectContext(start_dir=Path.cwd(), init=False)
    except RuntimeError as e:
        raise click.ClickException(str(e))

    # 2. Validate and normalize pipeline name
    is_valid, pipeline_result = validate_pipeline_name(pipeline)
    if not is_valid:
        raise click.BadParameter(pipeline_result, param_hint="'--pipeline'")

    normalized_pipeline_name = pipeline_result

    # 3. Validate pipeline exists
    pipeline_path = ctx.pipelines_folder_path / normalized_pipeline_name
    if not pipeline_path.exists():
        raise click.ClickException(
            f"Pipeline '{normalized_pipeline_name}' does not exist at {pipeline_path}. "
            f"Run 'pypeline create-pipeline --name {normalized_pipeline_name}' first."
        )

    # 4. Validate and normalize processor name
    is_valid, processor_result = validate_processor_name(name)
    if not is_valid:
        raise click.BadParameter(processor_result, param_hint="'--name'")

    normalized_processor_name = processor_result
    class_name = to_pascal_case(normalized_processor_name) + "Processor"

    # 5. Check if processor already exists
    processor_path = (
        pipeline_path / "processors" / f"{normalized_processor_name}_processor.py"
    )
    if processor_path.exists():
        raise click.ClickException(
            f"Processor '{normalized_processor_name}' already exists in pipeline "
            f"'{normalized_pipeline_name}' at {processor_path}"
        )

    # 6. Create processor structure
    try:
        click.echo(
            f"✓ Creating processor '{normalized_processor_name}' in pipeline '{normalized_pipeline_name}'...\n"
        )
        processor_manager = ProcessorManager(ctx=ctx)
        processor_file, test_file = processor_manager.create(
            processor_name=normalized_processor_name,
            class_name=class_name,
            pipeline_name=normalized_pipeline_name,
        )

        click.echo(
            f"\n✅ Successfully created processor '{normalized_processor_name}'!\n"
        )
        click.echo("📂 Created files:")
        click.echo(f"  • {processor_file.relative_to(ctx.project_root)}")
        click.echo(f"  • {test_file.relative_to(ctx.project_root)}")

        runner_file = pipeline_path / f"{normalized_pipeline_name}_runner.py"
        click.echo("\n📝 Auto-registered in:")
        click.echo(f"  • {runner_file.relative_to(ctx.project_root)}")

        click.echo("\n📝 Next steps:")
        click.echo(f"  1. Implement data extraction in {class_name}.__init__()")
        click.echo(f"  2. Add transformation logic in {class_name}.process()")
        click.echo(f"  3. Write unit tests in {test_file.name}")
        click.echo(
            f"  4. Update {normalized_pipeline_name}_runner.py to instantiate and use {class_name}"
        )

    except Exception as e:
        raise click.ClickException(f"Failed to create processor: {str(e)}")
