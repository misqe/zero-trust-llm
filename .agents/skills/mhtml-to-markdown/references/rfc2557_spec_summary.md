# RFC 2557 Specification Reference & Skill Extension Roadmap

This document serves as the architectural reference for **RFC 2557** (*MIME Encapsulation of Aggregate Documents, such as HTML (MHTML)*) and provides the roadmap for extending this skill from its current text/HTML extraction subset into a full, compliant MHTML unpacker.

The complete original RFC document is included alongside this file:
- **PDF Document**: [rfc2557.txt.pdf](./rfc2557.txt.pdf)

---

## 1. RFC 2557 Core Specification Map

RFC 2557 standardizes how multi-resource documents (HTML + CSS + images + applets) are packaged into a single MIME `multipart/related` stream.

| Section | Title | Key Mechanism | Current Status in Skill |
| :--- | :--- | :--- | :--- |
| **§4** | Content-Location Header | Labels body parts with relative or absolute URIs; allows URI folding/unfolding. | Ignored (parts traversed blindly). |
| **§5** | Base URI Resolution | 5-step fallback hierarchy: `<BASE>` tag ➔ part `Content-Location` ➔ parent `Content-Location` ➔ HTTP URI ➔ `thismessage:/`. | Not implemented. |
| **§7** | `multipart/related` & `start` | Defines container structure; `start="<content-id>"` points to root document (which may not be part 0). | Basic traversal; assumes root is first `text/html`. |
| **§8.2** | URI Resolution in HTML | Resolves relative/absolute URLs in HTML against sibling parts by matching `Content-Location` or `Content-ID`. | Not implemented (links left as-is). |
| **§8.3** | CID URLs (`cid:`) | Matches `<img src="cid:id@host">` against `Content-ID: <id@host>`. | Not implemented (images left unextracted). |
| **§9.6** | Nested Boundaries | Scoping rules for references across nested/parallel `multipart/related` parts. | Flat traversal only. |
| **§10** | Charsets & Encodings | Canonical CRLF line breaks, `charset` parameter, `quoted-printable` / `base64`. | **Fully Implemented** via `email` & `quopri`. |

---

## 2. Current Implementation Scope

The skill currently implements a **targeted extraction subset**:
- **Container Parsing**: Uses Python's standard `email.message_from_bytes()` to parse the MIME envelope.
- **Payload Decoding**: Decodes `quoted-printable` and `base64` Content-Transfer-Encodings.
- **Encoding Normalization**: Extracts `charset` (defaulting to UTF-8) and converts bytes to Unicode.
- **Root Extraction**: Pulls the first `text/html` part for conversion to Markdown.
- **Chat Turn Pipeline**: Specialized parsing for Gemini web component DOMs (`<share-turn-viewer>`, `<code-block>`, etc.) and multi-session overlap deduplication.

---

## 3. Future Expansion Roadmap

When the skill needs to handle general MHTML archives or extract multimedia assets, implement the following roadmap:

### Phase 1: CID & Content-Location Asset Unpacker
- **Goal**: Extract embedded images (`image/jpeg`, `image/png`, `image/gif`, `image/webp`) and stylesheets from the archive to a local `./assets/` or `./media/` directory.
- **Mechanism**:
  1. Build a dictionary mapping `part.get('Content-ID')` (stripped of angle brackets `<...>`) and `part.get('Content-Location')` to the decoded binary payload and suggested filename.
  2. In the extracted HTML/Markdown, replace `<img src="cid:xyz">` with `![image](./assets/xyz.png)`.
  3. Replace relative URLs matching sibling `Content-Location` headers with relative file paths.

### Phase 2: Full `start` Parameter Compliance
- **Goal**: Support archives where the root HTML is not the first part or is wrapped inside a `multipart/alternative` block.
- **Mechanism**:
  1. Inspect the top-level `Content-Type` header for the `start` parameter (e.g. `start="<root-part-id>"`).
  2. If present, find the part whose `Content-ID` matches `start`.
  3. Fall back to the first `text/html` part only if `start` is absent.

### Phase 3: Base URI Cascading & Rewriting
- **Goal**: Correctly resolve relative links and assets when documents rely on `<base href="...">` or header-level `Content-Location`.
- **Mechanism**:
  1. Parse the HTML `<base href="...">` tag if present.
  2. Fall back to parent container `Content-Location`.
  3. Resolve all internal relative URIs against the computed Base URI using `urllib.parse.urljoin()`.
