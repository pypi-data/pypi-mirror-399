import click
from typing import List
import shutil

from pathlib import Path

from .project_context import ProjectContext
from ...config import ScaffoldFile


class ScaffoldingManager:
    def __init__(self, ctx: ProjectContext) -> None:
        self.ctx = ctx

    def create_folder_scaffolding(self, paths: List[Path]):
        for path in paths:
            Path(path).mkdir(parents=False, exist_ok=False)
            # Create __init__.py in Python package folders
            if path.name in ["pipelines", "utils", "schemas"]:
                init_file = path / "__init__.py"
                init_file.touch()
                click.echo(f"Successfully created {init_file}")

    def create_files_from_templates(self, scaffold_files: List[ScaffoldFile]):
        for file in scaffold_files:
            self._create_file_from_template(file)

    def _create_file_from_template(self, scaffold_file: ScaffoldFile):
        destination = getattr(self.ctx, scaffold_file.destination_property)
        shutil.copy(scaffold_file.template_name, destination)
        click.echo(f"Successfully created {destination}")
