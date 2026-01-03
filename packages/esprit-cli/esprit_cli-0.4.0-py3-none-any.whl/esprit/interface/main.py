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
import sys
from typing import NoReturn

from rich.console import Console

from esprit.auth.commands import cmd_login, cmd_logout, cmd_status, cmd_whoami
from esprit.auth.credentials import get_auth_token, get_credentials, is_authenticated


console = Console()

# API Configuration
API_BASE_URL = "https://esprit.dev/api"
SUPABASE_URL = "https://frzsqgyzuikwgqsrdkgz.supabase.co"


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
            console.print("[yellow]⚠️  Quota exceeded[/]")
            console.print("[dim]Upgrade your plan at https://esprit.dev/billing[/]")
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
  esprit scan example.com --instruction "Focus on authentication"
        """,
    )
    scan_parser.add_argument(
        "target",
        help="Target URL or repository to scan",
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
