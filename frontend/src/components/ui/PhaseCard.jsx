import { motion } from "framer-motion";

export function PhaseCard({ title, accentClass, active, onClick, icon }) {
  return (
    <motion.button
      whileHover={{ y: -8, scale: 1.01 }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
      className={`group relative overflow-hidden rounded-[2rem] border border-white/15 bg-white/8 p-6 text-left shadow-neon backdrop-blur-2xl transition ${
        active ? "ring-2 ring-white/40" : ""
      }`}
    >
      <div
        className={`absolute inset-0 opacity-80 blur-3xl transition duration-500 group-hover:scale-110 ${accentClass}`}
      />
      <div className="relative z-10 flex h-full flex-col justify-between gap-8">
        <div className="flex items-center justify-between">
          <div className="text-white/85">{icon}</div>
          <span className="rounded-full border border-white/15 bg-black/20 px-3 py-1 text-xs uppercase tracking-[0.3em] text-white/60">
            Portal
          </span>
        </div>
        <div>
          <h3 className="font-display text-3xl uppercase tracking-[0.18em] text-white">{title}</h3>
        </div>
      </div>
    </motion.button>
  );
}
