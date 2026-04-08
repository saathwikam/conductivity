import { useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Atom, ChevronLeft, FlaskConical, Sparkles } from "lucide-react";

import { getExample, predict } from "./lib/api";
import { PhaseCard } from "./components/ui/PhaseCard";
import { ScannerOverlay } from "./components/ui/ScannerOverlay";
import { CountGauge } from "./components/ui/CountGauge";

const PHASE_CONTENT = {
  solid: {
    title: "Solid Electrolyte",
    subtitle: "Periodic graph analysis for ceramic and glassy lithium solid electrolytes.",
    accentClass: "bg-[radial-gradient(circle_at_top,rgba(56,189,248,0.45),transparent_65%)]",
    icon: <Atom className="h-8 w-8" />,
    placeholder: "Li7La3Zr2O12",
    helper: "Enter a solid electrolyte chemical formula.",
  },
  liquid: {
    title: "Liquid Electrolyte",
    subtitle: "Cluster-based graph analysis for liquid lithium salt and solvent formulations.",
    accentClass: "bg-[radial-gradient(circle_at_top,rgba(16,185,129,0.45),transparent_65%)]",
    icon: <FlaskConical className="h-8 w-8" />,
    placeholder: "LiPF6 in EC/EMC",
    helper: "Enter a liquid electrolyte formulation as a chemistry string.",
  },
};

export default function App() {
  const [phase, setPhase] = useState(null);
  const [formula, setFormula] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const current = phase ? PHASE_CONTENT[phase] : null;

  async function handleSubmit(event) {
    event.preventDefault();
    if (!phase || !formula.trim()) return;

    setLoading(true);
    setError("");
    try {
      const data = await predict({ phase, formula });
      setResult(data);
    } catch (submissionError) {
      setError(submissionError.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleUseExample() {
    if (!phase) return;

    setError("");
    try {
      const data = await getExample(phase);
      setFormula(data.formula);
      setResult(null);
    } catch (exampleError) {
      setError(exampleError.message);
    }
  }

  function handleReset() {
    setPhase(null);
    setFormula("");
    setResult(null);
    setError("");
  }

  return (
    <div className="min-h-screen overflow-hidden bg-[#040812] text-white">
      <ScannerOverlay active={loading} phase={phase} />
      <div className="pointer-events-none absolute inset-0 bg-grid bg-[length:32px_32px] opacity-20" />
      <div className="pointer-events-none absolute left-[-8rem] top-[-10rem] h-72 w-72 rounded-full bg-cyan-400/25 blur-3xl" />
      <div className="pointer-events-none absolute bottom-[-8rem] right-[-2rem] h-80 w-80 rounded-full bg-emerald-400/20 blur-3xl" />

      <main className="relative mx-auto flex min-h-screen w-full max-w-7xl flex-col px-5 py-8 sm:px-8 lg:px-12">
        <header className="flex items-center justify-between">
          <div>
            <p className="font-display text-sm uppercase tracking-[0.45em] text-white/50">Cyber-Lab Portal</p>
            <h1 className="mt-3 font-display text-4xl uppercase tracking-[0.18em] text-white sm:text-5xl">
              Ionic SL
            </h1>
          </div>
          {phase ? (
            <button
              onClick={handleReset}
              className="inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/5 px-4 py-2 text-sm text-white/70 transition hover:bg-white/10"
            >
              <ChevronLeft className="h-4 w-4" />
              Reset Portal
            </button>
          ) : null}
        </header>

        <AnimatePresence mode="wait">
          {!phase ? (
            <motion.section
              key="portal"
              initial={{ opacity: 0, scale: 0.96 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 1.04 }}
              transition={{ duration: 0.5 }}
              className="my-auto grid gap-6 py-14 md:grid-cols-2"
            >
              <PhaseCard
                {...PHASE_CONTENT.solid}
                active={phase === "solid"}
                onClick={() => setPhase("solid")}
              />
              <PhaseCard
                {...PHASE_CONTENT.liquid}
                active={phase === "liquid"}
                onClick={() => setPhase("liquid")}
              />
            </motion.section>
          ) : (
            <motion.section
              key="lab"
              initial={{ opacity: 0, y: 28, scale: 0.98 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: -12 }}
              transition={{ duration: 0.45 }}
              className="grid flex-1 gap-6 py-8 lg:grid-cols-[1.15fr_0.85fr]"
            >
              <div className="rounded-[2rem] border border-white/10 bg-white/6 p-6 shadow-neon backdrop-blur-2xl sm:p-8">
                <div className="flex items-center gap-3">
                  <div className="rounded-full border border-white/15 bg-white/8 p-3 text-white/85">{current.icon}</div>
                  <div>
                    <p className="text-sm uppercase tracking-[0.35em] text-white/45">Stage 2 - The Lab</p>
                    <h2 className="font-display text-3xl uppercase tracking-[0.14em] text-white">{current.title}</h2>
                  </div>
                </div>

                <p className="mt-5 max-w-2xl text-lg leading-7 text-white/68">{current.subtitle}</p>

                <form onSubmit={handleSubmit} className="mt-8 space-y-5">
                  <label className="block">
                    <span className="mb-3 block text-sm uppercase tracking-[0.35em] text-white/45">
                      {phase === "solid" ? "Chemical Formula" : "Chemical Formulation"}
                    </span>
                    <div className="rounded-[1.6rem] border border-white/15 bg-black/20 p-[1px]">
                      <input
                        value={formula}
                        onChange={(event) => setFormula(event.target.value)}
                        placeholder={current.placeholder}
                        className="w-full rounded-[1.55rem] border-0 bg-transparent px-6 py-5 text-xl text-white outline-none placeholder:text-white/25"
                      />
                    </div>
                  </label>

                  <div className="flex flex-wrap items-center gap-3 text-white/55">
                    <Sparkles className="h-4 w-4" />
                    <span>{current.helper}</span>
                  </div>

                  <div className="flex flex-wrap gap-3 pt-3">
                    <button
                      type="submit"
                      className="rounded-full bg-white px-6 py-3 font-display text-sm uppercase tracking-[0.3em] text-slate-950 transition hover:scale-[1.02]"
                    >
                      Launch Scan
                    </button>
                    <button
                      type="button"
                      onClick={handleUseExample}
                      className="rounded-full border border-white/15 bg-white/5 px-6 py-3 font-display text-sm uppercase tracking-[0.3em] text-white/75"
                    >
                      Use Example
                    </button>
                  </div>
                </form>

                {error ? (
                  <div className="mt-5 rounded-2xl border border-rose-400/25 bg-rose-400/10 px-4 py-3 text-rose-100">
                    {error}
                  </div>
                ) : null}

                {result ? (
                  <div className="mt-8 grid gap-4 sm:grid-cols-2">
                    <CountGauge value={result.prediction} label="Predicted Conductivity" />
                    <div className="rounded-[1.5rem] border border-white/10 bg-white/5 p-6 backdrop-blur-xl">
                      <p className="text-sm uppercase tracking-[0.35em] text-white/50">Graph Stats</p>
                      <div className="mt-5 space-y-3 text-white/80">
                        <div className="flex items-center justify-between">
                          <span>Graph type</span>
                          <span className="text-white/55">{result.graph_stats.graph_type}</span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span>Nodes</span>
                          <span className="text-white/55">{result.graph_stats.node_count}</span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span>Edges</span>
                          <span className="text-white/55">{result.graph_stats.edge_count}</span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span>Boundary mode</span>
                          <span className="text-white/55">
                            {result.graph_stats.periodic_boundary ? "Periodic" : "Cluster"}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                ) : null}
              </div>

              <div className="grid gap-6">
                <div className="rounded-[2rem] border border-white/10 bg-white/6 p-6 backdrop-blur-2xl">
                  <p className="text-sm uppercase tracking-[0.35em] text-white/45">Stage 4 - The Reveal</p>
                  {result ? (
                    <div className="mt-4 space-y-4">
                      <p className="text-white/72">{result.narrative}</p>
                      <pre className="overflow-x-auto rounded-[1.2rem] border border-white/10 bg-black/20 p-4 text-sm text-cyan-100/85">
                        {JSON.stringify(result.matched_record, null, 2)}
                      </pre>
                    </div>
                  ) : (
                    <p className="mt-4 text-white/45">
                      The response card will show the closest matched record, temperature, and conductivity target from the dataset.
                    </p>
                  )}
                </div>
              </div>
            </motion.section>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
}
