import { useEffect, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Clock, Mail, Target, Check } from "lucide-react";
import { api, type FocusItem, type Reminder } from "../api";
import { STAGES, deadlineBadge, initials } from "../lib";
import AppDetail from "./AppDetail";

const REMINDER_META: Record<
  Reminder["type"],
  { icon: typeof Clock; label: string; color: string }
> = {
  deadline: { icon: Clock, label: "Deadline", color: "text-rose-300" },
  follow_up: { icon: Mail, label: "Follow up", color: "text-sky-300" },
  interview: { icon: Target, label: "Interview", color: "text-amber-300" },
};

export default function FocusToday({
  version,
  reload,
}: {
  version: number;
  reload: () => void;
}) {
  const [items, setItems] = useState<FocusItem[] | null>(null);
  const [reminders, setReminders] = useState<Reminder[]>([]);
  const [openId, setOpenId] = useState<number | null>(null);

  const load = () => {
    api.focusToday().then(setItems);
    api.reminders(true).then(setReminders);
  };
  useEffect(load, [version]);

  async function resolve(id: number) {
    setReminders((rs) => rs.filter((r) => r.id !== id));
    await api.resolveReminder(id);
  }

  const maxScore = Math.max(1, ...(items ?? []).map((a) => a.priority_score));

  return (
    <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
      <section className="lg:col-span-2">
        <h2 className="font-display text-xl font-semibold text-slate-100">
          What to act on today
        </h2>
        <p className="mb-4 mt-1 text-sm text-slate-400">
          Ranked by a transparent score: stage + deadline proximity + interest +
          staleness.
        </p>
        <div className="space-y-2.5">
          {items?.map((a, i) => {
            const badge = deadlineBadge(a.deadline);
            const meta = STAGES[a.current_stage];
            return (
              <motion.div
                key={a.id}
                initial={{ opacity: 0, x: -16 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.04 }}
                whileHover={{ x: 3 }}
                onClick={() => setOpenId(a.id)}
                className="glass glass-hover relative flex cursor-pointer items-center gap-3 overflow-hidden p-3"
              >
                <div
                  className="absolute left-0 top-0 h-full w-1 bg-gradient-to-b"
                  style={{
                    backgroundImage: `linear-gradient(${meta.glow}, transparent)`,
                  }}
                />
                <div className="w-5 text-center font-display text-sm font-bold text-slate-600">
                  {i + 1}
                </div>
                <div
                  className={`flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-br ${meta.grad} text-xs font-bold text-black/80`}
                  style={{ boxShadow: `0 4px 14px -4px ${meta.glow}` }}
                >
                  {initials(a.company)}
                </div>
                <div className="min-w-0 flex-1">
                  <div className="truncate text-sm font-semibold text-slate-100">
                    {a.company}
                    <span className="font-normal text-slate-400"> · {a.role}</span>
                  </div>
                  <div className="mt-1 flex items-center gap-1.5">
                    <span className={`rounded-full px-1.5 py-0.5 text-[10px] font-medium ring-1 ${meta.chip}`}>
                      {meta.label}
                    </span>
                    {badge && (
                      <span className={`rounded-full px-1.5 py-0.5 text-[10px] font-medium ring-1 ${badge.cls}`}>
                        {badge.text}
                      </span>
                    )}
                  </div>
                </div>
                <div className="flex w-28 items-center gap-2">
                  <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-white/5">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${(a.priority_score / maxScore) * 100}%` }}
                      transition={{ delay: 0.2 + i * 0.04, duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
                      className="h-full rounded-full bg-gradient-to-r from-indigo-400 to-violet-400"
                    />
                  </div>
                  <div className="w-6 text-right font-display text-lg font-bold text-brand-400">
                    {a.priority_score}
                  </div>
                </div>
              </motion.div>
            );
          })}
          {items && items.length === 0 && (
            <div className="glass p-8 text-center text-sm text-slate-400">
              Nothing active to act on — nice work.
            </div>
          )}
        </div>
      </section>

      <section>
        <h2 className="font-display text-xl font-semibold text-slate-100">Reminders</h2>
        <p className="mb-4 mt-1 text-sm text-slate-400">
          Rule-generated nudges. Check them off when done.
        </p>
        <div className="space-y-2.5">
          <AnimatePresence>
            {reminders.map((r) => {
              const m = REMINDER_META[r.type];
              const Icon = m.icon;
              return (
                <motion.div
                  layout
                  key={r.id}
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, x: 40 }}
                  className="glass flex items-start gap-2.5 p-3"
                >
                  <Icon size={16} className={`mt-0.5 ${m.color}`} />
                  <div className="min-w-0 flex-1">
                    <div className="text-[10px] font-semibold uppercase tracking-wider text-slate-500">
                      {m.label}
                    </div>
                    <p className="text-sm text-slate-200">{r.message}</p>
                  </div>
                  <button
                    onClick={() => resolve(r.id)}
                    className="shrink-0 rounded-lg border border-white/10 p-1.5 text-slate-400 transition hover:border-emerald-400/40 hover:text-emerald-300"
                    title="Mark done"
                  >
                    <Check size={14} />
                  </button>
                </motion.div>
              );
            })}
          </AnimatePresence>
          {reminders.length === 0 && (
            <div className="glass p-8 text-center text-sm text-slate-400">
              No open reminders.
            </div>
          )}
        </div>
      </section>

      <AnimatePresence>
        {openId != null && (
          <AppDetail
            id={openId}
            onClose={() => setOpenId(null)}
            onChanged={() => {
              load();
              reload();
            }}
          />
        )}
      </AnimatePresence>
    </div>
  );
}
