"""Remote GPU deployment utilities.

Shared infrastructure for deploying code to remote GPUs via bifrost/kerbal.
Used by benchmarks/leetgpu and benchmarks/gpumode.

Tiger Style:
- Frozen dataclasses for config/state (immutable data)
- Pure functions for deployment/execution (no hidden state)
- Explicit error returns via tuples (no exceptions)
- Push ifs up, fors down

Pattern:
    # Setup once per evaluation session
    config = GPUDeploymentConfig(ssh_target="user@host:22", ...)
    state, err = await setup_gpu_deployment(config, requirements=["torch", "triton"])
    if err:
        handle_error(err)

    # Fast path for each submission
    code = "def my_kernel(): ..."
    results, err = await execute_remote_python(state, code, "python test.py")
"""

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Optional

# Type checking imports to avoid circular dependencies
if TYPE_CHECKING:
    from bifrost.client import BifrostClient

logger = logging.getLogger(__name__)

# Exit codes (POSIX standard)
EXIT_SUCCESS = 0
EXIT_FAILURE = 1


@dataclass(frozen=True)
class GPUDeploymentConfig:
    """Configuration for remote GPU deployment.

    Immutable configuration - create once, use many times.
    """

    ssh_target: str
    project_subdir: str  # e.g., "research/benchmarks/leetgpu"
    ssh_key: str = "~/.ssh/id_ed25519"
    gpu_id: int = 0
    workspace_path: str = "~/.bifrost/workspaces/wafer"
    cuda_launch_blocking: bool = False

    def __post_init__(self) -> None:
        """Validate configuration (Tiger Style assertions)."""
        assert self.ssh_target, "ssh_target cannot be empty"
        assert "@" in self.ssh_target, f"ssh_target missing '@' (must be user@host:port): {self.ssh_target}"
        assert ":" in self.ssh_target, f"ssh_target missing ':' (must be user@host:port): {self.ssh_target}"
        assert self.gpu_id >= 0, f"gpu_id must be >= 0, got {self.gpu_id}"
        assert self.project_subdir, "project_subdir cannot be empty"


@dataclass(frozen=True)
class GPUDeploymentState:
    """State after successful deployment setup.

    Immutable state snapshot - setup once, reuse for all submissions.
    Contains resources needed for fast remote execution.
    """

    bifrost_client: "BifrostClient"
    workspace_path: str
    venv_python: str
    config: GPUDeploymentConfig


# Setup functions (pure computation, minimal branching)


async def connect_and_deploy(
    config: GPUDeploymentConfig,
) -> tuple[Optional["BifrostClient"], str | None, str | None]:
    """Connect to remote host and deploy codebase via bifrost.

    Phase 1 of deployment: establish connection and sync files.

    Args:
        config: Deployment configuration

    Returns:
        (bifrost_client, project_path, error): Client and path on success, error on failure
    """
    from bifrost.client import BifrostClient

    logger.debug(f"📡 Connecting to {config.ssh_target}")
    bifrost_client = BifrostClient(config.ssh_target, config.ssh_key)

    logger.info("deploying codebase via bifrost")
    workspace = bifrost_client.push(workspace_path=config.workspace_path)
    logger.debug(f"   Deployed to: {workspace}")

    # Expand path (bifrost uses ~ shorthand)
    result = bifrost_client.exec(f"echo {workspace}")
    if result.exit_code != EXIT_SUCCESS:
        return None, None, f"Failed to expand workspace path: {result.stderr}"

    workspace_path_expanded = result.stdout.strip()
    project_path = f"{workspace_path_expanded}/{config.project_subdir}"

    # Verify project subdirectory exists
    check_result = bifrost_client.exec(f"test -d {project_path}")
    if check_result.exit_code != EXIT_SUCCESS:
        return (
            None,
            None,
            f"Project subdirectory not found: {project_path}\n"
            f"Expected bifrost to push monorepo including {config.project_subdir}",
        )

    logger.debug(f"   ✅ Project path: {project_path}")
    return bifrost_client, project_path, None


async def setup_python_venv(
    bifrost_client: "BifrostClient",
    project_path: str,
    requirements: list[str],
    gpu_id: int,
    python_version: str = "3.10",
) -> tuple[str | None, str | None]:
    """Setup Python virtual environment with dependencies.

    Phase 2 of deployment: create venv and install packages.
    Uses kerbal for environment setup.

    Args:
        bifrost_client: Connected bifrost client
        project_path: Path to project directory on remote
        requirements: List of pip requirements (e.g., ["torch", "triton"])
        gpu_id: GPU ID for target detection
        python_version: Minimum Python version

    Returns:
        (venv_python_path, error): Path to venv python on success, error on failure
    """
    from kerbal import setup_python_env

    from wafer_core.utils.path_utils import get_research_root

    # Import target config
    research_root = get_research_root(Path(__file__))
    import sys

    research_root_str = str(research_root)
    if research_root_str not in sys.path:
        sys.path.insert(0, research_root_str)
    from configs.base_config import TargetConfig

    logger.debug("📦 Setting up Python environment...")

    # Get target config (hardcoded for now - could parameterize if needed)
    target = TargetConfig(
        gpu_type="B200",
        gpu_ids=[gpu_id],
        compute_capability="10.0",
        python_version=python_version,
        cuda_version="12.8",
    )

    logger.debug(f"   Target: {target.gpu_type} (CUDA {target.cuda_version})")

    torch_req = target.get_torch_requirement()
    index_flags = target.get_uv_index_flags()

    # Create venv if needed
    venv_check = bifrost_client.exec(f"test -d {project_path}/.venv")
    if venv_check.exit_code != EXIT_SUCCESS:
        logger.debug("   Creating virtual environment...")
        create_venv_cmd = f"""
        export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
        cd {project_path}
        uv venv
        """
        result = bifrost_client.exec(create_venv_cmd)
        if result.exit_code != EXIT_SUCCESS:
            return None, f"Failed to create venv: {result.stderr}"
        logger.debug("   ✅ Virtual environment created")

    # Install PyTorch separately if custom index needed
    if index_flags:
        logger.debug("   Installing PyTorch...")
        install_torch_cmd = f"""
        export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
        cd {project_path}
        uv pip install --python .venv/bin/python {index_flags} "{torch_req}"
        """
        result = bifrost_client.exec(install_torch_cmd)
        if result.exit_code != EXIT_SUCCESS:
            return None, f"Failed to install PyTorch: {result.stderr}"
        logger.debug("   ✅ PyTorch installed")

    # Prepare requirements list
    other_requirements = list(requirements)  # Copy to avoid mutation
    if not index_flags:
        # Include torch with other deps if no special index needed
        other_requirements.insert(0, torch_req)

    # Install remaining dependencies via kerbal
    if other_requirements:
        logger.debug(f"   Installing dependencies: {', '.join(other_requirements)}")
        setup_python_env(
            bifrost_client,
            project_path,
            requirements=other_requirements,
            python_version=f">={python_version}",
        )

    venv_python = f"{project_path}/.venv/bin/python"
    logger.debug(f"   ✅ Python: {venv_python}")

    return venv_python, None


async def setup_gpu_deployment(
    config: GPUDeploymentConfig, requirements: list[str], python_version: str = "3.10"
) -> tuple[GPUDeploymentState | None, str | None]:
    """Complete deployment setup (Phase 1).

    One-time setup: connect, deploy codebase, setup Python environment.
    Returns immutable state for fast subsequent operations.

    Args:
        config: Deployment configuration
        requirements: Python packages to install (e.g., ["triton", "numpy"])
        python_version: Minimum Python version

    Returns:
        (state, error): Deployment state on success, error on failure

    Example:
        >>> config = GPUDeploymentConfig(
        ...     ssh_target="user@host:22",
        ...     project_subdir="research/benchmarks/leetgpu",
        ... )
        >>> state, err = await setup_gpu_deployment(
        ...     config,
        ...     requirements=["triton", "numpy", "nvidia-cutlass-dsl==4.3.0.dev0"]
        ... )
        >>> if err:
        ...     print(f"Setup failed: {err}")
        ... else:
        ...     # Use state for fast remote execution
        ...     result, err = await execute_remote_python(state, code, "test.py")
    """
    logger.info("gpu deployment setup")

    # Step 1: Connect and deploy codebase
    bifrost_client, project_path, err = await connect_and_deploy(config)
    if err:
        return None, err
    # Tiger Style: Assert non-None after error return
    assert bifrost_client is not None, "connect_and_deploy returned no error but bifrost_client is None"
    assert project_path is not None, "connect_and_deploy returned no error but project_path is None"

    # Step 2: Setup Python environment
    venv_python, err = await setup_python_venv(
        bifrost_client, project_path, requirements, config.gpu_id, python_version
    )
    if err:
        return None, err
    # Tiger Style: Assert non-None after error return
    assert venv_python is not None, "setup_python_venv returned no error but venv_python is None"

    logger.info("deployment setup complete")

    # Return immutable state
    state = GPUDeploymentState(
        bifrost_client=bifrost_client,
        workspace_path=project_path,
        venv_python=venv_python,
        config=config,
    )

    return state, None


# Execution functions (pure, operate on state)


def write_remote_file(bifrost_client: "BifrostClient", file_path: str, content: str) -> str | None:
    """Write content to remote file.

    Args:
        bifrost_client: Connected bifrost client
        file_path: Remote file path (absolute)
        content: File content

    Returns:
        error: Error message on failure, None on success
    """
    # Use heredoc for safe escaping (handles quotes, newlines, etc.)
    cmd = f"cat > '{file_path}' << 'EOF_GPU_DEPLOY'\n{content}\nEOF_GPU_DEPLOY"
    result = bifrost_client.exec(cmd)

    if result.exit_code != EXIT_SUCCESS:
        return f"Failed to write file {file_path}: {result.stderr}"

    return None


async def execute_remote_command(
    bifrost_client: "BifrostClient", command: str, timeout_seconds: int = 300
) -> tuple[object | None, str | None]:
    """Execute command on remote host.

    Args:
        bifrost_client: Connected bifrost client
        command: Shell command to execute
        timeout_seconds: Command timeout

    Returns:
        (result, error): Command result on success, error on failure

    Note:
        result has .exit_code, .stdout, .stderr attributes
    """
    result = bifrost_client.exec(command)

    if result.exit_code != EXIT_SUCCESS:
        error_msg = f"Command failed (exit code {result.exit_code})\n"
        error_msg += f"Command: {command}\n"
        error_msg += f"STDERR: {result.stderr}"
        return None, error_msg

    return result, None


async def execute_remote_python(
    state: GPUDeploymentState,
    code: str,
    test_command: str,
    code_path: str = "agent_code.py",
    working_dir: str | None = None,
) -> tuple[str | None, str | None]:
    """Execute Python code on remote GPU.

    Generic pattern: write code, run command, return stdout.
    Benchmark-specific logic (result parsing) happens in caller.

    Args:
        state: Deployment state from setup_gpu_deployment()
        code: Python code to execute
        test_command: Command to run (e.g., "python test.py")
        code_path: Where to write code (relative to working_dir)
        working_dir: Working directory (defaults to state.workspace_path)

    Returns:
        (stdout, error): Command stdout on success, error on failure

    Example:
        >>> code = "def solve(): return 42"
        >>> cmd = f"CUDA_VISIBLE_DEVICES={state.config.gpu_id} python eval.py"
        >>> stdout, err = await execute_remote_python(state, code, cmd)
        >>> if not err:
        ...     results = json.loads(stdout)
    """
    work_dir = working_dir or state.workspace_path
    file_path = f"{work_dir}/{code_path}"

    # Step 1: Write code to remote
    write_err = write_remote_file(state.bifrost_client, file_path, code)
    if write_err:
        return None, write_err

    # Step 2: Execute test command
    full_cmd = f"cd {work_dir} && CUDA_VISIBLE_DEVICES={state.config.gpu_id} {test_command}"
    result, err = await execute_remote_command(state.bifrost_client, full_cmd)
    if err:
        return None, err

    # Tiger Style: Assert result is not None after error check
    assert result is not None, "execute_remote_command returned no error but result is None"
    assert hasattr(result, "stdout"), "result must have stdout attribute"
    # Type narrowing: stdout should be a string
    stdout_val = str(result.stdout) if result.stdout is not None else ""

    return stdout_val, None


def parse_json_results(stdout: str, expected_keys: list[str] | None = None) -> tuple[dict | None, str | None]:
    """Parse JSON results from command output.

    Helper for parsing test results from remote execution.

    Args:
        stdout: Command stdout containing JSON
        expected_keys: Optional list of required keys to validate

    Returns:
        (parsed_dict, error): Parsed JSON on success, error on failure
    """
    try:
        results = json.loads(stdout)
    except json.JSONDecodeError as e:
        return None, f"Failed to parse JSON: {e}\nOutput: {stdout[:200]}"

    if expected_keys:
        missing = [k for k in expected_keys if k not in results]
        if missing:
            return None, f"Missing expected keys in results: {missing}"

    return results, None
