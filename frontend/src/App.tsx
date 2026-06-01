import { useState } from "react";
import { AnimatePresence } from "framer-motion";
import { token } from "./api";
import Login from "./components/Login";
import Board from "./components/Board";
import AddApplicationModal from "./components/AddApplicationModal";

export default function App() {
  const [authed, setAuthed] = useState(!!token.get());
  const [adding, setAdding] = useState(false);
  const [version, setVersion] = useState(0);
  const reload = () => setVersion((v) => v + 1);
  if (!authed) return <Login onAuthed={() => setAuthed(true)} />;
  return (
    <div className="min-h-full p-6">
      <button className="btn-primary mb-4" onClick={() => setAdding(true)}>+ Add application</button>
      <Board version={version} reload={reload} />
      <AnimatePresence>{adding && <AddApplicationModal onClose={() => setAdding(false)} onCreated={() => { setAdding(false); reload(); }} />}</AnimatePresence>
    </div>
  );
}
