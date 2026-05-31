import { useState } from "react";
import { token } from "./api";
import Login from "./components/Login";

export default function App() {
  const [authed, setAuthed] = useState(!!token.get());
  if (!authed) return <Login onAuthed={() => setAuthed(true)} />;
  return <div className="p-8 text-slate-200">Dashboard coming soon…</div>;
}
