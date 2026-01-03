"""Build wheel, sdist, and Snowflake-compatible ZIP."""

import shutil
import subprocess
import sys
from pathlib import Path


def main():
    """Build all distribution formats."""
    dist = Path("dist")
    snowflake_dir = dist / "snowflake"

    # Clean the dist folder
    if dist.exists():
        for item in dist.iterdir():
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)

    # Create snowflake directory
    snowflake_dir.mkdir(parents=True, exist_ok=True)

    # Build wheel and sdist
    print("🔨 Building distributions...")
    result = subprocess.run(["python", "-m", "build"], check=False)

    if result.returncode != 0:
        print("❌ Build failed")
        sys.exit(1)

    # Create Snowflake ZIPs from wheels
    print("\n📦 Creating Snowflake-compatible ZIPs...")

    zip_count = 0
    for whl in dist.glob("*.whl"):
        zip_file = snowflake_dir / whl.with_suffix(".zip").name
        shutil.copy(whl, zip_file)
        print(f"  ✅ snowflake/{zip_file.name}")
        zip_count += 1

    if zip_count == 0:
        print("  ⚠️  No wheel files found")

    # Show all distributions
    print("\n📊 Distribution files:")
    print("\n  PyPI distributions:")
    for file in sorted(dist.glob("pypeline_cli-*.whl")):
        size_kb = file.stat().st_size / 1024
        print(f"    • {file.name:<48} {size_kb:>7.1f} KB")

    for file in sorted(dist.glob("pypeline_cli-*.tar.gz")):
        size_kb = file.stat().st_size / 1024
        print(f"    • {file.name:<48} {size_kb:>7.1f} KB")

    print("\n  Snowflake distributions:")
    for file in sorted(snowflake_dir.glob("*.zip")):
        size_kb = file.stat().st_size / 1024
        print(f"    • snowflake/{file.name:<40} {size_kb:>7.1f} KB")

    print("\n✅ Build complete!")


if __name__ == "__main__":
    main()
