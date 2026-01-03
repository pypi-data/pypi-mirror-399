"""
Pipeline Manager

Handles creation of pipeline runner files and folder structures from templates.
"""

import click
from pathlib import Path
from string import Template

from .project_context import ProjectContext


class PipelineManager:
    """
    Manages pipeline folder and file creation from templates.

    Similar to LicenseManager, uses string.Template for variable substitution.
    """

    def __init__(self, ctx: ProjectContext) -> None:
        """
        Initialize PipelineManager.

        Args:
            ctx: Project context with path information
        """
        self.ctx = ctx
        self.templates_path = (
            Path(__file__).parent.parent.parent / "templates" / "pipelines"
        )

    def create(self, pipeline_name: str, class_name: str) -> Path:
        """
        Create a new pipeline folder structure with all files from templates.

        Args:
            pipeline_name: Normalized pipeline name (e.g., "beneficiary_claims")
            class_name: PascalCase class name (e.g., "BeneficiaryClaims")

        Returns:
            Path to created pipeline folder

        Raises:
            FileExistsError: If pipeline folder already exists
            RuntimeError: If template files not found
        """
        # 1. Create pipeline folder
        pipeline_folder = self.ctx.pipelines_folder_path / pipeline_name
        if pipeline_folder.exists():
            raise FileExistsError(
                f"Pipeline '{pipeline_name}' already exists at {pipeline_folder}"
            )

        pipeline_folder.mkdir(parents=False, exist_ok=False)

        # Create __init__.py in pipeline folder
        pipeline_init = pipeline_folder / "__init__.py"
        pipeline_init.touch()
        click.echo("  ✓ Created __init__.py")

        # 2. Create subfolders
        processors_folder = pipeline_folder / "processors"
        tests_folder = pipeline_folder / "tests"
        processors_folder.mkdir()
        tests_folder.mkdir()

        # 3. Prepare substitutions for templates
        substitutions = {
            "class_name": class_name,
            "pipeline_name": pipeline_name,
            "project_name": self.ctx.project_root.name,
        }

        # 4. Create files from templates
        self._create_from_template(
            "runner.py.template",
            pipeline_folder / f"{pipeline_name}_runner.py",
            substitutions,
        )
        self._create_from_template(
            "config.py.template", pipeline_folder / "config.py", substitutions
        )
        self._create_from_template(
            "README.md.template", pipeline_folder / "README.md", substitutions
        )
        self._create_from_template(
            "processors_init.py.template",
            processors_folder / "__init__.py",
            substitutions,
        )
        self._create_from_template(
            "tests_init.py.template", tests_folder / "__init__.py", substitutions
        )

        # 5. Register pipeline in package __init__.py for top-level import
        self._register_pipeline_import(pipeline_name, class_name)

        return pipeline_folder

    def _create_from_template(
        self, template_name: str, destination: Path, substitutions: dict
    ):
        """
        Create file from template with variable substitution.

        Args:
            template_name: Name of template file in templates/pipelines/
            destination: Full path to destination file
            substitutions: Dictionary of template variables

        Raises:
            RuntimeError: If template file not found
        """
        template_path = self.templates_path / template_name

        # Verify template exists
        if not template_path.exists():
            raise RuntimeError(f"Pipeline template not found at {template_path}")

        # Read template content
        with open(template_path, "r") as f:
            template_content = f.read()

        # Perform variable substitution
        template = Template(template_content)
        final_content = template.safe_substitute(**substitutions)

        # Write to destination
        with open(destination, "w") as f:
            f.write(final_content)

        click.echo(f"  ✓ Created {destination.name}")

    def _register_pipeline_import(self, pipeline_name: str, class_name: str):
        """
        Register pipeline class in package __init__.py for top-level imports.

        Adds an import statement like:
            from .pipelines.beneficiary_claims.beneficiary_claims_runner import BeneficiaryClaims

        And adds to __all__ for explicit exports:
            __all__ = ["BeneficiaryClaims", ...]

        This allows users to import pipelines as:
            from project_name import BeneficiaryClaims

        Args:
            pipeline_name: Normalized pipeline name (e.g., "beneficiary_claims")
            class_name: PascalCase class name (e.g., "BeneficiaryClaims")
        """
        init_file = self.ctx._init_file

        # Read existing content
        if init_file.exists():
            with open(init_file, "r") as f:
                content = f.read()
        else:
            content = ""

        # Create import statement
        import_statement = (
            f"from .pipelines.{pipeline_name}.{pipeline_name}_runner "
            f"import {class_name}\n"
        )

        # Check if import already exists
        if import_statement.strip() in content:
            return

        lines = content.splitlines(keepends=True)

        # Find where to insert import and track __all__ location
        import_insert_index = 0
        all_line_index = None

        for i, line in enumerate(lines):
            if line.startswith("from .pipelines."):
                import_insert_index = i + 1
            elif line.strip().startswith("__all__"):
                all_line_index = i

        # If no pipeline imports found, add at the beginning
        if import_insert_index == 0:
            if lines and not lines[0].startswith("#"):
                # Add blank line before first pipeline import if file has content
                import_statement = "\n" + import_statement
            import_insert_index = 0

        # Insert the import
        lines.insert(import_insert_index, import_statement)

        # Update or create __all__
        if all_line_index is not None:
            # __all__ exists, update it
            # Adjust index if we inserted before __all__
            if import_insert_index <= all_line_index:
                all_line_index += 1

            all_line = lines[all_line_index]
            # Parse existing __all__ and add new class
            if class_name not in all_line:
                # Simple approach: add before the closing bracket
                all_line = all_line.rstrip()
                if all_line.endswith("]"):
                    if '["' in all_line or "['" in all_line:
                        # Has existing items
                        all_line = all_line[:-1] + f', "{class_name}"]\n'
                    else:
                        # Empty list
                        all_line = all_line[:-1] + f'"{class_name}"]\n'
                lines[all_line_index] = all_line
        else:
            # Create __all__ after imports
            all_statement = f'\n__all__ = ["{class_name}"]\n'
            # Insert after the last import we just added
            lines.insert(import_insert_index + 1, all_statement)

        # Write back
        with open(init_file, "w") as f:
            f.writelines(lines)

        click.echo(f"  ✓ Registered {class_name} in package __init__.py")
