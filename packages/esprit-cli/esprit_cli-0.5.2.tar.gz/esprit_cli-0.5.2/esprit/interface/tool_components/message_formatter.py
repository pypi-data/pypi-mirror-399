"""
Plain-text message formatter for tool events.

This module provides a single source of truth for formatting tool messages.
Used by both:
- TUI renderers (for terminal display)
- Supabase streaming (for web display)

This ensures 1:1 parity between local CLI output and web UI.
"""

from typing import Any


def format_tool_message(tool_name: str, args: dict[str, Any]) -> str:
    """
    Format a tool call into a plain-text message matching CLI output.

    Args:
        tool_name: The name of the tool being called
        args: The arguments passed to the tool

    Returns:
        Plain-text message with emoji prefix (no Rich markup)
    """

    # File operations (str_replace_editor)
    if tool_name == "str_replace_editor":
        command = args.get("command", "")
        path = args.get("path", "")
        path_display = _truncate(path, 60)

        if command == "view":
            return f"📖 Reading file {path_display}"
        elif command == "str_replace":
            return f"✏️ Editing file {path_display}"
        elif command == "create":
            return f"📝 Creating file {path_display}"
        elif command == "insert":
            return f"✏️ Inserting text {path_display}"
        elif command == "undo_edit":
            return f"↩️ Undoing edit {path_display}"
        else:
            return f"📄 File operation {path_display}"

    # List files
    if tool_name == "list_files":
        path = args.get("path", "")
        path_display = _truncate(path, 60)
        if path:
            return f"📂 Listing files {path_display}"
        return "📂 Listing files"

    # Search files
    if tool_name == "search_files":
        path = args.get("path", "")
        regex = args.get("regex", "")
        path_display = _truncate(path, 30)
        regex_display = _truncate(regex, 30)

        if path and regex:
            return f"🔍 Searching files {path_display} for '{regex_display}'"
        elif path:
            return f"🔍 Searching files {path_display}"
        elif regex:
            return f"🔍 Searching for '{regex_display}'"
        return "🔍 Searching files"

    # Terminal
    if tool_name in ("terminal_execute", "terminal"):
        cmd = args.get("command", "")
        is_input = args.get("is_input", False)

        if not cmd.strip():
            return ">_ getting logs..."

        cmd_display = _truncate(cmd, 100)
        if is_input:
            return f">_ >>> {cmd_display}"
        return f">_ $ {cmd_display}"

    # Python
    if tool_name in ("python_action", "python"):
        action = args.get("action", "")
        code = args.get("code", "")

        if action in ("new_session", "execute") and code:
            code_display = _truncate(code, 100)
            return f"</> Python\n  {code_display}"
        elif action == "close":
            return "</> Python Closing session..."
        elif action == "list_sessions":
            return "</> Python Listing sessions..."
        return "</> Python Running..."

    # Browser
    if tool_name in ("browser", "browser_action"):
        action = args.get("action", "")
        url = args.get("url", "")

        if action == "navigate" and url:
            url_display = _truncate(url, 60)
            return f"🌐 Navigating to {url_display}"
        elif action == "click":
            selector = args.get("selector", "")
            return f"🌐 Clicking {_truncate(selector, 40)}"
        elif action == "screenshot":
            return "🌐 Taking screenshot"
        elif action == "scroll":
            return "🌐 Scrolling"
        elif action == "type":
            return "🌐 Typing text"
        elif action:
            return f"🌐 Browser {action}"
        return "🌐 Browser action"

    # Web search
    if tool_name == "web_search":
        query = args.get("query", "")
        query_display = _truncate(query, 60)
        return f"🌐 Searching the web... {query_display}"

    # Thinking
    if tool_name == "think":
        content = args.get("content", "")
        content_display = _truncate(content, 80)
        return f"🧠 Thinking {content_display}"

    # Agent operations
    if tool_name == "create_agent":
        name = args.get("name", "")
        return f"🤖 Creating {name}"

    if tool_name == "spawn_agent":
        name = args.get("name", "")
        return f"🤖 Spawned subagent {name}"

    if tool_name == "agent_finish":
        success = args.get("success", True)
        if success:
            return "🏁 Agent completed"
        return "🏁 Agent failed"

    if tool_name == "wait_for_message":
        return "⏸️ Waiting for messages"

    if tool_name == "send_message_to_agent":
        return "💬 Sending message"

    if tool_name == "view_agent_graph":
        return "🕸️ Viewing agents graph"

    # Vulnerability reporting
    if tool_name == "create_vulnerability_report":
        title = args.get("title", "")
        severity = args.get("severity", "")
        if title:
            return f"🐞 Vulnerability Report: [{severity.upper()}] {_truncate(title, 60)}"
        return "🐞 Vulnerability Report"

    # Finish scan
    if tool_name == "finish_scan":
        return "🏁 Finishing Scan"

    # Notes
    if tool_name == "create_note":
        title = args.get("title", "")
        return f"📝 Note {_truncate(title, 40)}"

    if tool_name == "delete_note":
        return "🗑️ Delete Note"

    # HTTP/Proxy tools
    if tool_name in ("list_requests", "http_list"):
        return "📋 Listing requests"

    if tool_name in ("view_request", "view_response", "http_view"):
        return "👀 Viewing request/response"

    if tool_name in ("send_request", "http_send"):
        method = args.get("method", "")
        return f"📤 Sending {method}" if method else "📤 Sending request"

    if tool_name in ("repeat_request", "http_repeat"):
        return "🔄 Repeating request"

    # Fallback - generic format
    return f"🔧 {tool_name}"


def _truncate(text: str, max_len: int) -> str:
    """Truncate text to max length, adding ... if truncated."""
    if not text:
        return ""
    text = str(text).replace("\n", " ").strip()
    if len(text) > max_len:
        return text[:max_len - 3] + "..."
    return text
