"use client";

import { useEffect, useState } from "react";

export default function PredictionResult({ result }) {
  const [animatedConfidence, setAnimatedConfidence] = useState(0);

  useEffect(() => {
    if (!result) return;
    const timer = setTimeout(() => {
      setAnimatedConfidence(Math.round(result.confidence * 100));
    }, 50);
    return () => clearTimeout(timer);
  }, [result]);

  if (!result) return null;

  const isError = Boolean(result.error) || result.prediction === "Error";
  const isSpam = !isError && result.prediction?.toLowerCase() === "spam";

  if (isError) {
    return (
      <section className="px-4 mt-10 animate-fade-up">
        <div className="max-w-3xl mx-auto p-1.5 md:p-2 rounded-[2rem] bg-white/[0.02] border border-white/[0.06]">
          <div className="rounded-[calc(2rem-0.375rem)] bg-white/[0.03] p-6 md:p-8 shadow-[inset_0_1px_1px_rgba(255,255,255,0.06)]">
            <div className="flex items-center gap-2 mb-4">
              <div className="w-2 h-2 rounded-full bg-amber-500" />
              <span className="text-[11px] uppercase tracking-[0.15em] font-semibold text-[#94a3b8]">
                Analysis Status
              </span>
            </div>
            <div className="rounded-2xl px-6 py-4 border bg-amber-500/10 border-amber-500/20">
              <div className="flex items-center gap-3">
                <span className="text-2xl">⚠️</span>
                <div>
                  <div className="text-sm font-bold text-amber-400">
                    Analysis Error
                  </div>
                  <div className="text-xs text-[#94a3b8] mt-1">
                    {result.error || "Unable to complete email analysis. Please verify the backend service is running."}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    );
  }

  return (
    <section className="px-4 mt-10 animate-fade-up">
      {/* Double-bezel shell */}
      <div className="max-w-3xl mx-auto p-1.5 md:p-2 rounded-[2rem] bg-white/[0.02] border border-white/[0.06]">
        <div className="rounded-[calc(2rem-0.375rem)] bg-white/[0.03] p-6 md:p-8 shadow-[inset_0_1px_1px_rgba(255,255,255,0.06)]">
          {/* Section label */}
          <div className="flex items-center gap-2 mb-6">
            <div
              className={`w-2 h-2 rounded-full ${
                isSpam ? "bg-red-500" : "bg-emerald-500"
              }`}
            />
            <span className="text-[11px] uppercase tracking-[0.15em] font-semibold text-[#94a3b8]">
              Prediction Result
            </span>
          </div>

          <div className="flex flex-col md:flex-row md:items-center gap-6">
            {/* Result badge */}
            <div
              className={`inline-flex items-center gap-3 rounded-2xl px-6 py-4 border ${
                isSpam
                  ? "bg-red-500/10 border-red-500/20 shadow-lg shadow-red-500/5"
                  : "bg-emerald-500/10 border-emerald-500/20 shadow-lg shadow-emerald-500/5"
              }`}
            >
              <span className="text-2xl">{isSpam ? "🚫" : "✅"}</span>
              <div>
                <div
                  className={`text-2xl font-bold tracking-tight ${
                    isSpam ? "text-red-400" : "text-emerald-400"
                  }`}
                >
                  {result.prediction}
                </div>
                <div className="text-xs text-[#94a3b8] mt-0.5">
                  {isSpam ? "Flagged as malicious" : "Safe email detected"}
                </div>
              </div>
            </div>

            {/* Confidence meter */}
            <div className="flex-1">
              <div className="flex items-baseline justify-between mb-2">
                <span className="text-xs text-[#94a3b8] uppercase tracking-wider font-medium">
                  Confidence Score
                </span>
                <span
                  className={`text-2xl font-bold tabular-nums ${
                    isSpam ? "text-red-400" : "text-emerald-400"
                  }`}
                >
                  {animatedConfidence}%
                </span>
              </div>

              {/* Progress bar */}
              <div className="h-2.5 rounded-full bg-white/[0.04] overflow-hidden border border-white/[0.04]">
                <div
                  className={`h-full rounded-full transition-all duration-1000 ease-[cubic-bezier(0.32,0.72,0,1)] ${
                    isSpam
                      ? "bg-gradient-to-r from-red-600 to-red-400 shadow-[0_0_12px_rgba(239,68,68,0.3)]"
                      : "bg-gradient-to-r from-emerald-600 to-emerald-400 shadow-[0_0_12px_rgba(16,185,129,0.3)]"
                  }`}
                  style={{ width: `${animatedConfidence}%` }}
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
