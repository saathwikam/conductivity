import { useEffect, useState } from "react";

export function CountGauge({ value, label }) {
  const [display, setDisplay] = useState(0);

  useEffect(() => {
    let frame = 0;
    let start;
    const duration = 1200;

    const tick = (timestamp) => {
      if (!start) start = timestamp;
      const progress = Math.min((timestamp - start) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      setDisplay(value * eased);
      if (progress < 1) {
        frame = requestAnimationFrame(tick);
      }
    };

    frame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame);
  }, [value]);

  const percentage = Math.min(Math.max(((display + 10) / 10) * 100, 0), 100);

  return (
    <div className="rounded-[1.5rem] border border-white/10 bg-white/5 p-6 backdrop-blur-xl">
      <p className="text-sm uppercase tracking-[0.35em] text-white/50">{label}</p>
      <div className="mt-6 flex items-end gap-4">
        <span className="font-display text-5xl text-white">{display.toFixed(3)}</span>
        <span className="pb-2 text-white/50">log σ</span>
      </div>
      <div className="mt-6 h-3 overflow-hidden rounded-full bg-white/10">
        <div
          className="h-full rounded-full bg-gradient-to-r from-cyan-300 via-sky-400 to-emerald-300 transition-all"
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}
