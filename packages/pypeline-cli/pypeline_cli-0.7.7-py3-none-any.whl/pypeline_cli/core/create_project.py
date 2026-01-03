from pathlib import Path

from .managers.project_context import ProjectContext
from .managers.toml_manager import TOMLManager
from .managers.dependencies_manager import DependenciesManager
from .managers.license_manager import LicenseManager
from .managers.scaffolding_manager import ScaffoldingManager
from .managers.git_manager import create_git_repo
from ..config import INIT_SCAFFOLD_FILES


def create_project(
    ctx: ProjectContext,
    name: str,
    author_name: str,
    author_email: str,
    description: str,
    license: str,
    company_name: str,
    path: Path,
    use_git: bool = False,
):
    # Create the project root
    Path.mkdir(path, parents=False, exist_ok=False)

    if use_git:
        create_git_repo(path)

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

    # Create TOML file
    toml_manager = TOMLManager(
        ctx=ctx,
    )

    toml_manager.create(
        name=name,
        author_name=author_name,
        author_email=author_email,
        description=description,
        license=license,
        use_git=use_git,
    )

    dependencies_manager = DependenciesManager(ctx=ctx)
    dependencies_manager.create()

    # Create license
    license_manager = LicenseManager(ctx=ctx)
    license_manager.create(
        name=name,
        author_name=author_name,
        author_email=author_email,
        description=description,
        license=license,
        company_name=company_name,
    )

    # Create initializer scaffolds
    scaffolding_manager = ScaffoldingManager(ctx=ctx)
    scaffolding_manager.create_folder_scaffolding(
        [
            ctx.import_folder,
            ctx.pipelines_folder_path,
            ctx.schemas_folder_path,
            ctx.integration_tests_folder_path,
            ctx.project_utils_folder_path,
        ]
    )

    scaffolding_manager.create_files_from_templates(scaffold_files=INIT_SCAFFOLD_FILES)
