from pathlib import Path
from typing import Any

from esprit.agents.base_agent import BaseAgent
from esprit.llm.config import LLMConfig


def _get_directory_tree(path: str, max_depth: int = 3, max_files: int = 100) -> str:
    """Generate a directory tree string for the given path."""
    try:
        path_obj = Path(path)
        if not path_obj.exists():
            return f"  (directory not found: {path})"

        lines = []
        file_count = 0

        def walk_dir(current_path: Path, prefix: str = "", depth: int = 0):
            nonlocal file_count
            if depth > max_depth or file_count > max_files:
                return

            try:
                entries = sorted(current_path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
            except PermissionError:
                return

            # Filter out common non-essential directories
            skip_dirs = {'.git', 'node_modules', '__pycache__', '.next', 'dist', 'build', '.venv', 'venv'}
            entries = [e for e in entries if e.name not in skip_dirs or not e.is_dir()]

            for i, entry in enumerate(entries):
                if file_count > max_files:
                    lines.append(f"{prefix}... (truncated, {max_files}+ files)")
                    return

                is_last = i == len(entries) - 1
                connector = "└── " if is_last else "├── "

                if entry.is_dir():
                    lines.append(f"{prefix}{connector}{entry.name}/")
                    new_prefix = prefix + ("    " if is_last else "│   ")
                    walk_dir(entry, new_prefix, depth + 1)
                else:
                    lines.append(f"{prefix}{connector}{entry.name}")
                    file_count += 1

        walk_dir(path_obj)
        return "\n".join(lines) if lines else "  (empty directory)"
    except Exception as e:
        return f"  (error reading directory: {e})"


class EspritAgent(BaseAgent):
    max_iterations = 10000  # Very high - budget is the real limiter

    def __init__(self, config: dict[str, Any]):
        default_modules = []

        state = config.get("state")
        if state is None or (hasattr(state, "parent_id") and state.parent_id is None):
            default_modules = ["root_agent"]

        self.default_llm_config = LLMConfig(prompt_modules=default_modules)

        super().__init__(config)

    async def execute_scan(self, scan_config: dict[str, Any]) -> dict[str, Any]:  # noqa: PLR0912
        user_instructions = scan_config.get("user_instructions", "")
        targets = scan_config.get("targets", [])

        repositories = []
        local_code = []
        urls = []
        ip_addresses = []

        for target in targets:
            target_type = target["type"]
            details = target["details"]
            workspace_subdir = details.get("workspace_subdir")
            workspace_path = f"/workspace/{workspace_subdir}" if workspace_subdir else "/workspace"

            if target_type == "repository":
                repo_url = details["target_repo"]
                cloned_path = details.get("cloned_repo_path")
                repositories.append(
                    {
                        "url": repo_url,
                        "workspace_path": workspace_path if cloned_path else None,
                    }
                )

            elif target_type == "local_code":
                original_path = details.get("target_path", "unknown")
                local_code.append(
                    {
                        "path": original_path,
                        "workspace_path": workspace_path,
                    }
                )

            elif target_type == "web_application":
                urls.append(details["target_url"])
            elif target_type == "ip_address":
                ip_addresses.append(details["target_ip"])

        task_parts = []

        if repositories:
            task_parts.append("\n\nRepositories:")
            for repo in repositories:
                if repo["workspace_path"]:
                    task_parts.append(f"- {repo['url']} (available at: {repo['workspace_path']})")
                    # Include directory structure so agent knows what's there
                    tree = _get_directory_tree(repo["workspace_path"])
                    task_parts.append(f"\n  Directory structure:\n{tree}")
                else:
                    task_parts.append(f"- {repo['url']}")

        if local_code:
            task_parts.append("\n\nLocal Codebases:")
            for code in local_code:
                # Use the actual resolved path for directory tree
                actual_path = code['path']
                task_parts.append(f"- {actual_path}")
                # Include directory structure so agent knows what's there
                tree = _get_directory_tree(actual_path)
                task_parts.append(f"\n  Directory structure:\n{tree}")

        if urls:
            task_parts.append("\n\nURLs:")
            task_parts.extend(f"- {url}" for url in urls)

        if ip_addresses:
            task_parts.append("\n\nIP Addresses:")
            task_parts.extend(f"- {ip}" for ip in ip_addresses)

        task_description = " ".join(task_parts)

        if user_instructions:
            task_description += f"\n\nSpecial instructions: {user_instructions}"

        return await self.agent_loop(task=task_description)
