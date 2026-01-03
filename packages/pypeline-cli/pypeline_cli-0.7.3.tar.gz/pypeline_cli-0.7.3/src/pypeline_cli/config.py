from pathlib import Path
from dataclasses import dataclass

PATH_TO_LICENSES = Path(__file__).parent / "templates" / "licenses"
PATH_TO_INIT_TEMPLATES = Path(__file__).parent / "templates" / "init"

LICENSES = {
    "MIT": PATH_TO_LICENSES / "mit.txt",
    "Apache-2.0": PATH_TO_LICENSES / "apache_license_2_0.txt",
    "GPL-3.0": PATH_TO_LICENSES / "gnu_general_public_license_v3_0.txt",
    "GPL-2.0": PATH_TO_LICENSES / "gnu_general_public_license_v2_0.txt",
    "LGPL-2.1": PATH_TO_LICENSES / "gnu_lesser_general_public_license_v2_1.txt",
    "BSD-2-Clause": PATH_TO_LICENSES / "bsd_2_clause_license.txt",
    "BSD-3-Clause": PATH_TO_LICENSES / "bsd_3_clause_license.txt",
    "BSL-1.0": PATH_TO_LICENSES / "boost_software_license_1_0.txt",
    "CC0-1.0": PATH_TO_LICENSES / "creative_commons_zero_v1_0_universal.txt",
    "EPL-2.0": PATH_TO_LICENSES / "eclipse_public_license_2_0.txt",
    "AGPL-3.0": PATH_TO_LICENSES / "gnu_affero_general_public_license_v3_0.txt",
    "MPL-2.0": PATH_TO_LICENSES / "mozilla_public_license_2_0.txt",
    "Unlicense": PATH_TO_LICENSES / "the_unlicense.txt",
    "Proprietary": PATH_TO_LICENSES / "proprietary.txt",
}

# Default dependencies for new projects
DEFAULT_DEPENDENCIES = [
    "snowflake-snowpark-python>=1.42.0",
    "numpy>=2.2.6",
    "pandas>=2.3.3",
    "build==1.3.0",
    "twine==6.2.0",
    "ruff==0.14.9",
    "pre-commit==4.5.1",
    "pytest==9.0.2",
    "pytest-cov==7.0.0",
    "pytest-asyncio==1.3.0",
]


@dataclass
class ScaffoldFile:
    """Configuration for a single scaffold file."""

    template_name: Path
    destination_property: str


INIT_SCAFFOLD_FILES = [
    ScaffoldFile(
        template_name=PATH_TO_INIT_TEMPLATES / "columns.py.template",
        destination_property="columns_file",
    ),
    ScaffoldFile(
        template_name=PATH_TO_INIT_TEMPLATES / "databases.py.template",
        destination_property="databases_file",
    ),
    ScaffoldFile(
        template_name=PATH_TO_INIT_TEMPLATES / "date_parser.py.template",
        destination_property="date_parser_file",
    ),
    ScaffoldFile(
        template_name=PATH_TO_INIT_TEMPLATES / "tables.py.template",
        destination_property="tables_file",
    ),
    ScaffoldFile(
        template_name=PATH_TO_INIT_TEMPLATES / "etl.py.template",
        destination_property="etl_file",
    ),
    ScaffoldFile(
        template_name=PATH_TO_INIT_TEMPLATES / "logger.py.template",
        destination_property="logger_file",
    ),
    ScaffoldFile(
        template_name=PATH_TO_INIT_TEMPLATES / "decorators.py.template",
        destination_property="decorators_file",
    ),
    ScaffoldFile(
        template_name=PATH_TO_INIT_TEMPLATES / "snowflake_utils.py.template",
        destination_property="snowflake_utils_file",
    ),
    ScaffoldFile(
        template_name=PATH_TO_INIT_TEMPLATES / "basic_test.py.template",
        destination_property="basic_test_file",
    ),
    ScaffoldFile(
        template_name=PATH_TO_INIT_TEMPLATES / ".gitignore.template",
        destination_property="gitignore_file",
    ),
    ScaffoldFile(
        template_name=PATH_TO_INIT_TEMPLATES / "README.md.template",
        destination_property="init_readme_file",
    ),
    ScaffoldFile(
        template_name=PATH_TO_INIT_TEMPLATES / "_init.py.template",
        destination_property="_init_file",
    ),
    ScaffoldFile(
        template_name=PATH_TO_INIT_TEMPLATES / "table_cache.py.template",
        destination_property="table_cache_file",
    ),
]
