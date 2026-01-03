import asyncio
import contextlib
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional


if TYPE_CHECKING:
    from esprit.telemetry.tracer import Tracer

from jinja2 import (
    Environment,
    FileSystemLoader,
    select_autoescape,
)

from esprit.llm import LLM, LLMConfig, LLMRequestFailedError
from esprit.llm.utils import clean_content
from esprit.tools import process_tool_invocations
from esprit.interface.tool_components.message_formatter import format_tool_message

from .state import AgentState


logger = logging.getLogger(__name__)

# Supabase client cache for optional cloud streaming
_supabase_client = None


def _is_sandbox_mode() -> bool:
    """Check if running in sandbox mode."""
    return os.getenv("ESPRIT_SANDBOX_MODE", "false").lower() == "true"


def _get_scan_id() -> str | None:
    """Get the scan ID from environment."""
    return os.getenv("SCAN_ID")


def _get_supabase_client():
    """Get or create Supabase client for streaming logs (optional)."""
    global _supabase_client
    if _supabase_client is not None:
        return _supabase_client

    supabase_url = os.environ.get('SUPABASE_URL')
    supabase_key = os.environ.get('SUPABASE_SERVICE_KEY')

    if not supabase_url or not supabase_key:
        return None

    try:
        from supabase import create_client
        _supabase_client = create_client(supabase_url, supabase_key)
        return _supabase_client
    except Exception:
        return None


def _sandbox_log(message: str) -> None:
    """Log message to stdout in sandbox mode for CloudWatch visibility."""
    if _is_sandbox_mode():
        print(f"[AGENT] {message}", flush=True)


def _stream_to_supabase(
    level: str,
    message: str,
    event_type: str | None = None,
    agent_id: str | None = None,
    agent_name: str | None = None,
    parent_agent_id: str | None = None,
    tool_name: str | None = None,
) -> None:
    """Stream log entry to Supabase (optional - only when configured)."""
    # Only stream if in sandbox mode or if Supabase is explicitly configured
    if not _is_sandbox_mode() and not os.environ.get('SUPABASE_URL'):
        return

    scan_id = _get_scan_id()
    if not scan_id:
        return

    client = _get_supabase_client()
    if not client:
        return

    try:
        # Truncate long messages
        truncated_message = message[:4000] if len(message) > 4000 else message

        # Build metadata
        metadata = {}
        if event_type:
            metadata['event_type'] = event_type
        if agent_id:
            metadata['agent_id'] = agent_id
        if agent_name:
            metadata['agent_name'] = agent_name
        if parent_agent_id:
            metadata['parent_agent_id'] = parent_agent_id
        if tool_name:
            metadata['tool_name'] = tool_name

        log_entry = {
            'scan_id': scan_id,
            'level': level,
            'message': truncated_message,
            'metadata': json.dumps(metadata),
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'event_type': event_type,
            'agent_id': agent_id,
            'agent_name': agent_name,
            'parent_agent_id': parent_agent_id,
            'tool_name': tool_name,
        }

        client.table('scan_logs').insert(log_entry).execute()

    except Exception as e:
        # Silently fail - don't break the scan for logging issues
        print(f"[STREAM_ERROR] {e}", flush=True)


class AgentMeta(type):
    agent_name: str
    jinja_env: Environment

    def __new__(cls, name: str, bases: tuple[type, ...], attrs: dict[str, Any]) -> type:
        new_cls = super().__new__(cls, name, bases, attrs)

        if name == "BaseAgent":
            return new_cls

        agents_dir = Path(__file__).parent
        prompt_dir = agents_dir / name

        new_cls.agent_name = name
        new_cls.jinja_env = Environment(
            loader=FileSystemLoader(prompt_dir),
            autoescape=select_autoescape(enabled_extensions=(), default_for_string=False),
        )

        return new_cls


class BaseAgent(metaclass=AgentMeta):
    max_iterations = 10000  # Very high - budget is the real limiter
    agent_name: str = ""
    jinja_env: Environment
    default_llm_config: LLMConfig | None = None

    def __init__(self, config: dict[str, Any]):
        self.config = config

        self.local_sources = config.get("local_sources", [])
        self.non_interactive = config.get("non_interactive", False)

        if "max_iterations" in config:
            self.max_iterations = config["max_iterations"]

        self.llm_config_name = config.get("llm_config_name", "default")
        self.llm_config = config.get("llm_config", self.default_llm_config)
        if self.llm_config is None:
            raise ValueError("llm_config is required but not provided")
        self.llm = LLM(self.llm_config, agent_name=self.agent_name)

        state_from_config = config.get("state")
        if state_from_config is not None:
            self.state = state_from_config
        else:
            self.state = AgentState(
                agent_name=self.agent_name,
                max_iterations=self.max_iterations,
            )

        with contextlib.suppress(Exception):
            self.llm.set_agent_identity(self.agent_name, self.state.agent_id)
        self._current_task: asyncio.Task[Any] | None = None

        from esprit.telemetry.tracer import get_global_tracer

        tracer = get_global_tracer()
        if tracer:
            tracer.log_agent_creation(
                agent_id=self.state.agent_id,
                name=self.state.agent_name,
                task=self.state.task,
                parent_id=self.state.parent_id,
            )
            if self.state.parent_id is None:
                scan_config = tracer.scan_config or {}
                exec_id = tracer.log_tool_execution_start(
                    agent_id=self.state.agent_id,
                    tool_name="scan_start_info",
                    args=scan_config,
                )
                tracer.update_tool_execution(execution_id=exec_id, status="completed", result={})

            else:
                exec_id = tracer.log_tool_execution_start(
                    agent_id=self.state.agent_id,
                    tool_name="subagent_start_info",
                    args={
                        "name": self.state.agent_name,
                        "task": self.state.task,
                        "parent_id": self.state.parent_id,
                    },
                )
                tracer.update_tool_execution(execution_id=exec_id, status="completed", result={})

        self._add_to_agents_graph()

        # Stream agent start to Supabase (optional)
        _stream_to_supabase(
            level='info',
            message=f"Agent '{self.state.agent_name}' started",
            event_type='agent_start',
            agent_id=self.state.agent_id,
            agent_name=self.state.agent_name,
            parent_agent_id=self.state.parent_id,
        )

        # Stream subagent spawn event for subagents
        if self.state.parent_id:
            _stream_to_supabase(
                level='info',
                message=f"Spawned subagent {self.state.agent_name}",
                event_type='subagent_spawn',
                agent_id=self.state.agent_id,
                agent_name=self.state.agent_name,
                parent_agent_id=self.state.parent_id,
            )

    def _add_to_agents_graph(self) -> None:
        from esprit.tools.agents_graph import agents_graph_actions

        node = {
            "id": self.state.agent_id,
            "name": self.state.agent_name,
            "task": self.state.task,
            "status": "running",
            "parent_id": self.state.parent_id,
            "created_at": self.state.start_time,
            "finished_at": None,
            "result": None,
            "llm_config": self.llm_config_name,
            "agent_type": self.__class__.__name__,
            "state": self.state.model_dump(),
        }
        agents_graph_actions._agent_graph["nodes"][self.state.agent_id] = node

        agents_graph_actions._agent_instances[self.state.agent_id] = self
        agents_graph_actions._agent_states[self.state.agent_id] = self.state

        if self.state.parent_id:
            agents_graph_actions._agent_graph["edges"].append(
                {"from": self.state.parent_id, "to": self.state.agent_id, "type": "delegation"}
            )

        if self.state.agent_id not in agents_graph_actions._agent_messages:
            agents_graph_actions._agent_messages[self.state.agent_id] = []

        if self.state.parent_id is None and agents_graph_actions._root_agent_id is None:
            agents_graph_actions._root_agent_id = self.state.agent_id

    def cancel_current_execution(self) -> None:
        if self._current_task and not self._current_task.done():
            self._current_task.cancel()
            self._current_task = None

    def _get_current_total_cost(self) -> float:
        """Get total cost across all agents in this scan."""
        from esprit.telemetry.tracer import get_global_tracer

        tracer = get_global_tracer()
        if tracer:
            stats = tracer.get_total_llm_stats()
            return stats.get("total", {}).get("cost", 0.0)
        return 0.0

    async def agent_loop(self, task: str) -> dict[str, Any]:  # noqa: PLR0912, PLR0915
        await self._initialize_sandbox_and_state(task)
        agent_short_id = self.state.agent_id[:8] if self.state.agent_id else "unknown"
        is_root = self.state.parent_id is None
        _sandbox_log(f"Agent started: {self.agent_name} ({agent_short_id}) {'[ROOT]' if is_root else '[SUB]'}")

        from esprit.telemetry.tracer import get_global_tracer

        tracer = get_global_tracer()

        while True:
            self._check_agent_messages(self.state)

            if self.state.is_waiting_for_input():
                await self._wait_for_input()
                continue

            if self.state.should_stop():
                if self.non_interactive:
                    return self.state.final_result or {}
                await self._enter_waiting_state(tracer)
                continue

            if self.state.llm_failed:
                await self._wait_for_input()
                continue

            self.state.increment_iteration()
            _sandbox_log(f"[{agent_short_id}] Iter {self.state.iteration}/{self.state.max_iterations}")

            if (
                self.state.is_approaching_max_iterations()
                and not self.state.max_iterations_warning_sent
            ):
                self.state.max_iterations_warning_sent = True
                remaining = self.state.max_iterations - self.state.iteration
                warning_msg = (
                    f"URGENT: You are approaching the maximum iteration limit. "
                    f"Current: {self.state.iteration}/{self.state.max_iterations} "
                    f"({remaining} iterations remaining). "
                    f"Please prioritize completing your required task(s) and calling "
                    f"the appropriate finish tool (finish_scan for root agent, "
                    f"agent_finish for sub-agents) as soon as possible."
                )
                self.state.add_message("user", warning_msg)

            if self.state.iteration == self.state.max_iterations - 3:
                final_warning_msg = (
                    "CRITICAL: You have only 3 iterations left! "
                    "Your next message MUST be the tool call to the appropriate "
                    "finish tool: finish_scan if you are the root agent, or "
                    "agent_finish if you are a sub-agent. "
                    "No other actions should be taken except finishing your work "
                    "immediately."
                )
                self.state.add_message("user", final_warning_msg)

            # Budget-based warnings (primary constraint, soft limits with hard stop at 130%)
            scan_budget_usd = float(os.getenv('SCAN_BUDGET_USD', '2.00'))
            current_cost = self._get_current_total_cost()
            budget_used_percent = (current_cost / scan_budget_usd * 100) if scan_budget_usd > 0 else 0
            remaining_budget = scan_budget_usd - current_cost

            # Warning at 75% budget used
            if budget_used_percent >= 75 and not self.state.budget_warning_75_sent:
                self.state.budget_warning_75_sent = True
                budget_warning_msg = (
                    f"BUDGET NOTICE: You have used ${current_cost:.2f} of your ${scan_budget_usd:.2f} budget ({budget_used_percent:.0f}%). "
                    f"About ${remaining_budget:.2f} remains. "
                    f"Consider prioritizing your most important findings."
                )
                self.state.add_message("user", budget_warning_msg)
                _sandbox_log(f"[{agent_short_id}] Budget 75%: ${current_cost:.2f}/${scan_budget_usd:.2f}")

            # Warning at 90% budget used
            if budget_used_percent >= 90 and not self.state.budget_warning_90_sent:
                self.state.budget_warning_90_sent = True
                budget_warning_msg = (
                    f"BUDGET WARNING: You have used ${current_cost:.2f} of your ${scan_budget_usd:.2f} budget ({budget_used_percent:.0f}%). "
                    f"Only ${remaining_budget:.2f} remains. "
                    f"Please start wrapping up your findings soon."
                )
                self.state.add_message("user", budget_warning_msg)
                _sandbox_log(f"[{agent_short_id}] Budget 90%: ${current_cost:.2f}/${scan_budget_usd:.2f}")

            # Urgent warning at 100% budget used (but NOT hard stop yet)
            if budget_used_percent >= 100 and not self.state.budget_warning_100_sent:
                self.state.budget_warning_100_sent = True
                budget_urgent_msg = (
                    f"BUDGET REACHED: You have used ${current_cost:.2f} which is 100% of your ${scan_budget_usd:.2f} budget. "
                    f"You should call finish_scan soon with your findings. "
                    f"You have a small grace period but please wrap up."
                )
                self.state.add_message("user", budget_urgent_msg)
                _sandbox_log(f"[{agent_short_id}] Budget 100%: ${current_cost:.2f}/${scan_budget_usd:.2f}")
                _stream_to_supabase(
                    level='warning',
                    message=f"Budget limit reached (${current_cost:.2f}/${scan_budget_usd:.2f}) - wrapping up",
                    event_type='budget_reached',
                    agent_id=self.state.agent_id,
                    agent_name=self.state.agent_name,
                )

            # HARD STOP at 130% budget (grace period exceeded)
            hard_stop_budget = scan_budget_usd * 1.30
            if current_cost >= hard_stop_budget:
                _sandbox_log(f"[{agent_short_id}] BUDGET HARD STOP: ${current_cost:.2f} >= ${hard_stop_budget:.2f} (130%)")
                _stream_to_supabase(
                    level='error',
                    message=f"Scan stopped - budget exceeded 130% (${current_cost:.2f}/${scan_budget_usd:.2f})",
                    event_type='budget_exceeded',
                    agent_id=self.state.agent_id,
                    agent_name=self.state.agent_name,
                )
                self.state.add_message("user",
                    f"BUDGET EXCEEDED (130%): You have spent ${current_cost:.2f} which is over 130% of your ${scan_budget_usd:.2f} budget. "
                    f"You MUST call finish_scan IMMEDIATELY. No more iterations allowed."
                )
                self.state.force_finish = True

            try:
                should_finish = await self._process_iteration(tracer)
                if should_finish:
                    if self.non_interactive:
                        self.state.set_completed({"success": True})
                        if tracer:
                            tracer.update_agent_status(self.state.agent_id, "completed")
                        return self.state.final_result or {}
                    await self._enter_waiting_state(tracer, task_completed=True)
                    continue

            except asyncio.CancelledError:
                if self.non_interactive:
                    raise
                await self._enter_waiting_state(tracer, error_occurred=False, was_cancelled=True)
                continue

            except LLMRequestFailedError as e:
                error_msg = str(e)
                error_details = getattr(e, "details", None)
                self.state.add_error(error_msg)

                # Stream LLM error to Supabase
                _stream_to_supabase(
                    level='error',
                    message=f"LLM Error: {error_msg}",
                    event_type='error',
                    agent_id=self.state.agent_id,
                    agent_name=self.state.agent_name,
                )

                if self.non_interactive:
                    self.state.set_completed({"success": False, "error": error_msg})
                    if tracer:
                        tracer.update_agent_status(self.state.agent_id, "failed", error_msg)
                        if error_details:
                            tracer.log_tool_execution_start(
                                self.state.agent_id,
                                "llm_error_details",
                                {"error": error_msg, "details": error_details},
                            )
                            tracer.update_tool_execution(
                                tracer._next_execution_id - 1, "failed", error_details
                            )
                    return {"success": False, "error": error_msg}

                self.state.enter_waiting_state(llm_failed=True)
                if tracer:
                    tracer.update_agent_status(self.state.agent_id, "llm_failed", error_msg)
                    if error_details:
                        tracer.log_tool_execution_start(
                            self.state.agent_id,
                            "llm_error_details",
                            {"error": error_msg, "details": error_details},
                        )
                        tracer.update_tool_execution(
                            tracer._next_execution_id - 1, "failed", error_details
                        )
                continue

            except (RuntimeError, ValueError, TypeError) as e:
                if not await self._handle_iteration_error(e, tracer):
                    if self.non_interactive:
                        self.state.set_completed({"success": False, "error": str(e)})
                        if tracer:
                            tracer.update_agent_status(self.state.agent_id, "failed")
                        raise
                    await self._enter_waiting_state(tracer, error_occurred=True)
                    continue

    async def _wait_for_input(self) -> None:
        import asyncio

        if self.state.has_waiting_timeout():
            self.state.resume_from_waiting()
            self.state.add_message("assistant", "Waiting timeout reached. Resuming execution.")

            from esprit.telemetry.tracer import get_global_tracer

            tracer = get_global_tracer()
            if tracer:
                tracer.update_agent_status(self.state.agent_id, "running")

            try:
                from esprit.tools.agents_graph.agents_graph_actions import _agent_graph

                if self.state.agent_id in _agent_graph["nodes"]:
                    _agent_graph["nodes"][self.state.agent_id]["status"] = "running"
            except (ImportError, KeyError):
                pass

            return

        await asyncio.sleep(0.5)

    async def _enter_waiting_state(
        self,
        tracer: Optional["Tracer"],
        task_completed: bool = False,
        error_occurred: bool = False,
        was_cancelled: bool = False,
    ) -> None:
        self.state.enter_waiting_state()

        if tracer:
            if task_completed:
                tracer.update_agent_status(self.state.agent_id, "completed")
            elif error_occurred:
                tracer.update_agent_status(self.state.agent_id, "error")
            elif was_cancelled:
                tracer.update_agent_status(self.state.agent_id, "stopped")
            else:
                tracer.update_agent_status(self.state.agent_id, "stopped")

        if task_completed:
            self.state.add_message(
                "assistant",
                "Task completed. I'm now waiting for follow-up instructions or new tasks.",
            )
        elif error_occurred:
            self.state.add_message(
                "assistant", "An error occurred. I'm now waiting for new instructions."
            )
        elif was_cancelled:
            self.state.add_message(
                "assistant", "Execution was cancelled. I'm now waiting for new instructions."
            )
        else:
            self.state.add_message(
                "assistant",
                "Execution paused. I'm now waiting for new instructions or any updates.",
            )

    async def _initialize_sandbox_and_state(self, task: str) -> None:
        import os

        sandbox_mode = os.getenv("ESPRIT_SANDBOX_MODE", "false").lower() == "true"
        if not sandbox_mode and self.state.sandbox_id is None:
            from esprit.runtime import get_runtime

            runtime = get_runtime()
            sandbox_info = await runtime.create_sandbox(
                self.state.agent_id, self.state.sandbox_token, self.local_sources
            )
            self.state.sandbox_id = sandbox_info["workspace_id"]
            self.state.sandbox_token = sandbox_info["auth_token"]
            self.state.sandbox_info = sandbox_info

            if "agent_id" in sandbox_info:
                self.state.sandbox_info["agent_id"] = sandbox_info["agent_id"]

        if not self.state.task:
            self.state.task = task

        self.state.add_message("user", task)

    async def _process_iteration(self, tracer: Optional["Tracer"]) -> bool:
        aid = self.state.agent_id[:8] if self.state.agent_id else "?"
        _sandbox_log(f"[{aid}] Calling LLM...")
        response = await self.llm.generate(self.state.get_conversation_history())
        _sandbox_log(f"[{aid}] LLM response received")

        content_stripped = (response.content or "").strip()

        if not content_stripped:
            corrective_message = (
                "You MUST NOT respond with empty messages. "
                "If you currently have nothing to do or say, use an appropriate tool instead:\n"
                "- Use agents_graph_actions.wait_for_message to wait for messages "
                "from user or other agents\n"
                "- Use agents_graph_actions.agent_finish if you are a sub-agent "
                "and your task is complete\n"
                "- Use finish_actions.finish_scan if you are the root/main agent "
                "and the scan is complete"
            )
            self.state.add_message("user", corrective_message)
            return False

        self.state.add_message("assistant", response.content)
        if tracer:
            tracer.log_chat_message(
                content=clean_content(response.content),
                role="assistant",
                agent_id=self.state.agent_id,
            )

        actions = (
            response.tool_invocations
            if hasattr(response, "tool_invocations") and response.tool_invocations
            else []
        )

        # Only stream LLM thinking to Supabase if there are NO tool invocations
        if not actions:
            content = clean_content(response.content)
            if content and content.strip():
                _stream_to_supabase(
                    level='info',
                    message=content[:500],  # Limit thinking display
                    event_type='thinking',
                    agent_id=self.state.agent_id,
                    agent_name=self.state.agent_name,
                )

        if actions:
            return await self._execute_actions(actions, tracer)

        return False

    async def _execute_actions(self, actions: list[Any], tracer: Optional["Tracer"]) -> bool:
        """Execute actions and return True if agent should finish."""
        aid = self.state.agent_id[:8] if self.state.agent_id else "?"
        # Tool invocations can be dicts with 'toolName' or objects with attributes
        tool_names = []
        for a in actions:
            if isinstance(a, dict):
                tool_names.append(a.get("toolName", "unknown"))
            else:
                tool_names.append(getattr(a, "toolName", getattr(a, "tool_name", "unknown")))
        _sandbox_log(f"[{aid}] Tools: {tool_names}")

        # Stream tool start events to Supabase
        for tool_name in tool_names:
            # Get the primary argument for the tool for display
            for a in actions:
                if isinstance(a, dict):
                    if a.get("toolName") == tool_name:
                        args = a.get("args", {})
                        break
                else:
                    if getattr(a, "toolName", getattr(a, "tool_name", "")) == tool_name:
                        args = getattr(a, "args", {}) if hasattr(a, "args") else {}
                        break
            else:
                args = {}

            # Use centralized formatter for 1:1 parity with CLI output
            msg = format_tool_message(tool_name, args)

            _stream_to_supabase(
                level='info',
                message=msg,
                event_type='tool_start',
                agent_id=self.state.agent_id,
                agent_name=self.state.agent_name,
                tool_name=tool_name,
            )

        for action in actions:
            self.state.add_action(action)

        conversation_history = self.state.get_conversation_history()

        tool_task = asyncio.create_task(
            process_tool_invocations(actions, conversation_history, self.state)
        )
        self._current_task = tool_task

        try:
            should_agent_finish = await tool_task
            self._current_task = None
            _sandbox_log(f"[{aid}] Tools done. Finish: {should_agent_finish}")
        except asyncio.CancelledError:
            self._current_task = None
            self.state.add_error("Tool execution cancelled by user")
            # Stream agent cancelled
            _stream_to_supabase(
                level='warning',
                message=f"Agent '{self.state.agent_name}' was cancelled",
                event_type='agent_end',
                agent_id=self.state.agent_id,
                agent_name=self.state.agent_name,
            )
            raise

        self.state.messages = conversation_history

        if should_agent_finish:
            self.state.set_completed({"success": True})
            if tracer:
                tracer.update_agent_status(self.state.agent_id, "completed")

            # Stream agent end to Supabase
            _stream_to_supabase(
                level='success',
                message=f"Agent '{self.state.agent_name}' completed successfully",
                event_type='agent_end',
                agent_id=self.state.agent_id,
                agent_name=self.state.agent_name,
            )

            if self.non_interactive and self.state.parent_id is None:
                return True
            return True

        return False

    async def _handle_iteration_error(
        self,
        error: RuntimeError | ValueError | TypeError | asyncio.CancelledError,
        tracer: Optional["Tracer"],
    ) -> bool:
        error_msg = f"Error in iteration {self.state.iteration}: {error!s}"
        logger.exception(error_msg)
        self.state.add_error(error_msg)
        if tracer:
            tracer.update_agent_status(self.state.agent_id, "error")

        # Stream error event to Supabase
        _stream_to_supabase(
            level='error',
            message=f"Error: {error!s}",
            event_type='error',
            agent_id=self.state.agent_id,
            agent_name=self.state.agent_name,
        )

        return True

    def _check_agent_messages(self, state: AgentState) -> None:  # noqa: PLR0912
        try:
            from esprit.tools.agents_graph.agents_graph_actions import _agent_graph, _agent_messages

            agent_id = state.agent_id
            if not agent_id or agent_id not in _agent_messages:
                return

            messages = _agent_messages[agent_id]
            if messages:
                has_new_messages = False
                for message in messages:
                    if not message.get("read", False):
                        sender_id = message.get("from")

                        if state.is_waiting_for_input():
                            if state.llm_failed:
                                if sender_id == "user":
                                    state.resume_from_waiting()
                                    has_new_messages = True

                                    from esprit.telemetry.tracer import get_global_tracer

                                    tracer = get_global_tracer()
                                    if tracer:
                                        tracer.update_agent_status(state.agent_id, "running")
                            else:
                                state.resume_from_waiting()
                                has_new_messages = True

                                from esprit.telemetry.tracer import get_global_tracer

                                tracer = get_global_tracer()
                                if tracer:
                                    tracer.update_agent_status(state.agent_id, "running")

                        if sender_id == "user":
                            sender_name = "User"
                            state.add_message("user", message.get("content", ""))
                        else:
                            if sender_id and sender_id in _agent_graph.get("nodes", {}):
                                sender_name = _agent_graph["nodes"][sender_id]["name"]

                            message_content = f"""<inter_agent_message>
    <delivery_notice>
        <important>You have received a message from another agent. You should acknowledge
        this message and respond appropriately based on its content. However, DO NOT echo
        back or repeat the entire message structure in your response. Simply process the
        content and respond naturally as/if needed.</important>
    </delivery_notice>
    <sender>
        <agent_name>{sender_name}</agent_name>
        <agent_id>{sender_id}</agent_id>
    </sender>
    <message_metadata>
        <type>{message.get("message_type", "information")}</type>
        <priority>{message.get("priority", "normal")}</priority>
        <timestamp>{message.get("timestamp", "")}</timestamp>
    </message_metadata>
    <content>
{message.get("content", "")}
    </content>
    <delivery_info>
        <note>This message was delivered during your task execution.
        Please acknowledge and respond if needed.</note>
    </delivery_info>
</inter_agent_message>"""
                            state.add_message("user", message_content.strip())

                        message["read"] = True

                if has_new_messages and not state.is_waiting_for_input():
                    from esprit.telemetry.tracer import get_global_tracer

                    tracer = get_global_tracer()
                    if tracer:
                        tracer.update_agent_status(agent_id, "running")

        except (AttributeError, KeyError, TypeError) as e:
            import logging

            logger = logging.getLogger(__name__)
            logger.warning(f"Error checking agent messages: {e}")
            return
