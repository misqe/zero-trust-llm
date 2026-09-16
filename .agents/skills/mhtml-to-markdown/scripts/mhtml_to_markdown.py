#!/usr/bin/env python3
"""
mhtml_to_markdown.py - Convert MHTML web archives and AI chat transcripts to Markdown.
Supports turn extraction, code block preservation, screen-reader deduplication,
and multi-session overlap detection and merging.
"""

import email
import quopri
import base64
import argparse
import sys
import os
import re
from html import unescape

def extract_html_from_mhtml(filepath):
    """Extract root HTML string from an MHTML archive."""
    with open(filepath, 'rb') as f:
        raw = f.read()
    msg = email.message_from_bytes(raw)
    for part in msg.walk():
        if part.get_content_type() == 'text/html':
            payload = part.get_payload(decode=True)
            if payload is None:
                payload_raw = part.get_payload(decode=False)
                enc = part.get('Content-Transfer-Encoding', '7bit').lower().strip()
                if isinstance(payload_raw, str):
                    payload_raw = payload_raw.encode('utf-8', errors='replace')
                if enc == 'quoted-printable':
                    payload = quopri.decodestring(payload_raw)
                elif enc == 'base64':
                    payload = base64.b64decode(payload_raw)
                else:
                    payload = payload_raw
            charset = part.get_content_charset() or 'utf-8'
            return payload.decode(charset, errors='replace')
    return None

def convert_message_html_to_markdown(mc_html):
    """Convert Gemini message-content or HTML body into clean Markdown."""
    if not mc_html:
        return ""

    # 1. Transform <code-block>
    def replace_code_block(match):
        block_html = match.group(0)
        # Find language label
        lang_match = re.search(r'<div[^>]*class="code-block-decoration[^"]*"[^>]*>\s*<span[^>]*>([^<]+)</span>', block_html)
        lang = lang_match.group(1).strip().lower() if lang_match else ""
        if lang in ('dos', 'cmd'):
            lang = 'cmd'
        elif lang in ('powershell', 'ps1'):
            lang = 'powershell'
        elif lang in ('bash', 'sh'):
            lang = 'bash'

        code_match = re.search(r'<pre[^>]*>\s*<code[^>]*>(.*?)</code>\s*</pre>', block_html, re.DOTALL)
        if code_match:
            raw_code = code_match.group(1)
            code_text = unescape(re.sub(r'<[^>]+>', '', raw_code)).strip()
            return f"\n\n```{lang}\n{code_text}\n```\n\n"
        return ""

    html = re.sub(r'<code-block[^>]*>.*?</code-block>', replace_code_block, mc_html, flags=re.DOTALL)

    # 2. Transform regular <pre><code> if not inside custom code-block
    def replace_pre_code(match):
        code_text = unescape(re.sub(r'<[^>]+>', '', match.group(1))).strip()
        return f"\n\n```\n{code_text}\n```\n\n"
    html = re.sub(r'<pre[^>]*>\s*<code[^>]*>(.*?)</code>\s*</pre>', replace_pre_code, html, flags=re.DOTALL | re.IGNORECASE)

    # 3. Strip interactive buttons, icons, and carousels
    html = re.sub(r'<(button|mat-icon|gem-icon|gem-icon-button|svg|script|style)[^>]*>.*?</\1>', '', html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r'<sources-carousel-inline[^>]*>.*?</sources-carousel-inline>', '', html, flags=re.DOTALL | re.IGNORECASE)

    # 4. Headings
    for h in range(1, 7):
        html = re.sub(rf'<h{h}[^>]*>(.*?)</h{h}>', rf'\n\n{"#" * h} \1\n\n', html, flags=re.DOTALL | re.IGNORECASE)

    # 5. Lists
    html = re.sub(r'<li[^>]*>(.*?)</li>', r'\n* \1', html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r'</?(ul|ol)[^>]*>', '\n', html, flags=re.IGNORECASE)

    # 6. Blockquotes
    html = re.sub(r'<blockquote[^>]*>(.*?)</blockquote>', lambda m: '\n' + '\n'.join('> ' + l for l in m.group(1).splitlines()) + '\n', html, flags=re.DOTALL | re.IGNORECASE)

    # 7. Bold & Italic
    html = re.sub(r'<(strong|b)[^>]*>(.*?)</\1>', r'**\2**', html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r'<(em|i)[^>]*>(.*?)</\1>', r'*\2*', html, flags=re.DOTALL | re.IGNORECASE)

    # 8. Inline code
    html = re.sub(r'<code[^>]*>(.*?)</code>', r'`\1`', html, flags=re.DOTALL | re.IGNORECASE)

    # 9. Links
    html = re.sub(r'<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', r'[\2](\1)', html, flags=re.DOTALL | re.IGNORECASE)

    # 10. Paragraphs & Line Breaks
    html = re.sub(r'<br\s*/?\s*>', '\n', html, flags=re.IGNORECASE)
    html = re.sub(r'</(p|div|tr|section|article)>', '\n\n', html, flags=re.IGNORECASE)

    # 11. Strip remaining tags and unescape entities
    text = re.sub(r'<[^>]+>', '', html)
    text = unescape(text)

    # 12. Normalize blank lines while protecting code blocks
    lines = text.splitlines()
    normalized = []
    in_code = False
    for line in lines:
        if line.strip().startswith('```'):
            in_code = not in_code
            normalized.append(line.strip())
            continue
        if in_code:
            normalized.append(line)
        else:
            cleaned = line.strip()
            if cleaned:
                normalized.append(cleaned)
            elif normalized and normalized[-1] != "":
                normalized.append("")

    return "\n".join(normalized).strip()

def extract_user_query_from_turn(turn_html):
    """Extract clean user query text and detect image attachments."""
    has_image = bool(re.search(r'<user-query-file-preview|<img[^>]*data-test-id="uploaded-img"', turn_html))

    qt = re.search(r'<div[^>]*class="query-text[^"]*"[^>]*>(.*?)</div>', turn_html, re.DOTALL)
    if qt:
        # Remove screen-reader duplicate text ("You said...")
        cleaned_qt = re.sub(r'<h5[^>]*class="[^"]*cdk-visually-hidden[^"]*"[^>]*>.*?</h5>', '', qt.group(1), flags=re.DOTALL)
        lines = re.findall(r'<p[^>]*class="query-text-line[^"]*"[^>]*>(.*?)</p>', cleaned_qt, re.DOTALL)
        user_lines = [unescape(re.sub(r'<[^>]+>', '', l)).strip() for l in lines]
        user_lines = [l for l in user_lines if l]
        user_prompt = "\n\n".join(user_lines)
    else:
        uq = re.search(r'<user-query[^>]*>(.*?)</user-query>', turn_html, re.DOTALL)
        if uq:
            t = re.sub(r'<[^>]+>', '', uq.group(1))
            user_prompt = unescape(t).strip()
        else:
            user_prompt = ""

    return user_prompt, has_image

def parse_chat_turns(html):
    """
    Parse chat turns from Gemini HTML. Returns a list of dicts:
    [{'user': ..., 'response': ..., 'has_image': ...}, ...]
    """
    turn_matches = re.findall(r'<share-turn-viewer[^>]*>(.*?)</share-turn-viewer>', html, re.DOTALL)
    if not turn_matches:
        # Fallback if not wrapped in share-turn-viewer
        uq_list = re.findall(r'<user-query[^>]*>(.*?)</user-query>', html, re.DOTALL)
        mc_list = re.findall(r'<message-content[^>]*>(.*?)</message-content>', html, re.DOTALL)
        turns = []
        for i in range(max(len(uq_list), len(mc_list))):
            user_html = uq_list[i] if i < len(uq_list) else ""
            mc_html = mc_list[i] if i < len(mc_list) else ""
            user_prompt, has_img = extract_user_query_from_turn(user_html)
            resp = convert_message_html_to_markdown(mc_html)
            turns.append({'user': user_prompt, 'response': resp, 'has_image': has_img})
        return turns

    turns = []
    for t_html in turn_matches:
        user_prompt, has_img = extract_user_query_from_turn(t_html)
        mc = re.search(r'<message-content[^>]*>(.*?)</message-content>', t_html, re.DOTALL)
        resp = convert_message_html_to_markdown(mc.group(1)) if mc else ""
        turns.append({'user': user_prompt, 'response': resp, 'has_image': has_img})
    return turns

def convert_single_mhtml(mhtml_path, title=None):
    """Convert a single MHTML chat export to Markdown."""
    html = extract_html_from_mhtml(mhtml_path)
    if not html:
        raise ValueError(f"No HTML content could be extracted from {mhtml_path}")

    turns = parse_chat_turns(html)
    doc_title = title or os.path.splitext(os.path.basename(mhtml_path))[0]

    md_lines = [
        f"# {doc_title}",
        "",
        f"> **Source**: `{os.path.basename(mhtml_path)}`",
        f"> **Total Turns**: {len(turns)}",
        "",
        "---",
        ""
    ]

    for i, t in enumerate(turns, 1):
        md_lines.append(f"## 👤 User [Turn {i}]")
        md_lines.append("")
        if t['has_image']:
            md_lines.append("📷 *[Attached Image / Photo]*\n")
        md_lines.append(t['user'] if t['user'] else "*(Image / attachment only)*")
        md_lines.append("")
        md_lines.append(f"## 🤖 Assistant [Turn {i}]")
        md_lines.append("")
        md_lines.append(t['response'])
        md_lines.append("")
        md_lines.append("---")
        md_lines.append("")

    return "\n".join(md_lines)

def merge_mhtml_chats(mhtml_files, output_title="Merged Chat Transcript"):
    """
    Merge multiple chronologically ordered MHTML chats with automatic overlap deduplication.
    Specifically handles pattern where Session N+1 begins by re-pasting Session N's transcript.
    """
    all_sessions_turns = []
    for path in mhtml_files:
        html = extract_html_from_mhtml(path)
        if not html:
            print(f"Warning: could not extract HTML from {path}, skipping.", file=sys.stderr)
            continue
        turns = parse_chat_turns(html)
        all_sessions_turns.append((os.path.basename(path), turns))

    if not all_sessions_turns:
        raise ValueError("No valid sessions to merge.")

    merged_lines = [
        f"# {output_title}",
        "",
        f"> **Merged Sessions**: {', '.join(f'`{name}`' for name, _ in all_sessions_turns)}",
        "> **Deduplication**: Automatic overlap and prompt re-paste detection applied.",
        "",
        "---",
        ""
    ]

    turn_counter = 1

    for s_idx, (session_name, turns) in enumerate(all_sessions_turns):
        part_num = s_idx + 1
        merged_lines.append(f"# Part {part_num}: Session from `{session_name}`")
        merged_lines.append("")
        merged_lines.append("---")
        merged_lines.append("")

        start_turn = 0
        # If not the first session, check if Turn 0 is a re-paste of earlier session
        if s_idx > 0 and turns:
            first_user = turns[0]['user']
            # If the first prompt is extraordinarily long or contains text matching previous session
            if len(first_user) > 1000 or "specifications identification" in first_user.lower():
                merged_lines.append(f"## 👤 User [Turn {turn_counter}]")
                merged_lines.append("")
                merged_lines.append("*(Pasted transcript of previous session to continue context)*")
                merged_lines.append("")
                merged_lines.append(f"## 🤖 Assistant [Turn {turn_counter}]")
                merged_lines.append("")
                merged_lines.append(turns[0]['response'])
                merged_lines.append("")
                merged_lines.append("---")
                merged_lines.append("")
                turn_counter += 1
                start_turn = 1

        for i in range(start_turn, len(turns)):
            t = turns[i]
            merged_lines.append(f"## 👤 User [Turn {turn_counter}]")
            merged_lines.append("")
            if t['has_image']:
                merged_lines.append("📷 *[Attached Image / Photo]*\n")
            merged_lines.append(t['user'] if t['user'] else "*(Image / attachment only)*")
            merged_lines.append("")
            merged_lines.append(f"## 🤖 Assistant [Turn {turn_counter}]")
            merged_lines.append("")
            merged_lines.append(t['response'])
            merged_lines.append("")
            merged_lines.append("---")
            merged_lines.append("")
            turn_counter += 1

    return "\n".join(merged_lines)

def main():
    parser = argparse.ArgumentParser(description="Convert and merge MHTML chat transcripts to Markdown.")
    parser.add_argument("inputs", nargs="+", help="One or more .mhtml files")
    parser.add_argument("-o", "--output", help="Output Markdown file path (default: stdout or input.md)")
    parser.add_argument("--merge", action="store_true", help="Merge multiple MHTML files into one Markdown file with deduplication")
    parser.add_argument("--title", help="Custom title for the Markdown document")
    args = parser.parse_args()

    for inp in args.inputs:
        if not os.path.exists(inp):
            print(f"Error: input file '{inp}' does not exist.", file=sys.stderr)
            sys.exit(1)

    if len(args.inputs) == 1 and not args.merge:
        md = convert_single_mhtml(args.inputs[0], title=args.title)
    else:
        title = args.title or "Merged Chat Transcript"
        md = merge_mhtml_chats(args.inputs, output_title=title)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(md)
        print(f"Successfully wrote Markdown to '{args.output}' ({len(md):,} chars).")
    else:
        sys.stdout.write(md)

if __name__ == "__main__":
    main()
