import { useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { LayoutGrid, Target, BarChart3, Plus, LogOut } from "lucide-react";
import { token } from "./api";
import Aurora from "./components/Aurora";
import Login from "./components/Login";
import Board from "./components/Board";
import FocusToday from "./components/FocusToday";
import Analytics from "./components/Analytics";
import AddApplicationModal from "./components/AddApplicationModal";

type Tab = "board" | "focus" | "analytics";

const TABS: { key: Tab; label: string; icon: typeof LayoutGrid }[] = [
  { key: "board", label: "Pipeline", icon: LayoutGrid },
  { key: "focus", label: "Focus today", icon: Target },
  { key: "analytics", label: "Analytics", icon: BarChart3 },
];

export default function App() {
  const [authed, setAuthed] = useState(!!token.get());
  const [tab, setTab] = useState<Tab>("board");
  const [adding, setAdding] = useState(false);
  const [version, setVersion] = useState(0);
  const reload = () => setVersion((v) => v + 1);

  if (!authed)
    return (
      <>
        <Aurora />
        <Login onAuthed={() => setAuthed(true)} />
      </>
    );

  return (
    <div className="min-h-full">
      <Aurora />

      <header className="sticky top-0 z-20 border-b border-white/5 bg-[#06060c]/60 backdrop-blur-xl">
        <div className="mx-auto flex max-w-6xl items-center gap-4 px-5 py-3">
          <div className="flex items-center gap-2.5">
            <div
              className="flex h-9 w-9 items-center justify-center rounded-xl font-display text-sm font-bold text-white"
              style={{
                backgroundImage:
                  "linear-gradient(135deg,#7c6cff,#b06cff,#5ad1ff)",
                boxShadow: "0 8px 24px -8px rgba(124,108,255,.8)",
              }}
            >
              OF
            </div>
            <span className="font-display text-lg font-semibold tracking-tight">
              Offer<span className="gradient-text">Funnel</span>
            </span>
          </div>

          <nav className="ml-4 flex items-center gap-1 rounded-2xl border border-white/5 bg-white/[0.03] p-1">
            {TABS.map((t) => {
              const Icon = t.icon;
              const active = tab === t.key;
              return (
                <button
                  key={t.key}
                  onClick={() => setTab(t.key)}
                  className={`relative flex items-center gap-2 rounded-xl px-3.5 py-1.5 text-sm font-medium transition ${
                    active ? "text-white" : "text-slate-400 hover:text-slate-200"
                  }`}
                >
                  {active && (
                    <motion.span
                      layoutId="navpill"
                      className="absolute inset-0 -z-10 rounded-xl bg-white/10 ring-1 ring-white/10"
                      transition={{ type: "spring", stiffness: 400, damping: 32 }}
                    />
                  )}
                  <Icon size={15} />
                  {t.label}
                </button>
              );
            })}
          </nav>

          <div className="ml-auto flex items-center gap-2">
            <button className="btn-primary" onClick={() => setAdding(true)}>
              <Plus size={16} /> Add application
            </button>
            <button
              className="btn-ghost"
              onClick={() => {
                token.clear();
                setAuthed(false);
              }}
            >
              <LogOut size={15} />
            </button>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-5 py-7">
        <AnimatePresence mode="wait">
          <motion.div
            key={tab}
            initial={{ opacity: 0, y: 12, filter: "blur(6px)" }}
            animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
            exit={{ opacity: 0, y: -8, filter: "blur(6px)" }}
            transition={{ duration: 0.35, ease: [0.16, 1, 0.3, 1] }}
          >
            {tab === "board" && <Board version={version} reload={reload} />}
            {tab === "focus" && <FocusToday version={version} reload={reload} />}
            {tab === "analytics" && <Analytics version={version} />}
          </motion.div>
        </AnimatePresence>
      </main>

      <AnimatePresence>
        {adding && (
          <AddApplicationModal
            onClose={() => setAdding(false)}
            onCreated={() => {
              setAdding(false);
              reload();
            }}
          />
        )}
      </AnimatePresence>
    </div>
  );
}
