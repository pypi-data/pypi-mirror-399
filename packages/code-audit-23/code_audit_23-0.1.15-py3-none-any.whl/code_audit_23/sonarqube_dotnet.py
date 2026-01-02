import shutil
import subprocess
from pathlib import Path
from typing import List

import click

try:
    from .logger import logger
except ImportError:
    from logger import logger


def discover_sln_files(root_dir: Path, max_depth: int = 3) -> List[Path]:
    """Discover .sln files with exclusions and depth limit."""
    sln_files = []
    root_dir = Path(root_dir)

    # Common directories to exclude
    exclude_dirs = {
        ".git",
        "bin",
        "obj",
        "node_modules",
        "dist",
        "build",
        "target",
        ".vs",
        ".vscode",
        ".idea",
        "venv",
        ".venv",
    }

    def _walk(current_dir: Path, depth: int):
        if depth > max_depth:
            return

        try:
            # Check for .sln files in current directory
            for f in current_dir.glob("*.sln"):
                if f.is_file():
                    sln_files.append(f)

            # Recurse into subdirectories
            for d in current_dir.iterdir():
                if (
                    d.is_dir()
                    and d.name not in exclude_dirs
                    and not d.name.startswith(".")
                ):
                    _walk(d, depth + 1)
        except PermissionError:
            logger.warning(f"Permission denied: {current_dir}")
        except Exception as e:
            logger.error(f"Error walking {current_dir}: {e}")

    _walk(root_dir, 0)
    # Sort for stable ordering and return as relative paths
    return sorted(sln_files)


def check_dotnet_prerequisites(non_interactive=False):
    """Check if dotnet and dotnet-sonarscanner are installed."""
    if not shutil.which("dotnet"):
        click.echo("❌ .NET SDK not found. Please install .NET SDK first.")
        return False

    try:
        # Check if dotnet-sonarscanner is installed
        result = subprocess.run(
            ["dotnet", "tool", "list", "-g"], capture_output=True, text=True, check=True
        )
        if "dotnet-sonarscanner" not in result.stdout:
            click.echo("⚠️  dotnet-sonarscanner tool not found.")
            if non_interactive or click.confirm(
                "Do you want to install dotnet-sonarscanner globally?", default=True
            ):
                subprocess.run(
                    ["dotnet", "tool", "install", "--global", "dotnet-sonarscanner"],
                    check=True,
                )
                click.echo("✅ dotnet-sonarscanner installed successfully.")
            else:
                return False
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to check/install dotnet tools: {e}")
        return False


def _cleanup_dotnet_temp_files(project_root: Path):
    """Remove .sonarqube and .scannerwork directories."""
    temp_dirs = ["code-audit-23", ".sonarqube", ".scannerwork"]
    for d_name in temp_dirs:
        d_path = project_root / d_name
        if d_path.exists() and d_path.is_dir():
            try:
                shutil.rmtree(d_path)
                logger.debug(f"Removed temporary directory: {d_path}")
            except Exception as e:
                logger.warning(f"Could not remove temporary directory {d_path}: {e}")


def run_dotnet_scan(
    project_key,
    sonar_url,
    token,
    project_root,
    env,
    solution_path=None,
    non_interactive=False,
):
    """Run SonarQube scan for .NET projects using dotnet sonarscanner."""
    if not check_dotnet_prerequisites(non_interactive=non_interactive):
        return False

    # Ensure conflicting properties file is removed for .NET projects
    props_file = project_root / "sonar-project.properties"
    if props_file.exists():
        try:
            props_file.unlink()
            click.echo("🧹 Removed conflicting sonar-project.properties for .NET scan")
        except Exception as e:
            click.echo(f"⚠️  Failed to remove sonar-project.properties: {e}")

    # Discover .sln files
    if solution_path:
        selected_sln = Path(solution_path).resolve()
        if not selected_sln.exists():
            click.echo(f"❌ Provided solution file not found: {solution_path}")
            return False
    else:
        sln_files = discover_sln_files(project_root)
        if not sln_files:
            click.echo("⚠️  No .sln files found. Skipping SonarQube scan for .NET.")
            click.echo(
                "ℹ️  To scan .NET projects, ensure you have a .sln file within 3 levels of the root."
            )
            # Cleanup even if skipped
            _cleanup_dotnet_temp_files(project_root)
            return True  # Continue execution

        if len(sln_files) == 1:
            selected_sln = sln_files[0]
            relative_path = selected_sln.relative_to(project_root)
            click.echo(f"🔍 Found solution: {relative_path}")
            click.echo(f"📝 Using this solution: {relative_path}")
        else:
            click.echo("🔍 Multiple solution files detected:\n")
            for idx, sln in enumerate(sln_files, 1):
                relative_path = sln.relative_to(project_root)
                click.echo(f"[{idx}] {relative_path}")

            click.echo("")  # New line
            choice = click.prompt(
                f"Select solution to scan (1-{len(sln_files)})",
                type=click.IntRange(1, len(sln_files)),
            )
            selected_sln = sln_files[choice - 1]

    relative_sln_path = selected_sln.relative_to(project_root)

    try:
        # Step 1: Begin
        click.echo(f"\n1️⃣  Beginning .NET SonarScanner for project: {project_key}...")
        begin_cmd = [
            "dotnet",
            "sonarscanner",
            "begin",
            f"/k:{project_key}",
            f"/d:sonar.host.url={sonar_url}",
            f"/d:sonar.login={token}",
            f"/d:sonar.cs.vscoveragexml.reportsPaths=coverage.xml",  # dotnet-coverage
            f"/d:sonar.cs.dotcover.reportsPaths=dotCover.Output.html",  # dotCover
            f"/d:sonar.cs.opencover.reportsPaths=coverage.xml",  # OpenCover / Coverlet
        ]
        subprocess.run(begin_cmd, cwd=project_root, env=env, check=True)

        # Step 2: Build
        click.echo(f"2️⃣  Building .NET project: {relative_sln_path}...")
        # Use --no-incremental as requested
        build_cmd = ["dotnet", "build", str(selected_sln), "--no-incremental"]
        subprocess.run(build_cmd, cwd=project_root, env=env, check=True)

        # Step 3: End
        click.echo("3️⃣  Ending .NET SonarScanner (uploading results)...")
        end_cmd = ["dotnet", "sonarscanner", "end", f"/d:sonar.login={token}"]
        subprocess.run(end_cmd, cwd=project_root, env=env, check=True)

        click.echo("✅ .NET Sonar scan completed successfully!")
        click.echo(f"👉 View results: {sonar_url}/dashboard?id={project_key}")
        return True

    except subprocess.CalledProcessError as e:
        click.echo(f"❌ .NET scan failed at step: {e.cmd}")
        return False
    finally:
        _cleanup_dotnet_temp_files(project_root)
