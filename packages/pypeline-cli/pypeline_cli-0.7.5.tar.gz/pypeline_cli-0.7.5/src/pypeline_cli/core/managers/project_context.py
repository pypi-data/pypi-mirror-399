from pathlib import Path
import tomllib


class ProjectContext:
    """Discovers and provides project paths dynamically."""

    def __init__(self, start_dir: Path, init: bool = False):
        if not init:
            self.project_root = self._find_project_root(start_dir)

        else:
            self.project_root = start_dir

    def _find_project_root(self, start_path: Path) -> Path:
        """Walk up directory tree to find pypeline's pyproject.toml"""
        current = start_path
        while current != current.parent:
            toml_path = current / "pyproject.toml"
            if toml_path.exists() and self._is_pypeline_project(toml_path):
                return current
            current = current.parent
        raise RuntimeError(
            "Not in a pypeline project (no pyproject.toml with [tool.pypeline] found)"
        )

    def _is_pypeline_project(self, toml_path: Path) -> bool:
        """Check if pyproject.toml is a pypeline-managed project"""
        try:
            with open(toml_path, "rb") as f:
                data = tomllib.load(f)
            return "tool" in data and "pypeline" in data.get("tool", {})
        except Exception:
            # If we can't read/parse the toml, it's not a pypeline project
            return False

    @property
    def toml_path(self) -> Path:
        return self.project_root / "pyproject.toml"

    @property
    def import_folder(self) -> Path:
        return self.project_root / self.project_root.name

    @property
    def dependencies_path(self) -> Path:
        return self.project_root / "dependencies.py"

    @property
    def dependencies_template(self) -> Path:
        return (
            Path(__file__).parent.parent.parent
            / "templates"
            / "dependencies.py.template"
        )

    @property
    def licenses_path(self) -> Path:
        return self.project_root / "LICENSE"

    @property
    def pipelines_folder_path(self) -> Path:
        return self.import_folder / "pipelines"

    @property
    def schemas_folder_path(self) -> Path:
        return self.import_folder / "schemas"

    @property
    def integration_tests_folder_path(self) -> Path:
        return self.project_root / "tests"

    @property
    def project_utils_folder_path(self) -> Path:
        return self.import_folder / "utils"

    @property
    def columns_file(self) -> Path:
        return self.project_utils_folder_path / "columns.py"

    @property
    def databases_file(self) -> Path:
        return self.project_utils_folder_path / "databases.py"

    @property
    def date_parser_file(self) -> Path:
        return self.project_utils_folder_path / "date_parser.py"

    @property
    def decorators_file(self) -> Path:
        return self.project_utils_folder_path / "decorators.py"

    @property
    def etl_file(self) -> Path:
        return self.project_utils_folder_path / "etl.py"

    @property
    def logger_file(self) -> Path:
        return self.project_utils_folder_path / "logger.py"

    @property
    def snowflake_utils_file(self) -> Path:
        return self.project_utils_folder_path / "snowflake_utils.py"

    @property
    def tables_file(self) -> Path:
        return self.project_utils_folder_path / "tables.py"

    @property
    def basic_test_file(self) -> Path:
        return self.integration_tests_folder_path / "basic_test.py"

    @property
    def gitignore_file(self) -> Path:
        return self.project_root / ".gitignore"

    @property
    def init_readme_file(self) -> Path:
        return self.project_root / "README.md"

    @property
    def _init_file(self) -> Path:
        return self.import_folder / "__init__.py"

    @property
    def table_cache_file(self) -> Path:
        return self.project_utils_folder_path / "table_cache.py"
