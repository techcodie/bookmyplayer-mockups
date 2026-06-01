import { useState } from "react";
import { motion } from "framer-motion";
import { api, type Stage } from "../api";
import { STAGES } from "../lib";

const STARTABLE: Stage[] = ["wishlist", "applied"];

export default function AddApplicationModal({
  onClose,
  onCreated,
}: {
  onClose: () => void;
  onCreated: () => void;
}) {
  const [f, setF] = useState({
    company: "",
    role: "",
    location: "",
    source: "",
    interest_level: 3,
    deadline: "",
    initial_stage: "wishlist" as Stage,
  });
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const set = (k: string, v: any) => setF((s) => ({ ...s, [k]: v }));

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    if (!f.company || !f.role) {
      setErr("Company and role are required.");
      return;
    }
    setBusy(true);
    setErr(null);
    try {
      await api.createApplication({
        company: f.company,
        role: f.role,
        location: f.location || null,
        source: f.source || null,
        interest_level: f.interest_level,
        deadline: f.deadline ? new Date(f.deadline).toISOString() : null,
        initial_stage: f.initial_stage,
      });
      onCreated();
    } catch (e: any) {
      setErr(e.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-30 flex items-start justify-center overflow-y-auto bg-black/60 p-4 backdrop-blur-sm sm:p-10"
      onClick={onClose}
    >
      <motion.form
        initial={{ opacity: 0, scale: 0.95, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.96, y: 12 }}
        transition={{ type: "spring", stiffness: 320, damping: 28 }}
        onSubmit={submit}
        className="glass w-full max-w-lg space-y-4 p-6"
        onClick={(e) => e.stopPropagation()}
      >
        <h2 className="font-display text-xl font-semibold text-slate-100">
          Add application
        </h2>

        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="label">Company *</label>
            <input className="input" value={f.company} onChange={(e) => set("company", e.target.value)} />
          </div>
          <div>
            <label className="label">Role *</label>
            <input className="input" value={f.role} onChange={(e) => set("role", e.target.value)} />
          </div>
          <div>
            <label className="label">Location</label>
            <input className="input" value={f.location} onChange={(e) => set("location", e.target.value)} />
          </div>
          <div>
            <label className="label">Source</label>
            <input className="input" value={f.source} onChange={(e) => set("source", e.target.value)} placeholder="LinkedIn, referral…" />
          </div>
          <div>
            <label className="label">Deadline</label>
            <input className="input [color-scheme:dark]" type="date" value={f.deadline} onChange={(e) => set("deadline", e.target.value)} />
          </div>
          <div>
            <label className="label">Interest · {f.interest_level}/5</label>
            <input
              type="range"
              min={1}
              max={5}
              value={f.interest_level}
              onChange={(e) => set("interest_level", Number(e.target.value))}
              className="mt-2 w-full accent-brand-500"
            />
          </div>
        </div>

        <div>
          <label className="label">Starting stage</label>
          <div className="flex gap-2">
            {STARTABLE.map((s) => (
              <button
                type="button"
                key={s}
                onClick={() => set("initial_stage", s)}
                className={f.initial_stage === s ? "btn-primary" : "btn-ghost"}
              >
                {STAGES[s].label}
              </button>
            ))}
          </div>
        </div>

        {err && <p className="text-sm text-rose-300">{err}</p>}

        <div className="flex justify-end gap-2 pt-1">
          <button type="button" className="btn-ghost" onClick={onClose}>
            Cancel
          </button>
          <button className="btn-primary" disabled={busy}>
            {busy ? "Saving…" : "Add application"}
          </button>
        </div>
      </motion.form>
    </motion.div>
  );
}
