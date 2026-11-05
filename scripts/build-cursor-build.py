"""Assemble CursorBuild.tsx: the swarm-cursors engine (verbatim, plus the listed patches) scoped to one
element, a component-sized App (app.js), and the React wrapper (wrapper.tsx, header.txt).

Usage, from this folder:
  curl -sL https://raw.githubusercontent.com/DhvanilPatel/swarm-cursors/main/swarm-rebuild/swarm.js -o swarm.js
  python3 build-cursor-build.py ../assets/CursorBuild.tsx
Every patch must match exactly once; if the upstream file changed, the script stops and names the patch.
The engine slice is lines 20-3459 of swarm.js (constants through the Sound class); re-check it on update."""
import pathlib, sys

HERE = pathlib.Path(__file__).parent
src = (HERE / "swarm.js").read_text().split("\n")
core = "\n".join(src[19:3459])  # constants .. end of Sound (lines 20-3459)
patches = 0


def rep(old, new, count=1):
    global core, patches
    n = core.count(old)
    if n != count:
        sys.exit(f"patch expected {count} match(es), found {n}: {old[:90]!r}")
    core = core.replace(old, new)
    patches += 1


def rep_fn(start, end_marker, new):
    """Replace from `start` up to and including the first `end_marker` after it."""
    global core, patches
    a = core.index(start)
    b = core.index(end_marker, a) + len(end_marker)
    core = core[:a] + new + core[b:]
    patches += 1


# 1. environment: the wrapped element is the "page"; its distance from the viewport top is the scroll
rep_fn(
    "  function detectEnv() {",
    "    return env;\n  }\n",
    """  function scopeEnv(scope, opts) {
    const box = () => scope.getBoundingClientRect();
    const scroller = scrollParent(scope);
    const env = {
      scope,
      opts,
      scroller,
      isRoot: true,
      host: null,
      pageBg: scopeBackground(scope),
      // world = the element's own box; the "scroll" is how far the viewport has moved past its top-left
      geom() {
        const r = box();
        return { ox: 0, oy: 0, sx: -r.left, sy: -r.top, vw: document.documentElement.clientWidth, vh: window.innerHeight };
      },
      scrollHeight: () => Math.ceil(box().height),
      scrollWidth: () => Math.ceil(box().width),
      scrollTo(y, x) {
        const r = box();
        if (scroller === window) window.scrollTo({ top: window.scrollY + r.top + y, behavior: "instant" });
        else scroller.scrollTo({ top: scroller.scrollTop + r.top - scroller.getBoundingClientRect().top + y, behavior: "instant" });
      },
      scrollBy(dy) {
        (scroller === window ? window : scroller).scrollBy({ top: dy, behavior: "instant" });
      },
    };
    return env;
  }

  function scrollParent(el) {
    for (let p = el.parentElement; p && p !== document.body && p !== document.documentElement; p = p.parentElement) {
      const oy = getComputedStyle(p).overflowY;
      if (/(auto|scroll|overlay)/.test(oy) && p.scrollHeight > p.clientHeight + 4) return p;
    }
    return window;
  }
""",
)

# 2. the blank canvas takes the colour behind the element, not the page's
rep_fn(
    "  function pageBackground() {",
    "    return { color: dark ? \"rgb(18, 18, 18)\" : \"rgb(255, 255, 255)\", image: \"none\", from: null };\n  }\n",
    """  function scopeBackground(scope) {
    const pick = (cs, from) => ({
      color: cs.backgroundColor,
      image: cs.backgroundImage,
      size: cs.backgroundSize,
      position: cs.backgroundPosition,
      repeat: cs.backgroundRepeat,
      from,
    });
    // first the element and the wrappers inside it that fill it (sections usually paint their own
    // background a level or two down), then the elements behind it
    const box = scope.getBoundingClientRect();
    for (let el = scope, depth = 0; el && depth < 6; depth++) {
      const cs = getComputedStyle(el);
      if (alphaOf(cs.backgroundColor) > 0.5) return pick(cs, el);
      const fill = [...el.children].find((c) => {
        const r = c.getBoundingClientRect();
        return r.width >= box.width * 0.95 && r.height >= box.height * 0.95;
      });
      el = fill || null;
    }
    for (let el = scope.parentElement; el; el = el.parentElement) {
      const cs = getComputedStyle(el);
      if (alphaOf(cs.backgroundColor) > 0.5) return pick(cs, el);
    }
    const dark = matchMedia("(prefers-color-scheme: dark)").matches && /dark/.test(getComputedStyle(document.documentElement).colorScheme);
    return { color: dark ? "rgb(18, 18, 18)" : "rgb(255, 255, 255)", image: "none", from: null };
  }
""",
)

# 3. capture: the world is the element's box, and the walk starts at the element
rep(
    "    const docW = Math.max(env.scrollWidth(), vw);\n    const docH = Math.min(Math.max(env.scrollHeight(), vh), MAX_WORLD_H);",
    "    const docW = env.scrollWidth();\n    const docH = Math.min(env.scrollHeight(), MAX_WORLD_H);",
)
rep(
    "    walk(html, { op: 1, layer: rootLayer, clip: rootClip, zTop: null, posd: false, boxItem: null }, null);",
    "    walk(env.scope, { op: 1, layer: rootLayer, clip: rootClip, zTop: null, posd: false, boxItem: null }, null);",
)

# 4. view: one overlay per instance, clicks pass through, the blank canvas lives in the world
rep('      for (const old of document.querySelectorAll("swarm-rebuild")) old.remove();\n', "")
rep(
    "pointer-events:auto !important;contain:strict !important;opacity:1;transition:opacity .6s ease;\";",
    "pointer-events:none !important;contain:strict !important;opacity:1;transition:opacity .6s ease;\";\n"
    "      host.style.setProperty(\"z-index\", String(env.opts.zIndex ?? 60), \"important\");",
)
rep(
    "      this.makeIntroLogo();\n",
    "      this.world.appendChild(this.bg);\n"
    "      if (env.opts.appear === \"grid\") {\n"
    "        this.grid = document.createElement(\"div\");\n"
    "        this.grid.className = \"gridfx\";\n"
    "        this.world.appendChild(this.grid);\n"
    "      }\n"
    "      this.world.style.width = env.scrollWidth() + \"px\";\n"
    "      this.world.style.height = env.scrollHeight() + \"px\";\n"
    "      this.makeIntro();\n",
)
rep_fn(
    "    makeIntroLogo() {",
    "      this.intro.appendChild(img);\n    }\n",
    """    makeIntro() {
      const o = this.env.opts;
      const kind = o.intro;
      this.intro.dataset.kind = kind;
      if (kind === "prompt") {
        this.intro.innerHTML = '<div class="pr"><em class="ph"></em><b>Build</b></div>';
        this.intro.querySelector("em").textContent = o.promptPlaceholder || "Describe a section…";
        return;
      }
      if (kind === "burst") {
        this.intro.innerHTML = '<div class="dot"><i></i><i></i></div>';
        return;
      }
      if (kind === "join") {
        this.intro.innerHTML = '<div class="join"></div>';
        return;
      }
      if (kind === "marquee") {
        this.intro.innerHTML = '<div class="mq"><i></i><i></i><i></i><i></i><span class="badge"></span></div>';
        return;
      }
      const label = (o.label || document.title || location.hostname || "?").replace(/^www\\./, "").trim();
      const mono = () => {
        this.intro.innerHTML = "";
        const d = document.createElement("div");
        d.className = "mono";
        d.textContent = (label[0] || "?").toUpperCase();
        this.intro.appendChild(d);
      };
      if (o.logo === false) return mono();
      let href = typeof o.logo === "string" ? o.logo : null;
      if (!href) {
        const links = [...document.querySelectorAll('link[rel~="icon"], link[rel="apple-touch-icon"], link[rel="shortcut icon"]')];
        const sized = links
          .map((l) => ({ href: l.href, s: parseInt((l.getAttribute("sizes") || "0").split("x")[0], 10) || (l.rel.includes("apple") ? 180 : 32) }))
          .filter((l) => l.href)
          .sort((a, b) => b.s - a.s);
        href = sized.length ? sized[0].href : location.origin + "/favicon.ico";
      }
      const img = document.createElement("img");
      img.onerror = mono;
      img.src = href;
      this.intro.appendChild(img);
    }
""",
)

# 5. view: each frame, clip the overlay to the element, centre the intro on it, anchor the rulers to it
rep(
    "    render(E) {\n      this.syncWorld();",
    """    place(E) {
      const vp = E.vp;
      const L = -vp.sx;
      const T = -vp.sy;
      const R = L + this.env.scrollWidth();
      const B = T + this.env.scrollHeight();
      this.rL = clamp(L, 0, this.W);
      this.rT = clamp(T, 0, this.H);
      if (this.env.opts.contain !== false) {
        const clip = `inset(${f1(Math.max(0, T))}px ${f1(Math.max(0, this.W - R))}px ${f1(Math.max(0, this.H - B))}px ${f1(Math.max(0, L))}px)`;
        if (clip !== this._clip) {
          this._clip = clip;
          this.host.style.setProperty("clip-path", clip, "important");
        }
      }
      const f = E.focus();
      this.intro.style.left = f1(f.x - vp.sx) + "px";
      this.intro.style.top = f1(f.y - vp.sy) + "px";
      this.applyFx(L, T, R - L, B - T, f, vp);
    }

    // How the canvas comes in over the section and goes away to hand it back (opts.appear).
    // (The host carries all:initial !important, so every property set on it needs !important too.)
    // "fade" and "grid" use opacity; "wipe", "scan" and "iris" mask the overlay.
    applyFx(L, T, W, H, f, vp) {
      const fx = this.fx;
      const mode = this.env.opts.appear;
      if (!fx || mode === "fade" || mode === "grid") return;
      const now = performance.now();
      const dur = fx.phase === "out" ? 900 : 700;
      let p = clamp((now - fx.t0) / dur, 0, 1);
      p = p < 0.5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2;
      let line = null;
      const st = this.host.style;
      const setMask = (m) => {
        st.setProperty("-webkit-mask-image", m, "important");
        st.setProperty("mask-image", m, "important");
      };
      if (mode === "wipe" || mode === "scan") {
        // the canvas covers the band [a, b] of the section, top to bottom
        const a = fx.phase === "out" ? p : 0;
        const b = fx.phase === "in" ? p : 1;
        const e = 0.6;
        setMask(`linear-gradient(to bottom, transparent ${f1(a * 100 - e)}%, #000 ${f1(a * 100)}%, #000 ${f1(b * 100)}%, transparent ${f1(b * 100 + e)}%)`);
        for (const k of ["-webkit-mask-size", "mask-size"]) st.setProperty(k, `${f1(W)}px ${f1(H)}px`, "important");
        for (const k of ["-webkit-mask-position", "mask-position"]) st.setProperty(k, `${f1(L)}px ${f1(T)}px`, "important");
        for (const k of ["-webkit-mask-repeat", "mask-repeat"]) st.setProperty(k, "no-repeat", "important");
        if (mode === "scan" && fx.phase !== "hold" && p < 1) line = T + (fx.phase === "out" ? a : b) * H;
      } else if (mode === "iris") {
        const cx = f.x - vp.sx;
        const cy = f.y - vp.sy;
        const R = Math.hypot(Math.max(cx - L, L + W - cx), Math.max(cy - T, T + H - cy)) + 4;
        const r = R * p;
        setMask(
          fx.phase === "out"
            ? `radial-gradient(circle at ${f1(cx)}px ${f1(cy)}px, transparent ${f1(r)}px, #000 ${f1(r + 1.5)}px)`
            : fx.phase === "in"
              ? `radial-gradient(circle at ${f1(cx)}px ${f1(cy)}px, #000 ${f1(r)}px, transparent ${f1(r + 1.5)}px)`
              : "none",
        );
      }
      if (!this.scanEl) {
        this.scanEl = document.createElement("div");
        this.scanEl.className = "scan";
        this.root.appendChild(this.scanEl);
      }
      if (line == null) this.scanEl.style.display = "none";
      else this.scanEl.style.cssText = `display:block;left:${f1(L)}px;top:${f1(line - 1)}px;width:${f1(W)}px`;
    }

    render(E) {
      this.syncWorld();
      this.place(E);""",
)
rep(
    '`<div class="ruler ruler-top" style="transform:translateY(${f1((t - 1) * 100)}%)"><svg width="${W}" height="${RULER}">${u}</svg></div>` +',
    '`<div class="ruler ruler-top" style="top:${f1(this.rT)}px;left:${f1(this.rL)}px;transform:translateY(${f1((t - 1) * 100)}%)"><svg width="${W}" height="${RULER}"><g transform="translate(${f1(-this.rL)} 0)">${u}</g></svg></div>` +',
)
rep(
    '`<div class="ruler ruler-left" style="transform:translateX(${f1((t - 1) * 100)}%)"><svg width="${RULER}" height="${H}">${a}</svg></div>` +',
    '`<div class="ruler ruler-left" style="top:${f1(this.rT)}px;left:${f1(this.rL)}px;transform:translateX(${f1((t - 1) * 100)}%)"><svg width="${RULER}" height="${H}"><g transform="translate(0 ${f1(-this.rT)})">${a}</g></svg></div>` +',
)
rep(
    '`<div class="ruler-corner" style="opacity:${f1(t)}"></div>`;',
    '`<div class="ruler-corner" style="top:${f1(this.rT)}px;left:${f1(this.rL)}px;opacity:${f1(t)}"></div>`;',
)
rep('<line x1="${RULER}" x2="${x}" y1=', '<line x1="${f1(this.rL + RULER)}" x2="${x}" y1=')
rep('y1="${RULER}" y2="${y}"/></g>', 'y1="${f1(this.rT + RULER)}" y2="${y}"/></g>')

# 6. cursors: optional Figma-style name labels, and with chat, what each one is doing
rep(
    "        svg.style.transform = `translate(${-el._hx}px,${-el._hy}px) rotate(${f1(c.angle)}deg) scale(${s})`;\n",
    """        svg.style.transform = `translate(${-el._hx}px,${-el._hy}px) rotate(${f1(c.angle)}deg) scale(${s})`;
        if (E.labels) {
          let nm = el._nm;
          if (!nm) {
            nm = document.createElement("span");
            nm.className = "nm";
            nm.style.background = c.color;
            el.appendChild(nm);
            el._nm = nm;
          }
          const msg = E.chat && c.task ? taskMsg(c.task.spec) : "";
          const txt = msg ? `${c.name} · ${msg}` : c.name;
          if (nm._t !== txt) {
            nm.textContent = txt;
            nm._t = txt;
          }
        }
""",
)

# 7. engine: names/colours/labels from the options; the intro waits for the prompt when there is one
rep(
    "      const vp = this.vp;\n      for (let n = 0; n < INTRO_AGENTS; n++) {",
    """      const o = view.env.opts || {};
      this.names = o.names && o.names.length ? o.names : NAMES;
      this.colors = o.colors && o.colors.length ? o.colors : COLORS;
      this.labels = !!(o.labels || o.chat);
      this.chat = !!o.chat;
      this.hold = o.intro === "prompt";
      this.introScale = { prompt: 1.7, burst: 0.22, join: 1.15, marquee: 2.1 }[o.intro] || 0.7;
      const vp = this.vp;
      for (let n = 0; n < INTRO_AGENTS; n++) {""",
)
rep(
    "        name: NAMES[id % NAMES.length],\n        color: COLORS[id % COLORS.length],",
    "        name: this.names[id % this.names.length],\n        color: this.colors[id % this.colors.length],",
)
rep("      if (this.started || !this.ready) return;", "      if (this.started || !this.ready || this.hold) return;")
rep(
    "        const center = this.fromViewport(vp.ox + vp.vw / 2, vp.oy + vp.vh / 2);\n        if (this.follow(dt, this.cursors, center, 0.7) && this.ready) this.start();",
    "        const center = this.focus();\n        if (this.follow(dt, this.cursors, center, this.introScale) && this.ready) this.start();",
)
# the swarm orbits / flocks on the element (the visible part of it), and follows the mouse only over it
rep_fn(
    "    flockTarget() {",
    "    }\n",
    """    // the middle of the part of the element that's on screen (world coords)
    focus() {
      const vp = this.vp;
      const W = this.view.env.scrollWidth();
      const H = this.view.env.scrollHeight();
      const l = clamp(vp.sx, 0, W);
      const r = clamp(vp.sx + vp.vw, 0, W);
      const t = clamp(vp.sy, 0, H);
      const b = clamp(vp.sy + vp.vh, 0, H);
      return { x: (l + r) / 2, y: (t + b) / 2, w: Math.max(0, r - l), h: Math.max(0, b - t) };
    }

    flockTarget() {
      const f = this.focus();
      if (this.mouse) {
        const m = this.fromViewport(this.mouse.x, this.mouse.y);
        if (Math.abs(m.x - f.x) <= f.w / 2 && Math.abs(m.y - f.y) <= f.h / 2) return m;
      }
      const t = this.time;
      return { x: f.x + f.w * 0.28 * Math.sin(t * 0.37), y: f.y + f.h * 0.25 * Math.sin(t * 0.53 + 1) };
    }
""",
)

# 8. styles: no HUD; the name labels and the prompt bar
rep(
    "@keyframes hudpulse{50%{box-shadow:0 0 0 4px rgba(13,153,255,.28)}}\n`;",
    """@keyframes hudpulse{50%{box-shadow:0 0 0 4px rgba(13,153,255,.28)}}
.hud{display:none!important}
.cursor .nm{position:absolute;left:14px;top:17px;padding:2px 7px;border-radius:4px 10px 10px 10px;color:#fff;font:600 11px/15px Inter,system-ui,-apple-system,"Segoe UI",sans-serif;white-space:nowrap;box-shadow:0 1px 2px rgba(0,0,0,.2)}
.intro .pr{display:flex;align-items:center;gap:10px;width:min(440px,80vw);height:46px;padding:0 6px 0 16px;border-radius:14px;background:rgba(24,24,27,.94);color:#fafafa;box-shadow:0 14px 36px rgba(0,0,0,.28),inset 0 0 0 1px rgba(255,255,255,.08);font:500 14px/1 Inter,system-ui,-apple-system,"Segoe UI",sans-serif;white-space:nowrap}
.intro .pr em{flex:1;overflow:hidden;font-style:normal}
.intro .pr em.ph{color:#8b8b93}
.intro .pr em i{display:inline-block;width:1.5px;height:1.05em;margin-left:1px;vertical-align:text-bottom;background:currentColor}
.intro .pr b{display:flex;align-items:center;height:34px;padding:0 14px;border-radius:10px;background:#0D99FF;color:#fff;font-weight:600;transition:transform .12s ease,filter .12s ease}
.intro .pr b.on{transform:scale(.94);filter:brightness(1.12)}
.intro .dot{position:relative;width:18px;height:18px;border-radius:50%;background:#0D99FF;box-shadow:0 0 0 6px rgba(13,153,255,.18),0 0 24px rgba(13,153,255,.55);transition:transform .6s cubic-bezier(.2,.8,.2,1),opacity .6s ease}
.intro .dot i{position:absolute;inset:-2px;border-radius:50%;border:1.5px solid rgba(13,153,255,.7);animation:ring 1.4s cubic-bezier(.2,.7,.2,1) infinite}
.intro .dot i+i{animation-delay:.7s}
@keyframes ring{from{transform:scale(1);opacity:.9}to{transform:scale(5.5);opacity:0}}
.intro[data-kind="burst"].gone{transform:translate(-50%,-50%);opacity:0;transition:opacity .5s ease .15s}
.intro[data-kind="burst"].gone .dot{transform:scale(14);opacity:0}
.intro .join{display:flex;flex-direction:column;align-items:flex-start;gap:6px;min-width:190px}
.intro .join span{display:flex;align-items:center;gap:8px;padding:5px 12px 5px 5px;border-radius:999px;background:rgba(24,24,27,.92);color:#d4d4d8;font:500 12px/1 Inter,system-ui,-apple-system,"Segoe UI",sans-serif;box-shadow:0 6px 18px rgba(0,0,0,.18);animation:pill .45s cubic-bezier(.2,.8,.2,1) both;white-space:nowrap}
.intro .join span i{width:18px;height:18px;border-radius:50%;color:#fff;font:700 10px/18px Inter,system-ui,sans-serif;font-style:normal;text-align:center}
.intro .join span b{font-weight:600;color:#fff}
@keyframes pill{from{opacity:0;transform:translateY(8px) scale(.92)}}
.intro .mq{position:relative;width:0;height:0;border:1.5px solid #0D99FF;background:rgba(13,153,255,.06);transition:width .9s cubic-bezier(.2,.8,.2,1),height .9s cubic-bezier(.2,.8,.2,1)}
.intro .mq i{position:absolute;width:8px;height:8px;background:#fff;border:1.5px solid #0D99FF}
.intro .mq i:nth-child(1){left:-5px;top:-5px}.intro .mq i:nth-child(2){right:-5px;top:-5px}.intro .mq i:nth-child(3){left:-5px;bottom:-5px}.intro .mq i:nth-child(4){right:-5px;bottom:-5px}
.intro .mq .badge{left:50%;top:calc(100% + 8px);background:#0D99FF}
.gridfx{position:absolute;inset:0;background-image:radial-gradient(rgba(120,120,128,.45) 1px,transparent 1.3px);background-size:18px 18px;opacity:0;transition:opacity .6s ease}
.gridfx.on{opacity:1}
.scan{position:absolute;height:2px;background:#0D99FF;box-shadow:0 0 12px 2px rgba(13,153,255,.7),0 0 40px 6px rgba(13,153,255,.25);pointer-events:none}
`;""",
)

# chat: what a cursor is doing, from its task
core = core.replace(
    "  // ------------------------------------------------------------------ capture",
    """  // what a cursor is doing (chat labels)
  function taskMsg(s) {
    const it = s.it;
    switch (s.type) {
      case "rect":
        return it ? `Frame ${Math.round(it.w)}×${Math.round(it.h)}` : "Frame";
      case "image":
        return "Placing image";
      case "line":
        return "Pen tool";
      case "text":
        return it && it.fs >= 26 ? `Heading · ${Math.round(it.fs)}px` : it ? `Text · ${Math.round(it.fs)}px` : "Typing";
      case "guide":
        return "Guide";
      case "dup":
        return "⌥ Duplicate";
      case "edit":
        return "Editing copy";
      case "restyle":
      case "swap":
        return "Restyling";
    }
    return "";
  }

  // ------------------------------------------------------------------ capture""",
    1,
)

# 9. how many cursors: per instance instead of the engine's fixed 18 / 8 / 48 / 36
rep(
    "      this.introScale = { prompt: 1.7, burst: 0.22, join: 1.15, marquee: 2.1 }[o.intro] || 0.7;",
    """      this.introScale = { prompt: 1.7, burst: 0.22, join: 1.15, marquee: 2.1 }[o.intro] || 0.7;
      // `cursors` sizes the whole crew (18 by default, the original); the others keep its proportions
      const n = Math.max(1, Math.round(o.cursors ?? INTRO_AGENTS));
      this.nIntro = n;
      this.nMin = Math.max(1, Math.round((n * MIN_AGENTS) / INTRO_AGENTS));
      this.nMax = Math.max(this.nMin, Math.round(o.maxCursors ?? (n * MAX_AGENTS) / INTRO_AGENTS));
      this.nFlock = Math.min(this.nMax, Math.max(1, Math.round((n * FLOCK_AGENTS) / INTRO_AGENTS)));""",
)
rep("      for (let n = 0; n < INTRO_AGENTS; n++) {", "      for (let n = 0; n < this.nIntro; n++) {")
rep("        const c = this.makeCursor(p.x, p.y, n < MIN_AGENTS);", "        const c = this.makeCursor(p.x, p.y, n < this.nMin);")
rep(
    "      const want = clamp(MIN_AGENTS + Math.floor(this.vel / 40) + Math.floor(avail.length / 2), MIN_AGENTS, MAX_AGENTS);",
    "      const want = clamp(this.nMin + Math.floor(this.vel / 40) + Math.floor(avail.length / 2), this.nMin, this.nMax);",
)
rep(
    "this.cursors.filter((m) => !m.leaving).length > MIN_AGENTS && !c.home",
    "this.cursors.filter((m) => !m.leaving).length > this.nMin && !c.home",
)
rep(
    "      if (this.cursors.length < FLOCK_AGENTS && this.spawnCooldown <= 0 && !this.releasing) {",
    "      if (this.cursors.length < this.nFlock && this.spawnCooldown <= 0 && !this.releasing) {",
)

# 10. the overlay element carries the component's name
rep('"param", "swarm-rebuild",', '"param", "cursor-build",')
rep('const host = document.createElement("swarm-rebuild");', 'const host = document.createElement("cursor-build");')

print("patches applied:", patches + 1)
app = (HERE / "app.js").read_text()
wrapper = (HERE / "wrapper.tsx").read_text()
header = (HERE / "header.txt").read_text()
out = header + "\nconst cursorBuild = (() => {\n  \"use strict\";\n\n" + core + "\n\n" + app + "\n  return { App };\n})();\n\n" + wrapper
target = pathlib.Path(sys.argv[1])
target.write_text(out)
print("wrote", target, len(out.splitlines()), "lines")
