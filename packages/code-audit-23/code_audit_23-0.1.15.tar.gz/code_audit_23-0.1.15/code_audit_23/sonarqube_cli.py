import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional

import click

try:
    from .logger import logger
except ImportError:
    from logger import logger

try:
    from .gitignore_utils import get_tool_specific_exclusions
except ImportError:
    from gitignore_utils import get_tool_specific_exclusions

try:
    from .sonarqube_java import get_java_home, get_jre_bin
except ImportError:
    from sonarqube_java import get_java_home, get_jre_bin

try:
    from .sonarqube_dotnet import run_dotnet_scan
except ImportError:
    from sonarqube_dotnet import run_dotnet_scan


def get_scanner_path():
    """Return path to sonar-scanner bundled folder"""
    if getattr(sys, "frozen", False):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).parent

    # Assume a 'sonar-scanner' folder is next to CLI
    scanner_bin = (
        base_path
        / "sonar-scanner"
        / "bin"
        / ("sonar-scanner.bat" if os.name == "nt" else "sonar-scanner")
    )
    if not scanner_bin.exists():
        raise FileNotFoundError(f"SonarScanner binary not found: {scanner_bin}")
    return scanner_bin


def detect_project_type(project_dir: Path) -> Optional[str]:
    """Detect project type based on build files."""
    project_dir = Path(project_dir)
    if (project_dir / "pom.xml").exists():
        return "maven"
    elif any((project_dir / f).exists() for f in ["build.gradle", "build.gradle.kts"]):
        return "gradle"
    elif any(project_dir.glob("*.sln")) or any(project_dir.glob("*.csproj")):
        return "dotnet"
    elif any(
        f.suffix == ".java"
        for f in project_dir.rglob("*.java")
        if not any(
            p.startswith(".") or p.startswith("target") or p.startswith("build")
            for p in f.parts
        )
    ):
        return "java"  # Plain Java project
    return None


def normalize_sonar_path(path: str | Path) -> str:
    """Normalize a path for SonarQube properties files.

    SonarQube properties files expect forward slashes as path separators
    on all platforms (Windows, Linux, macOS), regardless of the OS convention.

    Args:
        path: Path as string or Path object

    Returns:
        Path string with forward slashes
    """
    path_str = str(path)
    # Convert to forward slashes (works on all platforms)
    return path_str.replace("\\", "/")


def get_key_from_props(props_file: Path) -> Optional[str]:
    """Extract sonar.projectKey from properties file if it exists."""
    if not props_file.exists():
        return None
    try:
        content = props_file.read_text(encoding="utf-8")
        for line in content.splitlines():
            line = line.strip()
            if line.startswith("sonar.projectKey="):
                return line.split("=", 1)[1].strip()
    except Exception:
        pass
    return None


def run_sonarqube_scan(
    sonar_url,
    token,
    project_key=None,
    sources=".",
    non_interactive=False,
    solution_path=None,
):
    project_root = Path(sources).resolve()
    if not project_root.exists():
        click.echo("❌ Source directory not found.")
        sys.exit(1)

    props_file = project_root / "sonar-project.properties"

    # Priority 1: Use from sonar-project.properties if it exists
    if props_file.exists():
        key_from_file = get_key_from_props(props_file)
        if key_from_file:
            project_key = key_from_file
            logger.debug(f"Using project key from {props_file}: {project_key}")
        else:
            # File exists but key is missing, we might still need a key for the CLI arg or result URL
            project_key = project_key or project_root.name

    # Priority 2: If no key yet (file missing or key missing in file), use CLI arg or prompt
    if not project_key:
        if non_interactive:
            project_key = project_root.name
            logger.info(
                f"No project key provided in non-interactive mode. Using default: {project_key}"
            )
        else:
            project_key = click.prompt(
                f"❓ sonar-project.properties not found. Enter project key",
                default=project_root.name,
                show_default=True,
            )

    click.echo(f"🔍 Starting SonarQube scan for project: {project_key}")

    # Get gitignore patterns for SonarQube
    sonar_patterns = []
    try:
        sonar_patterns = get_tool_specific_exclusions(str(project_root), "sonarqube")
        if sonar_patterns:
            logger.debug(
                f"Using {len(sonar_patterns)} .gitignore patterns for SonarQube exclusions"
            )
    except Exception as e:
        logger.warning(f"Could not process .gitignore files: {e}")

    # Add default exclusions
    default_exclusions = [
        "**/*.sarif",
        "**/*.log",
        "**/node_modules/**",
        "**/bower_components/**",
        "**/*.min.*",
        "**/dist/**",
        "**/build/**",
        "**/target/**",
        "**/*.iml",
        "**/.idea/**",
        "**/.vscode/**",
        "**/venv/**",
        "**/.venv/**",
        "**/env/**",
        "**/.env*",
        "**/*.bak",
        "**/*.tmp",
        "**/tmp/**",
        "**/*~",
        "**/.git/**",
        "**/.github/**",
        "**/.gitlab-ci.yml",
        "**/sonar-project.properties",
        "**/migrations/**",
        "**/__pycache__/**",
        "**/*.pyc",
        "**/*.pyo",
        "**/*.pyd",
        "**/htmlcov/**",
        "**/.pytest_cache/**",
        "**/.tox/**",
        "**/db.sqlite3",
        "**/Dockerfile",
        "**/docker-compose.yml",
        "**/*.md",
        "**/requirements.txt",
        "**/conftest.py",
        "**/pytest.ini",
        "**/*.egg-info/**",
        "**/.eggs/**",
        "**/*.whl",
        "**/tests/**",
        "**/test_*.py",
        "**/test/**",
        "**/*Test.java",
        "**/*Tests.java",
    ]

    # Combine all exclusions
    all_exclusions = list(set(default_exclusions + sonar_patterns))
    exclusions_str = ",".join(all_exclusions)

    # Detect project type
    project_type = detect_project_type(project_root)

    if project_type in ("maven", "gradle", "java"):
        click.echo(f"🔍 Detected {project_type.upper()} project")

        skip_java = False
        makefile_path = project_root / "Makefile"
        make_cmd = shutil.which("make")

        if not makefile_path.exists():
            click.echo(
                click.style("⚠️  Makefile not found in project root.", fg="yellow")
            )
            skip_java = True
        elif not make_cmd:
            click.echo(
                click.style("⚠️  'make' command not found in system.", fg="yellow")
            )
            skip_java = True
        else:
            try:
                click.echo("🛠️  Running 'make build'...")
                subprocess.run([make_cmd, "build"], cwd=project_root, check=True)
                click.echo("✅ 'make build' completed successfully")
            except subprocess.CalledProcessError as e:
                click.echo(
                    click.style(
                        f"❌ 'make build' failed with exit code {e.returncode}",
                        fg="red",
                    )
                )
                skip_java = True
            except Exception as e:
                click.echo(
                    click.style(
                        f"❌ Unexpected error running 'make build': {e}", fg="red"
                    )
                )
                skip_java = True

        if skip_java:
            click.echo(
                click.style(
                    "⏭️  Skipping Java file analysis for this scan.",
                    fg="yellow",
                    bold=True,
                )
            )
            click.echo(
                click.style(
                    "ℹ️  To enable Java scanning, ensure you have a 'Makefile' with a 'build' target.",
                    fg="bright_white",
                )
            )
            click.echo(
                click.style(
                    "📖 Refer to DOCUMENTS/cli_tool_setup_guide.md for the standard interface requirements.",
                    fg="bright_cyan",
                )
            )

            # # Exclude Java files
            # all_exclusions.append("**/*.java")
            # exclusions_str = ",".join(list(set(all_exclusions)))

        # Base properties for Java projects
        sources_normalized = normalize_sonar_path(sources)
        properties = f"""
sonar.projectKey={project_key}
sonar.projectName={project_key}
sonar.sources={sources_normalized}
sonar.exclusions={exclusions_str}
sonar.sourceEncoding=UTF-8
""".strip()
    else:
        # For non-Java projects, use basic configuration
        sources_normalized = normalize_sonar_path(sources)
        properties = f"""
sonar.projectKey={project_key}
sonar.projectName={project_key}
sonar.sources={sources_normalized}
sonar.exclusions={exclusions_str}
sonar.sourceEncoding=UTF-8
""".strip()

    # Attempt to run 'make coverage' for all projects
    makefile_path = project_root / "Makefile"
    make_cmd = shutil.which("make")

    if makefile_path.exists() and make_cmd:
        try:
            click.echo("🧪 Running 'make coverage'...")
            # We don't use check=True here because we want to handle failure gracefully
            # and just inform the user instead of raising an exception.
            result = subprocess.run(
                [make_cmd, "coverage"],
                cwd=project_root,
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                click.echo("✅ 'make coverage' completed successfully")
            else:
                click.echo(
                    click.style(
                        f"⚠️  'make coverage' failed (exit code {result.returncode})",
                        fg="yellow",
                    )
                )
                if "No rule to make target 'coverage'" in result.stderr:
                    click.echo(
                        click.style(
                            "ℹ️  Missing 'coverage' target in Makefile.", fg="white"
                        )
                    )

                click.echo(
                    click.style(
                        "ℹ️  To enable code coverage, ensure you have a 'Makefile' with a 'coverage' target.",
                        fg="white",
                    )
                )
                click.echo(
                    click.style(
                        "📖 Refer to DOCUMENTS/cli_tool_setup_guide.md for instructions.",
                        fg="bright_cyan",
                    )
                )
        except Exception as e:
            click.echo(
                click.style(
                    f"⚠️  Unexpected error running 'make coverage': {e}", fg="yellow"
                )
            )
    else:
        if not makefile_path.exists():
            click.echo(
                click.style(
                    "ℹ️  Makefile not found. Skipping automatic coverage generation.",
                    fg="bright_black",
                )
            )
        elif not make_cmd:
            click.echo(
                click.style(
                    "⚠️  'make' command not found. Skipping automatic coverage generation.",
                    fg="yellow",
                )
            )

        click.echo(
            click.style(
                "ℹ️  To enable code coverage, please set up a 'Makefile' with a 'coverage' target.",
                fg="white",
            )
        )
        click.echo(
            click.style(
                "📖 Refer to DOCUMENTS/cli_tool_setup_guide.md for instructions.",
                fg="bright_cyan",
            )
        )

    # Get scanner and Java paths
    scanner_bin = get_scanner_path()
    java_bin = get_jre_bin()
    java_bin_path = Path(java_bin)
    java_home = get_java_home(java_bin)

    # Validate JAVA_HOME
    java_home_path = Path(java_home)
    java_exe_in_home = (
        java_home_path / "bin" / ("java.exe" if os.name == "nt" else "java")
    )
    if not java_exe_in_home.exists():
        # If JAVA_HOME doesn't have java.exe, try to use the java_bin's parent directory structure
        logger.warning(
            f"JAVA_HOME {java_home} does not contain java.exe. "
            f"Trying alternative detection..."
        )
        # Try parent.parent as fallback
        fallback_home = java_bin_path.parent.parent
        fallback_exe = (
            fallback_home / "bin" / ("java.exe" if os.name == "nt" else "java")
        )
        if fallback_exe.exists():
            java_home = str(fallback_home)
            logger.debug(f"Using fallback JAVA_HOME: {java_home}")
        else:
            # Last resort: just use the directory containing java.exe
            java_home = str(java_bin_path.parent)
            logger.warning(
                f"Could not find valid JAVA_HOME. Using java.exe directory: {java_home}"
            )

    env = os.environ.copy()
    env["JAVA_HOME"] = java_home

    # Handle PATH updates in a cross-platform way
    path_sep = ";" if os.name == "nt" else ":"
    path_parts = [str(java_bin_path.parent), env.get("PATH", "")]
    env["PATH"] = path_sep.join(filter(None, path_parts))

    env.update(
        {
            "PYTHONUNBUFFERED": "1",
            "PYTHONIOENCODING": "utf-8",
            "LANG": "C.UTF-8" if platform.system() != "Darwin" else "en_US.UTF-8",
            "LC_ALL": "C.UTF-8" if platform.system() != "Darwin" else "en_US.UTF-8",
        }
    )

    # # Ensure URL and token are properly formatted
    # sonar_url = sonar_url or SONAR_HOST_URL
    # token = token or SONAR_LOGIN

    # if not sonar_url or sonar_url == SONAR_HOST_URL:
    #     click.echo(f"⚠️  Using default SonarQube URL: {SONAR_HOST_URL}")
    if not token:
        error_msg = "No SonarQube token provided. Please set SONAR_LOGIN in your .env file or use --token"
        logger.error(error_msg)
        click.echo(f"❌ {error_msg}")
        sys.exit(1)

    env["SONAR_HOST_URL"] = sonar_url.rstrip("/")
    env["SONAR_TOKEN"] = token.strip()
    logger.debug("SonarQube configuration verified")

    # Handle .NET projects specifically
    if project_type == "dotnet":
        # Ensure conflicting properties file is removed
        props_file = project_root / "sonar-project.properties"
        if props_file.exists():
            try:
                props_file.unlink()
                click.echo(
                    "🧹 Removed conflicting sonar-project.properties for .NET scan"
                )
            except Exception as e:
                click.echo(f"⚠️  Failed to remove sonar-project.properties: {e}")

        click.echo("🚀 Starting .NET SonarScanner...")
        return run_dotnet_scan(
            project_key,
            sonar_url,
            token,
            project_root,
            env,
            solution_path=solution_path,
            non_interactive=non_interactive,
        )

    # Create sonar-project.properties if not exists
    props_file = project_root / "sonar-project.properties"
    if not props_file.exists():
        try:
            props_file.write_text(properties, encoding="utf-8")
            click.echo("📝 Created sonar-project.properties for future use")
        except Exception as e:
            click.echo(f"⚠️  Failed to create sonar-project.properties: {e}")
            return False

    # Prepare SARIF report paths
    reports_dir = project_root / "code-audit-23" / "reports"

    # Check which report files exist
    report_files = [
        "gitleaks.sarif",
        "semgrep.sarif",
        "trivy.sarif",
        "bandit.sarif",
        "eslint.sarif",
        "checkov.sarif",
    ]

    # Find existing report files
    existing_reports = [f for f in report_files if (reports_dir / f).exists()]

    # Build sonar-scanner command
    scanner_cmd = [
        str(scanner_bin),
        "-Dsonar.verbose=false",
        f"-Dsonar.exclusions={exclusions_str}",
    ]

    # Add SARIF reports if any exist
    if existing_reports:
        sarif_paths = [
            normalize_sonar_path(f"code-audit-23/reports/{report}")
            for report in existing_reports
        ]
        sarif_arg = "-Dsonar.sarifReportPaths=" + ",".join(sarif_paths)
        scanner_cmd.append(sarif_arg)
        click.echo(f"📊 Including SARIF reports: {', '.join(existing_reports)}")

    click.echo("🚀 Starting SonarScanner...")
    try:
        # Start the subprocess and stream logs in real-time
        process = subprocess.Popen(
            scanner_cmd,
            cwd=project_root,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        click.echo("🔍 Scanning code (streaming Sonar logs)...")
        streamed_output = []
        assert process.stdout is not None
        for line in process.stdout:
            streamed_output.append(line)
            click.echo(line.rstrip())

        process.wait()

        # No cleanup of sonar-project.properties (making it persistent)

        # Check the return code
        if process.returncode != 0:
            raise subprocess.CalledProcessError(
                process.returncode, process.args, output="".join(streamed_output)
            )

        click.echo("✅ Sonar scan completed successfully!")
        click.echo(f"👉 View results: {sonar_url}/dashboard?id={project_key}")
        return True

    except subprocess.CalledProcessError as e:
        # No cleanup of sonar-project.properties (making it persistent)

        error_msg = f"Sonar scan failed with exit code {e.returncode}"
        logger.error(error_msg)
        click.echo("❌ Sonar scan failed!")
        click.echo(f"Exit code: {e.returncode}")
        # sys.exit(1)
        return False

    except Exception as e:
        # No cleanup of sonar-project.properties (making it persistent)

        error_msg = f"Unexpected error during Sonar scan: {str(e)}"
        logger.exception(error_msg)
        click.echo(f"❌ {error_msg}")
        # sys.exit(1)
        return False
