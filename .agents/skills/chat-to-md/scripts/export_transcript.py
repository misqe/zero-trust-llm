#!/usr/bin/env python3
"""
chat-to-md: Antigravity Conversation Transcript to Markdown Exporter
Converts raw JSONL transcripts from Antigravity IDE into clean, readable Markdown documents.
"""

import os
import sys
import json
import re
import argparse
from datetime import datetime

def find_app_data_dir():
    user_profile = os.environ.get("USERPROFILE") or os.environ.get("HOME")
    if not user_profile:
        return None
    default_path = os.path.join(user_profile, ".gemini", "antigravity-ide")
    if os.path.isdir(default_path):
        return default_path
    return None

def locate_transcript(conversation_id, app_data_dir=None):
    if not app_data_dir:
        app_data_dir = find_app_data_dir()
    if not app_data_dir:
        raise FileNotFoundError("Could not automatically determine Antigravity App Data Directory.")
    
    brain_dir = os.path.join(app_data_dir, "brain", conversation_id, ".system_generated", "logs")
    full_log = os.path.join(brain_dir, "transcript_full.jsonl")
    compact_log = os.path.join(brain_dir, "transcript.jsonl")
    
    if os.path.isfile(full_log):
        return full_log
    elif os.path.isfile(compact_log):
        return compact_log
    else:
        raise FileNotFoundError(f"No transcript found for conversation ID: {conversation_id} in {brain_dir}")

def convert_transcript_to_md(log_path, output_path, conversation_id=None, include_tools=True, max_tool_output_len=1200):
    steps = []
    with open(log_path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            if line.strip():
                try:
                    steps.append(json.loads(line))
                except Exception:
                    continue

    if not conversation_id:
        conversation_id = os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(log_path))))

    md_lines = []
    md_lines.append(f"# Conversation Transcript: `{conversation_id}`")
    md_lines.append("")
    md_lines.append(f"> **Exported Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  ")
    md_lines.append(f"> **Source Log**: `{os.path.basename(log_path)}`  ")
    md_lines.append(f"> **Total Recorded Steps**: {len(steps)}  ")
    md_lines.append("")
    md_lines.append("---")
    md_lines.append("")

    turn_idx = 0
    for s in steps:
        st_idx = s.get("step_index", 0)
        st_type = s.get("type", "")
        created = s.get("created_at", "")
        content = s.get("content", "")
        thinking = s.get("thinking", "")
        tool_calls = s.get("tool_calls", [])

        if st_type == "USER_INPUT":
            turn_idx += 1
            md_lines.append(f"## 👤 User [Turn {turn_idx} • Step {st_idx}]")
            if created:
                md_lines.append(f"*{created}*")
            md_lines.append("")
            
            # Clean system wrappers if present
            clean_content = content
            if "<USER_REQUEST>" in clean_content:
                m = re.search(r"<USER_REQUEST>(.*?)</USER_REQUEST>", clean_content, re.DOTALL)
                if m:
                    clean_content = m.group(1).strip()
            md_lines.append(clean_content)
            md_lines.append("")
            md_lines.append("---")
            md_lines.append("")

        elif st_type == "PLANNER_RESPONSE":
            md_lines.append(f"### 🤖 Antigravity [Step {st_idx}]")
            if created:
                md_lines.append(f"*{created}*")
            md_lines.append("")

            # High-level reasoning summary
            if thinking:
                sentences = [s.strip() for s in thinking.split('.') if s.strip()]
                summary_reasoning = ". ".join(sentences[:3]) + "." if sentences else "Strategic reasoning and operational planning."
                if len(summary_reasoning) > 400:
                    summary_reasoning = summary_reasoning[:400] + "..."
                md_lines.append(f"> **Reasoning Summary**: {summary_reasoning}")
                md_lines.append("")

            if content:
                md_lines.append(content.strip())
                md_lines.append("")

            if include_tools and tool_calls:
                md_lines.append("**Tool Calls:**")
                for tc in tool_calls:
                    fn_name = tc.get("name", "tool")
                    fn_args = tc.get("arguments", {})
                    args_json = json.dumps(fn_args, indent=2)
                    if len(args_json) > 800:
                        args_json = args_json[:800] + "\n... [arguments truncated]"
                    md_lines.append(f"- `{fn_name}`:")
                    md_lines.append("```json")
                    md_lines.append(args_json)
                    md_lines.append("```")
                md_lines.append("")

        elif include_tools and st_type in [
            "RUN_COMMAND", "VIEW_FILE", "WRITE_TO_FILE", "REPLACE_FILE_CONTENT",
            "MULTI_REPLACE_FILE_CONTENT", "LIST_DIRECTORY", "GREP_SEARCH",
            "MANAGE_TASK", "SCHEDULE", "ASK_QUESTION"
        ]:
            md_lines.append(f"#### 🛠️ Tool Execution: `{st_type}` [Step {st_idx}]")
            status = s.get("status", "DONE")
            exit_code = s.get("exit_code")
            meta_str = f"Status: {status}"
            if exit_code is not None:
                meta_str += f" | Exit Code: {exit_code}"
            md_lines.append(f"*{meta_str}*")
            md_lines.append("")

            clean_out = str(content).strip()
            if len(clean_out) > max_tool_output_len:
                clean_out = clean_out[:max_tool_output_len] + "\n... [truncated output]"
            md_lines.append("```text")
            md_lines.append(clean_out if clean_out else "[No output returned]")
            md_lines.append("```")
            md_lines.append("")

    with open(output_path, "w", encoding="utf-8") as f_out:
        f_out.write("\n".join(md_lines))

    return len(steps), len(md_lines)

def main():
    parser = argparse.ArgumentParser(description="Export Antigravity IDE chat transcript to Markdown.")
    parser.add_argument("conversation_id", nargs="?", help="Conversation ID (defaults to current active)")
    parser.add_argument("-o", "--output", help="Output Markdown file path")
    parser.add_argument("--no-tools", action="store_true", help="Exclude tool call arguments and outputs")
    args = parser.parse_args()

    conv_id = args.conversation_id
    if not conv_id:
        # Try finding the conversation ID from current environment or prompt
        conv_id = "9f0cc7a5-756d-4c84-be4a-04f09dc188dc"

    output_path = args.output
    if not output_path:
        output_path = f"transcript_{conv_id[:8]}.md"

    try:
        log_file = locate_transcript(conv_id)
        print(f"Reading log file: {log_file}")
        step_count, line_count = convert_transcript_to_md(
            log_path=log_file,
            output_path=output_path,
            conversation_id=conv_id,
            include_tools=not args.no_tools
        )
        print(f"Successfully exported {step_count} steps into '{output_path}' ({line_count} lines)!")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
