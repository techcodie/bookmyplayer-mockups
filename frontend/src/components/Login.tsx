import { useState } from "react";
import { motion } from "framer-motion";
import { ArrowRight, Sparkles } from "lucide-react";
import { api } from "../api";

export default function Login({ onAuthed }: { onAuthed: () => void }) {
  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("demo@offerfunnel.app");
  const [password, setPassword] = useState("password123");
  const [name, setName] = useState("");
  const [err, setErr] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setErr(null);
    setBusy(true);
    try {
      if (mode === "register") await api.register(email, password, name || undefined);
      await api.login(email, password);
      onAuthed();
    } catch (e: any) {
      setErr(e.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="flex min-h-full items-center justify-center p-6">
      <motion.div
        initial={{ opacity: 0, y: 24, scale: 0.96 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
        className="w-full max-w-sm"
      >
        <div className="mb-7 text-center">
          <motion.div
            initial={{ rotate: -12, scale: 0.6, opacity: 0 }}
            animate={{ rotate: 0, scale: 1, opacity: 1 }}
            transition={{ delay: 0.1, type: "spring", stiffness: 200, damping: 14 }}
            className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl font-display text-xl font-bold text-white"
            style={{
              backgroundImage: "linear-gradient(135deg,#7c6cff,#b06cff,#5ad1ff)",
              boxShadow: "0 16px 40px -10px rgba(124,108,255,.9)",
            }}
          >
            OF
          </motion.div>
          <h1 className="font-display text-2xl font-semibold">
            Offer<span className="gradient-text">Funnel</span>
          </h1>
          <p className="mt-1 text-sm text-slate-400">
            Run your internship search like a pipeline.
          </p>
        </div>

        <form onSubmit={submit} className="glass space-y-3 p-6">
          {mode === "register" && (
            <div>
              <label className="label">Name</label>
              <input className="input" value={name} onChange={(e) => setName(e.target.value)} />
            </div>
          )}
          <div>
            <label className="label">Email</label>
            <input className="input" type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
          </div>
          <div>
            <label className="label">Password</label>
            <input className="input" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
          </div>

          {err && <p className="text-sm text-rose-300">{err}</p>}

          <button className="btn-primary w-full" disabled={busy}>
            {busy ? "…" : mode === "login" ? "Sign in" : "Create account"}
            {!busy && <ArrowRight size={16} />}
          </button>

          <button
            type="button"
            className="w-full text-center text-xs text-slate-400 transition hover:text-brand-400"
            onClick={() => setMode(mode === "login" ? "register" : "login")}
          >
            {mode === "login" ? "Need an account? Register" : "Have an account? Sign in"}
          </button>
        </form>

        <div className="mt-4 flex items-center justify-center gap-1.5 text-xs text-slate-500">
          <Sparkles size={12} /> Demo account is pre-filled — just hit Sign in.
        </div>
      </motion.div>
    </div>
  );
}
