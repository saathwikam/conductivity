import { AnimatePresence, motion } from "framer-motion";

const scannerLines = [
  "Analyzing atomic neighbors...",
  "Constructing line-graph edges...",
  "Resolving ionic pathways...",
  "Projecting conductivity signature...",
];

export function ScannerOverlay({ active, phase }) {
  return (
    <AnimatePresence>
      {active ? (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/92 backdrop-blur-md"
        >
          <div className="relative flex w-[min(92vw,52rem)] flex-col items-center gap-8 rounded-[2rem] border border-white/10 bg-white/5 px-8 py-12">
            <div className="absolute inset-0 rounded-[2rem] bg-gradient-to-br from-cyan-400/10 via-transparent to-emerald-400/10" />
            <div className="relative h-48 w-48 overflow-hidden rounded-full border border-white/20">
              <div className="absolute inset-6 rounded-full border border-white/15" />
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 3.2, repeat: Infinity, ease: "linear" }}
                className="absolute inset-0 rounded-full border-t border-cyan-300 border-r border-emerald-300"
              />
              <motion.div
                animate={{ y: ["-10%", "110%"] }}
                transition={{ duration: 1.8, repeat: Infinity, ease: "easeInOut" }}
                className="absolute left-0 right-0 h-20 bg-gradient-to-b from-transparent via-cyan-300/30 to-transparent"
              />
            </div>
            <div className="relative space-y-4 text-center">
              <p className="font-display text-sm uppercase tracking-[0.45em] text-white/55">
                {phase === "solid" ? "Solid Crystal Scan" : "Liquid Molecule Scan"}
              </p>
              <div className="space-y-2">
                {scannerLines.map((line, index) => (
                  <motion.p
                    key={line}
                    initial={{ opacity: 0.25 }}
                    animate={{ opacity: [0.25, 1, 0.25] }}
                    transition={{ delay: index * 0.2, duration: 1.4, repeat: Infinity }}
                    className="text-lg text-white/80"
                  >
                    {line}
                  </motion.p>
                ))}
              </div>
            </div>
          </div>
        </motion.div>
      ) : null}
    </AnimatePresence>
  );
}
