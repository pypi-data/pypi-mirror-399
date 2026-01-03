import html
import re
from typing import Any


def _truncate_to_first_function(content: str) -> str:
    if not content:
        return content

    function_starts = [match.start() for match in re.finditer(r"<function=", content)]

    if len(function_starts) >= 2:
        second_function_start = function_starts[1]

        return content[:second_function_start].rstrip()

    return content


def parse_tool_invocations(content: str) -> list[dict[str, Any]] | None:
    content = _fix_stopword(content)

    tool_invocations: list[dict[str, Any]] = []

    fn_regex_pattern = r"<function=([^>]+)>\n?(.*?)</function>"
    fn_param_regex_pattern = r"<parameter=([^>]+)>(.*?)</parameter>"

    fn_matches = re.finditer(fn_regex_pattern, content, re.DOTALL)

    for fn_match in fn_matches:
        fn_name = fn_match.group(1)
        fn_body = fn_match.group(2)

        param_matches = re.finditer(fn_param_regex_pattern, fn_body, re.DOTALL)

        args = {}
        for param_match in param_matches:
            param_name = param_match.group(1)
            param_value = param_match.group(2).strip()

            param_value = html.unescape(param_value)
            args[param_name] = param_value

        tool_invocations.append({"toolName": fn_name, "args": args})

    # If no XML tools found, try fallback patterns for emoji/alternative formats
    if not tool_invocations:
        tool_invocations = _parse_alternative_tool_formats(content)

    return tool_invocations if tool_invocations else None


def _fix_stopword(content: str) -> str:
    if "<function=" in content and content.count("<function=") == 1:
        if content.endswith("</"):
            content = content.rstrip() + "function>"
        elif not content.rstrip().endswith("</function>"):
            content = content + "\n</function>"
    return content


def _parse_alternative_tool_formats(content: str) -> list[dict[str, Any]]:
    """Parse tool invocations from emoji and alternative formats.

    Handles patterns where the LLM outputs tool names with emoji prefixes:
    - ⚙️ tool_name: function_name
    - 🌐 Browser: action_name
    - 📂 File: path
    - 📄 Read: filepath
    - 🔍 Search: query
    """
    tool_invocations: list[dict[str, Any]] = []

    # Pattern 1: ⚙️ tool_name: function_name (generic tool indicator)
    emoji_tool_pattern = r"⚙️\s*tool_name\s*:\s*(\w+)"
    for match in re.finditer(emoji_tool_pattern, content):
        tool_name = match.group(1)
        if tool_name:
            tool_invocations.append({"toolName": tool_name, "args": {}})

    # Pattern 2: Emoji + description (e.g., 🌐 Browser: action)
    emoji_patterns = [
        (r"🌐\s+[Bb]rowser\s*:\s*(\w+)", lambda m: {"toolName": "browser_action", "args": {"action": m.group(1)}}),
        (r"📂\s+(?:[Ll]isting|[Ff]ile|[Dd]ir)\s*:\s*(.+?)(?:\n|$)", lambda m: {"toolName": "list_files", "args": {"path": m.group(1).strip()}}),
        (r"📄\s+(?:[Rr]ead|[Ff]ile)\s*:\s*(.+?)(?:\n|$)", lambda m: {"toolName": "read_file", "args": {"file_path": m.group(1).strip()}}),
        (r"🔍\s+[Ss]earch\s*:\s*(.+?)(?:\n|$)", lambda m: {"toolName": "search", "args": {"query": m.group(1).strip()}}),
        (r"🤖\s+(?:[Cc]reate|[Ss]pawn)\s+[Aa]gent\s*:\s*(.+?)(?:\n|$)", lambda m: {"toolName": "create_agent", "args": {"prompt": m.group(1).strip()}}),
    ]

    for pattern, tool_fn in emoji_patterns:
        for match in re.finditer(pattern, content, re.MULTILINE):
            try:
                tool_data = tool_fn(match)
                if tool_data not in tool_invocations:
                    tool_invocations.append(tool_data)
            except (IndexError, AttributeError):
                pass

    return tool_invocations


def format_tool_call(tool_name: str, args: dict[str, Any]) -> str:
    xml_parts = [f"<function={tool_name}>"]

    for key, value in args.items():
        xml_parts.append(f"<parameter={key}>{value}</parameter>")

    xml_parts.append("</function>")

    return "\n".join(xml_parts)


def clean_content(content: str) -> str:
    if not content:
        return ""

    content = _fix_stopword(content)

    tool_pattern = r"<function=[^>]+>.*?</function>"
    cleaned = re.sub(tool_pattern, "", content, flags=re.DOTALL)

    hidden_xml_patterns = [
        r"<inter_agent_message>.*?</inter_agent_message>",
        r"<agent_completion_report>.*?</agent_completion_report>",
    ]
    for pattern in hidden_xml_patterns:
        cleaned = re.sub(pattern, "", cleaned, flags=re.DOTALL | re.IGNORECASE)

    cleaned = re.sub(r"\n\s*\n", "\n\n", cleaned)

    return cleaned.strip()
