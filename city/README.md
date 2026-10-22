# city/ — the walkable map of SemiAgency

`python scripts/build_city.py` writes `index.html` at the repo root (GitHub Pages serves it as the site's home page): one self-contained page (no network, no corporate data) that shows everything in this repo as the painted island city, always fully in view, with a small hero who walks its streets like in an old top-down game. One **area per flow**, one **building per step**, four **piers** for the M365 scenarios. Standing at a building (or clicking it, or picking it in the panel) opens what it is, how to use it with copy buttons, and the full prompt or build sheet behind it. The panel's **Scenarios** ("I want to…") list, when one is picked, the steps one line each with a *required* / *optional* flag, a copy chip for every command or M365 prompt, and the stops numbered on the map; **Next step** walks the hero there. The **Prompt library** tab lists every prompt and agent with Copy, Download and a one-click zip of all of them.

Controls: WASD or arrows to walk the streets (Shift runs), click a street to walk there (the hero finds the way around buildings and water), click a building or its name to visit it, `E` to enter, `H` hides the panel, `?` shows this list. Works on a phone (the panel becomes a bottom sheet; tap to walk).

Where the hero may walk is read off the painting at load time: turquoise pixels are water, the traced building polygons are solid, the piers are stone. No mask file to maintain; a new painting only needs its buildings traced again.

## Files

- `city.json` — the manifest. Districts, one entry per building (`name`, `district`, `pitch`, `steps` with copy blocks, the `prompts` / `agents` / `docs` it contains, `audience`, `hotspot` for its place on the island), the `journeys` (label, a plain-language "when", ordered stops with one line each), `landmarks` (the piers: a place that opens a route), the `redact` map and the `never_embed` list. Optional per building: `sub` (subtitle), `mode` (`auto`, `click`, `paste`, `prompt`, `run`, `setup`, `read`), `shape` (how the building looks: `hall columns studio factory dome warehouse house tower office lighthouse clock embassy observatory workshop small construction`), `asks` (rows of *say / when / you get*, tagged with the `journeys` they belong to), `picker: true` (the “Help: what do I run?” cards). Top level: `area_label_at` pins each area's name.
- `template.html` — the page: CSS, the canvas world (painting, walkable mask, A* path-finding, the pixel hero, routes), the panel and the library. `build_city.py` fills in `__DATA__`, `__TITLE__`, `__TAGLINE__`, `__BUILT__`, `__VERSION__`. Edit this to change how the city looks or behaves. No libraries.
- `scene.jpg` — the painting (prompt at the bottom). Embedded in the page.
- `hotspots.json` — one polygon per building, per pier and per free lot, traced on the painting with `hotspot-editor.html` (open in any browser, load `scene.jpg`, trace, export). The `hotspot` field in `city.json` is the only link between a building and a polygon. Optional per journey stop: `"optional": true` marks a step the scenario list shows as optional (a `say` starting with "Optional" or "Only if" counts too).

## Adding a prompt

```
python scripts/new_prompt.py
```

It asks for the command name, a description, the area, the building's name, subtitle and pitch, a shape, and which route the stop belongs to (or a new route). It then writes `.github/prompts/<name>.prompt.md` with a skeleton body, adds the building and the stop to `city.json`, and rebuilds the map and `docs/menu.md`. You write the prompt's instructions, try `/<name>` in Copilot Chat, commit. All the questions have `--flags` for scripting; `--selftest` as everywhere.

Why one script for three things: a prompt file alone is found by `build_city.py` and shown in **Not placed yet**, but the `/start` guide can only send people to a stop on a route, so `build_menu.py --check` fails until the prompt is on one. `/new-flow` (Add a new flow) does the same for a whole flow, with an interview.

A building added this way has no `hotspot`, so it takes the first free lot (the build prints which; the free lots are the empty plazas and spare houses in the painting). To pin it elsewhere: give it another free lot's id, or trace a new polygon in `hotspot-editor.html`. When the free lots run out, generate a new painting with more plazas — the hotspots are the only thing to re-trace.

## Privacy

The page embeds only what `city.json` names, after applying `redact` (replace names, sites, time zones). `never_embed` paths are refused even if named. The build fails if a redacted string survives into the output. Keep `engagements/`, `brand/` and `tracker/` in `never_embed`; they are the corporate data. The library's download buttons give out exactly the embedded (redacted) files.

## Image prompt (one area per flow)

The current `scene.jpg` came from this prompt. Keep the same wording if you regenerate, so the areas and hotspot ids stay valid; then re-trace the buildings.

> A detailed illustrated bird's-eye view (three-quarter aerial perspective, slightly isometric) of a fantasy island city that is ancient Athens reimagined with subtle futuristic additions. Bright clean daylight, clear pale sky, calm turquoise Aegean sea all around. Painterly storybook illustration, soft warm colours (marble white, terracotta, olive green, turquoise, gold accents), crisp edges, high detail, no text or lettering anywhere.
>
> The island is divided into eight clearly separate areas, connected by paved stone roads that all start from one central plaza. Each area has its own colour, carried by its roof tiles, awnings, banners and the tint of its paving stones, so the boundaries between areas are easy to see from above:
> (1) Central agora (gold) in the exact centre: a large open marble plaza with golden paving inlays, a stately town hall with a small tower and a golden roof, and a small round information kiosk with a glass dome; six wide roads leave the plaza.
> (2) Acropolis quarter (deep terracotta red), the largest area, on a high hill in the upper centre: seven distinct buildings along one winding road that climbs the hill — a small scribe's house, a columned archive temple, a design studio with tall windows, a print workshop with chimneys, a round domed theatre, a warehouse, and a grand Parthenon-like temple at the summit; red roof tiles and red banners.
> (3) Blue street (Aegean blue), a shorter straight street on the lower right of the agora: four smaller buildings in a row — a small archive, a small studio, a small print workshop and a small open-air theatre — clearly smaller cousins of the acropolis buildings, with blue Santorini-style domes and blue awnings.
> (4) Violet corner (lavender violet), just below the agora: one elegant stone notary house with violet awnings and a small walled garden.
> (5) Gate of envoys (teal) at the bottom centre, where a stone bridge reaches the island from a small islet: a monumental columned gateway and an embassy house with teal flags; a road runs from the gate straight up to the acropolis.
> (6) Observatory hill (silver and pale lavender), a small hilltop on the upper left: an observatory with a silver dome and a telescope among cypress trees, with one empty platform beside it.
> (7) Harbour (sea green) along the whole right coast: six buildings with sea-green roofs — a tall antenna tower with a glowing orb, a harbour office, a striped lighthouse on the point, a columned library, a post-office house, and a clock tower — and four clearly separate stone piers jutting into the sea, each with moored sailboats whose sails have one colour per pier: sunflower yellow, coral orange, turquoise, white.
> (8) Construction yard (sandstone and orange) at the bottom left near a second small bridge: a craftsman's workshop, a cartographer's studio with a large map table visible under an awning, a half-built building with sleek white construction cranes, and stacked marble blocks.
>
> Futuristic touches kept subtle: a sleek white monorail curving between the agora, the acropolis and the harbour on slender arches, glass domes on a few marble buildings, gently glowing lanterns along the roads, a waterfall cascading from the acropolis cliff into the sea. Leave 8–10 empty marble plazas or foundation platforms with low walls, clearly unbuilt, spread over the areas.
>
> Composition rules: every building fully visible and separated by roads, gardens or water — no building hidden behind another; about 26 distinct buildings; the roads from the central agora to every area clearly visible; wide landscape format 16:9; the whole island fits in frame with sea on all sides; no people in the foreground, no vehicles except the monorail and boats, no frames, borders or text.

Avoid (negative prompt): text, letters, watermark, signature, blurry, dark, night, neon, cyberpunk, overlapping buildings, buildings hidden behind others, cropped edges, people close-up, photo-realistic, fog, heavy shadows.

## Publishing on GitHub Pages

**Simplest:** Settings → Pages → *Deploy from a branch* → `main`, folder `/ (root)`. GitHub serves `index.html` as the home page. It also serves every other file in the repo (prompts, sheets, `tracker/`, `brand/`). That's fine for a public repo, which is readable anyway.

**Only the map (optional):** publish `index.html` alone with a GitHub Action.

1. Settings → Pages → Source: **GitHub Actions**.
2. Save the workflow below as `.github/workflows/pages.yml` and push.
3. It runs on every push to `main` that changes `index.html`, and on demand from the Actions tab (*Run workflow*). The site is `https://<user>.github.io/<repo>/`.

It publishes the committed `index.html` as it is: rebuild with `python scripts/build_city.py` and commit before pushing.

```yaml
name: Publish map

on:
  push:
    branches: [main]
    paths: [index.html]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: true

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - uses: actions/checkout@v4
      - name: Keep only the map
        run: |
          mkdir _site
          cp index.html _site/
          touch _site/.nojekyll
      - uses: actions/configure-pages@v5
      - uses: actions/upload-pages-artifact@v3
        with:
          path: _site
      - id: deployment
        uses: actions/deploy-pages@v4
```
