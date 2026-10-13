#!/usr/bin/env python3
"""Look at a built explainer without opening it by hand: screenshots of chosen steps, and a layout lint.

usage: shoot.py PAGE --frames 0,12,30 [--out shots] [--size 1600x1000]     screenshots of video frames at rest
       shoot.py PAGE --slides 0,4,9   [--out shots] [--size 1600x1000]     screenshots of slides (gates unlocked)
       shoot.py PAGE --lint                                                 overlaps, clipped or tiny text, on every frame

PAGE is a preview-*-video.html or preview-*-slides.html written by build.py (a path or an http URL).
Needs Chrome or Chromium; set CHROME to its binary if it is not found."""
import argparse, json, os, pathlib, re, shutil, subprocess, sys, tempfile, time

def chrome():
    c = [os.environ.get('CHROME'), '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
         '/Applications/Chromium.app/Contents/MacOS/Chromium', shutil.which('google-chrome'), shutil.which('chromium'), shutil.which('chromium-browser')]
    for p in c:
        if p and pathlib.Path(p).exists():
            return p
    sys.exit('Chrome not found. Set CHROME to the browser binary, or check the page in a browser by hand.')

def run(args, done, timeout=45):
    """Headless Chrome often stays alive after its work is done, so stop it as soon as done() is true."""
    prof = tempfile.mkdtemp(prefix='kx-chrome-')
    p = subprocess.Popen([chrome(), '--headless=new', '--disable-gpu', '--hide-scrollbars', '--no-first-run', '--user-data-dir=' + prof] + args,
                         stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    t0 = time.time(); out = b''
    try:
        while time.time() - t0 < timeout:
            if done():
                time.sleep(.4); break
            if p.poll() is not None:
                break
            time.sleep(.25)
    finally:
        if p.poll() is None:
            p.terminate()
        try:
            out = p.communicate(timeout=5)[0]
        except Exception:
            p.kill()
        shutil.rmtree(prof, ignore_errors=True)
    return out.decode('utf-8', 'replace')

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('page'); ap.add_argument('--frames'); ap.add_argument('--slides'); ap.add_argument('--lint', action='store_true')
    ap.add_argument('--out', default='shots'); ap.add_argument('--size', default='1600x1000')
    a = ap.parse_args()
    base = a.page if re.match(r'https?://', a.page) else pathlib.Path(a.page).resolve().as_uri()
    w, h = a.size.split('x')
    if a.lint:
        tmp = pathlib.Path(tempfile.mkdtemp(prefix='kx-lint-')) / 'dom.html'
        with open(tmp, 'wb') as f:
            p = subprocess.Popen([chrome(), '--headless=new', '--disable-gpu', '--no-first-run', '--user-data-dir=' + tempfile.mkdtemp(prefix='kx-chrome-'),
                                  '--window-size=1600,1000', '--virtual-time-budget=60000', '--dump-dom', base + '?lint=1&still=1'], stdout=f, stderr=subprocess.DEVNULL)
            t0 = time.time()
            while time.time() - t0 < 90 and p.poll() is None:
                time.sleep(.5)
                if b'LINT_DONE' in tmp.read_bytes():
                    time.sleep(.5); break
            if p.poll() is None:
                p.terminate()
        m = re.search(r'<pre id="lint">(.*?)</pre>', tmp.read_text('utf-8', 'replace'), re.S)
        if not m or not m.group(1).strip():
            sys.exit('lint did not finish; open the page with ?lint=1 in a browser instead')
        import html as H
        rep = json.loads(H.unescape(m.group(1)))
        print('%d frames, about %s minutes at 1x' % (rep['frames'], rep['minutes']))
        if not rep['problems']:
            print('no layout problems found')
        for msg, frames in sorted(rep['problems'].items(), key=lambda kv: kv[1][0]):
            print('  frames %s: %s' % (','.join(map(str, frames[:8])) + ('…' if len(frames) > 8 else ''), msg))
        return
    out = pathlib.Path(a.out); out.mkdir(parents=True, exist_ok=True)
    key, picks = ('s', a.slides) if a.slides else ('f', a.frames or '0')
    for n in picks.split(','):
        png = out / ('%s%03d.png' % (key, int(n)))
        if png.exists():
            png.unlink()
        url = '%s?still=1&%s%s=%s' % (base, 'unlock=1&' if a.slides else '', key, n.strip())
        run(['--window-size=%s,%s' % (w, h), '--virtual-time-budget=8000', '--screenshot=' + str(png), url], lambda: png.exists() and png.stat().st_size > 0)
        print(png if png.exists() else 'FAILED %s' % png)

if __name__ == '__main__':
    main()
