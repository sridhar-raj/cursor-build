"use client";

// Example page for CursorBuild (from the OriginKit X studio; swap the section imports for your own): sections, each one full viewport, each building
// in with its own intro and its own appear as you scroll to it.
import type { ComponentType } from "react";

import CursorBuild, { type CursorBuildProps } from "./CursorBuild";
import LedgerBento from "@/sections/19-ledger-bento/Section";
import NightreelPricing from "@/sections/23-nightreel-pricing/Section";
import RelaywaveHero from "@/sections/04-relaywave-hero/Section";
import StudioBento from "@/sections/12-studio-bento/Section";
import SundialFooter from "@/sections/15-sundial-footer/Section";

type Demo = {
  n: number;
  intro: NonNullable<CursorBuildProps["intro"]>;
  appear: NonNullable<CursorBuildProps["appear"]>;
  bg: string;
  Section: ComponentType;
  props: Partial<CursorBuildProps>;
};

const DEMOS: Demo[] = [
  { n: 1, intro: "logo", appear: "fade", bg: "#eeeef0", Section: RelaywaveHero, props: { cursors: 6 } },
  { n: 2, intro: "prompt", appear: "wipe", bg: "#08080A", Section: NightreelPricing, props: { prompt: "Pricing section, dark, three plans, Studio highlighted", chat: true } },
  { n: 3, intro: "burst", appear: "iris", bg: "#F7EFE7", Section: LedgerBento, props: { cursors: 40 } },
  { n: 4, intro: "join", appear: "scan", bg: "#F6F3F1", Section: SundialFooter, props: { labels: true } },
  { n: 5, intro: "marquee", appear: "grid", bg: "#EBEBEC", Section: StudioBento, props: { agents: true, chat: true } },
];

export default function CursorBuildLab() {
  return (
    <main style={{ background: "#0B0B0C" }}>
      <header style={{ height: "100dvh", display: "grid", placeContent: "center", textAlign: "center", gap: 14, color: "#fff", fontFamily: "ui-sans-serif, system-ui" }}>
        <h1 style={{ margin: 0, fontSize: 56, letterSpacing: "-0.04em" }}>CursorBuild</h1>
        <p style={{ margin: 0, color: "#a1a1aa" }}>5 sections, each with its own intro and appear. Each builds in when you scroll to it.</p>
        <p style={{ margin: 0, color: "#71717a", fontSize: 13 }}>Scroll ↓</p>
      </header>
      {DEMOS.map((d) => (
        <div key={d.n} style={{ position: "relative" }}>
          <span
            style={{
              position: "absolute",
              zIndex: 100,
              left: 16,
              top: 16,
              display: "flex",
              alignItems: "center",
              gap: 6,
              padding: 5,
              borderRadius: 999,
              background: "rgba(10,10,12,.9)",
              font: "600 12px/1 ui-monospace, SFMono-Regular, Menlo, monospace",
              boxShadow: "0 6px 20px rgba(0,0,0,.25)",
              pointerEvents: "none",
            }}
          >
            <b style={{ padding: "5px 9px", color: "#a1a1aa" }}>{String(d.n).padStart(2, "0")}</b>
            <b style={{ padding: "5px 10px", borderRadius: 999, background: "#A259FF", color: "#fff" }}>intro: {d.intro}</b>
            <b style={{ padding: "5px 10px", borderRadius: 999, background: "#0D99FF", color: "#fff" }}>appear: {d.appear}</b>
          </span>
          <CursorBuild threshold={0.7} intro={d.intro} appear={d.appear} {...d.props}>
            <div style={{ height: "100dvh", background: d.bg, overflow: "hidden" }}>
              <d.Section />
            </div>
          </CursorBuild>
        </div>
      ))}
      <footer style={{ height: "30vh" }} />
    </main>
  );
}
