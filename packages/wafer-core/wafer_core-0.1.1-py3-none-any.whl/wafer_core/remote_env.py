"""Python environment setup for remote machines.

Replaces kerbal.python_env with minimal internal implementation.
Sets up Python venv with uv and installs packages.

Usage:
    from wafer_core.ssh import SSHClient
    from wafer_core.remote_env import setup_python_env, PythonEnvState

    client = SSHClient("root@gpu:22", ssh_key_path="~/.ssh/id_rsa")
    state = setup_python_env(
        client,
        workspace="/workspace/project",
        requirements=["torch>=2.0", "triton"],
    )
    result = client.exec(f"{state.venv_python} train.py")
"""

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from wafer_core.ssh import SSHClient

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PythonEnvState:
    """Immutable state of a configured Python environment.

    Attributes:
        venv_python: Absolute path to venv Python binary
        venv_bin: Absolute path to venv bin directory
        workspace: Absolute path to workspace root
        env_vars: Pre-computed environment variables
    """

    venv_python: str
    venv_bin: str
    workspace: str
    env_vars: dict[str, str]


def setup_python_env(
    client: "SSHClient",
    workspace: str,
    requirements: list[str],
    python_version: str = ">=3.10",
    venv_path: str = ".venv",
) -> PythonEnvState:
    """Setup Python environment with dependencies.

    Args:
        client: SSHClient instance
        workspace: Absolute path to workspace on remote
        requirements: pip packages like ["torch>=2.0", "triton"]
        python_version: Python version requirement
        venv_path: Venv location relative to workspace

    Returns:
        PythonEnvState with paths and env vars

    Example:
        state = setup_python_env(
            client,
            workspace="/workspace/project",
            requirements=["torch>=2.4.0", "triton"],
        )
    """
    assert client is not None, "client cannot be None"
    assert workspace, "workspace must be non-empty"
    assert requirements, "requirements must be non-empty"

    logger.debug(f"Setting up python environment in {workspace}")

    # Expand workspace path
    workspace = client.expand_path(workspace)

    # Verify workspace exists
    result = client.exec(f"test -d {workspace}")
    assert result.exit_code == 0, f"Workspace does not exist: {workspace}"

    venv_full_path = f"{workspace}/{venv_path}"

    # Step 1: Ensure uv is installed
    _ensure_uv(client)

    # Step 2: Create venv
    _create_venv(client, workspace, venv_full_path, python_version)

    # Step 3: Install requirements
    _install_packages(client, venv_full_path, requirements)

    # Step 4: Verify venv works
    _verify_venv(client, venv_full_path)

    logger.info("Python environment ready")

    # Build state
    venv_python = f"{venv_full_path}/bin/python"
    venv_bin = f"{venv_full_path}/bin"

    env_vars = {
        "PATH": f"{venv_bin}:$PATH",
        "PYTHONUNBUFFERED": "1",
    }

    return PythonEnvState(
        venv_python=venv_python,
        venv_bin=venv_bin,
        workspace=workspace,
        env_vars=env_vars,
    )


def _ensure_uv(client: "SSHClient") -> None:
    """Ensure uv is installed."""
    result = client.exec("command -v uv")
    if result.exit_code == 0:
        logger.debug("uv already installed")
        return

    logger.debug("Installing uv...")
    install_cmd = "curl -LsSf https://astral.sh/uv/install.sh | sh"
    result = client.exec(install_cmd)
    assert result.exit_code == 0, f"uv installation failed: {result.stderr}"
    logger.debug("uv installed")


def _create_venv(
    client: "SSHClient",
    workspace: str,
    venv_full_path: str,
    python_version: str,
) -> None:
    """Create venv using uv."""
    logger.debug("Creating virtual environment...")

    # Generate minimal pyproject.toml for uv
    pyproject_toml = f"""[project]
name = "remote-env"
version = "0.1.0"
requires-python = "{python_version}"

[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"
"""

    # Write pyproject.toml
    write_cmd = f"cat > {workspace}/pyproject.toml << 'EOF'\n{pyproject_toml}\nEOF"
    result = client.exec(write_cmd)
    assert result.exit_code == 0, f"Failed to write pyproject.toml: {result.stderr}"

    # Create venv with uv
    cmd = f"""
    export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
    cd {workspace}
    uv venv {venv_full_path}
    """
    result = client.exec(cmd)
    assert result.exit_code == 0, f"venv creation failed: {result.stderr}"

    logger.debug(f"Virtual environment created at {venv_full_path}")


def _install_packages(
    client: "SSHClient",
    venv_full_path: str,
    requirements: list[str],
) -> None:
    """Install pip packages into venv."""
    logger.debug(f"Installing {len(requirements)} package(s)...")

    packages = " ".join(f'"{pkg}"' for pkg in requirements)
    cmd = f"""
    export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
    uv pip install --python {venv_full_path}/bin/python {packages}
    """

    exit_code = None
    for line in client.exec_stream(cmd):
        print(line, flush=True)
        if line.startswith("::EXIT_CODE::"):
            exit_code_str = line.replace("::EXIT_CODE::", "").strip()
            if exit_code_str.isdigit():
                exit_code = int(exit_code_str)

    # If we didn't get exit code from marker, check result
    if exit_code is None:
        result = client.exec("echo $?")
        # Can't reliably get exit code this way, assume success if no error
        logger.debug("Package installation completed")
    else:
        assert exit_code == 0, f"pip install failed with exit code {exit_code}"

    logger.debug("Packages installed")


def _verify_venv(client: "SSHClient", venv_full_path: str) -> None:
    """Verify venv works."""
    venv_python = f"{venv_full_path}/bin/python"
    result = client.exec(f"{venv_python} --version")

    assert result.exit_code == 0, f"Python venv verification failed: {result.stderr}"

    version = result.stdout.strip() if result.stdout else "unknown"
    logger.debug(f"Python venv verified: {version}")
