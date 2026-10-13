# Output skills

The third stage is a slot. Any skill that can turn a body of content into a finished deliverable
can sit in it. The research and scope stages do not change when the output does, so a dossier
made once can be turned into a video today and a slide deck next month.

## What a skill needs in order to fit the slot

1. **It builds from content it is given.** The deep-dive pipeline hands it a dossier folder and
   a scope file. It must not need the topic to be baked into its own instructions.
2. **It decides form, not coverage.** What must appear is settled by the scope. The output
   skill chooses how each thing is shown: which format, what order of scenes, what moves.
3. **It writes files under the folder it is told to use** (`<run>/output/`), as text the coverage
   check can read: HTML, JavaScript, JSON, Markdown, SVG or subtitles. A binary-only output
   (a rendered video file, a `.pptx`) should keep its text source beside it, or the names and
   numbers cannot be checked.
4. **It lets real names and numbers through.** If its style rules would replace an identifier
   or a figure with a friendlier paraphrase, the coverage check will report the item. Either
   show the exact string, or record the wording used with `as:` in the ledger.

5. **It can list its places, if it has them.** A skill whose output has numbered frames, slides
   or pages should be able to print them as plain text: a line starting with `# ` for each
   chapter, and a line starting with its number for each place. Saved as
   `<run>/output/outline.txt`, that listing lets the coverage check confirm that every place the
   ledger names exists. Without it the check still runs, and says that places were not checked.

Nothing else is required. The skill does not need to know the dossier format in advance: the
brief in `produce.md` tells it where everything is.

## Adding one

1. Install the skill where skills are loaded from (for this kit: `./install.sh --adopt <folder>`
   copies it into `skills/` and links it).
2. Say in its description what it produces and which versions it offers.
3. That is all. The scope stage offers every installed output skill as a choice, and writes the
   chosen one into `output_skill:`.

## The one in use now

`visual-explainer`: explains a subject through animated, visual scenes rather than text. It
knows several presentation formats and picks the one that fits each explanation, and it offers
two versions of the same content: a video that plays everything through, and scroll-through
slides where the viewer operates the interactive parts themselves.
