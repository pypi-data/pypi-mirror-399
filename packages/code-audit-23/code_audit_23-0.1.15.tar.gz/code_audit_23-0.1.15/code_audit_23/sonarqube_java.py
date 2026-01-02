import json
import os
import platform
import shutil
import stat
import subprocess
import tarfile
import urllib.request
import zipfile
from pathlib import Path

import click

try:
    from .logger import logger
except ImportError:
    from logger import logger

# Cache folder for downloaded JRE
CACHE_DIR = Path.home() / ".audit_scan"
JRE_DIR = CACHE_DIR / "jre"
JRE_DIR.mkdir(parents=True, exist_ok=True)


def find_java():
    """Check system java or JAVA_HOME"""
    logger.debug("Looking for Java installation")
    system = platform.system()

    def _is_working_java(java_binary: Path) -> bool:
        if not java_binary or not java_binary.exists():
            return False
        try:
            result = subprocess.run(
                [str(java_binary), "-version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )
        except Exception as exc:  # noqa: BLE001
            logger.debug(f"Failed to execute Java binary {java_binary}: {exc}")
            return False

        output = (result.stdout or "") + (result.stderr or "")
        if result.returncode != 0 or "Unable to locate a Java Runtime" in output:
            logger.debug(
                f"Java binary at {java_binary} is not usable "
                f"(returncode={result.returncode})."
            )
            if output:
                logger.debug(output.strip())
            return False
        return True

    def _validate_java_home(java_home_dir: Path) -> str | None:
        java_bin_name = "java.exe" if os.name == "nt" else "java"
        java_candidate = java_home_dir / "bin" / java_bin_name
        if _is_working_java(java_candidate):
            logger.debug(f"Found Java in JAVA_HOME: {java_candidate}")
            return str(java_candidate)
        return None

    java_path = shutil.which("java")
    if java_path and _is_working_java(Path(java_path)):
        logger.debug(f"Found Java on PATH: {java_path}")
        return java_path
    if java_path and system == "Darwin":
        logger.debug(f"Ignoring non-functional macOS stub at {java_path}")

    java_home = os.environ.get("JAVA_HOME")
    if java_home:
        validated = _validate_java_home(Path(java_home))
        if validated:
            return validated

    if system == "Darwin":
        java_home_tool = Path("/usr/libexec/java_home")
        if java_home_tool.exists():
            try:
                result = subprocess.run(
                    [str(java_home_tool)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=False,
                )
                java_home_path = result.stdout.strip()
                if result.returncode == 0 and java_home_path:
                    validated = _validate_java_home(Path(java_home_path))
                    if validated:
                        return validated
            except Exception as exc:  # noqa: BLE001
                logger.debug(
                    f"Failed to resolve JAVA_HOME via /usr/libexec/java_home: {exc}"
                )

        brew_prefixes = [Path("/opt/homebrew"), Path("/usr/local")]
        brew_formula_globs = ("openjdk*", "temurin*")
        for prefix in brew_prefixes:
            opt_dir = prefix / "opt"
            if not opt_dir.exists():
                continue
            for pattern in brew_formula_globs:
                for candidate_dir in sorted(
                    opt_dir.glob(pattern), key=lambda p: p.name, reverse=True
                ):
                    java_bins = [
                        candidate_dir / "bin" / "java",
                        candidate_dir
                        / "libexec"
                        / "openjdk.jdk"
                        / "Contents"
                        / "Home"
                        / "bin"
                        / "java",
                    ]
                    for java_candidate in java_bins:
                        if _is_working_java(java_candidate):
                            logger.debug(
                                f"Found Java via Homebrew at: {java_candidate}"
                            )
                            return str(java_candidate)

        jvm_dir = Path("/Library/Java/JavaVirtualMachines")
        if jvm_dir.exists():
            for jdk_dir in sorted(
                jvm_dir.iterdir(), key=lambda p: p.name, reverse=True
            ):
                java_candidate = (
                    jdk_dir
                    / "Contents"
                    / "Home"
                    / "bin"
                    / ("java.exe" if os.name == "nt" else "java")
                )
                if _is_working_java(java_candidate):
                    logger.debug(f"Found Java in JVM directory: {java_candidate}")
                    return str(java_candidate)

    if platform.system() == "Darwin":
        try:
            ensure_openjdk17()
            # After installation, try finding Java again
            java_path = shutil.which("java")
            if java_path and _is_working_java(Path(java_path)):
                logger.debug(f"Found Java after installation: {java_path}")
                return java_path
        except Exception as e:
            logger.warning(f"Failed to install OpenJDK 17: {e}")

    logger.warning("Java not found in PATH or JAVA_HOME")
    return None


def ensure_openjdk17():
    """Ensure OpenJDK 17 is installed, symlinked, and environment variables set on macOS."""
    logger.info("Checking for OpenJDK 17 installation...")

    brew_path = shutil.which("brew")
    if not brew_path:
        raise RuntimeError(
            "Homebrew not found. Please install Homebrew first from https://brew.sh/"
        )

    try:
        # Check if java is already available
        subprocess.run(
            ["java", "--version"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        logger.info("✅ Java is already available.")
        return
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.info("Java not found or misconfigured. Installing OpenJDK 17...")

    # Install openjdk@17 using Homebrew
    try:
        click.echo("Installing OpenJDK 17... might ask for sudo privileges...")
        subprocess.run(["brew", "install", "--quiet", "openjdk@17"], check=True)
        logger.info("✅ Installed openjdk@17 via Homebrew.")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to install openjdk@17: {e}")

    # Create system symlink (macOS specific)
    if platform.system() == "Darwin":
        jdk_symlink = Path("/Library/Java/JavaVirtualMachines/openjdk-17.jdk")
        jdk_target = Path("/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk")

        try:
            subprocess.run(
                ["sudo", "ln", "-sfn", str(jdk_target), str(jdk_symlink)], check=True
            )
            logger.info(f"🔗 Symlinked {jdk_target} → {jdk_symlink}")
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            logger.warning(
                f"⚠️  Could not create symlink: {e}\n"
                "Please run manually with admin privileges:\n"
                f"sudo ln -sfn {jdk_target} {jdk_symlink}"
            )

    # Update environment variables
    if platform.system() == "Darwin":
        java_home = "/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home"
        java_bin = "/opt/homebrew/opt/openjdk@17/bin"
    else:
        java_home = "/usr/lib/jvm/java-17-openjdk"
        java_bin = f"{java_home}/bin"

    path_line = f'export PATH="{java_bin}:$PATH"'
    java_home_line = f'export JAVA_HOME="{java_home}"'

    # Update shell config
    shell_configs = [
        Path.home() / ".zshrc",
        Path.home() / ".bash_profile",
        Path.home() / ".bashrc",
    ]

    # If none of the config files exist, create .zshrc
    if not any(config.exists() for config in shell_configs):
        zshrc = Path.home() / ".zshrc"
        zshrc.touch()  # Create empty .zshrc if it doesn't exist
        logger.info(f"ℹ️  Created {zshrc} as no shell config files were found.")

    config_updated = False
    for config in shell_configs:
        try:
            if not config.exists():
                continue

            content = config.read_text()
            lines = content.splitlines()
            new_lines = []

            if path_line not in content:
                new_lines.append(path_line)
            if java_home_line not in content:
                new_lines.append(java_home_line)

            if new_lines:
                with config.open("a") as f:
                    for line in new_lines:
                        f.write(f"\n{line}")
                logger.info(f"🔧 Updated {config} with JAVA_HOME and PATH settings.")
                config_updated = True

        except (IOError, OSError) as e:
            logger.warning(f"⚠️  Could not update {config}: {e}")

    # Source the configuration if it was updated
    if config_updated:
        try:
            # Try to source the most common shell config file that exists
            for config in shell_configs:
                if config.exists():
                    subprocess.run(
                        ["sh", "-c", f"source {config} 2>/dev/null || true"],
                        check=False,
                    )
                    logger.info(
                        f"🔄 Sourced {config} to update current shell environment"
                    )
                    break
        except Exception as e:
            logger.warning(f"⚠️  Could not source shell config: {e}")
            logger.info(
                "   Please restart your shell or run 'source ~/.zshrc' (or your shell's config file) for changes to take effect."
            )

    # Set environment for current process
    os.environ["JAVA_HOME"] = java_home
    os.environ["PATH"] = f"{java_bin}:{os.environ.get('PATH', '')}"

    # Verify Java is available in current session
    try:
        subprocess.run(
            ["java", "--version"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        logger.info("✅ OpenJDK 17 installation and setup completed successfully!")
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.warning(
            "⚠️  Java installation may not be immediately available in the current shell.\n"
            "   Please restart your shell or run: source ~/.zshrc (or your shell's config file)"
        )


def download_jre():
    """Download minimal JRE into cache folder"""
    system = platform.system().lower()
    dest = None

    # Get the machine architecture (e.g., 'x86_64', 'arm64')
    arch = platform.machine()
    os_name = (
        "macos"
        if system == "darwin"
        else ("windows" if system == "windows" else "linux")
    )
    ext = "zip" if system != "linux" else "tar.gz"
    zulu_url = f"https://api.azul.com/zulu/download/community/v1.0/bundles/latest?os={os_name}&arch={arch}&ext={ext}&bundle_type=jre&java_version=17"
    try:
        with urllib.request.urlopen(zulu_url) as r:
            data = json.load(r)
            url = data["url"]
    except Exception as exc:
        error_msg = f"Failed to fetch JRE metadata: {exc}"
        logger.exception(error_msg)
        raise RuntimeError(error_msg) from exc

    if "windows" in system:
        dest = CACHE_DIR / "jre.zip"
    elif "darwin" in system:
        dest = CACHE_DIR / "jre.zip"
    else:  # linux
        dest = CACHE_DIR / "jre.tar.gz"

    try:
        print(f"🌐 Downloading JRE from {url} ...")
        urllib.request.urlretrieve(url, dest)
    except Exception as exc:
        error_msg = f"Failed to download JRE archive: {exc}"
        logger.exception(error_msg)
        raise RuntimeError(error_msg) from exc

    try:
        # Extract
        if dest.suffix == ".zip":
            with zipfile.ZipFile(dest, "r") as zip_ref:
                zip_ref.extractall(JRE_DIR)
        else:
            with tarfile.open(dest, "r:gz") as tar_ref:
                tar_ref.extractall(JRE_DIR)
    except Exception as exc:
        error_msg = f"Failed to extract JRE archive: {exc}"
        logger.exception(error_msg)
        raise RuntimeError(error_msg) from exc
    finally:
        if dest.exists():
            try:
                dest.unlink()
            except Exception as unlink_exc:
                logger.warning(
                    f"Could not remove temporary JRE archive {dest}: {unlink_exc}"
                )

    # Ensure the extracted java binaries are executable (particularly for zip archives)
    try:
        for jre_root in sorted([d for d in JRE_DIR.iterdir() if d.is_dir()]):
            bin_dir = jre_root / "bin"
            if bin_dir.exists():
                for binary in bin_dir.iterdir():
                    if binary.is_file():
                        current_mode = binary.stat().st_mode
                        binary.chmod(
                            current_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
                        )
    except Exception as exc:
        error_msg = f"Failed to set executable permissions on JRE binaries: {exc}"
        logger.exception(error_msg)
        raise RuntimeError(error_msg) from exc

    print(f"✅ JRE installed to {JRE_DIR}")


def get_jre_bin():
    """Return path to java binary"""
    java_bin = find_java()
    if java_bin:
        return java_bin

    # Download and find inside extracted folder
    java_filename = "java.exe" if os.name == "nt" else "java"
    subdirs = [
        d
        for d in JRE_DIR.iterdir()
        if d.is_dir() and (d / "bin" / java_filename).exists()
    ]
    if not subdirs:
        download_jre()
        subdirs = [
            d
            for d in JRE_DIR.iterdir()
            if d.is_dir() and (d / "bin" / java_filename).exists()
        ]
    if not subdirs:
        raise RuntimeError("JRE download failed or empty.")
    java_bin = subdirs[0] / "bin" / java_filename
    if not java_bin.exists():
        raise RuntimeError(f"Java binary not found in {java_bin}")
    return str(java_bin)


def get_java_home(java_bin: str) -> str:
    """Get JAVA_HOME from Java binary path, handling symlinks and redirects on all platforms."""
    # First, check if JAVA_HOME is already set
    java_home_env = os.environ.get("JAVA_HOME")
    if java_home_env:
        java_home_path = Path(java_home_env)
        java_exe = java_home_path / "bin" / ("java.exe" if os.name == "nt" else "java")
        if java_exe.exists():
            logger.debug(f"Using JAVA_HOME from environment: {java_home_env}")
            return java_home_env

    java_bin_path = Path(java_bin)

    # Resolve symlinks/redirects on all platforms
    try:
        # Use resolve() which handles symlinks on Unix and Windows
        real_java_bin = java_bin_path.resolve()
        if real_java_bin != java_bin_path:
            logger.debug(f"Resolved Java path: {java_bin_path} -> {real_java_bin}")
            java_bin_path = real_java_bin
    except (OSError, ValueError) as e:
        logger.debug(f"Could not resolve real path: {e}")

    # Try to query Java for its home directory (works on all platforms)
    try:
        result = subprocess.run(
            [str(java_bin_path), "-XshowSettings:properties", "-version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
            timeout=10,
        )
        # Parse java.home from output (stderr is redirected to stdout)
        output = result.stdout or ""
        for line in output.splitlines():
            if "java.home" in line.lower():
                # Format: "    java.home = /path/to/java/home" or "java.home = C:\path\to\java\home"
                parts = line.split("=", 1)
                if len(parts) == 2:
                    java_home = parts[1].strip()
                    java_home_path = Path(java_home)
                    if java_home_path.exists():
                        logger.debug(
                            f"Found JAVA_HOME from Java properties: {java_home}"
                        )
                        return str(java_home_path)
    except (subprocess.TimeoutExpired, subprocess.SubprocessError, Exception) as e:
        logger.debug(f"Could not query Java for home directory: {e}")

    # Platform-specific common installation locations
    if os.name == "nt":
        # Windows common paths
        common_paths = [
            Path(os.environ.get("ProgramFiles", "C:\\Program Files")) / "Java",
            Path(os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)"))
            / "Java",
        ]
        java_exe_name = "java.exe"
    else:
        # Unix-like systems (Linux, macOS)
        common_paths = [
            Path("/usr/lib/jvm"),
            Path("/usr/java"),
            Path("/Library/Java/JavaVirtualMachines"),  # macOS
            Path("/opt/java"),
            Path.home() / ".sdkman" / "candidates" / "java",  # SDKMAN
        ]
        java_exe_name = "java"

    for java_dir in common_paths:
        if java_dir.exists():
            # Look for JDK/JRE directories
            for jdk_dir in sorted(
                java_dir.iterdir(), key=lambda p: p.name, reverse=True
            ):
                if jdk_dir.is_dir():
                    # Check various possible bin locations
                    possible_bins = [
                        jdk_dir / "bin" / java_exe_name,
                        jdk_dir / "Contents" / "Home" / "bin" / java_exe_name,  # macOS
                        jdk_dir / "jre" / "bin" / java_exe_name,
                    ]
                    for java_exe in possible_bins:
                        if java_exe.exists():
                            try:
                                if java_exe.resolve() == java_bin_path.resolve():
                                    # For macOS, return Contents/Home if it exists
                                    if (jdk_dir / "Contents" / "Home").exists():
                                        java_home = jdk_dir / "Contents" / "Home"
                                    else:
                                        java_home = jdk_dir
                                    logger.debug(
                                        f"Found JAVA_HOME in common location: {java_home}"
                                    )
                                    return str(java_home)
                            except (OSError, ValueError):
                                continue

    # Fallback: assume standard structure (bin/java -> JAVA_HOME/bin/java)
    java_home = java_bin_path.parent.parent
    logger.debug(f"Using fallback JAVA_HOME: {java_home}")
    return str(java_home)
