"""
GitHub PR creation actions for Esprit.

Creates pull requests with security fixes after a scan completes.
Uses the GitHub REST API with installation tokens.
"""

import base64
import logging
import os
import subprocess
from pathlib import Path
from typing import Any

import httpx

from esprit.tools.registry import register_tool

logger = logging.getLogger(__name__)

# GitHub API base URL
GITHUB_API_URL = "https://api.github.com"


def _get_github_headers(token: str) -> dict[str, str]:
    """Get headers for GitHub API requests."""
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def _build_file_info(workspace: Path, file_path: str, status: str) -> dict[str, Any]:
    """Build file info dict with content for non-deleted files."""
    file_info: dict[str, Any] = {
        "path": file_path,
        "status": status,
    }

    # Read content for non-deleted files
    if status != "deleted":
        full_path = workspace / file_path
        if full_path.exists():
            try:
                file_info["content"] = full_path.read_text()
            except (OSError, UnicodeDecodeError) as e:
                logger.warning(f"Could not read file {file_path}: {e}")
                file_info["content"] = None

    return file_info


def _parse_repo_url(repo_url: str) -> tuple[str, str]:
    """
    Parse repo URL to get owner and repo name.

    Handles formats like:
    - github.com/owner/repo
    - https://github.com/owner/repo
    - owner/repo
    """
    # Remove protocol and domain if present
    url = repo_url.replace("https://", "").replace("http://", "")
    url = url.replace("github.com/", "")
    url = url.rstrip("/").rstrip(".git")

    parts = url.split("/")
    if len(parts) >= 2:
        return parts[0], parts[1]
    raise ValueError(f"Invalid repo URL format: {repo_url}")


def get_modified_files(workspace_path: str = "/workspace/repo") -> list[dict[str, Any]]:
    """
    Get list of files modified or created in the workspace.

    Uses both git diff (for tracked file changes) and git status (for untracked files).

    Returns list of dicts with:
    - path: relative file path
    - status: 'modified', 'added', or 'deleted'
    - content: file content (for modified/added files)
    """
    workspace = Path(workspace_path)
    if not workspace.exists():
        # Fallback to current directory if workspace not found (e.g. running locally)
        workspace = Path(".")
        if not workspace_path or workspace_path == "/workspace/repo":
            logger.info(f"Workspace path {workspace_path} not found, falling back to current directory")
        else:
            logger.warning(f"Workspace path {workspace_path} not found, falling back to current directory")

    try:
        # Track files we've seen to avoid duplicates
        seen_files: set[str] = set()
        modified_files: list[dict[str, Any]] = []

        # 1. Get tracked file changes with git diff
        diff_result = subprocess.run(
            ["git", "diff", "--name-status", "HEAD"],
            cwd=workspace,
            capture_output=True,
            text=True,
            check=False,
        )

        if diff_result.returncode == 0 and diff_result.stdout.strip():
            for line in diff_result.stdout.strip().split("\n"):
                if not line.strip():
                    continue
                parts = line.split(maxsplit=1)
                if len(parts) < 2:
                    continue

                status_code, file_path = parts[0], parts[1]
                file_path = file_path.strip()

                if file_path in seen_files:
                    continue
                seen_files.add(file_path)

                # Map git diff status codes
                if status_code == "M":
                    status = "modified"
                elif status_code == "A":
                    status = "added"
                elif status_code == "D":
                    status = "deleted"
                else:
                    status = "modified"

                file_info = _build_file_info(workspace, file_path, status)
                modified_files.append(file_info)

        # 2. Get untracked and staged files with git status --porcelain
        # This catches NEW files that git diff doesn't show
        status_result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=workspace,
            capture_output=True,
            text=True,
            check=False,
        )

        if status_result.returncode == 0 and status_result.stdout.strip():
            for line in status_result.stdout.strip().split("\n"):
                if not line.strip():
                    continue

                # git status --porcelain format: XY filename
                # X = index status, Y = work tree status
                if len(line) < 3:
                    continue

                status_code = line[:2]
                file_path = line[3:].strip()

                # Handle renamed files (R  old -> new)
                if " -> " in file_path:
                    file_path = file_path.split(" -> ")[1]

                if file_path in seen_files:
                    continue
                seen_files.add(file_path)

                # Map git status codes
                if status_code == "??":
                    status = "added"  # Untracked file (new)
                elif status_code.startswith("A") or status_code.endswith("A"):
                    status = "added"
                elif status_code.startswith("D") or status_code.endswith("D"):
                    status = "deleted"
                elif status_code.startswith("M") or status_code.endswith("M"):
                    status = "modified"
                else:
                    status = "modified"

                file_info = _build_file_info(workspace, file_path, status)
                modified_files.append(file_info)

        logger.info(f"Found {len(modified_files)} modified/new files in {workspace}")
        return modified_files

    except subprocess.SubprocessError as e:
        logger.error(f"Git command failed: {e}")
        return []


async def _get_default_branch_sha(
    client: httpx.AsyncClient,
    owner: str,
    repo: str,
    headers: dict[str, str],
    branch: str = "main",
) -> str | None:
    """Get the SHA of the default branch HEAD."""
    try:
        # Try main first, then master
        for branch_name in [branch, "main", "master"]:
            response = await client.get(
                f"{GITHUB_API_URL}/repos/{owner}/{repo}/git/ref/heads/{branch_name}",
                headers=headers,
            )
            if response.status_code == 200:
                return response.json()["object"]["sha"]
        return None
    except httpx.RequestError as e:
        logger.error(f"Failed to get branch SHA: {e}")
        return None


async def _create_branch(
    client: httpx.AsyncClient,
    owner: str,
    repo: str,
    headers: dict[str, str],
    branch_name: str,
    from_sha: str,
) -> bool:
    """Create a new branch from a SHA."""
    try:
        response = await client.post(
            f"{GITHUB_API_URL}/repos/{owner}/{repo}/git/refs",
            headers=headers,
            json={
                "ref": f"refs/heads/{branch_name}",
                "sha": from_sha,
            },
        )
        if response.status_code == 201:
            logger.info(f"Created branch: {branch_name}")
            return True
        elif response.status_code == 422:
            # Branch might already exist
            logger.info(f"Branch {branch_name} may already exist")
            return True
        else:
            logger.error(f"Failed to create branch: {response.text}")
            return False
    except httpx.RequestError as e:
        logger.error(f"Failed to create branch: {e}")
        return False


async def _get_file_sha(
    client: httpx.AsyncClient,
    owner: str,
    repo: str,
    headers: dict[str, str],
    file_path: str,
    branch: str,
) -> str | None:
    """Get the SHA of an existing file (needed for updates)."""
    try:
        response = await client.get(
            f"{GITHUB_API_URL}/repos/{owner}/{repo}/contents/{file_path}",
            headers=headers,
            params={"ref": branch},
        )
        if response.status_code == 200:
            return response.json().get("sha")
        return None
    except httpx.RequestError:
        return None


async def _update_file(
    client: httpx.AsyncClient,
    owner: str,
    repo: str,
    headers: dict[str, str],
    file_path: str,
    content: str,
    message: str,
    branch: str,
    file_sha: str | None = None,
) -> bool:
    """Create or update a file on a branch."""
    try:
        # If we don't have the SHA, try to get it
        if file_sha is None:
            file_sha = await _get_file_sha(client, owner, repo, headers, file_path, branch)

        payload: dict[str, Any] = {
            "message": message,
            "content": base64.b64encode(content.encode()).decode(),
            "branch": branch,
        }

        if file_sha:
            payload["sha"] = file_sha

        response = await client.put(
            f"{GITHUB_API_URL}/repos/{owner}/{repo}/contents/{file_path}",
            headers=headers,
            json=payload,
        )

        if response.status_code in (200, 201):
            logger.info(f"Updated file: {file_path}")
            return True
        else:
            logger.error(f"Failed to update file {file_path}: {response.text}")
            return False

    except httpx.RequestError as e:
        logger.error(f"Failed to update file {file_path}: {e}")
        return False


async def _create_pull_request(
    client: httpx.AsyncClient,
    owner: str,
    repo: str,
    headers: dict[str, str],
    title: str,
    body: str,
    head: str,
    base: str = "main",
) -> dict[str, Any] | None:
    """Create a pull request."""
    try:
        response = await client.post(
            f"{GITHUB_API_URL}/repos/{owner}/{repo}/pulls",
            headers=headers,
            json={
                "title": title,
                "body": body,
                "head": head,
                "base": base,
            },
        )

        if response.status_code == 201:
            data = response.json()
            logger.info(f"Created PR #{data['number']}: {data['html_url']}")
            return {
                "number": data["number"],
                "url": data["html_url"],
                "state": data["state"],
            }
        else:
            logger.error(f"Failed to create PR: {response.text}")
            return None

    except httpx.RequestError as e:
        logger.error(f"Failed to create PR: {e}")
        return None


@register_tool(sandbox_execution=False)
def create_fix_pr(
    repo_url: str | None = None,
    branch_name: str | None = None,
    title: str | None = None,
    description: str | None = None,
    workspace_path: str = "/workspace/repo",
    agent_state: Any = None,
) -> dict[str, Any]:
    """
    Create a pull request with security fixes from the current workspace.

    This tool:
    1. Detects modified files in the workspace using git
    2. Creates a new branch from main
    3. Commits all changes to the branch
    4. Opens a pull request

    Args:
        repo_url: GitHub repo URL (auto-detected from GITHUB_REPO_URL env if not provided)
        branch_name: Branch name for fixes (default: esprit/security-fixes-{scan_id})
        title: PR title (default: "Security fixes from Esprit scan")
        description: PR description/body
        workspace_path: Path to the git workspace

    Returns:
        Dict with PR URL and details, or error message
    """
    import asyncio

    # Get GitHub token from environment
    github_token = os.environ.get("GITHUB_TOKEN")
    if not github_token:
        return {
            "success": False,
            "error": "GITHUB_TOKEN environment variable not set",
        }

    # Get repo URL from environment if not provided
    if not repo_url:
        repo_url = os.environ.get("GITHUB_REPO_URL")
        if not repo_url:
            return {
                "success": False,
                "error": "repo_url not provided and GITHUB_REPO_URL not set",
            }

    # Parse repo owner and name
    try:
        owner, repo = _parse_repo_url(repo_url)
    except ValueError as e:
        return {"success": False, "error": str(e)}

    # Get modified files
    modified_files = get_modified_files(workspace_path)

    if not modified_files:
        return {
            "success": False,
            "error": "No modified files found in workspace. Nothing to commit.",
        }

    # Generate branch name
    scan_id = os.environ.get("SCAN_ID", "unknown")[:8]
    if not branch_name:
        branch_name = f"esprit/security-fixes-{scan_id}"

    # Generate default title and description
    if not title:
        title = f"Security fixes from Esprit scan"

    if not description:
        # Build description from modified files
        file_list = "\n".join([f"- `{f['path']}` ({f['status']})" for f in modified_files])
        description = f"""## Security Fixes

This PR contains automated security fixes generated by Esprit.

### Modified Files
{file_list}

### Scan Details
- Scan ID: `{scan_id}`
- Files changed: {len(modified_files)}

---
*This PR was automatically generated by [Esprit](https://github.com/esprit-security/esprit)*
"""

    async def _create_pr():
        headers = _get_github_headers(github_token)

        async with httpx.AsyncClient(timeout=30.0) as client:
            # Get main branch SHA
            base_sha = await _get_default_branch_sha(client, owner, repo, headers)
            if not base_sha:
                return {
                    "success": False,
                    "error": "Could not get main branch SHA",
                }

            # Create feature branch
            branch_created = await _create_branch(
                client, owner, repo, headers, branch_name, base_sha
            )
            if not branch_created:
                return {
                    "success": False,
                    "error": f"Could not create branch: {branch_name}",
                }

            # Commit each modified file
            files_committed = 0
            for file_info in modified_files:
                if file_info["status"] == "deleted":
                    # TODO: Handle file deletion
                    continue

                content = file_info.get("content")
                if not content:
                    continue

                commit_msg = f"fix: security fix for {file_info['path']}"

                success = await _update_file(
                    client, owner, repo, headers,
                    file_info["path"],
                    content,
                    commit_msg,
                    branch_name,
                )

                if success:
                    files_committed += 1

            if files_committed == 0:
                return {
                    "success": False,
                    "error": "No files were committed",
                }

            # Create pull request
            pr_result = await _create_pull_request(
                client, owner, repo, headers,
                title, description, branch_name, "main"
            )

            if pr_result:
                return {
                    "success": True,
                    "pr_url": pr_result["url"],
                    "pr_number": pr_result["number"],
                    "branch": branch_name,
                    "files_committed": files_committed,
                    "message": f"Created PR #{pr_result['number']} with {files_committed} file(s)",
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to create pull request",
                    "branch": branch_name,
                    "files_committed": files_committed,
                }

    # Run async function - handle case where we're already in an event loop
    def _run_async():
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # No running loop, safe to use asyncio.run()
            return asyncio.run(_create_pr())

        # Already in a running loop - run in a thread to avoid conflict
        import concurrent.futures

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(asyncio.run, _create_pr())
            return future.result(timeout=120)

    try:
        return _run_async()
    except Exception as e:
        logger.exception("Error creating PR")
        return {
            "success": False,
            "error": f"Error creating PR: {str(e)}",
        }
