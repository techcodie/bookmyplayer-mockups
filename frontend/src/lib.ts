import type { Stage } from "./api";

// Per-stage display metadata tuned for the dark theme.
// `grad` powers funnel/velocity bars, `glow` is the column accent + card glow,
// `chip` is the small stage pill, `dot` is the solid timeline marker.
export const STAGES: Record<
  Stage,
  { label: string; grad: string; glow: string; chip: string; dot: string }
> = {
  wishlist: {
    label: "Wishlist",
    grad: "from-slate-400 to-slate-500",
    glow: "rgba(148,163,184,.45)",
    chip: "bg-slate-400/15 text-slate-300 ring-slate-400/20",
    dot: "bg-slate-400",
  },
  applied: {
    label: "Applied",
    grad: "from-sky-400 to-cyan-400",
    glow: "rgba(56,189,248,.55)",
    chip: "bg-sky-400/15 text-sky-300 ring-sky-400/20",
    dot: "bg-sky-400",
  },
  oa: {
    label: "OA",
    grad: "from-violet-400 to-fuchsia-400",
    glow: "rgba(167,139,250,.55)",
    chip: "bg-violet-400/15 text-violet-300 ring-violet-400/20",
    dot: "bg-violet-400",
  },
  interview: {
    label: "Interview",
    grad: "from-amber-300 to-orange-400",
    glow: "rgba(251,191,36,.55)",
    chip: "bg-amber-400/15 text-amber-300 ring-amber-400/20",
    dot: "bg-amber-400",
  },
  offer: {
    label: "Offer",
    grad: "from-emerald-300 to-teal-400",
    glow: "rgba(52,211,153,.6)",
    chip: "bg-emerald-400/15 text-emerald-300 ring-emerald-400/20",
    dot: "bg-emerald-400",
  },
  rejected: {
    label: "Rejected",
    grad: "from-rose-400 to-pink-500",
    glow: "rgba(251,113,133,.5)",
    chip: "bg-rose-400/15 text-rose-300 ring-rose-400/20",
    dot: "bg-rose-400",
  },
  ghosted: {
    label: "Ghosted",
    grad: "from-zinc-400 to-zinc-500",
    glow: "rgba(161,161,170,.4)",
    chip: "bg-zinc-400/15 text-zinc-400 ring-zinc-400/20",
    dot: "bg-zinc-400",
  },
};

// Mirror of the backend ALLOWED_TRANSITIONS table.
export const ALLOWED: Record<Stage, Stage[]> = {
  wishlist: ["applied", "rejected", "ghosted"],
  applied: ["oa", "interview", "rejected", "ghosted"],
  oa: ["interview", "rejected", "ghosted"],
  interview: ["offer", "rejected", "ghosted"],
  offer: [],
  rejected: [],
  ghosted: [],
};

// Columns shown on the board, in pipeline order.
export const BOARD_STAGES: Stage[] = [
  "wishlist",
  "applied",
  "oa",
  "interview",
  "offer",
];

export function deadlineBadge(deadline: string | null): {
  text: string;
  cls: string;
} | null {
  if (!deadline) return null;
  const d = Math.ceil((new Date(deadline).getTime() - Date.now()) / 86400000);
  if (d < 0) return { text: `${-d}d overdue`, cls: "bg-rose-500/20 text-rose-300 ring-rose-400/30" };
  if (d === 0) return { text: "due today", cls: "bg-rose-500/20 text-rose-300 ring-rose-400/30" };
  if (d <= 3) return { text: `${d}d left`, cls: "bg-amber-500/20 text-amber-300 ring-amber-400/30" };
  if (d <= 7) return { text: `${d}d left`, cls: "bg-yellow-500/15 text-yellow-300 ring-yellow-400/20" };
  return { text: `${d}d left`, cls: "bg-white/5 text-slate-400 ring-white/10" };
}

export const pct = (v: number | null) =>
  v == null ? "—" : `${Math.round(v * 100)}%`;

export const days = (v: number | null) =>
  v == null ? "—" : `${v.toFixed(1)}d`;

export const initials = (company: string) =>
  company
    .split(/\s+/)
    .slice(0, 2)
    .map((w) => w[0]?.toUpperCase() ?? "")
    .join("");
