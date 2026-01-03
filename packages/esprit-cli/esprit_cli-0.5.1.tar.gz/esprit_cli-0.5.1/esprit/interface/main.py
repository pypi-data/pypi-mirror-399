#!/usr/bin/env python3
"""
Esprit CLI - AI-Powered Penetration Testing

Commands:
  esprit login          Login to Esprit (OAuth via browser)
  esprit logout         Logout and clear credentials
  esprit whoami         Show current user info
  esprit status         Show account status and usage
  esprit scan <target>  Run a penetration test scan
"""

import argparse
import asyncio
import os
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path
from typing import NoReturn

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from esprit.auth.commands import cmd_login, cmd_logout, cmd_status, cmd_whoami
from esprit.auth.credentials import get_auth_token, get_credentials, is_authenticated


console = Console()

# API Configuration
API_BASE_URL = "https://esprit.dev/api"
SUPABASE_URL = "https://frzsqgyzuikwgqsrdkgz.supabase.co"

# Local upload limits
MAX_UPLOAD_SIZE_MB = 500


def cmd_scan(args: argparse.Namespace) -> int:
    """Run a penetration test scan via Esprit cloud."""
    import uuid
    from datetime import datetime, timezone

    import requests
    from rich.live import Live
    from rich.panel import Panel
    from rich.spinner import Spinner
    from rich.text import Text

    # Check authentication
    if not is_authenticated():
        console.print()
        console.print("[red]Not logged in.[/]")
        console.print("[dim]Run 'esprit login' first.[/]")
        console.print()
        return 1

    creds = get_credentials()
    if not creds:
        console.print("[red]Error reading credentials.[/]")
        return 1

    access_token = creds.get("access_token", "")
    user_id = creds.get("user_id", "")

    target = args.target
    instruction = args.instruction

    # Check if target is a local folder (but NOT if running inside sandbox container)
    # The sandbox sets ESPRIT_SANDBOX_MODE=true and runs CLI with local paths
    if os.path.isdir(target) and not os.environ.get("ESPRIT_SANDBOX_MODE"):
        return _cmd_scan_local(target, instruction, access_token, user_id, args)

    # Determine target type
    if target.startswith("https://github.com/") or target.startswith("github.com/"):
        target_type = "public_repository"
    elif target.startswith("http://") or target.startswith("https://"):
        target_type = "url"
    else:
        target_type = "url"
        if not target.startswith("http"):
            target = f"https://{target}"

    console.print()
    console.print(f"[bold cyan]🛡️  Starting Esprit Scan[/]")
    console.print(f"[dim]Target:[/] {target}")
    if instruction:
        console.print(f"[dim]Instructions:[/] {instruction[:50]}...")
    console.print()

    # Step 1: Create scan record in Supabase
    scan_id = str(uuid.uuid4())

    headers = {
        "apikey": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZyenNxZ3l6dWlrd2dxc3Jka2d6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQxOTU5MDYsImV4cCI6MjA3OTc3MTkwNn0.ZRVsq1lCp8_HPy4EsljdYAn3GhqFfZ1yekQOV2d6KLQ",
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal",
    }

    scan_data = {
        "id": scan_id,
        "user_id": user_id,
        "target": target,
        "target_type": target_type,
        "scan_type": "standard",
        "status": "pending",
        "instruction": instruction,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    try:
        # Create scan in Supabase
        resp = requests.post(
            f"{SUPABASE_URL}/rest/v1/scans",
            headers=headers,
            json=scan_data,
            timeout=30,
        )

        if resp.status_code not in (200, 201, 204):
            console.print(f"[red]Failed to create scan: {resp.text}[/]")
            return 1

        console.print(f"[dim]Scan ID:[/] {scan_id[:8]}")

        # Step 2: Start the scan via API
        start_headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        start_resp = requests.post(
            f"{API_BASE_URL}/scans/{scan_id}/start",
            headers=start_headers,
            json={"instruction": instruction} if instruction else {},
            timeout=60,
        )

        if start_resp.status_code == 402:
            console.print()
            try:
                detail = start_resp.json().get("detail", "Subscription required")
            except Exception:
                detail = "Subscription required"
            console.print(f"[yellow]⚠️  {detail}[/]")
            console.print("[dim]Subscribe at https://esprit.dev/pricing[/]")
            console.print()
            return 1

        if start_resp.status_code != 200:
            error_detail = "Unknown error"
            try:
                error_detail = start_resp.json().get("detail", error_detail)
            except Exception:
                error_detail = start_resp.text
            console.print(f"[red]Failed to start scan: {error_detail}[/]")
            return 1

        console.print("[green]✓[/] Scan started successfully")
        console.print()
        console.print(f"[bold]View live progress at:[/]")
        console.print(f"  [cyan]https://esprit.dev/dashboard/scans/{scan_id}[/]")
        console.print()

        # Step 3: Stream logs in real-time
        if not args.no_stream:
            console.print("[dim]Streaming logs (Ctrl+C to stop watching)...[/]")
            console.print()

            return asyncio.run(_stream_scan_logs(scan_id, access_token))

        return 0

    except requests.RequestException as e:
        console.print(f"[red]Network error: {e}[/]")
        return 1
    except KeyboardInterrupt:
        console.print()
        console.print("[yellow]Scan continues in background.[/]")
        console.print(f"[dim]View at: https://esprit.dev/dashboard/scans/{scan_id}[/]")
        return 0


async def _stream_scan_logs(scan_id: str, access_token: str) -> int:
    """Stream scan logs from Supabase in real-time."""
    import time

    import requests
    from rich.text import Text

    headers = {
        "apikey": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZyenNxZ3l6dWlrd2dxc3Jka2d6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQxOTU5MDYsImV4cCI6MjA3OTc3MTkwNn0.ZRVsq1lCp8_HPy4EsljdYAn3GhqFfZ1yekQOV2d6KLQ",
        "Authorization": f"Bearer {access_token}",
    }

    last_log_id = None
    scan_complete = False

    while not scan_complete:
        try:
            # Check scan status
            scan_resp = requests.get(
                f"{SUPABASE_URL}/rest/v1/scans?id=eq.{scan_id}&select=status,vulnerabilities_found",
                headers=headers,
                timeout=10,
            )

            if scan_resp.status_code == 200:
                scans = scan_resp.json()
                if scans:
                    status = scans[0].get("status")
                    if status in ("completed", "failed", "cancelled"):
                        scan_complete = True
                        vuln_count = scans[0].get("vulnerabilities_found", 0)

                        console.print()
                        if status == "completed":
                            console.print(f"[green]✓ Scan completed![/] Found {vuln_count} vulnerabilities.")
                        elif status == "failed":
                            console.print("[red]✗ Scan failed.[/]")
                        else:
                            console.print("[yellow]⚠ Scan cancelled.[/]")

                        console.print(f"[dim]View full results: https://esprit.dev/dashboard/scans/{scan_id}[/]")
                        continue

            # Fetch new logs
            url = f"{SUPABASE_URL}/rest/v1/scan_logs?scan_id=eq.{scan_id}&order=created_at.asc"
            if last_log_id:
                url += f"&id=gt.{last_log_id}"

            logs_resp = requests.get(url, headers=headers, timeout=10)

            if logs_resp.status_code == 200:
                logs = logs_resp.json()
                for log in logs:
                    last_log_id = log.get("id")
                    level = log.get("level", "info")
                    message = log.get("message", "")
                    event_type = log.get("event_type", "")

                    # Format based on event type
                    if event_type == "vulnerability_found":
                        console.print(f"[red]🔴 VULNERABILITY:[/] {message}")
                    elif event_type == "tool_start":
                        console.print(f"[cyan]⚙️[/] {message}")
                    elif event_type == "agent_start":
                        console.print(f"[blue]🤖[/] {message}")
                    elif event_type == "thinking":
                        console.print(f"[dim]💭 {message[:100]}...[/]" if len(message) > 100 else f"[dim]💭 {message}[/]")
                    elif level == "error":
                        console.print(f"[red]❌[/] {message}")
                    elif level == "warning":
                        console.print(f"[yellow]⚠️[/] {message}")
                    elif level == "success":
                        console.print(f"[green]✓[/] {message}")
                    else:
                        console.print(f"[dim]•[/] {message}")

            await asyncio.sleep(2)  # Poll every 2 seconds

        except KeyboardInterrupt:
            console.print()
            console.print("[yellow]Stopped watching. Scan continues in background.[/]")
            return 0
        except Exception as e:
            console.print(f"[red]Error streaming logs: {e}[/]")
            await asyncio.sleep(5)

    return 0


def _cmd_scan_local(
    folder_path: str,
    instruction: str | None,
    access_token: str,
    user_id: str,
    args: argparse.Namespace,
) -> int:
    """Scan a local folder via cloud upload."""
    import uuid
    from datetime import datetime, timezone

    import requests

    folder_path = os.path.abspath(folder_path)
    folder_name = os.path.basename(folder_path)

    console.print()
    console.print("[bold cyan]🛡️  Starting Esprit Scan (Local Folder)[/]")
    console.print(f"[dim]Target:[/] {folder_path}")
    if instruction:
        console.print(f"[dim]Instructions:[/] {instruction[:50]}...")
    console.print()

    # Step 1: Compress folder
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Compressing folder...", total=None)

        tar_path = _compress_folder(folder_path)
        if not tar_path:
            console.print("[red]Failed to compress folder.[/]")
            return 1

        # Check file size
        tar_size_mb = os.path.getsize(tar_path) / (1024 * 1024)
        if tar_size_mb > MAX_UPLOAD_SIZE_MB:
            console.print(f"[red]Folder too large ({tar_size_mb:.1f}MB). Max: {MAX_UPLOAD_SIZE_MB}MB[/]")
            os.unlink(tar_path)
            return 1

        progress.update(task, description=f"Compressed ({tar_size_mb:.1f}MB)")

    # Step 2: Create scan record and get upload URL
    scan_id = str(uuid.uuid4())

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    try:
        # Get presigned upload URL
        upload_resp = requests.post(
            f"{API_BASE_URL}/uploads/presigned-url",
            headers=headers,
            json={"scan_id": scan_id},
            timeout=30,
        )

        if upload_resp.status_code == 402:
            console.print()
            try:
                detail = upload_resp.json().get("detail", "Subscription required")
            except Exception:
                detail = "Subscription required"
            console.print(f"[yellow]⚠️  {detail}[/]")
            console.print("[dim]Subscribe at https://esprit.dev/pricing[/]")
            console.print()
            os.unlink(tar_path)
            return 1

        if upload_resp.status_code != 200:
            console.print(f"[red]Failed to get upload URL: {upload_resp.text}[/]")
            os.unlink(tar_path)
            return 1

        upload_info = upload_resp.json()
        upload_url = upload_info["upload_url"]

        # Step 3: Upload to S3
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Uploading to cloud...", total=None)

            with open(tar_path, "rb") as f:
                put_resp = requests.put(
                    upload_url,
                    data=f,
                    headers={"Content-Type": "application/gzip"},
                    timeout=600,  # 10 min timeout for large uploads
                )

            if put_resp.status_code not in (200, 201):
                console.print(f"[red]Upload failed: {put_resp.status_code}[/]")
                os.unlink(tar_path)
                return 1

            progress.update(task, description="Upload complete")

        # Clean up tar file
        os.unlink(tar_path)

        # Step 4: Create scan record in Supabase
        supabase_headers = {
            "apikey": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZyenNxZ3l6dWlrd2dxc3Jka2d6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQxOTU5MDYsImV4cCI6MjA3OTc3MTkwNn0.ZRVsq1lCp8_HPy4EsljdYAn3GhqFfZ1yekQOV2d6KLQ",
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal",
        }

        scan_data = {
            "id": scan_id,
            "user_id": user_id,
            "target": folder_name,
            "target_type": "local_upload",
            "scan_type": "standard",
            "status": "pending",
            "instruction": instruction,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        resp = requests.post(
            f"{SUPABASE_URL}/rest/v1/scans",
            headers=supabase_headers,
            json=scan_data,
            timeout=30,
        )

        if resp.status_code not in (200, 201, 204):
            console.print(f"[red]Failed to create scan: {resp.text}[/]")
            return 1

        console.print(f"[dim]Scan ID:[/] {scan_id[:8]}")

        # Step 5: Start the scan
        start_resp = requests.post(
            f"{API_BASE_URL}/scans/{scan_id}/start",
            headers=headers,
            json={"instruction": instruction} if instruction else {},
            timeout=60,
        )

        if start_resp.status_code == 402:
            console.print()
            try:
                detail = start_resp.json().get("detail", "Subscription required")
            except Exception:
                detail = "Subscription required"
            console.print(f"[yellow]⚠️  {detail}[/]")
            console.print("[dim]Subscribe at https://esprit.dev/pricing[/]")
            console.print()
            return 1

        if start_resp.status_code != 200:
            error_detail = "Unknown error"
            try:
                error_detail = start_resp.json().get("detail", error_detail)
            except Exception:
                error_detail = start_resp.text
            console.print(f"[red]Failed to start scan: {error_detail}[/]")
            return 1

        console.print("[green]✓[/] Scan started successfully")
        console.print()
        console.print(f"[bold]View live progress at:[/]")
        console.print(f"  [cyan]https://esprit.dev/dashboard/scans/{scan_id}[/]")
        console.print()

        # Step 6: Stream logs
        if not args.no_stream:
            console.print("[dim]Streaming logs (Ctrl+C to stop watching)...[/]")
            console.print()
            result = asyncio.run(_stream_scan_logs(scan_id, access_token))

            # Step 7: After completion, offer to apply fixes
            if result == 0:
                _apply_fixes_prompt(scan_id, folder_path, access_token)

            return result

        return 0

    except requests.RequestException as e:
        console.print(f"[red]Network error: {e}[/]")
        return 1
    except KeyboardInterrupt:
        console.print()
        console.print("[yellow]Scan continues in background.[/]")
        console.print(f"[dim]View at: https://esprit.dev/dashboard/scans/{scan_id}[/]")
        return 0


def _compress_folder(folder_path: str) -> str | None:
    """Compress a folder to a tar.gz file, respecting .gitignore."""
    try:
        # Create temp file for the archive
        fd, tar_path = tempfile.mkstemp(suffix=".tar.gz")
        os.close(fd)

        folder_path = os.path.abspath(folder_path)
        folder_name = os.path.basename(folder_path)

        # Get list of files to exclude (from .gitignore)
        excluded_patterns = _get_gitignore_patterns(folder_path)

        with tarfile.open(tar_path, "w:gz") as tar:
            for root, dirs, files in os.walk(folder_path):
                # Filter out excluded directories
                dirs[:] = [d for d in dirs if not _should_exclude(os.path.join(root, d), folder_path, excluded_patterns)]

                for file in files:
                    file_path = os.path.join(root, file)
                    if not _should_exclude(file_path, folder_path, excluded_patterns):
                        arcname = os.path.relpath(file_path, os.path.dirname(folder_path))
                        tar.add(file_path, arcname=arcname)

        return tar_path
    except Exception as e:
        console.print(f"[red]Error compressing folder: {e}[/]")
        return None


def _get_gitignore_patterns(folder_path: str) -> list[str]:
    """Get patterns from .gitignore file."""
    patterns = [
        # Always exclude these
        ".git",
        ".git/",
        "__pycache__",
        "__pycache__/",
        "*.pyc",
        "node_modules",
        "node_modules/",
        ".env",
        ".env.*",
        "*.log",
        ".DS_Store",
        "venv",
        "venv/",
        ".venv",
        ".venv/",
    ]

    gitignore_path = os.path.join(folder_path, ".gitignore")
    if os.path.exists(gitignore_path):
        try:
            with open(gitignore_path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        patterns.append(line)
        except Exception:
            pass

    return patterns


def _should_exclude(path: str, base_path: str, patterns: list[str]) -> bool:
    """Check if a path should be excluded based on patterns."""
    rel_path = os.path.relpath(path, base_path)
    name = os.path.basename(path)

    for pattern in patterns:
        # Simple pattern matching
        if pattern.endswith("/"):
            # Directory pattern
            if os.path.isdir(path) and (name == pattern[:-1] or rel_path.startswith(pattern[:-1])):
                return True
        elif "*" in pattern:
            # Glob pattern - simple implementation
            import fnmatch
            if fnmatch.fnmatch(name, pattern) or fnmatch.fnmatch(rel_path, pattern):
                return True
        else:
            # Exact match
            if name == pattern or rel_path == pattern or rel_path.startswith(pattern + "/"):
                return True

    return False


def _apply_fixes_prompt(scan_id: str, folder_path: str, access_token: str) -> None:
    """Prompt user to apply fixes from the scan."""
    import requests
    from rich.prompt import Confirm

    headers = {
        "Authorization": f"Bearer {access_token}",
    }

    try:
        # Check if patch exists
        patch_resp = requests.get(
            f"{API_BASE_URL}/scans/{scan_id}/patch",
            headers=headers,
            timeout=30,
        )

        if patch_resp.status_code != 200:
            return

        patch_info = patch_resp.json()
        if not patch_info.get("has_patch"):
            console.print("[dim]No fixes available to apply.[/]")
            return

        console.print()
        if not Confirm.ask("Apply fixes to local folder?"):
            console.print("[dim]Fixes not applied. You can download them from the dashboard.[/]")
            return

        # Download patch
        download_url = patch_info.get("download_url")
        if not download_url:
            console.print("[red]No download URL available.[/]")
            return

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Downloading patch...", total=None)

            patch_download = requests.get(download_url, timeout=60)
            if patch_download.status_code != 200:
                console.print("[red]Failed to download patch.[/]")
                return

            patch_content = patch_download.text
            progress.update(task, description="Patch downloaded")

        # Apply patch
        console.print("Applying fixes...")

        # Try git apply first
        result = subprocess.run(
            ["git", "apply", "--stat", "-"],
            input=patch_content,
            capture_output=True,
            text=True,
            cwd=folder_path,
        )

        if result.returncode == 0:
            # Actually apply it
            subprocess.run(
                ["git", "apply", "-"],
                input=patch_content,
                capture_output=True,
                text=True,
                cwd=folder_path,
            )
            console.print("[green]✓ Fixes applied successfully![/]")
            if result.stdout:
                console.print(result.stdout)
        else:
            # Try patch command as fallback
            result = subprocess.run(
                ["patch", "-p1", "--dry-run"],
                input=patch_content,
                capture_output=True,
                text=True,
                cwd=folder_path,
            )

            if result.returncode == 0:
                subprocess.run(
                    ["patch", "-p1"],
                    input=patch_content,
                    capture_output=True,
                    text=True,
                    cwd=folder_path,
                )
                console.print("[green]✓ Fixes applied successfully![/]")
            else:
                # Save patch for manual application
                patch_path = os.path.join(folder_path, f"esprit-fixes-{scan_id[:8]}.patch")
                with open(patch_path, "w") as f:
                    f.write(patch_content)
                console.print(f"[yellow]Could not auto-apply patch. Saved to:[/]")
                console.print(f"  {patch_path}")
                console.print("[dim]Apply manually: git apply esprit-fixes-*.patch[/]")

    except Exception as e:
        console.print(f"[red]Error applying fixes: {e}[/]")


def main() -> NoReturn:
    """Main entry point for Esprit CLI."""
    parser = argparse.ArgumentParser(
        prog="esprit",
        description="Esprit - AI-Powered Penetration Testing CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  esprit login                     Login via browser (GitHub/Google OAuth)
  esprit scan https://example.com  Scan a website
  esprit scan github.com/user/repo Scan a public repository
  esprit scan ./my-project         Scan a local folder
  esprit status                    Check your usage and quota

For more info: https://esprit.dev/docs
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Login command
    login_parser = subparsers.add_parser("login", help="Login to Esprit")
    login_parser.add_argument(
        "--provider",
        choices=["github", "google"],
        default="github",
        help="OAuth provider (default: github)",
    )

    # Logout command
    subparsers.add_parser("logout", help="Logout from Esprit")

    # Whoami command
    subparsers.add_parser("whoami", help="Show current user info")

    # Status command
    subparsers.add_parser("status", help="Show account status and usage")

    # Scan command
    scan_parser = subparsers.add_parser(
        "scan",
        help="Run a penetration test scan",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  esprit scan https://example.com
  esprit scan github.com/user/repo
  esprit scan ./my-project
  esprit scan . --instruction "Focus on authentication"
        """,
    )
    scan_parser.add_argument(
        "target",
        help="Target URL, repository, or local folder to scan",
    )
    scan_parser.add_argument(
        "-i", "--instruction",
        help="Custom instructions for the scan",
    )
    scan_parser.add_argument(
        "--no-stream",
        action="store_true",
        help="Don't stream logs, just start the scan",
    )

    # Parse arguments
    args = parser.parse_args()

    # Handle commands
    if args.command == "login":
        sys.exit(cmd_login(args.provider))
    elif args.command == "logout":
        sys.exit(cmd_logout())
    elif args.command == "whoami":
        sys.exit(cmd_whoami())
    elif args.command == "status":
        sys.exit(cmd_status())
    elif args.command == "scan":
        sys.exit(cmd_scan(args))
    else:
        # No command provided - show help
        parser.print_help()
        sys.exit(0)


if __name__ == "__main__":
    main()
