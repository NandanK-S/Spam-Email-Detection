"use client";

import { useEffect, useState } from "react";
import { mockGetModelComparison } from "../../mock/mockApi";

export default function ModelComparisonCard() {
  const [models, setModels] = useState([]);

  useEffect(() => {
    mockGetModelComparison().then(setModels);
  }, []);

  if (models.length === 0) return null;

  const metrics = ["accuracy", "precision", "recall", "f1Score"];
  const metricLabels = {
    accuracy: "Accuracy",
    precision: "Precision",
    recall: "Recall",
    f1Score: "F1-Score",
  };

  return (
    <section className="px-4 mt-16 md:mt-24 pb-24 md:pb-32 animate-fade-up-delay-4">
      <div className="max-w-4xl mx-auto">
        {/* Section header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-2 rounded-full px-4 py-1.5 text-[11px] uppercase tracking-[0.2em] font-medium bg-white/[0.04] border border-white/[0.06] text-[#94a3b8] mb-4">
            <span className="w-1.5 h-1.5 rounded-full bg-violet-400" />
            Benchmark Results
          </div>
          <h2 className="text-2xl md:text-3xl font-bold tracking-tight">
            <span className="bg-gradient-to-r from-white to-white/60 bg-clip-text text-transparent">
              Model Comparison
            </span>
          </h2>
          <p className="text-sm text-[#64748b] mt-2">
            Performance evaluation across three classification algorithms
          </p>
        </div>

        {/* Model cards grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-5">
          {models.map((model, idx) => (
            <div
              key={model.name}
              className={`group relative p-1.5 rounded-[2rem] transition-all duration-500 ease-[cubic-bezier(0.32,0.72,0,1)] ${
                model.selected
                  ? "bg-gradient-to-br from-violet-500/20 via-indigo-500/10 to-emerald-500/10 border border-violet-500/20 shadow-lg shadow-violet-500/5"
                  : "bg-white/[0.02] border border-white/[0.06] hover:border-white/[0.1]"
              }`}
              style={{ animationDelay: `${idx * 100}ms` }}
            >
              {/* Selected badge */}
              {model.selected && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2 z-10">
                  <span className="inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-[9px] uppercase tracking-[0.2em] font-bold bg-gradient-to-r from-violet-600 to-indigo-600 text-white shadow-lg shadow-violet-500/25 border border-violet-400/20">
                    <svg
                      className="w-2.5 h-2.5"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="3"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    >
                      <polyline points="20 6 9 17 4 12" />
                    </svg>
                    Selected Model
                  </span>
                </div>
              )}

              {/* Inner content */}
              <div
                className={`rounded-[calc(2rem-0.375rem)] p-6 shadow-[inset_0_1px_1px_rgba(255,255,255,0.06)] ${
                  model.selected ? "bg-white/[0.04]" : "bg-white/[0.03]"
                }`}
              >
                {/* Model name */}
                <h3
                  className={`text-lg font-bold tracking-tight mb-1 ${
                    model.selected ? "text-white" : "text-[#94a3b8]"
                  }`}
                >
                  {model.name}
                </h3>
                <div className="text-[10px] text-[#64748b] uppercase tracking-wider mb-6">
                  Classification Model
                </div>

                {/* Metrics */}
                <div className="space-y-4">
                  {metrics.map((metric) => {
                    const value = Math.round(model[metric] * 1000) / 10;
                    return (
                      <div key={metric}>
                        <div className="flex items-baseline justify-between mb-1.5">
                          <span className="text-[10px] uppercase tracking-wider text-[#64748b] font-medium">
                            {metricLabels[metric]}
                          </span>
                          <span
                            className={`text-sm font-bold tabular-nums ${
                              model.selected
                                ? "text-violet-300"
                                : "text-[#94a3b8]"
                            }`}
                          >
                            {value}%
                          </span>
                        </div>
                        <div className="h-1.5 rounded-full bg-white/[0.04] overflow-hidden">
                          <div
                            className={`h-full rounded-full transition-all duration-1000 ease-[cubic-bezier(0.32,0.72,0,1)] ${
                              model.selected
                                ? "bg-gradient-to-r from-violet-500 to-indigo-400"
                                : "bg-white/[0.12]"
                            }`}
                            style={{ width: `${value}%` }}
                          />
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
