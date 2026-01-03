import click

from ..utils.resolve_path import resolve_path
from ..core.create_project import create_project
from ..utils.valdators import validate_params
from ..core.managers.project_context import ProjectContext
from ..config import LICENSES


@click.command()
@click.option(
    "--destination",
    prompt="Please enter the destination path of new etl package root",
    help="Destination path of new etl package root.",
)
@click.option(
    "--name", prompt="Please enter the name of the project", help="Name of the project."
)
@click.option(
    "--author-name", prompt="Please enter your name", help="Name of the author."
)
@click.option(
    "--author-email", prompt="Please enter your email", help="Email of the author."
)
@click.option(
    "--description",
    prompt="Please enter a description of this project",
    help="Description of the project.",
)
@click.option(
    "--license",
    type=click.Choice(LICENSES.keys(), case_sensitive=False),
    prompt="Select license type",
    default="MIT",
    help="License type",
    show_choices=True,
)
@click.option(
    "--company-name",
    default="",
    prompt="[OPTIONAL] Please enter your company name",
    help="Company or organization name (optional, for license)",
)
@click.option(
    "--git/--no-git",
    default=False,
    help="Initialize a git repository (default: disabled)",
)
def init(
    destination: str,
    name: str,
    author_name: str,
    author_email: str,
    description: str,
    license: str,
    company_name: str,
    git: bool,
):
    """Create new ETL pipeline architecture"""

    click.echo("\n🚀 Initializing new pypeline project...\n")

    # Validate specific input params
    click.echo("✓ Validating inputs...")
    validate_params(name=name, author_email=author_email)

    path = resolve_path(destination=destination, action="creating project", name=name)

    click.echo(f"\n📁 Creating project '{name}' at: {path}")

    ctx = ProjectContext(path, init=True)

    if path:
        create_project(
            ctx=ctx,
            name=name,
            author_name=author_name,
            author_email=author_email,
            description=description,
            license=license,
            company_name=company_name,
            path=path,
            use_git=git,
        )

        click.echo(f"\n✅ Successfully created project '{name}'!")
        click.echo("\n📝 Project details:")
        click.echo(f"  • Name: {name}")
        click.echo(f"  • Author: {author_name} <{author_email}>")
        click.echo(f"  • Description: {description}")
        click.echo(f"  • License: {license}")
        click.echo("\n📂 Next steps:")
        click.echo(f"  1. cd {path}")
        click.echo("  2. pypeline install")
        click.echo("  3. source .venv/bin/activate  # macOS/Linux")
        click.echo("     .venv\\Scripts\\activate  # Windows")
