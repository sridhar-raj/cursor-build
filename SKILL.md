---
name: cursor-build
description: Make website sections build themselves as they scroll into view, with a crew of live multiplayer cursors (Figma style) that rebuilds each section in front of the visitor. Crosshair-drawn boxes with W × H badges, typed text, pen-tool lines, rulers and red guides, ⌥-drag duplicates, images swept on, then the real section is handed back. It has 5 intros (logo, prompt, burst, join, marquee), 5 appears (fade, wipe, scan, iris, grid), cursor count, name and chat labels, and agent teams. One paste-in React file (CursorBuild) built on the original swarm-cursors engine. Use whenever someone wants a section, hero, pricing table, bento grid or whole landing page to "build itself", a scroll-in or appear animation with cursors, an "AI is building your site" or multiplayer moment, or a launch or X post where a UI assembles on screen, even if they never say "swarm" or "cursors".
---

# Cursor Build

`CursorBuild` wraps a section of a React site. When the section scrolls into view, a blank canvas covers it and an intro plays. Then a crew of multiplayer cursors rebuilds the section live:
- crosshair-drawn boxes with a W × H badge, typed text with an I-beam and caret
- pen-tool lines, Figma rulers and red guides that text snaps to
- repeated cards ⌥-dragged off the first, images swept on top to bottom

Last, the cursors flock and leave, and the real, clickable section is handed back. The page never re-renders, so links, forms and hover states work as before.

Cursor engine: [swarm-cursors](https://github.com/DhvanilPatel/swarm-cursors) by Dhvanil Patel, adapted from [Swarm](https://califa.github.io/swarm-site/) by Joel Califa.

## Files

- `assets/CursorBuild.tsx`: the component. One file, needs only React (18+). **Generated, don't hand-edit**; see "Changing it".
- `assets/demo-cursor-build.tsx`: an example page with five full-viewport sections, each with its own intro and appear. It imports the OriginKit X studio's sections; swap them for the site's own.
- `scripts/`: the generator (`build-cursor-build.py`), the original `swarm.js`, and the parts added on top: `app.js` (start on view, intros, appears, hand-back), `wrapper.tsx` (the React component and its props) and `header.txt`.

## Add it to a site

1. Copy `assets/CursorBuild.tsx` into the project's components folder.
2. Wrap each section that should build in. Give each section a full viewport and `threshold={0.7}`, so it starts only once it fills the screen. Give each section its own pair (`logo`+`fade`, `prompt`+`wipe`, `burst`+`iris`, `join`+`scan`, `marquee`+`grid`), and don't wrap every section: two or three per page reads as a feature, ten reads as a gimmick.

```tsx
import CursorBuild from "@/components/CursorBuild";

<CursorBuild intro="burst" appear="iris" cursors={14} threshold={0.7}>
  <section style={{ minHeight: "100dvh" }}>…</section>
</CursorBuild>

<CursorBuild intro="prompt" prompt="Pricing section, three plans, Pro highlighted" appear="wipe" chat threshold={0.7}>
  <Pricing />
</CursorBuild>
```

3. Run it and scroll each wrapped section into view. Check it against "Check it" below, then tune `cursors`, `speed` and the pairs.

The section is hidden with a clip-path until the cursors hand it back. The layout never shifts, and nothing flashes before it scrolls in. With reduced motion it just shows.

## Props

| Prop | Default | What it does |
|---|---|---|
| `speed` | 1 | The engine's own pace; 2 and 3 are its fast settings |
| `threshold` | 0.35 | Share of the section on screen before it starts; tall sections start once they fill half the viewport |
| `intro` | `"logo"` | **5 intros.** `"logo"` the cursors orbit the site's logo (the original) · `"prompt"` a prompt bar types `prompt`, Build is pressed, the cursors fan out of it · `"burst"` the cursors knot around a pulsing dot, then explodes outward with a shockwave · `"join"` presence pills stack up as each cursor arrives ("Ada joined") · `"marquee"` a selection box grows over the section with a live W × H badge |
| `appear` | `"fade"` | **5 appears**, how the canvas comes in over the section and hands it back. `"fade"` fades in and out (the original) · `"wipe"` wipes down over it, then away top to bottom · `"scan"` the same, led by a glowing scan line · `"iris"` a circle opens it; a growing hole reveals the real section · `"grid"` builds on a dotted design canvas whose dots fade before the hand-back |
| `logo` | site favicon | The image for the `"logo"` intro. `false` uses the first letter of `label` |
| `label` | page title | Text for the letter mark |
| `prompt` | — | The request the `"prompt"` intro types (setting it picks that intro) |
| `labels` | false | **Added.** Figma-style name pills on the cursors (the original has none) |
| `chat` | false | **Added.** The pills say what each cursor is doing ("Ada · Heading · 48px", "Linus · ⌥ Duplicate", "Grace · Pen tool") |
| `agents` | false | **Added.** Names the cursors as a team: Layout, Type, Image, Grid, Copy, QA… |
| `names`, `colors` | the original's | **Added.** Your own cursor names and colours, cycled |
| `cursors` | 18 | **How many cursors.** The size of the build in the intro; how many build at once and the finale flock scale with it (the original's 18 means 8 building at the least, up to 48 when the visitor scrolls fast, 36 in the flock). 6–10 reads calm, 30+ reads as a crowd |
| `maxCursors` | cursors × 48 ⁄ 18 | The most cursors at once while building. The crew grows toward it as the visitor scrolls faster and work piles up |
| `sound` | false | The engine's synthesized sound: keyboard clicks, glass-piano notes, a finale chord. Browsers keep it silent until the visitor clicks |
| `hold` | 1400 | ms the finished crew flocks over the section, following the mouse, before it leaves; `-1` keeps it there |
| `introMs` | 1500 (burst 1900, marquee 2200, join 2500) | Minimum time the intro plays before the build |
| `contain` | true | Clip the cursors to the section; `false` lets the cursors roam the whole viewport, as in the extension |
| `onBuilt`, `onDone` | — | Built, and handed back |

## Pitfalls

- **Split-letter text** (Rolling Letters, per-character animations) keeps hidden copies of each letter; the snapshot draws them, so the headline shows doubled letters while building ("QuQQQ"). Don't wrap sections that use them, or turn the effect off inside the wrapper.
- **Children that start invisible** (opacity 0 entrance animations) are skipped by the snapshot and pop in at hand-back. Let them finish first, or turn them off inside the wrapper.
- **Canvas and WebGL** are copied as a still frame, or a grey placeholder when the canvas can't be read; the live element returns at hand-back.
- **Fonts:** the snapshot copies computed styles, so web fonts must be loaded. It waits up to 1.2 s for `document.fonts.ready`.
- **Background:** the blank canvas takes the colour of the section (or a wrapper filling it), else the page behind it. A section with a transparent background over an image looks wrong while building.
- **Several sections on screen at once** each build at the same time in their own box. Raise `threshold` if they should wait their turn.
- **Next.js:** it's a client component (`"use client"` is in the file). Import it from a client page, or wrap it in one.

## Check it

Scroll each wrapped section in at the size it ships:
- The intro reads before the build starts, and the build starts once the section fills the screen.
- No part of the real section shows before its cursor reaches it.
- The hand-back is clean: when the canvas has gone, the section looks exactly as it does without the wrapper, with no doubled text and nothing missing.
- There are no console errors. Every overlay is removed once its section has been handed back: `document.querySelectorAll("cursor-build").length` is 0.

## Changing it

`CursorBuild.tsx` is generated. The engine part of `swarm.js` is copied verbatim, then a list of named patches scopes it to one element and adds the options. Never edit the generated file; edit the parts, then rebuild:

```bash
cd scripts
python3 build-cursor-build.py ../assets/CursorBuild.tsx
```

- **New prop:** add it to `wrapper.tsx` (type, default, the `opts` object). Read it in `app.js`, or in the engine through a patch in the build script.
- **New intro or appear:** markup in the `makeIntro` patch, motion in `playIntro` (`app.js`), the mask or opacity in the `applyFx` patch, styles in the style patch.
- **Styles on the overlay host** need `!important`: the engine gives it `all: initial !important`.
- **Updating from a newer swarm-cursors:** download its `swarm.js` (command in the script's header) and rebuild. Each patch must match exactly once, and the script stops and names any patch that no longer does.

What the patches change in the engine, so it works on one element instead of a whole page:
- The wrapped element is the "page": its box is the world, and the viewport's offset from it is the scroll. Tasks still unlock top-down as it scrolls into view.
- The blank canvas covers only the element, in its own colour.
- The overlay lets clicks through, is clipped to the element, and several instances run at once.
- The intro and the finale flock centre on the element; the rulers sit on its corner.
- No HUD, no keyboard shortcuts, no page scan or auto-scroll.
