// ------------------------------------------------------------------------------- React

export type CursorBuildProps = {
  children: ReactNode;
  /** Build pace: 1 is the original; 2 and 3 are its fast settings. */
  speed?: number;
  /** How much of the section must be on screen before it starts (0 to 1). Tall sections start once half the viewport is filled. */
  threshold?: number;
  /** The intro: the cursors orbit this logo (an image URL). Default: the site's favicon. `false` shows the label's first letter. */
  logo?: string | false;
  /** Used for the letter mark when there's no logo. Default: the page title. */
  label?: string;
  /**
   * What plays before the build:
   *   "logo"    the cursors orbit the site's logo (the original)
   *   "prompt"  a prompt bar types `prompt`, Build is pressed, the cursors fan out of it
   *   "burst"   the cursors knot tight around a pulsing dot, then explodes outward with a shockwave
   *   "join"    presence pills stack up as each cursor arrives: "Ada joined", "Linus joined"…
   *   "marquee" a selection box grows over the section with a live W × H badge, the cursors circling it
   * Default: "prompt" when `prompt` is set, otherwise "logo".
   */
  intro?: "logo" | "prompt" | "burst" | "join" | "marquee";
  /**
   * How the section comes in under the cursors and is handed back:
   *   "fade"  the canvas fades in, and fades away over the real section (the original)
   *   "wipe"  the canvas wipes down over the section, then wipes away top to bottom
   *   "scan"  the same, led by a glowing scan line
   *   "iris"  a circle opens the canvas from the middle; a growing hole reveals the real section
   *   "grid"  the cursors build on a dotted design canvas whose dots fade before the hand-back
   */
  appear?: "fade" | "wipe" | "scan" | "iris" | "grid";
  /** The request typed by the "prompt" intro (setting it picks that intro). */
  prompt?: string;
  promptPlaceholder?: string;
  /** Figma-style name labels on the cursors. */
  labels?: boolean;
  /** Labels also say what each cursor is doing ("Ada · Heading · 48px", "Linus · ⌥ Duplicate"). Turns labels on. */
  chat?: boolean;
  /** Name the cursors as a team with jobs (Layout, Type, Image, Grid, Copy, QA…). Turns labels on. */
  agents?: boolean;
  /** Your own cursor names and colours (cycled). */
  names?: string[];
  colors?: string[];
  /**
   * How many cursors: the size of the crew in the intro, which also scales how many build at once
   * and the finale flock. 18 is the original (8 building at the least, up to 48 when the visitor
   * scrolls fast, 36 in the flock). 6 to 10 reads calm; 30+ reads as a crowd.
   */
  cursors?: number;
  /** The most cursors at once while building (default: cursors × 48 / 18). The crew grows toward it as the visitor scrolls faster and work piles up. */
  maxCursors?: number;
  /** Synthesized clicks, typing and notes (Web Audio). Browsers keep it silent until the visitor clicks. */
  sound?: boolean;
  /** How long the finished crew flocks (following the mouse over the section) before it leaves, in ms. -1 keeps it. */
  hold?: number;
  /** Minimum time the intro plays before building, in ms (default: 1500, longer for burst, join and marquee). */
  introMs?: number;
  /** Clip the cursors to the section (default). false lets them roam the whole viewport. */
  contain?: boolean;
  zIndex?: number;
  className?: string;
  style?: CSSProperties;
  /** Fires when the cursors have finished building. */
  onBuilt?: () => void;
  /** Fires when the real section has been handed back. */
  onDone?: () => void;
};

const AGENT_NAMES = ["Layout", "Type", "Image", "Grid", "Copy", "QA", "Motion", "Icons", "Color", "Spacing"];
const AGENT_COLORS = ["#A259FF", "#F24E1E", "#0ACF83", "#9747FF", "#E8467C", "#E5A800", "#1ABCFE", "#FF7262", "#14AE5C", "#0D99FF"];

export default function CursorBuild({
  children,
  speed = 1,
  threshold = 0.35,
  logo,
  label,
  intro,
  appear = "fade",
  prompt,
  promptPlaceholder,
  labels = false,
  chat = false,
  agents = false,
  names,
  colors,
  sound = false,
  cursors,
  maxCursors,
  hold = 1400,
  introMs,
  contain = true,
  zIndex = 60,
  className,
  style,
  onBuilt,
  onDone,
}: CursorBuildProps) {
  const outer = useRef<HTMLDivElement>(null);
  const scope = useRef<HTMLDivElement>(null);
  // hidden until the cursors hand it back; the overlay's blank canvas covers it meanwhile
  const [hidden, setHidden] = useState(true);
  const opts = useRef({
    speed,
    intro: intro ?? (prompt ? "prompt" : "logo"),
    appear,
    logo,
    label,
    prompt: prompt ?? "Build this section",
    promptPlaceholder,
    labels: labels || chat || agents,
    chat,
    names: names ?? (agents ? AGENT_NAMES : undefined),
    colors: colors ?? (agents ? AGENT_COLORS : undefined),
    sound,
    cursors,
    maxCursors,
    hold,
    // each intro gets the time it needs to read before the build starts
    introMs: introMs ?? ({ burst: 1900, join: 2500, marquee: 2200 } as Record<string, number>)[intro ?? ""] ?? 1500,
    contain,
    zIndex,
  });
  const cb = useRef({ onBuilt, onDone });
  useEffect(() => {
    cb.current = { onBuilt, onDone };
  }, [onBuilt, onDone]);

  useEffect(() => {
    const el = outer.current;
    const sc = scope.current;
    if (!el || !sc) return;
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      setHidden(false);
      return;
    }
    let app: { run: () => Promise<void>; destroy: () => void } | null = null;
    const io = new IntersectionObserver(
      ([e]) => {
        if (app || !e.isIntersecting) return;
        const enough =
          e.intersectionRatio >= threshold || e.intersectionRect.height >= window.innerHeight * 0.5;
        if (!enough) return;
        io.disconnect();
        app = new cursorBuild.App(sc, opts.current, {
          built: () => cb.current.onBuilt?.(),
          reveal: () => setHidden(false),
          done: () => cb.current.onDone?.(),
        });
        app.run().catch((err: unknown) => {
          console.error("[cursor-build]", err);
          app?.destroy();
          setHidden(false);
        });
      },
      { threshold: Array.from({ length: 21 }, (_, i) => i / 20) },
    );
    io.observe(el);
    return () => {
      io.disconnect();
      app?.destroy();
      app = null;
    };
  }, [threshold]);

  return (
    // the outer box is what the scroll trigger watches (a clipped box never counts as on screen)
    <div ref={outer} className={className} style={style}>
      {/* clip-path hides it without touching layout or computed styles, so the engine can still read it */}
      <div style={{ clipPath: hidden ? "polygon(0 0, 0 0, 0 0)" : undefined }}>
        <div ref={scope}>{children}</div>
      </div>
    </div>
  );
}
