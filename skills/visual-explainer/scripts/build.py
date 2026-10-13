#!/usr/bin/env python3
"""Build the two delivery versions of an explainer from one story.

usage: build.py --title "Name" [--name slug] [--out dist] [--kit DIR] [--video-title T] [--slides-title T] [--only video|slides] story.js [more.js ...]

Writes into --out:
  <name>-video.html, <name>-slides.html    page fragments, ready to publish as artifacts
  preview-<name>-video.html, preview-<name>-slides.html    wrapped documents for a local browser
Story files are concatenated in the order given. Nothing is fetched and nothing outside --out is written."""
import argparse, html, pathlib, re, shutil, subprocess, sys, tempfile

WRAP = ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
        '<style>:root{color-scheme:light}body{margin:0;font:14px system-ui}img{max-width:100%}[hidden]{display:none!important}</style>'
        '</head><body>\n@@PAGE@@\n</body></html>\n')

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('stories', nargs='+')
    ap.add_argument('--title', required=True)
    ap.add_argument('--name')
    ap.add_argument('--video-title'); ap.add_argument('--slides-title')
    ap.add_argument('--only', choices=['video', 'slides'])
    ap.add_argument('--out', default='dist')
    ap.add_argument('--kit', default=str(pathlib.Path(__file__).resolve().parent.parent / 'assets' / 'kit'))
    a = ap.parse_args()
    kit = pathlib.Path(a.kit)
    name = a.name or re.sub(r'[^a-z0-9]+', '-', a.title.lower()).strip('-')
    out = pathlib.Path(a.out); out.mkdir(parents=True, exist_ok=True)
    read = lambda p: pathlib.Path(p).read_text(encoding='utf-8')
    css = read(kit / 'kit.css')
    js = read(kit / 'engine.js') + '\n' + read(kit / 'formats.js')
    story = '\n'.join(read(s) for s in a.stories)
    # a quick syntax check of everything that will run, before it is inlined
    if shutil.which('node'):
        with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as t:
            t.write(js + '\n' + story); tmp = t.name
        r = subprocess.run(['node', '--check', tmp], capture_output=True, text=True)
        pathlib.Path(tmp).unlink()
        if r.returncode:
            sys.exit('syntax error in kit or story:\n' + r.stderr)
    safe = lambda s: s.replace('</script', '<\\/script')
    titles = {'video': a.video_title or a.title, 'slides': a.slides_title or a.title + ' in Slides'}
    for shell in ([a.only] if a.only else ['video', 'slides']):
        page = read(kit / (shell + '.html'))
        page = page.replace('{{TITLE}}', html.escape(titles[shell])).replace('/*{{CSS}}*/', css)
        page = page.replace('/*{{KIT}}*/', safe(js)).replace('/*{{STORY}}*/', safe(story))
        f = out / ('%s-%s.html' % (name, shell)); f.write_text(page, encoding='utf-8')
        (out / ('preview-%s-%s.html' % (name, shell))).write_text(WRAP.replace('@@PAGE@@', page), encoding='utf-8')
        print('%s  %.0f KB' % (f, len(page.encode('utf-8')) / 1024))

if __name__ == '__main__':
    main()
