import click
from datetime import datetime
from string import Template

from pathlib import Path

from ...core.managers.project_context import ProjectContext
from ...config import LICENSES


class LicenseManager:
    def __init__(self, ctx: ProjectContext) -> None:
        self.license_path = ctx.licenses_path

    def create(
        self,
        name: str,
        author_name: str,
        author_email: str,
        description: str,
        license: str,
        company_name: str,
    ):
        license_template_path: Path = LICENSES[license]

        with open(license_template_path, "r") as template_file:
            template_content = template_file.read()

        substitutions = {
            "year": str(datetime.now().year),
            "author_name": author_name,
            "author_email": author_email,
            "company_name": company_name,
            "description": description,
            "name": name,
        }

        template = Template(template_content)
        license_text = template.safe_substitute(**substitutions)

        with open(self.license_path, "w") as f:
            f.write(license_text)

        click.echo(f"✓ Created {license} LICENSE file")
