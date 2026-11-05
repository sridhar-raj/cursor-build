  // -------------------------------------------------------------------- app (one element)

  class App {
    constructor(scope, opts, hooks) {
      this.scope = scope;
      this.opts = opts;
      this.hooks = hooks || {};
      this.dead = false;
      this.releasing = false;
      this.t0 = performance.now();
    }

    async run() {
      const o = this.opts;
      this.env = scopeEnv(this.scope, o);
      this.view = new View(this.env);
      this.engine = new Engine(this.view);
      this.engine.speed = o.speed || 1;
      if (o.sound) {
        this.sfx = new Sound();
        this.sfx.init();
        this.engine.sfx = this.sfx;
      }
      this.engine.onStart = () => this.view.intro.classList.add("gone");
      this.engine.onComplete = () => this.onComplete();
      this.bind();
      // Snapshot first, while the section is still hidden: reading a big section blocks for a moment,
      // and doing it before anything moves keeps the appear effect and the intro smooth.
      try {
        await Promise.race([document.fonts.ready, sleep(1200)]);
      } catch (_) {}
      if (this.dead) return;
      this.view.measure();
      let model;
      try {
        model = captureModel(this.env, null);
      } catch (err) {
        console.error("[cursor-build] capture failed", err);
        model = { items: [], tasks: [], groups: [], guides: [], docW: 0, docH: 0 };
      }
      if (this.dead) return;
      this.view.mount(model);
      this.engine.setModel(model);
      this.model = model;
      // now the show: the canvas comes in over the section, the intro plays, the cursors gather
      this.last = performance.now();
      this.raf = requestAnimationFrame((t) => this.frame(t));
      await nextFrame();
      if (this.sfx) this.sfx.intro();
      this.view.bg.classList.add("on");
      this.view.intro.classList.add("on");
      this.view.fx = { phase: "in", t0: performance.now() };
      if (this.view.grid) this.view.grid.classList.add("on");
      this.t0 = performance.now();
      this.playIntro();
      if (o.intro === "prompt") await this.typePrompt();
      const wait = (o.introMs ?? 1500) - (performance.now() - this.t0);
      if (wait > 0) await sleep(wait);
      if (this.dead) return;
      this.engine.hold = false;
      this.engine.start();
    }

    // intros that animate on their own while the cursors circle
    async playIntro() {
      const kind = this.opts.intro;
      const intro = this.view.intro;
      if (kind === "join") {
        // presence pills, one per cursor as it arrives: "Ada joined"
        const list = intro.querySelector(".join");
        const crew = this.engine.cursors.slice(0, 6);
        await sleep(260);
        for (const c of crew) {
          if (this.dead || this.engine.started) return;
          const pill = document.createElement("span");
          pill.innerHTML = `<i style="background:${c.color}">${c.name[0]}</i><b></b> joined`;
          pill.querySelector("b").textContent = c.name;
          list.appendChild(pill);
          if (this.sfx) this.sfx.press(innerWidth / 2, innerWidth);
          await sleep(170);
        }
      } else if (kind === "marquee") {
        // a selection box drawn over the section, with its size counting up
        const box = intro.querySelector(".mq");
        const badge = intro.querySelector(".mq .badge");
        await sleep(200);
        const f = this.engine.focus();
        box.style.width = Math.round(f.w * 0.82) + "px";
        box.style.height = Math.round(f.h * 0.7) + "px";
        const t0 = performance.now();
        while (!this.dead && performance.now() - t0 < 1100) {
          badge.textContent = `${box.offsetWidth} × ${box.offsetHeight}`;
          await nextFrame();
        }
      }
    }

    // the prompt bar types the request, then Build is pressed and the cursors fan out
    async typePrompt() {
      const em = this.view.intro.querySelector(".pr em");
      const btn = this.view.intro.querySelector(".pr b");
      const text = this.opts.prompt;
      const sp = this.opts.speed || 1;
      await sleep(300);
      em.classList.remove("ph");
      const caret = document.createElement("i");
      for (let i = 1; i <= text.length && !this.dead; i++) {
        em.textContent = text.slice(0, i);
        em.appendChild(caret);
        await sleep(rand(22, 58) / sp);
      }
      await sleep(280);
      caret.remove();
      btn.classList.add("on");
      if (this.sfx) this.sfx.press(innerWidth / 2, innerWidth);
      await sleep(170);
      btn.classList.remove("on");
    }

    bind() {
      const on = (t, ev, fn, o) => {
        t.addEventListener(ev, fn, o);
        (this.unbinds || (this.unbinds = [])).push(() => t.removeEventListener(ev, fn, o));
      };
      on(window, "resize", () => this.view.measure());
      on(window, "pointermove", (e) => {
        this.engine.mouse = { x: e.clientX, y: e.clientY };
      }, { passive: true });
      on(document.documentElement, "pointerleave", () => {
        this.engine.mouse = null;
      });
      // browsers only let audio start after a click/keypress on the page
      if (this.sfx)
        on(window, "pointerdown", () => {
          if (this.sfx.blocked) this.sfx.resume();
        }, true);
    }

    frame(now) {
      if (this.dead) return;
      const fx = this.view && this.view.fx;
      if (fx && fx.phase === "in" && now - fx.t0 > 720) fx.phase = "hold";
      const dt = Math.min(0.05, (now - this.last) / 1000);
      this.last = now;
      try {
        this.engine.step(dt);
        this.view.render(this.engine);
      } catch (err) {
        console.error("[cursor-build]", err);
      }
      this.raf = requestAnimationFrame((t) => this.frame(t));
    }

    onComplete() {
      if (this.sfx) this.sfx.finale();
      if (this.hooks.built) this.hooks.built();
      const hold = this.opts.hold ?? 1400;
      if (hold >= 0) this.holdT = setTimeout(() => this.release(), hold);
    }

    // the cursors leave, the real section is put back under the canvas, and the canvas fades away
    release() {
      if (this.dead || this.releasing) return;
      this.releasing = true;
      const E = this.engine;
      E.releasing = true;
      E.flocking = true;
      for (const c of E.cursors) {
        c.gen = null;
        c.follow = false;
      }
      if (this.sfx) {
        this.sfx.release();
        this.sfx.close(1.4);
      }
      if (this.view.grid) this.view.grid.classList.remove("on");
      // fade / grid: the canvas fades away; wipe / scan / iris: it's masked away over the real section
      const masked = ["wipe", "scan", "iris"].includes(this.opts.appear);
      this.t1 = setTimeout(() => {
        if (this.hooks.reveal) this.hooks.reveal();
        if (masked) this.view.fx = { phase: "out", t0: performance.now() };
        else this.view.host.style.setProperty("opacity", "0", "important");
      }, this.view.grid ? 650 : 450);
      this.t2 = setTimeout(() => {
        this.destroy();
        if (this.hooks.done) this.hooks.done();
      }, masked ? 1450 : this.view.grid ? 1350 : 1150);
    }

    destroy() {
      if (this.dead) return;
      this.dead = true;
      clearTimeout(this.holdT);
      clearTimeout(this.t1);
      clearTimeout(this.t2);
      cancelAnimationFrame(this.raf);
      for (const u of this.unbinds || []) u();
      if (this.view) this.view.host.remove();
      if (this.sfx && !this.releasing) this.sfx.close(0.1);
    }
  }
