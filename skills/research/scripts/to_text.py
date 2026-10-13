#!/usr/bin/env python3
"""Turn one source into plain text on disk, keeping page or section boundaries.

    to_text.py SOURCE -o OUT.txt

SOURCE is a local file (.pdf, .html, .htm, .txt, .md, ...) or an http(s) URL.

  PDF   pages are separated by "===== PAGE n =====" lines, so facts can cite pages.
  HTML  is split at h1/h2 headings into "===== SECTION n: title =====" blocks.
  Text  is copied under a single "===== PAGE 1 =====" marker.

Lines longer than about 240 characters are wrapped at spaces, because file
readers cut long lines off and the lost text is easy to miss.

For a URL the original file is kept next to OUT (same name, original extension).
An arXiv abstract link is rewritten to the PDF, because the abstract page holds
only the abstract.

Prints a one-line JSON summary. Exit code 2 means no text could be extracted
(for example a scanned PDF): look at the pages as images instead.

Uses only the standard library. PDF text comes from the first backend that
works: pdftotext, pypdf / PyPDF2, PyMuPDF, pdfminer.six, macOS PDFKit.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import textwrap
import urllib.error
import urllib.request
from html.parser import HTMLParser

THIN_PAGE_CHARS = 200
WRAP_AT = 200
MAX_DOWNLOAD = 200 * 1024 * 1024
USER_AGENT = "Mozilla/5.0 (research-skill to_text.py)"


# ---------- PDF backends ----------

def pdf_pdftotext(path):
    exe = shutil.which("pdftotext")
    if not exe:
        return None
    run = subprocess.run([exe, "-layout", "-enc", "UTF-8", path, "-"],
                         capture_output=True, timeout=600)
    if run.returncode != 0:
        return None
    pages = run.stdout.decode("utf-8", "replace").split("\f")
    if pages and not pages[-1].strip():
        pages.pop()
    return pages


def pdf_pypdf(path):
    try:
        from pypdf import PdfReader
    except ImportError:
        try:
            from PyPDF2 import PdfReader
        except ImportError:
            return None
    return [(page.extract_text() or "") for page in PdfReader(path).pages]


def pdf_pymupdf(path):
    try:
        import fitz
    except ImportError:
        return None
    with fitz.open(path) as doc:
        return [page.get_text() for page in doc]


def pdf_pdfminer(path):
    try:
        from pdfminer.high_level import extract_pages
        from pdfminer.layout import LTTextContainer
    except ImportError:
        return None
    return ["".join(el.get_text() for el in layout if isinstance(el, LTTextContainer))
            for layout in extract_pages(path)]


JXA = r"""
ObjC.import("Quartz");
ObjC.import("Foundation");
function run(argv) {
  var doc = $.PDFDocument.alloc.initWithURL($.NSURL.fileURLWithPath(argv[0]));
  if (!doc || doc.isNil()) { return "ERR"; }
  var n = doc.pageCount, pages = [];
  for (var i = 0; i < n; i++) {
    var s = ObjC.unwrap(doc.pageAtIndex(i).string);
    pages.push(s ? s : "");
  }
  $(JSON.stringify(pages)).writeToFileAtomicallyEncodingError(argv[1], true, $.NSUTF8StringEncoding, null);
  return String(n);
}
"""


def pdf_pdfkit(path):
    if sys.platform != "darwin" or not shutil.which("osascript"):
        return None
    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, "pages.json")
        run = subprocess.run(["osascript", "-l", "JavaScript", "-e", JXA, os.path.abspath(path), out],
                             capture_output=True, timeout=600)
        if run.returncode != 0 or not os.path.exists(out):
            return None
        with open(out, encoding="utf-8") as f:
            return json.load(f)


PDF_BACKENDS = [("pdftotext", pdf_pdftotext), ("pypdf", pdf_pypdf), ("pymupdf", pdf_pymupdf),
                ("pdfminer", pdf_pdfminer), ("pdfkit", pdf_pdfkit)]


def pdf_to_pages(path):
    for name, backend in PDF_BACKENDS:
        try:
            pages = backend(path)
        except Exception as exc:  # a broken backend should not hide a working one
            print(f"to_text: {name} failed: {exc}", file=sys.stderr)
            pages = None
        if pages:
            return name, pages
    return None, []


# ---------- HTML ----------

BLOCK = {"p", "div", "section", "article", "main", "header", "footer", "aside", "ul", "ol", "dl",
         "table", "figure", "figcaption", "blockquote", "pre", "form", "dt", "dd", "tr"}
SKIP = {"script", "style", "noscript", "svg", "template", "nav", "button"}
HEADINGS = {"h1": 1, "h2": 2, "h3": 3, "h4": 4, "h5": 5, "h6": 6}


class TextExtractor(HTMLParser):
    """Collects readable text; h1/h2 start a new section."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.sections = [["", []]]
        self.skip = 0
        self.math = 0
        self.pre = 0
        self.heading = None
        self.heading_buf = []
        self.title = ""
        self.in_title = False

    def out(self, text):
        self.sections[-1][1].append(text)

    def handle_starttag(self, tag, attrs):
        if tag in SKIP:
            self.skip += 1
            return
        if self.skip:
            return
        if tag == "math":
            alt = dict(attrs).get("alttext")
            if not self.math and alt:
                (self.heading_buf if self.heading else self.sections[-1][1]).append(f" ${alt}$ ")
            self.math += 1
            return
        if self.math:
            return
        if tag == "title":
            self.in_title = True
        elif tag in HEADINGS:
            self.heading = tag
            self.heading_buf = []
        elif tag == "pre":
            self.pre += 1
            self.out("\n\n")
        elif tag in BLOCK:
            self.out("\n\n")
        elif tag == "br":
            self.out("\n")
        elif tag == "li":
            self.out("\n- ")
        elif tag in ("td", "th"):
            self.out(" | ")

    def handle_endtag(self, tag):
        if tag in SKIP:
            self.skip = max(0, self.skip - 1)
            return
        if self.skip:
            return
        if tag == "math":
            self.math = max(0, self.math - 1)
            return
        if self.math:
            return
        if tag == "title":
            self.in_title = False
        elif tag in HEADINGS and self.heading == tag:
            text = " ".join("".join(self.heading_buf).split())
            level = HEADINGS[tag]
            if level <= 2 and text:
                self.sections.append([text, []])
            if text:
                self.out("\n\n" + "#" * level + " " + text + "\n\n")
            self.heading = None
        elif tag == "pre":
            self.pre = max(0, self.pre - 1)
            self.out("\n\n")
        elif tag in BLOCK:
            self.out("\n\n")

    def handle_data(self, data):
        if self.skip or self.math:
            return
        if self.in_title:
            self.title += data
        elif self.heading:
            self.heading_buf.append(data)
        elif self.pre:
            self.out(data)
        else:
            self.out(re.sub(r"\s+", " ", data))


def html_to_sections(raw):
    parser = TextExtractor()
    parser.feed(raw)
    parser.close()
    sections = []
    for title, chunks in parser.sections:
        text = "".join(chunks)
        text = re.sub(r"[ \t]+\n", "\n", text)
        text = re.sub(r"\n{3,}", "\n\n", text).strip()
        if text:
            sections.append((title, text))
    return " ".join(parser.title.split()), sections


def wrap(text):
    """Break very long lines at spaces: file readers cut long lines off, which loses text silently."""
    lines = []
    for line in text.split("\n"):
        if len(line) <= WRAP_AT + 40:
            lines.append(line)
        else:
            lines += textwrap.wrap(line, WRAP_AT, break_long_words=False, break_on_hyphens=False) or [""]
    return "\n".join(lines)


# ---------- input ----------

def arxiv_pdf_url(url):
    m = re.match(r"https?://(?:www\.)?arxiv\.org/abs/([^?#]+)", url)
    return f"https://arxiv.org/pdf/{m.group(1)}" if m else None


def fetch_with_curl(url):
    """Python on some machines has no certificate bundle and cannot open any https URL; curl uses the system's."""
    exe = shutil.which("curl")
    if not exe:
        return None
    with tempfile.TemporaryDirectory() as tmp:
        target = os.path.join(tmp, "body")
        run = subprocess.run([exe, "-fsSL", "--max-time", "300", "--max-filesize", str(MAX_DOWNLOAD),
                              "-A", USER_AGENT, "-o", target, "-w", "%{content_type}\n%{url_effective}", url],
                             capture_output=True, text=True)
        if run.returncode != 0 or not os.path.isfile(target):
            print(f"to_text: curl failed too: {run.stderr.strip()}", file=sys.stderr)
            return None
        with open(target, "rb") as f:
            body = f.read()
    ctype, _, final_url = run.stdout.partition("\n")
    return body, ctype.strip(), final_url.strip() or url


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            body = resp.read(MAX_DOWNLOAD + 1)
            if len(body) > MAX_DOWNLOAD:
                raise SystemExit(f"to_text: {url} is larger than {MAX_DOWNLOAD} bytes, refusing")
            return body, resp.headers.get("Content-Type", ""), resp.geturl()
    except urllib.error.HTTPError as exc:
        raise SystemExit(f"to_text: {url} answered {exc.code} {exc.reason}")
    except (urllib.error.URLError, OSError) as exc:
        print(f"to_text: Python could not open the URL ({getattr(exc, 'reason', exc)}); trying curl", file=sys.stderr)
        got = fetch_with_curl(url)
        if got is None:
            raise SystemExit(f"to_text: could not download {url}. Download it another way and pass the file.")
        return got


def decode(body, content_type=""):
    m = re.search(r"charset=([\w-]+)", content_type or "")
    encodings = ([m.group(1)] if m else []) + ["utf-8", "latin-1"]
    for enc in encodings:
        try:
            return body.decode(enc)
        except (LookupError, UnicodeDecodeError):
            continue
    return body.decode("utf-8", "replace")


def main():
    ap = argparse.ArgumentParser(description="Turn a PDF, HTML page, text file or URL into plain text.")
    ap.add_argument("source", help="local path or http(s) URL")
    ap.add_argument("-o", "--out", required=True, help="output .txt path")
    args = ap.parse_args()

    out = os.path.abspath(args.out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    stem = os.path.splitext(out)[0]
    summary = {"source": args.source, "out": out}

    if re.match(r"https?://", args.source):
        url = args.source
        rewritten = arxiv_pdf_url(url)
        if rewritten:
            summary["rewritten_from"] = url
            url = rewritten
        body, ctype, final_url = fetch(url)
        summary["url"] = final_url
        is_pdf = body[:5] == b"%PDF-" or "pdf" in ctype.lower()
        original = stem + (".pdf" if is_pdf else ".html")
        with open(original, "wb") as f:
            f.write(body)
        summary["original"] = original
        path, kind = original, ("pdf" if is_pdf else "html")
    else:
        path = os.path.abspath(os.path.expanduser(args.source))
        if not os.path.isfile(path):
            raise SystemExit(f"to_text: no such file: {path}")
        with open(path, "rb") as f:
            head = f.read(5)
        ext = os.path.splitext(path)[1].lower()
        kind = "pdf" if head == b"%PDF-" else ("html" if ext in (".html", ".htm", ".xhtml") else "text")
        ctype = ""

    blocks = []
    if kind == "pdf":
        backend, pages = pdf_to_pages(path)
        summary.update(kind="pdf", backend=backend, pages=len(pages))
        if not any(p.strip() for p in pages):
            summary["error"] = ("no text could be extracted (scanned PDF, or no PDF backend available); "
                                "look at the pages as images instead")
            print(json.dumps(summary, ensure_ascii=False))
            sys.exit(2)
        summary["thin_pages"] = [i + 1 for i, p in enumerate(pages) if len(p.strip()) < THIN_PAGE_CHARS]
        blocks = [(f"===== PAGE {i + 1} =====", p.strip()) for i, p in enumerate(pages)]
    elif kind == "html":
        with open(path, "rb") as f:
            raw = decode(f.read(), ctype)
        title, sections = html_to_sections(raw)
        summary.update(kind="html", title=title, sections=len(sections))
        blocks = [(f"===== SECTION {i + 1}: {t or title or '(untitled)'} =====", text)
                  for i, (t, text) in enumerate(sections)]
        if not blocks:
            summary["error"] = "the page has no readable text (it may need JavaScript to render)"
            print(json.dumps(summary, ensure_ascii=False))
            sys.exit(2)
    else:
        with open(path, "rb") as f:
            text = decode(f.read())
        summary.update(kind="text")
        blocks = [("===== PAGE 1 =====", text.strip())]

    with open(out, "w", encoding="utf-8") as f:
        for marker, text in blocks:
            f.write(marker + "\n" + wrap(text) + "\n\n")
    summary["chars"] = sum(len(t) for _, t in blocks)
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
