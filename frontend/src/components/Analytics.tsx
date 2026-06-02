import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { ArrowDown, Flame, Zap, Activity, Trophy } from "lucide-react";
import { api, type Funnel, type Stage, type Summary, type VelocityStep } from "../api";
import { STAGES } from "../lib";
import AnimatedNumber from "./AnimatedNumber";

function Stat({
  icon: Icon,
  label,
  value,
  format,
  sub,
}: {
  icon: typeof Flame;
  label: string;
  value: number;
  format?: (n: number) => string;
  sub?: string;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass glass-hover p-4"
    >
      <div className="flex items-center gap-2 text-[11px] font-semibold uppercase tracking-wider text-slate-400">
        <Icon size={14} className="text-brand-400" /> {label}
      </div>
      <div className="mt-1.5 font-display text-3xl font-bold text-slate-100">
        <AnimatedNumber value={value} format={format} />
      </div>
      {sub && <div className="text-xs text-slate-500">{sub}</div>}
    </motion.div>
  );
}

export default function Analytics({ version }: { version: number }) {
  const [funnel, setFunnel] = useState<Funnel | null>(null);
  const [summary, setSummary] = useState<Summary | null>(null);
  const [velocity, setVelocity] = useState<VelocityStep[]>([]);

  useEffect(() => {
    api.funnel().then(setFunnel);
    api.summary().then(setSummary);
    api.velocity().then(setVelocity);
  }, [version]);

  const maxReached = funnel ? Math.max(1, ...funnel.steps.map((s) => s.reached)) : 1;
  const maxVel = Math.max(1, ...velocity.map((v) => v.avg_days));

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        {summary && (
          <>
            <Stat icon={Activity} label="Active" value={summary.active} sub={`${summary.total} total`} />
            <Stat
              icon={Zap}
              label="Response rate"
              value={(summary.response_rate ?? 0) * 100}
              format={(n) => `${Math.round(n)}%`}
              sub={`${summary.responded}/${summary.applied} applied`}
            />
            <Stat
              icon={Trophy}
              label="Offer rate"
              value={(summary.offer_rate ?? 0) * 100}
              format={(n) => `${Math.round(n)}%`}
              sub={`${summary.offers} offer${summary.offers === 1 ? "" : "s"}`}
            />
            <Stat
              icon={Flame}
              label="Avg time to response"
              value={summary.avg_time_to_response_days ?? 0}
              format={(n) => `${n.toFixed(1)}d`}
            />
          </>
        )}
      </div>

      {/* Funnel — the hero */}
      <section className="glass p-6">
        <h2 className="font-display text-xl font-semibold text-slate-100">
          Conversion funnel
        </h2>
        <p className="mb-6 mt-1 text-sm text-slate-400">
          Each application counts toward the <em>furthest</em> stage it ever
          reached — a rejection after an interview still counts as “reached
          Interview.”
        </p>

        <div className="space-y-3">
          {funnel?.steps.map((s, i) => {
            const prev = funnel.steps[i - 1];
            const isDrop =
              funnel.biggest_dropoff?.to === s.stage &&
              funnel.biggest_dropoff?.from === prev?.stage;
            const meta = STAGES[s.stage as Stage];
            const conv = s.conversion == null ? null : Math.round(s.conversion * 100);
            return (
              <div key={s.stage}>
                {i > 0 && (
                  <div
                    className={`mb-1.5 ml-1 flex items-center gap-2 text-xs ${
                      isDrop ? "font-semibold text-rose-300" : "text-slate-500"
                    }`}
                  >
                    <ArrowDown size={12} /> {conv}% convert
                    {isDrop && (
                      <span className="flex items-center gap-1 rounded-full bg-rose-500/20 px-2 py-0.5 text-[10px] font-semibold text-rose-200 ring-1 ring-rose-400/30">
                        <Flame size={10} /> biggest drop-off
                      </span>
                    )}
                  </div>
                )}
                <div className="flex items-center gap-3">
                  <div className="w-20 shrink-0 text-sm font-medium text-slate-300">
                    {meta.label}
                  </div>
                  <div className="h-10 flex-1 overflow-hidden rounded-xl bg-white/5">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${Math.max(7, (s.reached / maxReached) * 100)}%` }}
                      transition={{ delay: 0.15 + i * 0.12, duration: 0.9, ease: [0.16, 1, 0.3, 1] }}
                      className={`flex h-10 items-center justify-end rounded-xl bg-gradient-to-r ${meta.grad} px-3 font-display text-sm font-bold text-black/80`}
                      style={{ boxShadow: `0 6px 24px -8px ${meta.glow}` }}
                    >
                      {s.reached}
                    </motion.div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* Velocity */}
      <section className="glass p-6">
        <h2 className="font-display text-xl font-semibold text-slate-100">
          Velocity — avg time in stage
        </h2>
        <p className="mb-6 mt-1 text-sm text-slate-400">
          Measured only for stages an application actually left (completed stays).
        </p>
        <div className="space-y-2.5">
          {velocity.map((v, i) => {
            const meta = STAGES[v.stage as Stage];
            return (
              <div key={v.stage} className="flex items-center gap-3">
                <div className="w-20 shrink-0 text-sm font-medium text-slate-300">
                  {meta.label}
                </div>
                <div className="h-6 flex-1 overflow-hidden rounded-lg bg-white/5">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${(v.avg_days / maxVel) * 100}%` }}
                    transition={{ delay: 0.1 + i * 0.1, duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
                    className={`h-6 rounded-lg bg-gradient-to-r ${meta.grad} opacity-90`}
                  />
                </div>
                <div className="w-24 shrink-0 text-right text-sm text-slate-400">
                  {v.avg_days.toFixed(1)}d · n={v.n}
                </div>
              </div>
            );
          })}
          {velocity.length === 0 && (
            <p className="text-sm text-slate-500">
              Not enough movement yet to measure velocity.
            </p>
          )}
        </div>
      </section>
    </div>
  );
}
