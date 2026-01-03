import json
import logging
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional
from uuid import uuid4


if TYPE_CHECKING:
    from collections.abc import Callable


logger = logging.getLogger(__name__)

# Supabase streaming for optional cloud integration
_supabase_client = None


def _is_sandbox_mode() -> bool:
    return os.getenv("ESPRIT_SANDBOX_MODE", "false").lower() == "true"


def _get_scan_id() -> str | None:
    return os.getenv("SCAN_ID")


def _get_supabase_client():
    global _supabase_client
    if _supabase_client is not None:
        return _supabase_client

    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY")

    if not supabase_url or not supabase_key:
        return None

    try:
        from supabase import create_client
        _supabase_client = create_client(supabase_url, supabase_key)
        return _supabase_client
    except Exception as e:
        logger.warning(f"Failed to create Supabase client: {e}")
        return None


def _stream_to_supabase(
    level: str,
    message: str,
    event_type: str | None = None,
    metadata: dict[str, Any] | None = None,
    max_length: int = 10000,  # Default 10KB, can be increased for final report
) -> None:
    """Stream a log entry to Supabase for web frontend display (optional)."""
    # Only stream if in sandbox mode or if Supabase is explicitly configured
    if not _is_sandbox_mode() and not os.getenv("SUPABASE_URL"):
        return

    scan_id = _get_scan_id()
    if not scan_id:
        return

    client = _get_supabase_client()
    if not client:
        return

    try:
        log_entry = {
            "scan_id": scan_id,
            "level": level,
            "message": message[:max_length] if len(message) > max_length else message,
            "timestamp": datetime.now(UTC).isoformat(),
            "metadata": json.dumps(metadata or {}),
        }

        if event_type:
            log_entry["event_type"] = event_type

        client.table("scan_logs").insert(log_entry).execute()
    except Exception as e:
        logger.warning(f"Failed to stream to Supabase: {e}")


_global_tracer: Optional["Tracer"] = None


def get_global_tracer() -> Optional["Tracer"]:
    return _global_tracer


def set_global_tracer(tracer: "Tracer") -> None:
    global _global_tracer  # noqa: PLW0603
    _global_tracer = tracer


class Tracer:
    def __init__(self, run_name: str | None = None):
        self.run_name = run_name
        self.run_id = run_name or f"run-{uuid4().hex[:8]}"
        self.start_time = datetime.now(UTC).isoformat()
        self.end_time: str | None = None

        self.agents: dict[str, dict[str, Any]] = {}
        self.tool_executions: dict[int, dict[str, Any]] = {}
        self.chat_messages: list[dict[str, Any]] = []

        self.vulnerability_reports: list[dict[str, Any]] = []
        self.final_scan_result: str | None = None

        self.scan_results: dict[str, Any] | None = None
        self.scan_config: dict[str, Any] | None = None
        self.run_metadata: dict[str, Any] = {
            "run_id": self.run_id,
            "run_name": self.run_name,
            "start_time": self.start_time,
            "end_time": None,
            "targets": [],
            "status": "running",
        }
        self._run_dir: Path | None = None
        self._next_execution_id = 1
        self._next_message_id = 1
        self._saved_vuln_ids: set[str] = set()

        self.vulnerability_found_callback: Callable[[str, str, str, str], None] | None = None

    def set_run_name(self, run_name: str) -> None:
        self.run_name = run_name
        self.run_id = run_name

    def get_run_dir(self) -> Path:
        if self._run_dir is None:
            runs_dir = Path.cwd() / "esprit_runs"
            runs_dir.mkdir(exist_ok=True)

            run_dir_name = self.run_name if self.run_name else self.run_id
            self._run_dir = runs_dir / run_dir_name
            self._run_dir.mkdir(exist_ok=True)

        return self._run_dir

    def add_vulnerability_report(
        self,
        title: str,
        content: str,
        severity: str,
    ) -> str:
        report_id = f"vuln-{len(self.vulnerability_reports) + 1:04d}"

        report = {
            "id": report_id,
            "title": title.strip(),
            "content": content.strip(),
            "severity": severity.lower().strip(),
            "timestamp": datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC"),
        }

        self.vulnerability_reports.append(report)
        logger.info(f"Added vulnerability report: {report_id} - {title}")

        if self.vulnerability_found_callback:
            self.vulnerability_found_callback(
                report_id, title.strip(), content.strip(), severity.lower().strip()
            )

        # Stream vulnerability to Supabase for web frontend (optional)
        sev = severity.lower().strip()
        level = "error" if sev in ["critical", "high"] else "warning"
        _stream_to_supabase(
            level=level,
            message=f"Vulnerability found [{sev.upper()}] {title.strip()}",
            event_type="vulnerability_found",
            metadata={
                "vuln_id": report_id,
                "severity": sev,
                "title": title.strip(),
                "description": content.strip(),
            },
        )

        self.save_run_data()
        return report_id

    def set_final_scan_result(
        self,
        content: str,
        success: bool = True,
    ) -> None:
        self.final_scan_result = content.strip()

        self.scan_results = {
            "scan_completed": True,
            "content": content,
            "success": success,
        }

        logger.info(f"Set final scan result: success={success}")

        # Calculate vulnerability summary by severity
        vuln_summary = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
        for vuln in self.vulnerability_reports:
            sev = vuln.get("severity", "info").lower()
            if sev in vuln_summary:
                vuln_summary[sev] += 1

        # Stream final report content to Supabase for Activity Feed display (optional)
        _stream_to_supabase(
            level="success" if success else "error",
            message=content.strip(),
            event_type="final_report",
            metadata={
                "success": success,
                "vulnerability_count": len(self.vulnerability_reports),
                "vuln_summary": vuln_summary,
            },
            max_length=50000,  # Allow up to 50KB for final report
        )

        # Stream scan complete status to Supabase for web frontend (optional)
        _stream_to_supabase(
            level="success" if success else "error",
            message=f"Scan {'completed successfully' if success else 'failed'}",
            event_type="scan_complete",
            metadata={
                "success": success,
                "vulnerability_count": len(self.vulnerability_reports),
                "vuln_summary": vuln_summary,
                "agent_count": len(self.agents),
                "tool_count": self.get_real_tool_count(),
            },
        )

        # Update scan record in Supabase (optional)
        if _is_sandbox_mode() or os.getenv("SUPABASE_URL"):
            scan_id = _get_scan_id()
            client = _get_supabase_client()
            if scan_id and client:
                try:
                    from esprit.tools.github_pr.pr_actions import get_modified_files
                    modified_files = get_modified_files()
                    has_modified = len(modified_files) > 0

                    # Build update data
                    final_report_truncated = content.strip()[:100000] if len(content) > 100000 else content.strip()

                    update_data = {
                        "status": "completed",
                        "completed_at": datetime.now(UTC).isoformat(),
                        "has_modified_files": has_modified,
                        "vulnerabilities_found": len(self.vulnerability_reports),
                        "critical_count": vuln_summary.get("critical", 0),
                        "high_count": vuln_summary.get("high", 0),
                        "medium_count": vuln_summary.get("medium", 0),
                        "low_count": vuln_summary.get("low", 0),
                        "final_report": final_report_truncated,
                    }

                    if has_modified:
                        update_data["pr_metadata"] = {
                            "modified_files_count": len(modified_files),
                        }

                    client.table("scans").update(update_data).eq("id", scan_id).execute()
                    logger.info(f"Updated scan {scan_id} with has_modified_files={has_modified}")
                except Exception as e:
                    logger.warning(f"Failed to update scan with modified files flag: {e}")

        self.save_run_data(mark_complete=True)

    def log_agent_creation(
        self, agent_id: str, name: str, task: str, parent_id: str | None = None
    ) -> None:
        agent_data: dict[str, Any] = {
            "id": agent_id,
            "name": name,
            "task": task,
            "status": "running",
            "parent_id": parent_id,
            "created_at": datetime.now(UTC).isoformat(),
            "updated_at": datetime.now(UTC).isoformat(),
            "tool_executions": [],
        }

        self.agents[agent_id] = agent_data

    def log_chat_message(
        self,
        content: str,
        role: str,
        agent_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> int:
        message_id = self._next_message_id
        self._next_message_id += 1

        message_data = {
            "message_id": message_id,
            "content": content,
            "role": role,
            "agent_id": agent_id,
            "timestamp": datetime.now(UTC).isoformat(),
            "metadata": metadata or {},
        }

        self.chat_messages.append(message_data)
        return message_id

    def log_tool_execution_start(self, agent_id: str, tool_name: str, args: dict[str, Any]) -> int:
        execution_id = self._next_execution_id
        self._next_execution_id += 1

        now = datetime.now(UTC).isoformat()
        execution_data = {
            "execution_id": execution_id,
            "agent_id": agent_id,
            "tool_name": tool_name,
            "args": args,
            "status": "running",
            "result": None,
            "timestamp": now,
            "started_at": now,
            "completed_at": None,
        }

        self.tool_executions[execution_id] = execution_data

        if agent_id in self.agents:
            self.agents[agent_id]["tool_executions"].append(execution_id)

        return execution_id

    def update_tool_execution(
        self, execution_id: int, status: str, result: Any | None = None
    ) -> None:
        if execution_id in self.tool_executions:
            self.tool_executions[execution_id]["status"] = status
            self.tool_executions[execution_id]["result"] = result
            self.tool_executions[execution_id]["completed_at"] = datetime.now(UTC).isoformat()

    def update_agent_status(
        self, agent_id: str, status: str, error_message: str | None = None
    ) -> None:
        if agent_id in self.agents:
            self.agents[agent_id]["status"] = status
            self.agents[agent_id]["updated_at"] = datetime.now(UTC).isoformat()
            if error_message:
                self.agents[agent_id]["error_message"] = error_message
            # Note: We don't stream agent_status here to avoid duplicates
            # base_agent.py handles all agent-related streaming (agent_start, agent_end, tool_start)

    def set_scan_config(self, config: dict[str, Any]) -> None:
        self.scan_config = config
        self.run_metadata.update(
            {
                "targets": config.get("targets", []),
                "user_instructions": config.get("user_instructions", ""),
                "max_iterations": config.get("max_iterations", 200),
            }
        )
        self.get_run_dir()

        # Stream scan start to Supabase for web frontend (optional)
        targets = config.get("targets", [])
        if targets:
            if isinstance(targets[0], dict):
                target_str = ", ".join(t.get("original", str(t)) for t in targets)
            else:
                target_str = ", ".join(str(t) for t in targets)
        else:
            target_str = "No targets specified"
        _stream_to_supabase(
            level="info",
            message=f"Starting penetration test on: {target_str}",
            event_type="scan_start",
            metadata={
                "targets": targets,
                "max_iterations": config.get("max_iterations", 200),
                "run_name": self.run_name,
            },
        )

    def save_run_data(self, mark_complete: bool = False) -> None:
        try:
            run_dir = self.get_run_dir()
            if mark_complete:
                self.end_time = datetime.now(UTC).isoformat()

            if self.final_scan_result:
                penetration_test_report_file = run_dir / "penetration_test_report.md"
                with penetration_test_report_file.open("w", encoding="utf-8") as f:
                    f.write("# Security Penetration Test Report\n\n")
                    f.write(
                        f"**Generated:** {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n"
                    )
                    f.write(f"{self.final_scan_result}\n")
                logger.info(
                    f"Saved final penetration test report to: {penetration_test_report_file}"
                )

            if self.vulnerability_reports:
                vuln_dir = run_dir / "vulnerabilities"
                vuln_dir.mkdir(exist_ok=True)

                new_reports = [
                    report
                    for report in self.vulnerability_reports
                    if report["id"] not in self._saved_vuln_ids
                ]

                for report in new_reports:
                    vuln_file = vuln_dir / f"{report['id']}.md"
                    with vuln_file.open("w", encoding="utf-8") as f:
                        f.write(f"# {report['title']}\n\n")
                        f.write(f"**ID:** {report['id']}\n")
                        f.write(f"**Severity:** {report['severity'].upper()}\n")
                        f.write(f"**Found:** {report['timestamp']}\n\n")
                        f.write("## Description\n\n")
                        f.write(f"{report['content']}\n")
                    self._saved_vuln_ids.add(report["id"])

                if self.vulnerability_reports:
                    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
                    sorted_reports = sorted(
                        self.vulnerability_reports,
                        key=lambda x: (severity_order.get(x["severity"], 5), x["timestamp"]),
                    )

                    vuln_csv_file = run_dir / "vulnerabilities.csv"
                    with vuln_csv_file.open("w", encoding="utf-8", newline="") as f:
                        import csv

                        fieldnames = ["id", "title", "severity", "timestamp", "file"]
                        writer = csv.DictWriter(f, fieldnames=fieldnames)
                        writer.writeheader()

                        for report in sorted_reports:
                            writer.writerow(
                                {
                                    "id": report["id"],
                                    "title": report["title"],
                                    "severity": report["severity"].upper(),
                                    "timestamp": report["timestamp"],
                                    "file": f"vulnerabilities/{report['id']}.md",
                                }
                            )

                if new_reports:
                    logger.info(
                        f"Saved {len(new_reports)} new vulnerability report(s) to: {vuln_dir}"
                    )
                logger.info(f"Updated vulnerability index: {vuln_csv_file}")

            logger.info(f"📊 Essential scan data saved to: {run_dir}")

        except (OSError, RuntimeError):
            logger.exception("Failed to save scan data")

    def _calculate_duration(self) -> float:
        try:
            start = datetime.fromisoformat(self.start_time.replace("Z", "+00:00"))
            if self.end_time:
                end = datetime.fromisoformat(self.end_time.replace("Z", "+00:00"))
                return (end - start).total_seconds()
        except (ValueError, TypeError):
            pass
        return 0.0

    def get_agent_tools(self, agent_id: str) -> list[dict[str, Any]]:
        return [
            exec_data
            for exec_data in self.tool_executions.values()
            if exec_data.get("agent_id") == agent_id
        ]

    def get_real_tool_count(self) -> int:
        return sum(
            1
            for exec_data in self.tool_executions.values()
            if exec_data.get("tool_name") not in ["scan_start_info", "subagent_start_info"]
        )

    def get_total_llm_stats(self) -> dict[str, Any]:
        from esprit.tools.agents_graph.agents_graph_actions import _agent_instances

        total_stats = {
            "input_tokens": 0,
            "output_tokens": 0,
            "cached_tokens": 0,
            "cache_creation_tokens": 0,
            "cost": 0.0,
            "requests": 0,
            "failed_requests": 0,
        }

        for agent_instance in _agent_instances.values():
            if hasattr(agent_instance, "llm") and hasattr(agent_instance.llm, "_total_stats"):
                agent_stats = agent_instance.llm._total_stats
                total_stats["input_tokens"] += agent_stats.input_tokens
                total_stats["output_tokens"] += agent_stats.output_tokens
                total_stats["cached_tokens"] += agent_stats.cached_tokens
                total_stats["cache_creation_tokens"] += agent_stats.cache_creation_tokens
                total_stats["cost"] += agent_stats.cost
                total_stats["requests"] += agent_stats.requests
                total_stats["failed_requests"] += agent_stats.failed_requests

        total_stats["cost"] = round(total_stats["cost"], 4)

        return {
            "total": total_stats,
            "total_tokens": total_stats["input_tokens"] + total_stats["output_tokens"],
        }

    def cleanup(self) -> None:
        self.save_run_data(mark_complete=True)
