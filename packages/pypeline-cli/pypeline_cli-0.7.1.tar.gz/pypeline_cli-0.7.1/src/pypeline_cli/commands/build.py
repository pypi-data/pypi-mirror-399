import click
import shutil
import zipfile

from pathlib import Path

from ..core.managers.project_context import ProjectContext


@click.command()
def build():
    """Create Snowflake-compatible ZIP with package at root and pyproject.toml"""

    click.echo("\n🚀 Building Snowflake distribution...\n")

    # Find project root
    ctx = ProjectContext(start_dir=Path.cwd(), init=False)
    click.echo(f"📁 Project root: {ctx.project_root}")

    # Read project name and version from pyproject.toml
    import tomllib

    with open(ctx.toml_path, "rb") as f:
        toml_data = tomllib.load(f)

    project_name = toml_data["project"]["name"]
    version = toml_data["project"].get("version", "0.0.0")
    package_name = project_name.replace("-", "_")

    # Find the package directory
    package_dir = ctx.project_root / package_name

    if not package_dir.exists():
        click.echo(f"❌ Package directory not found: {package_dir}")
        return

    dist = ctx.project_root / "dist"
    snowflake_dir = dist / "snowflake"

    # Clean and create dist directories with retry for Windows
    if snowflake_dir.exists():
        click.echo("🧹 Cleaning dist/snowflake folder...")
        import time

        max_retries = 3
        for attempt in range(max_retries):
            try:
                shutil.rmtree(snowflake_dir)
                break
            except PermissionError:
                if attempt < max_retries - 1:
                    click.echo(
                        f"   ⚠️  Retrying... (attempt {attempt + 1}/{max_retries})"
                    )
                    time.sleep(1)
                else:
                    click.echo(
                        "\n❌ Failed to clean folder. Close any open programs and try again."
                    )
                    return

    snowflake_dir.mkdir(parents=True, exist_ok=True)

    # Create ZIP filename
    zip_filename = f"{project_name}-{version}.zip"
    zip_path = snowflake_dir / zip_filename

    click.echo(f"\n📦 Creating Snowflake ZIP: {zip_filename}")
    click.echo(f"   Package '{package_name}' will be at root level\n")

    # Files and directories to exclude
    exclude_patterns = {
        "__pycache__",
        ".pytest_cache",
        ".ruff_cache",
        "*.pyc",
        "*.pyo",
        "*.pyd",
        ".DS_Store",
    }

    def should_exclude(path: Path) -> bool:
        """Check if path should be excluded from ZIP."""
        for part in path.parts:
            if part in exclude_patterns:
                return True
        if path.suffix in [".pyc", ".pyo", ".pyd"]:
            return True
        if path.name == ".DS_Store":
            return True
        return False

    # Create ZIP with proper structure
    file_count = 0
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        # 1. Add pyproject.toml at root (REQUIRED by Snowflake)
        zipf.write(ctx.toml_path, "pyproject.toml")
        click.echo("   ✓ pyproject.toml")
        file_count += 1

        # 2. Add the package directory at root
        for item in package_dir.rglob("*"):
            if item.is_file() and not should_exclude(item):
                # Make path relative to project_root so package is at root
                arcname = item.relative_to(ctx.project_root)
                zipf.write(item, arcname)
                file_count += 1

                if file_count <= 15:
                    click.echo(f"   ✓ {arcname}")

    if file_count > 15:
        click.echo(f"   ... and {file_count - 15} more files")

    # Show ZIP info
    zip_size_kb = zip_path.stat().st_size / 1024
    click.echo("\n📊 Snowflake distribution:")
    click.echo(f"   • snowflake/{zip_filename:<40} {zip_size_kb:>7.1f} KB")
    click.echo(f"   • Total files: {file_count}")

    # Verify structure
    with zipfile.ZipFile(zip_path, "r") as zipf:
        namelist = zipf.namelist()

        # Check for pyproject.toml at root
        if "pyproject.toml" in namelist:
            click.echo("\n✅ Verified: pyproject.toml at root")
        else:
            click.echo("\n❌ ERROR: pyproject.toml missing")
            return

        # Check package is at root
        package_init = f"{package_name}/__init__.py"
        if package_init in namelist:
            click.echo(f"✅ Verified: {package_name}/ at root level (importable)")
        else:
            click.echo(f"❌ ERROR: {package_init} not at root")
            click.echo(f"   First 10 files: {namelist[:10]}")
            return

    click.echo("\n✅ Build complete!")
    click.echo("\n💡 Upload to Snowflake:")
    click.echo(
        f"   PUT file://{zip_path.relative_to(ctx.project_root)} @your_stage AUTO_COMPRESS=FALSE OVERWRITE=TRUE"
    )
    click.echo("\n💡 Import in Snowflake:")
    click.echo(f"   from {package_name} import BeneficiaryPipeline")
