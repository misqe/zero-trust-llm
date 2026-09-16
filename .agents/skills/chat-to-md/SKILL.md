---
name: chat-to-md
description: Automatically parse, extract, and convert raw Antigravity IDE JSONL chat transcripts into clean, readable, fully formatted Markdown archive files. Use whenever the user asks to export the current or historical conversation, convert transcripts to markdown, or archive conversation logs.
---

# Chat to Markdown Exporter (`chat-to-md`)

## Overview

The `chat-to-md` skill enables agents and users to export raw Antigravity IDE JSONL session logs (`transcript_full.jsonl` / `transcript.jsonl`) into structured, clean, human-readable Markdown files.

It automatically resolves the conversation log path from `<appDataDir>\brain\<conversation-id>\.system_generated\logs`, extracts user prompts, planner responses, high-level reasoning summaries, tool invocations, and command execution outputs, formatting them chronologically with turn numbers and timestamps.

---

## When to Use This Skill

Activate this skill whenever:
- The user asks to *"export transcript of this chat"*, *"save this conversation to markdown"*, or *"archive this session"*.
- You need to generate an offline, shareable report of an entire troubleshooting or engineering session.
- You need to inspect and analyze a previous conversation transcript without manually parsing JSONL.

---

## Script Usage & Command Examples

The skill bundles an automated Python conversion tool:
`scripts/export_transcript.py`

### 1. Export Current Conversation to Markdown
```powershell
python .agents/skills/chat-to-md/scripts/export_transcript.py <conversation_id> -o MySessionTranscript.md
```

### 2. Export Without Specifying Conversation ID (Auto-detects active session)
```powershell
python .agents/skills/chat-to-md/scripts/export_transcript.py -o session_export.md
```

### 3. Export Clean Narrative Only (Exclude verbose tool JSON and outputs)
```powershell
python .agents/skills/chat-to-md/scripts/export_transcript.py <conversation_id> --no-tools -o narrative_transcript.md
```

---

## Transcript Structure in Generated Markdown

The exported document produces a clean GitHub-flavored Markdown hierarchy:

1. **Header & Metadata Block**:
   - Conversation ID
   - Export timestamp
   - Total recorded steps and turn count
   - Source log file (`transcript_full.jsonl`)
2. **User Prompts (`## 👤 User [Turn N • Step S]`)**:
   - Clean, untruncated prompt text.
   - Internal XML tags and system prompt wrappers stripped for pure readability.
3. **Agent Responses (`### 🤖 Antigravity [Step S]`)**:
   - High-level reasoning summaries.
   - Full conversational responses, code blocks, diffs, and explanations.
   - Tool call signatures (function name and JSON arguments).
4. **Tool Executions (`#### 🛠️ Tool Execution: <TYPE> [Step S]`)**:
   - Status, exit code, and captured standard output.
