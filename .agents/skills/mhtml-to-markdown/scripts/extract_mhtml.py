#!/usr/bin/env python3
"""
extract_mhtml.py - Extract and decode the root HTML document from an MHTML web archive.
Compliant with RFC 2557 (MIME Encapsulation of Aggregate Documents).
"""

import email
import quopri
import base64
import argparse
import sys
import os

def extract_html_from_mhtml(filepath):
    """
    Extract and decode the main HTML content from an MHTML file.
    The first text/html part is typically the root resource.
    """
    with open(filepath, 'rb') as f:
        raw_bytes = f.read()

    msg = email.message_from_bytes(raw_bytes)

    for i, part in enumerate(msg.walk()):
        ct = part.get_content_type()
        if ct == 'text/html':
            payload_bytes = part.get_payload(decode=True)
            if payload_bytes is None:
                payload_raw = part.get_payload(decode=False)
                enc = part.get('Content-Transfer-Encoding', '7bit').lower().strip()
                if isinstance(payload_raw, str):
                    payload_raw = payload_raw.encode('utf-8', errors='replace')
                if enc == 'quoted-printable':
                    payload_bytes = quopri.decodestring(payload_raw)
                elif enc == 'base64':
                    payload_bytes = base64.b64decode(payload_raw)
                else:
                    payload_bytes = payload_raw

            charset = part.get_content_charset() or 'utf-8'
            html = payload_bytes.decode(charset, errors='replace')
            return html

    return None

def main():
    parser = argparse.ArgumentParser(description="Extract raw HTML from an MHTML file.")
    parser.add_argument("mhtml_file", help="Path to input .mhtml file")
    parser.add_argument("-o", "--output", help="Output .html file path (default: stdout or file.html)")
    args = parser.parse_args()

    if not os.path.exists(args.mhtml_file):
        print(f"Error: file '{args.mhtml_file}' does not exist.", file=sys.stderr)
        sys.exit(1)

    html = extract_html_from_mhtml(args.mhtml_file)
    if not html:
        print(f"Error: no text/html part found in '{args.mhtml_file}'.", file=sys.stderr)
        sys.exit(1)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"Successfully extracted {len(html):,} chars to '{args.output}'.")
    else:
        sys.stdout.write(html)

if __name__ == "__main__":
    main()
