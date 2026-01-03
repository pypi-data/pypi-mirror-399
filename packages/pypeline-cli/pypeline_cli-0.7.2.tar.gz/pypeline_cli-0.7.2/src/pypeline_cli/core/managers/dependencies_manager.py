import click
import shutil

import ast
from typing import List

from .project_context import ProjectContext


class DependenciesManager:
    def __init__(self, ctx: ProjectContext) -> None:
        self.dependencies_path = ctx.dependencies_path
        self.dependencies_template = ctx.dependencies_template

    def create(self):
        shutil.copy(self.dependencies_template, self.dependencies_path)
        click.echo(f"Created the dependecies file at {self.dependencies_path}")

    def read_user_dependencies(self) -> List[str] | None:
        """
        Read USER_DEPENDENCIES from the user's dependencies.py file.

        Args:
            file_path: Path to the dependencies.py file

        Returns:
            List of dependency strings

        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If USER_DEPENDENCIES is not found or invalid
        """
        path = self.dependencies_path

        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        # Read and parse the file
        with open(path, "r") as f:
            content = f.read()

        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            raise ValueError(f"Invalid Python syntax in {path}: {e}")

        # Find USER_DEPENDENCIES
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if (
                        isinstance(target, ast.Name)
                        and target.id == "USER_DEPENDENCIES"
                    ):
                        if isinstance(node.value, ast.List):
                            dependencies = []
                            for element in node.value.elts:
                                if isinstance(element, ast.Constant):
                                    dependencies.append(element.value)
                                else:
                                    print(
                                        "Warning: Skipping non-string element in USER_DEPENDENCIES"
                                    )
                            return dependencies
                        else:
                            raise ValueError("USER_DEPENDENCIES must be a list")

        raise ValueError("USER_DEPENDENCIES not found in file")
