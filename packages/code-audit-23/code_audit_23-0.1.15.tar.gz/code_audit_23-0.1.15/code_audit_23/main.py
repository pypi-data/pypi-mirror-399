import os
import shutil
import sys
from pathlib import Path

import click
import tomli
from dotenv import load_dotenv

# Allow running both as package and script
if __package__ is None or __package__ == "":
    # Running as script (e.g. python main.py)
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from logger import get_log_dir, logger
    from semgrep_cli import run_semgrep_scan
    from sonarqube_cli import run_sonarqube_scan
    from trivy_cli import run_trivy_scan
else:
    # Running as installed package
    from .logger import get_log_dir, logger
    from .semgrep_cli import run_semgrep_scan
    from .sonarqube_cli import run_sonarqube_scan
    from .trivy_cli import run_trivy_scan

# Load environment variables from .env file
load_dotenv()

# Default SonarQube configuration
SONAR_HOST_URL = os.getenv("SONAR_HOST_URL", "https://sonarqube.brainstation-23.xyz")
SONAR_LOGIN = os.getenv("SONAR_LOGIN", "sqa_eb118830887767100489ecfc4b55e42a134bf2cb")


def ensure_reports_dir():
    """Ensure the reports directory exists"""
    reports_dir = Path("code-audit-23/reports")
    reports_dir.mkdir(exist_ok=True, parents=True)
    return reports_dir


def get_sonarqube_credentials():
    """Prompt user for SonarQube credentials if not in environment"""
    click.echo(
        click.style("\n🔑 SonarQube Configuration Required", fg="yellow", bold=True)
    )
    click.echo(click.style("-" * 40, fg="bright_black"))
    sonar_url = click.prompt(
        click.style(
            "Enter SonarQube URL (e.g., http://localhost:9000)", fg="bright_cyan"
        ),
        type=str,
    )
    sonar_token = click.prompt(
        click.style("Enter SonarQube Token (will be hidden)", fg="bright_cyan"),
        hide_input=True,
    )
    click.echo(click.style("✅ Credentials saved for this session\n", fg="green"))
    return sonar_url, sonar_token


def get_version():
    """Get version from package metadata or pyproject.toml"""
    # Try to get version from package metadata first (works in installed package)
    try:
        from importlib.metadata import PackageNotFoundError, version

        try:
            ver = version("code-audit-23")
            logger.debug(f"Got version from package metadata: {ver}")
            return ver
        except PackageNotFoundError:
            logger.debug("Package not found in metadata, trying pyproject.toml")
    except ImportError:
        logger.debug("importlib.metadata not available, falling back to pyproject.toml")

    # For development/local execution or when package isn't installed
    try:
        # List of possible locations to find pyproject.toml
        possible_paths = [
            # For development
            Path(__file__).parent.parent / "pyproject.toml",
            # For PyInstaller binary
            (
                Path(sys._MEIPASS) / "pyproject.toml"
                if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")
                else None
            ),
            # Current directory as fallback
            Path.cwd() / "pyproject.toml",
        ]

        # Filter out None values and find first existing file
        pyproject_path = next((p for p in possible_paths if p and p.exists()), None)

        if pyproject_path:
            logger.debug(f"Found pyproject.toml at: {pyproject_path}")
            with open(pyproject_path, "rb") as f:
                pyproject = tomli.load(f)
                if "project" in pyproject and "version" in pyproject["project"]:
                    ver = pyproject["project"]["version"]
                    logger.debug(f"Got version from {pyproject_path}: {ver}")
                    return ver
                else:
                    logger.warning(f"Version not found in {pyproject_path}")
        else:
            logger.warning("Could not find pyproject.toml in any expected location")

    except Exception as e:
        logger.warning(f"Error determining version: {e}", exc_info=True)

    logger.warning("Falling back to default version: 0.1.0")
    return "0.1.0"


def show_welcome_banner():
    """Display welcome banner with ASCII art"""
    version = get_version()
    banner = """
     ██████╗ ██████╗ ██████╗ ███████╗    █████╗ ██╗   ██╗██████╗ ██╗████████╗    ██████╗ ██████╗ 
    ██╔════╝██╔═══██╗██╔══██╗██╔════╝   ██╔══██╗██║   ██║██╔══██╗██║╚══██╔══╝    ╚════██╗╚════██╗
    ██║     ██║   ██║██║  ██║█████╗     ███████║██║   ██║██║  ██║██║   ██║        █████╔╝ █████╔╝
    ██║     ██║   ██║██║  ██║██╔══╝     ██╔══██║██║   ██║██║  ██║██║   ██║       ██╔═══╝  ╚═══██╗
    ╚██████╗╚██████╔╝██████╔╝███████╗   ██║  ██║╚██████╔╝██████╔╝██║   ██║      ███████╗██████╔╝
     ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝   ╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚═╝   ╚═╝      ╚══════╝╚═════╝ 
    """
    click.echo(click.style(banner, fg="bright_cyan"))
    click.echo(
        click.style(
            " " * 25 + "🚀  Code Quality & Security Scanner  🚀",
            fg="bright_white",
            bold=True,
        )
    )
    click.echo(click.style(f" " * 35 + f"Version {version}", fg="bright_black"))

    # Ensure reports directory exists
    ensure_reports_dir()


def show_menu():
    """Display main interactive menu"""
    click.echo(click.style("═" * 80, fg="bright_blue"))
    click.echo(
        click.style(
            " " * 22 + "🔍  CODE AUDIT 23 MENU  🔍", fg="bright_cyan", bold=True
        )
    )
    click.echo(click.style("═" * 80, fg="bright_blue"))

    menu_items = [
        (
            "1",
            "All Scans (Trivy + Semgrep + SonarQube)",
            "Run all security scans in sequence",
        ),
        (
            "2",
            "Trivy Scan",
            "Scan for vulnerabilities in dependencies and container images",
        ),
        ("3", "Semgrep Scan", "Static code analysis for security issues"),
        ("4", "SonarQube Scan", "Analyze code quality and security issues"),
        ("q", "Quit", "Exit the application"),
    ]

    for num, title, desc in menu_items:
        click.echo(
            click.style(f"  [{num}] ", fg="bright_green", bold=True)
            + click.style(f"{title}", fg="white", bold=True)
        )
        click.echo(click.style(f"      {desc}", fg="bright_black"))
        # click.echo()

    click.echo(click.style("─" * 80, fg="bright_blue"))


def prompt_choice():
    """Prompt user for menu selection with validation"""
    while True:
        choice = (
            click.prompt(
                click.style("\nSelect an option", fg="bright_yellow"),
                type=str,
                default="1",
                show_default=False,
            )
            .strip()
            .lower()
        )

        if choice in ["1", "2", "3", "4", "q", "quit"]:
            return choice
        click.echo(
            click.style(
                "❌ Invalid choice. Please select 1, 2, 3, or q to quit.", fg="red"
            )
        )


def perform_cleanup():
    """Perform automatic cleanup of scanner-generated folders"""
    click.echo(click.style("\n🧹 Performing automatic cleanup...", fg="yellow"))
    for folder in ["code-audit-23", ".sonarqube", ".scannerwork"]:
        folder_path = Path.cwd() / folder
        if folder_path.exists() and folder_path.is_dir():
            try:
                shutil.rmtree(folder_path)
                click.echo(click.style(f"✅ Removed {folder}/", fg="bright_black"))
            except Exception as e:
                click.echo(click.style(f"⚠️  Could not remove {folder}/: {e}", fg="red"))


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """Code Audit 23 - Security and Quality Scanner"""
    if ctx.invoked_subcommand is None:
        ctx.invoke(menu)


@cli.command()
def menu():
    """Interactive entrypoint for Audit Scanner"""
    # Clear screen and show welcome banner
    click.clear()
    show_welcome_banner()

    # Initialize SonarQube credentials
    global SONAR_HOST_URL, SONAR_LOGIN
    sonar_credentials_provided = bool(SONAR_HOST_URL and SONAR_LOGIN)

    try:
        while True:
            try:
                show_menu()
                choice = prompt_choice()
                # click.clear()

                # Handle quit option
                if choice.lower() in ["q", "quit"]:
                    break

                # Run Trivy scan for All Scans or Trivy only
                if choice in ["1", "2"]:
                    if choice == "1":
                        click.echo("\n" + "─" * 80)
                    report_path = "code-audit-23/reports/trivy.sarif"
                    click.echo(
                        click.style(
                            f"🔍 Starting Trivy Vulnerability Scan... (Report will be saved to {report_path})",
                            fg="bright_cyan",
                            bold=True,
                        )
                    )
                    result = run_trivy_scan(report_path)
                    if choice in ["1", "2"] and result:
                        click.echo(
                            click.style(
                                f"\n✅ Trivy Scan completed successfully! Report saved to {report_path}",
                                fg="bright_green",
                                bold=True,
                            )
                        )

                # Run Semgrep scan for All Scans or Semgrep only
                if choice in ["1", "3"]:
                    if choice == "1":
                        click.echo("\n" + "─" * 80)
                    click.echo(
                        click.style(
                            "🔍 Starting Semgrep Scan... (Report will be saved to code-audit-23/reports/semgrep.sarif)",
                            fg="bright_cyan",
                            bold=True,
                        )
                    )
                    result = run_semgrep_scan()
                    if choice in ["1", "3"] and result:
                        click.echo(
                            click.style(
                                "\n✅ Semgrep Scan completed successfully! Report saved to code-audit-23/reports/semgrep.sarif",
                                fg="bright_green",
                                bold=True,
                            )
                        )

                # Run SonarQube scan for All Scans or SonarQube only
                if choice in ["1", "4"]:
                    if choice == "1":
                        click.echo("\n" + "─" * 80)
                    click.echo(
                        click.style(
                            "🚀 Starting SonarQube Scan...", fg="bright_cyan", bold=True
                        )
                    )
                    try:
                        # Get credentials if not already provided
                        if not sonar_credentials_provided:
                            SONAR_HOST_URL, SONAR_LOGIN = get_sonarqube_credentials()
                            sonar_credentials_provided = True

                        result = run_sonarqube_scan(
                            sonar_url=SONAR_HOST_URL,
                            token=SONAR_LOGIN,
                            project_key=None,
                            sources=".",
                            non_interactive=False,
                        )
                    except Exception as e:
                        logger.error(f"SonarQube scan failed: {e}")
                        click.echo(
                            click.style(f"❌ SonarQube scan failed: {str(e)}", fg="red")
                        )
                        if click.confirm(
                            click.style(
                                "Do you want to update SonarQube credentials?",
                                fg="yellow",
                            )
                        ):
                            sonar_url, sonar_token = get_sonarqube_credentials()
                            SONAR_HOST_URL = sonar_url
                            SONAR_LOGIN = sonar_token
                            # Retry the scan with new credentials
                            result = run_sonarqube_scan(
                                sonar_url=SONAR_HOST_URL,
                                token=SONAR_LOGIN,
                                project_key=None,
                                sources=".",
                                non_interactive=False,
                            )
                    if choice in ["1", "4"] and result:
                        click.echo(
                            click.style(
                                "\n✅ SonarQube Scan completed successfully!",
                                fg="bright_green",
                                bold=True,
                            )
                        )

                # Show completion message for All Scans
                if choice == "1":
                    click.echo(click.style("=" * 80 + "\n", fg="bright_green"))
                    click.echo(
                        click.style(
                            "✅ All Scans completed successfully!",
                            fg="bright_green",
                            bold=True,
                        )
                    )
                    click.echo(click.style("=" * 80 + "\n", fg="bright_green"))

                log_dir = get_log_dir()
                click.echo(
                    click.style(
                        f"📝 Logs are available at: {log_dir}", fg="bright_black"
                    )
                )
            except Exception as e:
                logger.error(f"Scan failed: {e}")
                click.echo(
                    click.style("\n❌ An error occurred during the scan.", fg="red")
                )
                if not click.confirm(
                    click.style("Would you like to try again?", fg="yellow")
                ):
                    break
    except KeyboardInterrupt:
        click.echo(click.style("\n\n⚠️  Scan interrupted by user.", fg="yellow"))
    finally:
        perform_cleanup()
        try:
            log_dir = get_log_dir()
            click.echo(
                click.style(f"📝 Logs are saved at: {log_dir}", fg="bright_black")
            )
        except Exception:
            pass
        click.echo(
            click.style(
                "👋 Thank you for using Code Audit 23. Goodbye!\n",
                fg="bright_blue",
                bold=True,
            )
        )


@cli.command()
@click.option(
    "--type",
    "-t",
    type=click.Choice(["all", "trivy", "semgrep", "sonarqube"]),
    default="all",
    help="Type of scan to run",
)
@click.option("--sonar-url", help="SonarQube server URL")
@click.option("--sonar-token", help="SonarQube authentication token")
@click.option("--project-key", help="SonarQube project key")
@click.option("--sources", default=".", help="Path to sources")
@click.option("--solution", help="Path to .sln file (for .NET projects)")
@click.option(
    "--non-interactive", is_flag=True, default=True, help="Run in non-interactive mode"
)
def scan(type, sonar_url, sonar_token, project_key, sources, solution, non_interactive):
    """Run scans in non-interactive mode using CLI arguments"""
    show_welcome_banner()

    global SONAR_HOST_URL, SONAR_LOGIN
    sonar_url = sonar_url or SONAR_HOST_URL
    sonar_token = sonar_token or SONAR_LOGIN

    try:
        # Run Trivy scan
        if type in ["all", "trivy"]:
            click.echo("\n" + "─" * 80)
            report_path = "code-audit-23/reports/trivy.sarif"
            click.echo(
                click.style(
                    f"🔍 Starting Trivy Vulnerability Scan... (Report will be saved to {report_path})",
                    fg="bright_cyan",
                    bold=True,
                )
            )
            run_trivy_scan(report_path, target_path=sources)

        # Run Semgrep scan
        if type in ["all", "semgrep"]:
            click.echo("\n" + "─" * 80)
            click.echo(
                click.style(
                    "🔍 Starting Semgrep Scan... (Report will be saved to code-audit-23/reports/semgrep.sarif)",
                    fg="bright_cyan",
                    bold=True,
                )
            )
            # Semgrep CLI needs more work if we want to change target path easily,
            # but currently it's hardcoded to "." in semgrep_cli.run_semgrep_scan
            run_semgrep_scan()

        # Run SonarQube scan
        if type in ["all", "sonarqube"]:
            click.echo("\n" + "─" * 80)
            click.echo(
                click.style(
                    "🚀 Starting SonarQube Scan...", fg="bright_cyan", bold=True
                )
            )
            if not sonar_url or not sonar_token:
                click.echo(
                    click.style(
                        "❌ SonarQube URL and Token are required for SonarQube scan.",
                        fg="red",
                    )
                )
                sys.exit(1)

            run_sonarqube_scan(
                sonar_url=sonar_url,
                token=sonar_token,
                project_key=project_key,
                sources=sources,
                non_interactive=non_interactive,
                solution_path=solution,
            )

        click.echo("\n" + "=" * 80)
        click.echo(
            click.style(
                "✅ Non-interactive scan(s) completed!", fg="bright_green", bold=True
            )
        )
        click.echo("=" * 80 + "\n")

    except Exception as e:
        logger.error(f"Scan failed: {e}")
        click.echo(click.style(f"\n❌ An error occurred: {str(e)}", fg="red"))
        sys.exit(1)
    finally:
        perform_cleanup()
        log_dir = get_log_dir()
        click.echo(
            click.style(f"📝 Logs are available at: {log_dir}", fg="bright_black")
        )


# Alias for backward compatibility with entry points
main = cli

if __name__ == "__main__":
    cli()
