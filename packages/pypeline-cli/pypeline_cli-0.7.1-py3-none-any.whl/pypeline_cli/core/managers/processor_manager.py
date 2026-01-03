"""
Processor Manager

Handles creation of processor classes and test files within pipeline structures.
"""

import click
from pathlib import Path
from string import Template

from .project_context import ProjectContext


class ProcessorManager:
    """
    Manages processor file and test creation from templates.

    Similar to PipelineManager, uses string.Template for variable substitution.
    Handles auto-registration of processor imports in pipeline runner files.
    """

    def __init__(self, ctx: ProjectContext) -> None:
        """
        Initialize ProcessorManager.

        Args:
            ctx: Project context with path information
        """
        self.ctx = ctx
        self.templates_path = (
            Path(__file__).parent.parent.parent / "templates" / "processors"
        )

    def create(
        self, processor_name: str, class_name: str, pipeline_name: str
    ) -> tuple[Path, Path]:
        """
        Create a new processor class with test file.

        Args:
            processor_name: Normalized processor name (e.g., "msp")
            class_name: PascalCase class name (e.g., "MSPProcessor")
            pipeline_name: Normalized pipeline name (e.g., "beneficiary_claims")

        Returns:
            Tuple of (processor_file_path, test_file_path)

        Raises:
            FileExistsError: If processor file already exists
            RuntimeError: If template files not found or pipeline doesn't exist
        """
        # 1. Validate pipeline exists
        pipeline_folder = self.ctx.pipelines_folder_path / pipeline_name
        if not pipeline_folder.exists():
            raise RuntimeError(
                f"Pipeline '{pipeline_name}' not found at {pipeline_folder}"
            )

        processors_folder = pipeline_folder / "processors"
        if not processors_folder.exists():
            raise RuntimeError(
                f"Processors folder not found at {processors_folder}. "
                "Is this a valid pypeline pipeline?"
            )

        # 2. Create tests subdirectory if it doesn't exist
        tests_folder = processors_folder / "tests"
        tests_folder.mkdir(exist_ok=True)

        # Create __init__.py in tests folder if it doesn't exist
        tests_init = tests_folder / "__init__.py"
        if not tests_init.exists():
            tests_init.write_text('"""Unit tests for processors."""\n')

        # 3. Prepare substitutions for templates
        substitutions = {
            "class_name": class_name,
            "processor_name": processor_name,
            "pipeline_name": pipeline_name,
            "project_name": self.ctx.project_root.name,
        }

        # 4. Create processor file from template
        processor_file = processors_folder / f"{processor_name}_processor.py"
        self._create_from_template(
            "processor.py.template", processor_file, substitutions
        )

        # 5. Create test file from template
        test_file = tests_folder / f"test_{processor_name}_processor.py"
        self._create_from_template(
            "test_processor.py.template", test_file, substitutions
        )

        # 6. Register processor import in runner file
        runner_file = pipeline_folder / f"{pipeline_name}_runner.py"
        self._register_processor_import(runner_file, processor_name, class_name)

        return processor_file, test_file

    def _create_from_template(
        self, template_name: str, destination: Path, substitutions: dict
    ):
        """
        Create file from template with variable substitution.

        Args:
            template_name: Name of template file in templates/processors/
            destination: Full path to destination file
            substitutions: Dictionary of template variables

        Raises:
            RuntimeError: If template file not found
        """
        template_path = self.templates_path / template_name

        # Verify template exists
        if not template_path.exists():
            raise RuntimeError(f"Processor template not found at {template_path}")

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

    def _register_processor_import(
        self, runner_file: Path, processor_name: str, class_name: str
    ):
        """
        Register processor import in pipeline runner file.

        Adds an import statement in the imports section:
            from .processors.msp_processor import MSPProcessor

        Args:
            runner_file: Path to pipeline runner file
            processor_name: Normalized processor name (e.g., "msp")
            class_name: PascalCase class name (e.g., "MSPProcessor")

        Raises:
            RuntimeError: If runner file doesn't exist
        """
        if not runner_file.exists():
            raise RuntimeError(f"Runner file not found at {runner_file}")

        # Read existing content
        with open(runner_file, "r") as f:
            content = f.read()

        # Create import statement
        import_statement = (
            f"from .processors.{processor_name}_processor import {class_name}"
        )

        # Check if import already exists
        if import_statement in content:
            click.echo(f"  ✓ Import for {class_name} already exists in runner")
            return

        lines = content.splitlines(keepends=True)

        # Skip past module docstring
        i = 0
        in_docstring = False
        docstring_char = None

        # Skip shebang and encoding declarations if present
        while i < len(lines) and (lines[i].startswith("#") or not lines[i].strip()):
            i += 1

        # Check for docstring (""" or ''')
        if i < len(lines):
            stripped = lines[i].strip()
            if stripped.startswith('"""') or stripped.startswith("'''"):
                docstring_char = stripped[:3]
                # Check if it's a single-line docstring
                if stripped.endswith(docstring_char) and len(stripped) > 6:
                    i += 1
                else:
                    # Multi-line docstring
                    in_docstring = True
                    i += 1
                    while i < len(lines) and in_docstring:
                        if docstring_char in lines[i]:
                            in_docstring = False
                        i += 1

        # Skip blank lines after docstring
        while i < len(lines) and not lines[i].strip():
            i += 1

        # Now find the right place in the import section
        import_insert_index = i
        last_processor_import_index = None
        last_import_index = None

        for idx in range(i, len(lines)):
            line = lines[idx].strip()

            # Stop when we hit non-import content (class, def, etc.)
            if line and not line.startswith(("from", "import", "#")):
                break

            # Track imports
            if line.startswith("from") or line.startswith("import"):
                last_import_index = idx

                # Specifically track processor imports
                if line.startswith("from .processors."):
                    last_processor_import_index = idx

        # Insert after last processor import, or after last import, or at start of import section
        if last_processor_import_index is not None:
            import_insert_index = last_processor_import_index + 1
        elif last_import_index is not None:
            import_insert_index = last_import_index + 1

        # Insert the import
        lines.insert(import_insert_index, import_statement + "\n")

        # Write back
        with open(runner_file, "w") as f:
            f.writelines(lines)

        click.echo(f"  ✓ Registered {class_name} import in runner file")
