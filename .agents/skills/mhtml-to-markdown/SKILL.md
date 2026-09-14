---
name: mhtml-to-markdown
description: >-
  Use this skill whenever the user needs to inspect, extract, or convert MHTML
  (.mhtml) web archives or exported web chats (such as Gemini, ChatGPT, or web pages)
  into clean, formatted Markdown files, or merge multiple overlapping chat sessions
  into a single deduplicated transcript.
---

# MHTML Extraction and Markdown Conversion

Automated pipeline and runbook for decoding RFC 2557 MIME web archives (`.mhtml`), extracting internal HTML resources, cleaning web-app and screen-reader artifacts, and converting conversational web sessions into structured, syntax-highlighted Markdown (`.md`) documents with automatic overlap deduplication.

---

## When to Use

- The user provides `.mhtml` files (e.g., saved from Chrome, Edge, or Brave via "Save Page As > Webpage, Complete / Single File").
- The user asks to convert chat exports (such as Gemini shared chats, ChatGPT logs, Claude shares) from `.mhtml` to Markdown.
- The user has sequential or multi-part chat exports (e.g. `Chat (A).mhtml`, `Chat (B).mhtml`) where later sessions re-paste earlier transcripts to preserve context, and needs them merged without redundant text.
- Standard tools fail to parse `.mhtml` due to `quoted-printable` or `base64` transfer encoding.

---

## Architecture & How It Works

### 1. RFC 2557 MIME Structure
MHTML files wrap HTML, CSS, images, and fonts into a `multipart/related` MIME envelope:
- **Boundary**: Demarcates individual parts.
- **Root Resource**: Typically the first `text/html` part (`Content-Type: text/html`).
- **Transfer Encodings**: `quoted-printable` (soft line breaks `= \n`, hex characters `=3D`, `=20`) or `base64`.
- **Decoding**: Handled natively in Python using `email.message_from_bytes()` with `quopri.decodestring()` or `base64.b64decode()`.

### 2. Conversational DOM Parsing (Gemini / Web Chats)
Gemini web exports store turns in custom web component containers:
- `<share-turn-viewer>`: Encapsulates a complete user prompt + assistant response pair.
- `<user-query>`: Contains the user's prompt text and file attachments.
  - Screen-reader noise: `<h5 class="cdk-visually-hidden"><span>You said</span>...</h5>` is deduplicated to avoid repeating the prompt twice.
  - Image attachments: `<user-query-file-preview>` or `<img data-test-id="uploaded-img">` are converted to `📷 *[Attached Image / Photo]*`.
- `<message-content>`: Contains the assistant response.
  - `<code-block>`: Contains language badges (`DOS`, `PowerShell`, `bash`, `python`) and code inside `<pre><code>`. These are cleanly converted into GitHub-flavored Markdown code fences:
    ````markdown
    ```powershell
    Get-Disk | Select-Object Number, FriendlyName
    ```
    ````
  - Formatting: Preserves headings, bold/italics, bulleted and numbered lists, blockquotes, and hyperlinks while stripping UI button boilerplate (`Copy code`, `Download code`, `Share`, SVGs).

### 3. Multi-Session Overlap Deduplication
When continuing long projects across multiple chat windows, users frequently copy the entire transcript of Session A into Turn 0 of Session B to prime the AI. This skill's merger:
1. Retains all turns from the primary session (Session A).
2. Detects that Turn 0 of Session B is a reproduction of Session A.
3. Suppresses the duplicated user prompt while preserving the assistant's transitional bridge response.
4. Appends all subsequent unique turns from Session B.

---

## Provided Utilities

The skill provides two production scripts in `scripts/`:

### 1. `mhtml_to_markdown.py` (Full Pipeline)
Converts single MHTML files or merges multiple files with automatic deduplication.

```bash
# Convert a single MHTML file to Markdown
python "C:\Users\micha\.gemini\config\skills\mhtml-to-markdown\scripts\mhtml_to_markdown.py" "path/to/chat.mhtml" -o "output.md"

# Convert and merge two sequential chats with overlap removal
python "C:\Users\micha\.gemini\config\skills\mhtml-to-markdown\scripts\mhtml_to_markdown.py" "chat_A.mhtml" "chat_B.mhtml" --merge --title "ASUS VivoBook Complete Transcript" -o "merged_transcript.md"
```

### 2. `extract_mhtml.py` (Raw Extraction)
Extracts the decoded root HTML document from any MHTML archive for inspection or custom processing.

```bash
python "C:\Users\micha\.gemini\config\skills\mhtml-to-markdown\scripts\extract_mhtml.py" "archive.mhtml" -o "decoded.html"
```

---

## Step-by-Step Procedure for the Agent

When tasked with processing `.mhtml` files:

1. **Locate Target Files**:
   Identify the `.mhtml` archives in the user's workspace.
2. **Determine Scope**:
   - Single file: Run `mhtml_to_markdown.py` directly.
   - Multiple sequential files: Inspect whether subsequent files re-seed context from earlier files. Run with `--merge`.
3. **Execute Conversion**:
   Run the CLI tool specifying the target workspace destination and descriptive markdown filename.
4. **Verify Output**:
   Check line count, verify code block fences, and confirm that user prompts and model responses flow continuously without duplicate headers or lost text.

---

## References & Standards Compliance

- **Specification Summary & Expansion Roadmap**: [rfc2557_spec_summary.md](./references/rfc2557_spec_summary.md) — Detailed mapping of current implementation versus full RFC 2557 requirements, along with the technical blueprint for future multi-resource asset unpacking (CID matching, image extraction, and Base URI resolution).
- **Original RFC Specification**: [rfc2557.txt.pdf](./references/rfc2557.txt.pdf) — Complete 28-page normative standard (*MIME Encapsulation of Aggregate Documents, such as HTML (MHTML)*).

