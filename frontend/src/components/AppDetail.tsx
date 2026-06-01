import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { X, MapPin, ArrowRight, Plus } from "lucide-react";
import { api, type ApplicationDetail, type Stage } from "../api";
import { ALLOWED, STAGES } from "../lib";

const fmt = (d: string) =>
  new Date(d).toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
  });

export default function AppDetail({
  id,
  onClose,
  onChanged,
}: {
  id: number;
  onClose: () => void;
  onChanged: () => void;
}) {
  const [app, setApp] = useState<ApplicationDetail | null>(null);
  const [tag, setTag] = useState("");
  const [err, setErr] = useState<string | null>(null);

  const load = () => api.getApplication(id).then(setApp);
  useEffect(() => {
    load();
  }, [id]);

  async function move(to: Stage) {
    setErr(null);
    try {
      await api.transition(id, to);
      await load();
      onChanged();
    } catch (e: any) {
      setErr(e.message);
    }
  }

  async function addTag(e: React.FormEvent) {
    e.preventDefault();
    if (!tag.trim()) return;
    await api.addTag(id, tag.trim());
    setTag("");
    await load();
    onChanged();
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-30 flex items-start justify-center overflow-y-auto bg-black/60 p-4 backdrop-blur-sm sm:p-10"
      onClick={onClose}
    >
      <motion.div
        initial={{ opacity: 0, scale: 0.95, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.96, y: 12 }}
        transition={{ type: "spring", stiffness: 320, damping: 28 }}
        className="glass w-full max-w-2xl p-6"
        onClick={(e) => e.stopPropagation()}
      >
        {!app ? (
          <p className="text-sm text-slate-500">Loading…</p>
        ) : (
          <>
            <div className="flex items-start justify-between">
              <div>
                <h2 className="font-display text-2xl font-semibold text-slate-100">
                  {app.company}
                </h2>
                <p className="text-slate-400">{app.role}</p>
              </div>
              <button className="btn-ghost !px-2.5" onClick={onClose}>
                <X size={16} />
              </button>
            </div>

            <div className="mt-4 flex flex-wrap items-center gap-2 text-sm text-slate-400">
              <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ring-1 ${STAGES[app.current_stage].chip}`}>
                {STAGES[app.current_stage].label}
              </span>
              {app.location && (
                <span className="flex items-center gap-1">
                  <MapPin size={13} /> {app.location}
                </span>
              )}
              {app.source && <span>via {app.source}</span>}
              {(app.salary_min || app.salary_max) && (
                <span className="text-emerald-300">
                  ${app.salary_min ?? "?"}k–${app.salary_max ?? "?"}k
                </span>
              )}
            </div>

            <div className="mt-3 flex flex-wrap items-center gap-1.5">
              {app.tags.map((t) => (
                <span key={t} className="rounded-full bg-white/5 px-2 py-0.5 text-xs text-slate-300 ring-1 ring-white/10">
                  #{t}
                </span>
              ))}
              <form onSubmit={addTag} className="inline-flex items-center">
                <Plus size={12} className="mr-0.5 text-slate-500" />
                <input
                  value={tag}
                  onChange={(e) => setTag(e.target.value)}
                  placeholder="tag"
                  className="w-16 rounded-full border border-dashed border-white/15 bg-transparent px-2 py-0.5 text-xs text-slate-200 outline-none focus:border-brand-400/60"
                />
              </form>
            </div>

            <div className="mt-6">
              <div className="label">Move to</div>
              {ALLOWED[app.current_stage].length === 0 ? (
                <p className="text-sm text-slate-500">
                  {STAGES[app.current_stage].label} is a terminal stage.
                </p>
              ) : (
                <div className="flex flex-wrap gap-2">
                  {ALLOWED[app.current_stage].map((to) => (
                    <button key={to} className="btn-ghost" onClick={() => move(to)}>
                      <ArrowRight size={14} /> {STAGES[to].label}
                    </button>
                  ))}
                </div>
              )}
              {err && <p className="mt-2 text-sm text-rose-300">{err}</p>}
            </div>

            <div className="mt-7">
              <div className="label">Timeline</div>
              <ol className="relative ml-2 border-l border-white/10">
                {app.events.map((ev, i) => (
                  <motion.li
                    key={ev.id}
                    initial={{ opacity: 0, x: -8 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.06 }}
                    className="mb-3.5 ml-4"
                  >
                    <span
                      className={`absolute -left-[5px] mt-1.5 h-2.5 w-2.5 rounded-full ${STAGES[ev.to_stage].dot}`}
                      style={{ boxShadow: `0 0 10px ${STAGES[ev.to_stage].glow}` }}
                    />
                    <div className="text-sm">
                      <span className="font-medium text-slate-200">
                        {ev.from_stage
                          ? `${STAGES[ev.from_stage].label} → ${STAGES[ev.to_stage].label}`
                          : `Created in ${STAGES[ev.to_stage].label}`}
                      </span>
                      <span className="ml-2 text-xs text-slate-500">{fmt(ev.occurred_at)}</span>
                    </div>
                    {ev.note && <p className="text-xs text-slate-500">{ev.note}</p>}
                  </motion.li>
                ))}
              </ol>
            </div>
          </>
        )}
      </motion.div>
    </motion.div>
  );
}
