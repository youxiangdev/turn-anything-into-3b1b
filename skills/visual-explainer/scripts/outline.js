#!/usr/bin/env node
/* Print a story as a script: every frame of the video version with its chapter, segment, step and narration line.
   usage: node outline.js [--kit DIR] story.js [more.js ...]
   Use it to proofread the narration in one read, to count steps per chapter, and to say where each fact is shown.
   Lines longer than about 230 characters are marked with "!". Needs nothing but Node. */
const fs = require('fs'), path = require('path'), vm = require('vm');
const args = process.argv.slice(2), files = [];
let kit = path.join(__dirname, '..', 'assets', 'kit');
for (let i = 0; i < args.length; i++) { if (args[i] === '--kit') kit = args[++i]; else files.push(args[i]); }
if (!files.length) { console.error('usage: node outline.js [--kit DIR] story.js [more.js ...]'); process.exit(2); }
/* the kit only touches the page when a segment is mounted, so a few stand-ins are enough to load a story */
const box = { console, setTimeout, clearTimeout, performance: { now: () => 0 }, requestAnimationFrame: () => 0, cancelAnimationFrame: () => {}, document: {}, matchMedia: () => ({ matches: false }) };
box.window = box; vm.createContext(box);
for (const f of [path.join(kit, 'engine.js'), path.join(kit, 'formats.js')].concat(files)) vm.runInContext(fs.readFileSync(f, 'utf8'), box, { filename: f });
const Kit = box.Kit, S = Kit.STORY;
if (!S) { console.error('no Kit.story(...) call found in the story files'); process.exit(1); }
const F = Kit.frames(S); let c = -1, s = -1, long = 0;
F.forEach((f, i) => {
  if (f.c !== c) { c = f.c; console.log('\n# ' + (S.chapters[c].kicker || ('Part ' + (c + 1))) + ' · ' + S.chapters[c].title); }
  if (f.s !== s) { s = f.s; console.log('\n## ' + f.seg.kind + (f.seg.title ? ' · ' + f.seg.title : '')); }
  const tag = f.rewind ? 'rewind' : f.pick ? 'press ' + Object.keys(f.pick).map(k => f.pick[k]).join(' + ') : f.gate ? f.gate.type + ' gate' : '';
  const over = (f.cap || '').length > 230; if (over) long++;
  console.log(String(i).padStart(4) + (over ? ' !' : '  ') + 'step ' + String(f.k + 1).padStart(2) + (tag ? '  [' + tag + ']' : '') + '  ' + f.cap);
});
const total = F.reduce((a, f) => a + Kit.dwell(f) + 1500, 0);
console.log('\nTotal: ' + F.length + ' frames, about ' + (total / 60000).toFixed(1) + ' minutes at 1x, ' + S.chapters.length + ' chapters' + (long ? ', ' + long + ' lines over 230 characters' : ''));
