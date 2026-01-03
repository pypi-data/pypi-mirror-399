"""GPU execution tool for LM agents.

Provides a tool for agents to run Python files on remote GPUs.

Tiger Style:
- Async functions for I/O
- Pure functions where possible
- Explicit error handling via ToolResult
"""

from pathlib import Path

from rollouts.dtypes import ToolResult

from wafer_core.utils.kernel_utils.targets.config import BaremetalTarget, VMTarget
from wafer_core.utils.workspace_tools import validate_path


async def run_file(
    filepath: str,
    args: list[str] | None,
    workspace_dir: Path,
    target: BaremetalTarget | VMTarget,
    gpu_id: int | None = None,
) -> ToolResult:
    """Run Python file on remote GPU.

    Tool function for LM agents to execute Python code on GPUs.

    Args:
        filepath: Path to Python file relative to workspace
        args: Command line arguments to pass to script
        workspace_dir: Local workspace directory containing the file
        target: GPU target configuration (must have docker_image)
        gpu_id: Optional GPU ID override

    Returns:
        ToolResult with stdout on success, error on failure

    Example:
        >>> result = await run_file(
        ...     "kernel.py",
        ...     ["--test"],
        ...     workspace_dir,
        ...     target,
        ... )
        >>> if not result.is_error:
        ...     print(result.content)  # stdout
    """
    from bifrost.async_client import AsyncBifrostClient

    # Validate path
    path, err = validate_path(filepath, workspace_dir)
    if err:
        return ToolResult(is_error=True, content="", error=err)

    assert path is not None

    # Check file exists
    if not path.exists():
        return ToolResult(is_error=True, content="", error=f"File not found: {filepath}")

    if not path.is_file():
        return ToolResult(is_error=True, content="", error=f"Not a file: {filepath}")

    # Validate target
    if not target.docker_image:
        return ToolResult(
            is_error=True,
            content="",
            error=f"Target '{target.name}' does not have docker_image configured",
        )

    # Read file content
    try:
        code = path.read_text()
    except Exception as e:
        return ToolResult(is_error=True, content="", error=f"Failed to read file: {e}")

    args = args or []
    effective_gpu_id = gpu_id if gpu_id is not None else target.gpu_ids[0]
    workspace = "~/.bifrost/workspaces/gpu_run"

    try:
        async with AsyncBifrostClient(target.ssh_target, ssh_key_path=target.ssh_key) as client:
            # Create workspace
            await client.exec(f"mkdir -p {workspace}")
            expanded = await client.expand_path(workspace)

            # Write code to remote
            remote_file = f"{expanded}/{Path(filepath).name}"
            # Use heredoc for safe escaping
            write_result = await client.exec(f"cat > '{remote_file}' << 'EOF_CODE'\n{code}\nEOF_CODE")
            if write_result.exit_code != 0:
                return ToolResult(
                    is_error=True,
                    content="",
                    error=f"Failed to write file to remote: {write_result.stderr}",
                )

            # Build command
            script_args = " ".join(args)
            cmd = (
                f"pip install -q uv && "
                f"CUDA_VISIBLE_DEVICES={effective_gpu_id} uv run python {Path(filepath).name} {script_args}"
            )

            volumes = {expanded: "/workspace"}

            # Execute
            result = await client.exec_docker(
                image=target.docker_image,
                command=cmd,
                volumes=volumes,
                working_dir="/workspace",
            )

            if result.exit_code != 0:
                # Include both stdout and stderr in error case
                error_output = []
                if result.stdout:
                    error_output.append(f"stdout:\n{result.stdout}")
                if result.stderr:
                    error_output.append(f"stderr:\n{result.stderr}")
                error_msg = "\n".join(error_output) if error_output else f"Exit code {result.exit_code}"

                return ToolResult(
                    is_error=True,
                    content=result.stdout or "",
                    error=error_msg,
                )

            return ToolResult(is_error=False, content=result.stdout or "", error=None)

    except Exception as e:
        return ToolResult(is_error=True, content="", error=f"Execution failed: {e}")
