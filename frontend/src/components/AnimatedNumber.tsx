import { useEffect, useRef, useState } from "react";
import { animate } from "framer-motion";

// Counts up to `value` on mount / change. `format` lets callers render
// percentages, days, etc. while keeping the smooth tween.
export default function AnimatedNumber({
  value,
  format = (n) => `${Math.round(n)}`,
  duration = 1.1,
}: {
  value: number;
  format?: (n: number) => string;
  duration?: number;
}) {
  const [display, setDisplay] = useState("0");
  const prev = useRef(0);

  useEffect(() => {
    const controls = animate(prev.current, value, {
      duration,
      ease: [0.16, 1, 0.3, 1],
      onUpdate: (v) => setDisplay(format(v)),
    });
    prev.current = value;
    return () => controls.stop();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [value]);

  return <span>{display}</span>;
}
