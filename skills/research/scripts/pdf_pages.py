#!/usr/bin/env python3
"""Render pages of a PDF as PNG images, so that tables and figures can be looked at.

    pdf_pages.py PDF OUT_DIR PAGES

PAGES is a list such as `30`, `35-38` or `5,10,35-38`.

Text extraction scrambles tables, drops figures, and changes some characters
(a double hyphen can arrive as a dash). When a statement depends on a table or
a figure, or on the exact spelling of a flag or identifier, render the page and
read it from the image.

Uses the first backend that works: pdftoppm, PyMuPDF, macOS PDFKit.
Prints one line per image written. Exit code 2 when no backend is available.
"""
import argparse
import os
import shutil
import subprocess
import sys

DPI = 150


def parse_pages(text):
    pages = []
    for chunk in text.replace(" ", "").split(","):
        if not chunk:
            continue
        lo, _, hi = chunk.partition("-")
        lo, hi = int(lo), int(hi or lo)
        if lo < 1 or hi < lo:
            raise SystemExit(f"pdf_pages: bad page range '{chunk}'")
        pages += range(lo, hi + 1)
    return sorted(set(pages))


def name(out_dir, page):
    return os.path.join(out_dir, f"page-{page:03d}.png")


def with_pdftoppm(pdf, out_dir, pages):
    exe = shutil.which("pdftoppm")
    if not exe:
        return None
    done = []
    for page in pages:
        target = name(out_dir, page)
        run = subprocess.run([exe, "-png", "-r", str(DPI), "-f", str(page), "-l", str(page), "-singlefile",
                              pdf, target[:-4]], capture_output=True, timeout=300)
        if run.returncode != 0 or not os.path.exists(target):
            return None
        done.append(target)
    return done


def with_pymupdf(pdf, out_dir, pages):
    try:
        import fitz
    except ImportError:
        return None
    done = []
    with fitz.open(pdf) as doc:
        for page in pages:
            if page > doc.page_count:
                raise SystemExit(f"pdf_pages: the document has {doc.page_count} pages, no page {page}")
            target = name(out_dir, page)
            doc[page - 1].get_pixmap(dpi=DPI).save(target)
            done.append(target)
    return done


JXA = r"""
ObjC.import("Quartz");
ObjC.import("AppKit");
function run(argv) {
  var doc = $.PDFDocument.alloc.initWithURL($.NSURL.fileURLWithPath(argv[0]));
  if (!doc || doc.isNil()) { return "ERR cannot open the PDF"; }
  var scale = parseFloat(argv[2]), done = [];
  for (var k = 3; k < argv.length; k++) {
    var p = parseInt(argv[k], 10);
    if (p > doc.pageCount) { return "ERR the document has " + doc.pageCount + " pages, no page " + p; }
    var page = doc.pageAtIndex(p - 1);
    var box = page.boundsForBox($.kPDFDisplayBoxMediaBox);
    var size = $.NSMakeSize(box.size.width * scale, box.size.height * scale);
    var image = page.thumbnailOfSizeForBox(size, $.kPDFDisplayBoxMediaBox);
    var rep = $.NSBitmapImageRep.imageRepWithData(image.TIFFRepresentation);
    var png = rep.representationUsingTypeProperties($.NSBitmapImageFileTypePNG, $({}));
    var out = argv[1] + "/page-" + ("000" + p).slice(-3) + ".png";
    png.writeToFileAtomically(out, true);
    done.push(out);
  }
  return done.join("\n");
}
"""


def with_pdfkit(pdf, out_dir, pages):
    if sys.platform != "darwin" or not shutil.which("osascript"):
        return None
    run = subprocess.run(["osascript", "-l", "JavaScript", "-e", JXA, pdf, out_dir, str(DPI / 72.0)]
                         + [str(p) for p in pages], capture_output=True, text=True, timeout=600)
    out = run.stdout.strip()
    if out.startswith("ERR"):
        raise SystemExit("pdf_pages: " + out[4:])
    if run.returncode != 0 or not out:
        return None
    return out.split("\n")


def main():
    ap = argparse.ArgumentParser(description="Render pages of a PDF as PNG images.")
    ap.add_argument("pdf")
    ap.add_argument("out_dir")
    ap.add_argument("pages", help="for example 30 or 35-38 or 5,10,35-38")
    args = ap.parse_args()
    pdf = os.path.abspath(os.path.expanduser(args.pdf))
    if not os.path.isfile(pdf):
        raise SystemExit(f"pdf_pages: no such file: {pdf}")
    out_dir = os.path.abspath(os.path.expanduser(args.out_dir))
    os.makedirs(out_dir, exist_ok=True)
    pages = parse_pages(args.pages)
    for backend in (with_pdftoppm, with_pymupdf, with_pdfkit):
        done = backend(pdf, out_dir, pages)
        if done:
            print("\n".join(done))
            return
    print("pdf_pages: no way to render PDF pages here (needs pdftoppm, PyMuPDF, or macOS)", file=sys.stderr)
    sys.exit(2)


if __name__ == "__main__":
    main()
