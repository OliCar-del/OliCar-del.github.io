# olicar-del.github.io

Source for [Oliver Carnew's engineering portfolio](https://olicar-del.github.io/), a Jekyll site that
GitHub Pages builds and publishes from the `main` branch. Commands below run from the repo folder in
PowerShell or the VS Code terminal.

## Preview changes before pushing

Ruby, the site's gems and ffmpeg are installed in WSL (Ubuntu).

```
wsl bash scripts/serve.sh
```

Open http://localhost:4000. Saving a file rebuilds the site and refreshes the browser after a few
seconds. Stop it with Ctrl+C.

To build once and run the same checks GitHub runs (broken links, missing images and videos, files
over 10 MB):

```
wsl bash scripts/check.sh
```

## Adding a project

1. Make a folder `_projects/NN_short-name/` (the number sets the order on the site) and copy
   `Reference/template.md` into it as `index.md`.
2. Put the project's images, videos and PDFs in the same folder and fill in the template.
3. Run `python scripts/optimize_images.py NN_short-name`. It shrinks oversized photos, converts heavy
   PNGs to WebP (updating `index.md` to match), makes the card thumbnail and adds the `thumb:` line.
   Originals are copied to `../media-originals/` first.
4. Preview, then commit and push. Add `published: false` to the front matter to keep a draft offline.

## Images, video and files

- **Images**: `{% include image-gallery.html images="a.webp, b.webp" height="400" caption="Figure 1: ..." %}`.
  The caption also becomes the alt text. Visitors can click any image to see it full size. If a
  caption contains a double quote, write it as `&quot;`.
- **Short clips**: never commit GIFs (one 14-second clip was 100 MB as a GIF and 1 MB as MP4).
  Convert screen recordings and GIFs with:

  ```
  wsl ffmpeg -i clip.gif -vf "fps=30,format=yuv420p" -c:v libx264 -preset slow -crf 25 -tune animation -movflags +faststart -an clip.mp4
  ```

  then `{% include video.html file="clip.mp4" height="500" caption="..." %}`. Clips play muted and
  looping while on screen.
- **YouTube**: `{% include youtube-video.html id="VIDEO_ID" title="What it shows" width="1200px" caption="..." %}`
  (the player only loads when clicked).
- **PDFs and other files**: put them in the project folder and link with `[Schematic (PDF)](file.pdf)`.

## Checks

The **Check site** workflow (`.github/workflows/check-site.yml`) runs on every push. It builds the site
with the same builder GitHub Pages uses and fails, with an email to you, if a page links to a missing
file or a file over 10 MB is added. Open the run in the repo's **Actions** tab to see what broke.
Publishing isn't blocked by it.

## Where things are

| What | Where |
| --- | --- |
| Name, headline, intro, skills, links, colours, CV path | `_config.yml` |
| Projects (one folder each) | `_projects/` |
| CV | `assets/resume/Oliver_Carnew_CV.pdf`: replace this file to update it (keep the name) |
| Page templates, styles, script | `_layouts/`, `_includes/`, `css/styles.css`, `assets/js/script.js` |
| Icons | `_data/icons.yml` |
| Favicons | `python scripts/optimize_images.py --favicons` (made from the profile photo) |

## Analytics

GoatCounter (https://portfold.goatcounter.com) shows visits, where they came from, and CV downloads
(`cv-download`). Add `?campaign=company-name` to the site link in an application to see whether that
application led to a visit.

---

Started from Lowinertia's free-to-engineer portfolio template (CC0).
