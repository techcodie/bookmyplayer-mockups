import { useEffect, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Star, AlertTriangle } from "lucide-react";
import { api, type Application, type Stage } from "../api";
import { ALLOWED, BOARD_STAGES, STAGES, deadlineBadge, initials } from "../lib";
import AppDetail from "./AppDetail";

export default function Board({
  version,
  reload,
}: {
  version: number;
  reload: () => void;
}) {
  const [apps, setApps] = useState<Application[] | null>(null);
  const [dragId, setDragId] = useState<number | null>(null);
  const [hover, setHover] = useState<Stage | null>(null);
  const [openId, setOpenId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.listApplications().then(setApps).catch((e) => setError(e.message));
  }, [version]);

  async function drop(stage: Stage) {
    setHover(null);
    const app = apps?.find((a) => a.id === dragId);
    setDragId(null);
    if (!app || app.current_stage === stage) return;
    if (!ALLOWED[app.current_stage].includes(stage)) {
      setError(`Can't move ${app.company} from ${STAGES[app.current_stage].label} → ${STAGES[stage].label}`);
      setTimeout(() => setError(null), 2600);
      return;
    }
    try {
      await api.transition(app.id, stage);
      reload();
    } catch (e: any) {
      setError(e.message);
    }
  }

  if (!apps)
    return <p className="text-sm text-slate-500">Loading pipeline…</p>;

  if (apps.length === 0)
    return (
      <div className="glass mx-auto max-w-md p-10 text-center">
        <h2 className="font-display text-lg font-semibold">No applications yet</h2>
        <p className="mt-1 text-sm text-slate-400">
          Add your first application and watch the funnel come alive.
        </p>
      </div>
    );

  return (
    <>
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -12 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -12 }}
            className="mb-4 flex items-center gap-2 rounded-xl border border-rose-400/30 bg-rose-500/15 px-3 py-2 text-sm text-rose-200"
          >
            <AlertTriangle size={15} /> {error}
          </motion.div>
        )}
      </AnimatePresence>

      <p className="mb-4 text-sm text-slate-400">
        Drag a card to a new stage — only legal pipeline moves are accepted.
      </p>

      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-5">
        {BOARD_STAGES.map((stage, ci) => {
          const inStage = apps.filter((a) => a.current_stage === stage);
          const meta = STAGES[stage];
          const isHover = hover === stage;
          return (
            <motion.div
              key={stage}
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: ci * 0.05, duration: 0.4 }}
              onDragOver={(e) => {
                e.preventDefault();
                setHover(stage);
              }}
              onDragLeave={() => setHover((h) => (h === stage ? null : h))}
              onDrop={() => drop(stage)}
              className="glass flex min-h-[62vh] flex-col p-2.5 transition-all duration-300"
              style={
                isHover
                  ? { boxShadow: `0 0 0 1px ${meta.glow}, 0 20px 60px -20px ${meta.glow}` }
                  : undefined
              }
            >
              <div className="mb-3 flex items-center gap-2 px-1.5 pt-1">
                <span
                  className={`h-2 w-2 rounded-full bg-gradient-to-br ${meta.grad}`}
                  style={{ boxShadow: `0 0 10px ${meta.glow}` }}
                />
                <span className="text-sm font-semibold text-slate-200">{meta.label}</span>
                <span className="ml-auto rounded-full bg-white/5 px-2 py-0.5 text-xs font-medium text-slate-400 ring-1 ring-white/10">
                  {inStage.length}
                </span>
              </div>

              <div className="flex flex-col gap-2.5">
                <AnimatePresence>
                  {inStage.map((a) => {
                    const badge = deadlineBadge(a.deadline);
                    return (
                      <motion.div
                        layout
                        key={a.id}
                        initial={{ opacity: 0, scale: 0.92 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0, scale: 0.9 }}
                        whileHover={{ y: -3 }}
                        whileDrag={{ scale: 1.04, rotate: -1.5 }}
                        draggable
                        onDragStart={() => setDragId(a.id)}
                        onClick={() => setOpenId(a.id)}
                        className="group cursor-grab rounded-xl border border-white/10 bg-white/[0.04] p-3 transition active:cursor-grabbing hover:border-white/20"
                      >
                        <div className="flex items-start gap-2.5">
                          <div
                            className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-gradient-to-br ${meta.grad} text-xs font-bold text-black/80`}
                            style={{ boxShadow: `0 4px 14px -4px ${meta.glow}` }}
                          >
                            {initials(a.company)}
                          </div>
                          <div className="min-w-0">
                            <div className="truncate text-sm font-semibold text-slate-100">
                              {a.company}
                            </div>
                            <div className="truncate text-xs text-slate-400">{a.role}</div>
                          </div>
                        </div>
                        <div className="mt-2.5 flex flex-wrap items-center gap-1">
                          <span className="flex items-center gap-0.5">
                            {Array.from({ length: 5 }).map((_, i) => (
                              <Star
                                key={i}
                                size={11}
                                className={
                                  i < a.interest_level
                                    ? "fill-amber-400 text-amber-400"
                                    : "text-slate-600"
                                }
                              />
                            ))}
                          </span>
                          {badge && (
                            <span className={`rounded-full px-1.5 py-0.5 text-[10px] font-medium ring-1 ${badge.cls}`}>
                              {badge.text}
                            </span>
                          )}
                          {a.tags.map((t) => (
                            <span
                              key={t}
                              className="rounded-full bg-white/5 px-1.5 py-0.5 text-[10px] text-slate-400 ring-1 ring-white/10"
                            >
                              #{t}
                            </span>
                          ))}
                        </div>
                      </motion.div>
                    );
                  })}
                </AnimatePresence>
              </div>
            </motion.div>
          );
        })}
      </div>

      <AnimatePresence>
        {openId != null && (
          <AppDetail id={openId} onClose={() => setOpenId(null)} onChanged={reload} />
        )}
      </AnimatePresence>
    </>
  );
}
