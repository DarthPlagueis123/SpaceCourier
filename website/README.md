# Space Courier educational website

A React, TypeScript, and Vite field guide to the real Space Courier game and Double DQN experiment. Uses local project artifacts, not demonstration training data. The game and model are preserved.

## Run

Requires Node.js 22.12+ (Node 22 LTS recommended). Dependencies are locked in `package-lock.json`.

```sh
cd website
npm ci
npm run dev
```

Open the Local URL printed by Vite, normally `http://127.0.0.1:5173`.

```sh
npm run build
npm run preview
```

Production output is `dist/`. The production build performs strict TypeScript checking first. Pages and the full state inspector load on demand. Videos use `preload="none"` and native controls; no autoplay or sound is forced on visitors.

## Pages

- `/`: arcade cabinet hero, learning route, original game, measured overview.
- `/learn/:slug`: 15 beginner-friendly chapters, saved browser progress, sticky chapter navigation, exact Python excerpts, interactive illustrations.
- `/game`: direct entry to the game chapter.
- `/results`: six selectable interactive training metrics, real evaluation comparison, and validation checkpoint history.
- `/watch`: five actual recordings from untrained through last checkpoint.
- `/download`: game source, complete project, learned weights, CSV, metadata, and evaluation JSON.
- `/train`: Verified Windows / PowerShell reproduction commands.
- `/about`: evidence, real project tree, limitations, and primary-source references.

## Structure

```text
website/
  src/
    App.tsx, main.tsx, data.ts
    styles.css, syntax.css
    components/             Navigation, code, charts, state inspector, diagrams, setup, player
    content/lessons.ts       Tutorial narrative and section definitions
    pages/                  Home, tutorial, results, watch, download, train, about
    generated/              Derived real metadata, history, excerpts, and manifests
  public/
    media/                  Real screenshots, H.264 recordings, sprite, observed state trace
    downloads/              Actual ZIP, PTH, CSV, and JSON files
    _redirects              SPA fallback for Netlify
  scripts/
    prepare_assets.py       Derive data/excerpts/downloads from the parent Python project
    record_checkpoints.py   Record the saved policies; no training
    enrich_trace.py         Reproduce and verify the original trace with actual inputs/Q-values
    verify_assets.py        Provenance, source, checksum, ZIP, and media verification
  index.html
  vite.config.ts, tsconfig.json
  package.json, package-lock.json
  netlify.toml, vercel.json
```

## Data and media provenance

All results come from parent `data/training_history.csv`, `data/random_baseline.json`, `data/evaluation_results.json`, `data/validation_history.json`, and `models/model_metadata.json`. Source snippets are exact line slices extracted from the real Python files. The state inspector uses all 952 original decisions from seed 100002, reproduced exactly with the delivered model to record input tensors and Q-values.

Recordings use actual untrained, 50,000-, 100,000-, 150,000-, and 250,000-decision saved weights on the same seed. The selected policy at 150,000 decisions had 833 completed episodes at save; the last checkpoint had 1,059. No recordings are scripted or retrained. Recordings are silent H.264 MP4, 480 × 640 at 30 FPS with fast-start metadata.

The learning loop, action mapping, Bellman sliders, network dots, and small replay illustration are labeled teaching aids. Bellman slider values are illustrative; state vectors, Q-values, videos, and training/evaluation statistics are actual observations.

The game download is Python source, not an executable. Complete source includes the existing models, data, results, and website source. Recursive download archives, installed packages, and build output are excluded.

## Regenerate or verify

Run from `website/` in the existing project, with Python AI dependencies available:

```sh
npm run prepare:assets
npm run verify:assets
```

If working from the complete source archive, run `npm run prepare:assets` before building to recreate the downloadable ZIPs and their checksum manifest. The archive omits recursive download copies.

To regenerate media, install FFmpeg from its official distribution and make `ffmpeg` / `ffprobe` available on PATH:

```sh
python scripts/record_checkpoints.py
python scripts/enrich_trace.py
npm run prepare:assets
```

These commands do not train or change the original game. Existing bundled media and generated data let ordinary `npm ci`, `npm run dev`, and `npm run build` run without Python or FFmpeg.

## Deployment

For Netlify or Vercel, choose `pixel-panic/website` as the project/root directory, `npm run build` as the build command, and `dist` as output. SPA fallback configuration is included for deep links; existing static files take precedence. Keep the included `public/media` and `public/downloads` assets.

Before public deployment, set an absolute Open Graph image URL for the final domain and add a canonical URL once that domain exists. Avoid inventing a production URL in local source. The included social image and favicon are real local assets. Client-side routes update page titles, while shared description/Open Graph tags live in `index.html`; a future prerendering pass would improve per-chapter search/social previews.

No hosting account, domain, executable package, public repository, or browser-native game was created. Model inference is shown as actual recorded video in the browser and runs live in local Python.

## Accessibility and verification

Semantic headings, skip link, visible keyboard focus, native accessible video controls, alt text, reduced-motion preferences, keyboard-operable diagrams, chart inspection with arrow keys, responsive navigation, and local chapter progress are included. Storage failure does not prevent reading.

The native Windows environment and documented Windows extraction/venv/CLI commands were verified. Other operating-system setup paths have not been verified and are not presented as tested commands. Verification includes production build, provenance checks, all page routes, media/download availability, code copying, progress persistence, and desktop/mobile layouts.
