import click
import tomllib
import tomli_w

from typing import List

from .project_context import ProjectContext
from ...config import DEFAULT_DEPENDENCIES
from ...utils.dependency_parser import parse_dependencies


class TOMLManager:
    def __init__(self, ctx: ProjectContext) -> None:
        self.toml_path = ctx.toml_path

    def create(
        self,
        name: str,
        author_name: str,
        author_email: str,
        description: str,
        license: str,
        use_git: bool = False,
    ):
        # Build system configuration depends on whether we're using git versioning
        if use_git:
            build_system = {
                "requires": ["hatchling", "hatch-vcs"],
                "build-backend": "hatchling.build",
            }
            project_version = {"dynamic": ["version"]}
            hatch_config = {
                "version": {
                    "source": "vcs",
                },
                "build": {
                    "hooks": {
                        "vcs": {
                            "version-file": f"{name}/_version.py",
                        },
                    },
                },
            }
        else:
            build_system = {
                "requires": ["hatchling"],
                "build-backend": "hatchling.build",
            }
            project_version = {"version": "0.1.0"}
            hatch_config = {}

        data = {
            "build-system": build_system,
            "project": {
                "name": name,
                **project_version,
                "authors": [{"name": author_name, "email": author_email}],
                "description": description,
                "readme": "README.md",
                "requires-python": ">=3.12,<3.14",
                "license": license,
                "dependencies": DEFAULT_DEPENDENCIES.copy(),
            },
            "tool": {
                "hatch": hatch_config,
                "ruff": {
                    "line-length": 88,
                    "target-version": "py39",
                    "format": {
                        "quote-style": "double",
                        "indent-style": "space",
                        "docstring-code-format": True,
                        "skip-magic-trailing-comma": False,
                        "line-ending": "auto",
                    },
                },
                "pytest": {
                    "ini_options": {
                        "testpaths": ["tests"],
                        "python_files": ["test_*.py"],
                        "python_classes": ["Test*"],
                        "python_functions": ["test_*"],
                        "addopts": [
                            "-v",
                            "--strict-markers",
                            "--cov=pypeline_cli",
                            "--cov-report=term-missing",
                            "--cov-report=html",
                        ],
                        "markers": [
                            "slow: marks tests as slow",
                            "integration: marks tests as integration tests",
                        ],
                    },
                },
                "pypeline": {"managed": True},
            },
        }

        click.echo(f"Writing to {self.toml_path}...")

        self.write(data)

        click.echo("Created toml file!")

    def read(self) -> dict:
        """Read and parse the pyproject.toml file."""
        if not self.toml_path.exists():
            raise FileNotFoundError(f"pyproject.toml not found at {self.toml_path}")

        with open(self.toml_path, "rb") as f:
            return tomllib.load(f)

    def write(self, data: dict) -> None:
        """Write data to pyproject.toml file."""
        with open(self.toml_path, "wb") as f:
            tomli_w.dump(data, f)

    def update_dependencies(self, key: str, updated_data: List[str] | None) -> None:
        data = self.read()
        existing_deps = data["project"]["dependencies"]

        if updated_data:
            # Parse new dependencies into structured format
            new_deps = parse_dependencies(updated_data)

            # Create a dict of existing deps by package name
            existing_dict = {dep.name: dep for dep in parse_dependencies(existing_deps)}

            # Update/add new dependencies
            for new_dep in new_deps:
                existing_dict[new_dep.name] = new_dep

            # Convert back to dependency strings
            from ...utils.dependency_parser import format_dependency

            data["project"]["dependencies"] = [
                format_dependency(dep.name, dep.version_spec)
                for dep in existing_dict.values()
            ]

            self.write(data)
            click.echo(f"Updated {len(new_deps)} dependencies")
