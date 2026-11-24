"use client";

import { useState } from "react";

export default function BlockchainLog({ blocks }) {
  const [visibleCount, setVisibleCount] = useState(10);

  if (!blocks || blocks.length === 0) return null;

  const displayedBlocks = blocks.slice(0, visibleCount);
  const hasMore = blocks.length > visibleCount;

  const truncateHash = (hash) => {
    return `${hash.slice(0, 6)}...${hash.slice(-4)}`;
  };

  const formatTimestamp = (rawTs) => {
    if (!rawTs) return "";
    try {
      // Parse UTC timestamp: "2026-09-06 18:59:29" -> "2026-09-06T18:59:29Z"
      const utcString = rawTs.includes("T")
        ? (rawTs.endsWith("Z") ? rawTs : rawTs + "Z")
        : rawTs.replace(" ", "T") + "Z";
      const date = new Date(utcString);
      if (!isNaN(date.getTime())) {
        return date.toLocaleString(undefined, {
          year: "numeric",
          month: "short",
          day: "numeric",
          hour: "2-digit",
          minute: "2-digit",
          second: "2-digit",
          hour12: true,
        });
      }
    } catch {
      // fallback to raw string
    }
    return rawTs;
  };

  const isSpam = (prediction) =>
    prediction?.toLowerCase() === "spam";

  return (
    <section className="px-4 mt-16 md:mt-24 animate-fade-up-delay-2">
      <div className="max-w-4xl mx-auto">
        {/* Section header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-2 rounded-full px-4 py-1.5 text-[11px] uppercase tracking-[0.2em] font-medium bg-white/[0.04] border border-white/[0.06] text-[#94a3b8] mb-4">
            <span className="w-1.5 h-1.5 rounded-full bg-indigo-400" />
            Immutable Ledger
          </div>
          <h2 className="text-2xl md:text-3xl font-bold tracking-tight">
            <span className="bg-gradient-to-r from-white to-white/60 bg-clip-text text-transparent">
              Blockchain Audit Log
            </span>
          </h2>
          <p className="text-sm text-[#64748b] mt-2">
            All Predictions — Tamper-Proof Records
          </p>
        </div>

        {/* Double-bezel table card */}
        <div className="p-1.5 md:p-2 rounded-[2rem] bg-white/[0.02] border border-white/[0.06]">
          <div className="rounded-[calc(2rem-0.375rem)] bg-white/[0.03] overflow-hidden shadow-[inset_0_1px_1px_rgba(255,255,255,0.06)]">
            {/* Desktop table */}
            <div className="hidden md:block overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-white/[0.06]">
                    <th className="text-left px-6 py-4 text-[10px] uppercase tracking-[0.15em] font-semibold text-[#64748b]">
                      Block #
                    </th>
                    <th className="text-left px-6 py-4 text-[10px] uppercase tracking-[0.15em] font-semibold text-[#64748b]">
                      Timestamp
                    </th>
                    <th className="text-left px-6 py-4 text-[10px] uppercase tracking-[0.15em] font-semibold text-[#64748b]">
                      Email Hash
                    </th>
                    <th className="text-left px-6 py-4 text-[10px] uppercase tracking-[0.15em] font-semibold text-[#64748b]">
                      Prediction
                    </th>
                    <th className="text-right px-6 py-4 text-[10px] uppercase tracking-[0.15em] font-semibold text-[#64748b]">
                      Confidence
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {displayedBlocks.map((block, i) => (
                    <tr
                      key={`${block.blockNumber}-${i}`}
                      className={`border-b border-white/[0.03] transition-colors duration-300 hover:bg-white/[0.02] ${
                        i === 0 ? "bg-white/[0.02]" : ""
                      }`}
                    >
                      <td className="px-6 py-4">
                        <span className="inline-flex items-center justify-center w-8 h-8 rounded-lg bg-white/[0.04] border border-white/[0.06] text-xs font-bold text-violet-400 tabular-nums">
                          {block.blockNumber}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-[#94a3b8] text-xs font-mono tabular-nums whitespace-nowrap">
                        {formatTimestamp(block.timestamp)}
                      </td>
                      <td className="px-6 py-4">
                        <code className="text-xs font-mono bg-white/[0.04] border border-white/[0.06] px-2.5 py-1 rounded-md text-indigo-300">
                          {truncateHash(block.emailHash)}
                        </code>
                      </td>
                      <td className="px-6 py-4">
                        <span
                          className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-[10px] uppercase tracking-wider font-bold ${
                            isSpam(block.prediction)
                              ? "bg-red-500/10 border border-red-500/20 text-red-400"
                              : "bg-emerald-500/10 border border-emerald-500/20 text-emerald-400"
                          }`}
                        >
                          <span
                            className={`w-1 h-1 rounded-full ${
                              isSpam(block.prediction)
                                ? "bg-red-400"
                                : "bg-emerald-400"
                            }`}
                          />
                          {block.prediction}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-right">
                        <span className="text-sm font-bold text-[#f8fafc] tabular-nums">
                          {Math.round(block.confidence * 100)}%
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Mobile cards */}
            <div className="md:hidden divide-y divide-white/[0.04]">
              {displayedBlocks.map((block, i) => (
                <div
                  key={`mobile-${block.blockNumber}-${i}`}
                  className={`p-5 ${i === 0 ? "bg-white/[0.02]" : ""}`}
                >
                  <div className="flex items-center justify-between mb-3">
                    <span className="inline-flex items-center justify-center w-8 h-8 rounded-lg bg-white/[0.04] border border-white/[0.06] text-xs font-bold text-violet-400">
                      #{block.blockNumber}
                    </span>
                    <span
                      className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-[10px] uppercase tracking-wider font-bold ${
                        isSpam(block.prediction)
                          ? "bg-red-500/10 border border-red-500/20 text-red-400"
                          : "bg-emerald-500/10 border border-emerald-500/20 text-emerald-400"
                      }`}
                    >
                      <span
                        className={`w-1 h-1 rounded-full ${
                          isSpam(block.prediction)
                            ? "bg-red-400"
                            : "bg-emerald-400"
                        }`}
                      />
                      {block.prediction}
                    </span>
                  </div>
                  <div className="space-y-1.5 text-xs">
                    <div className="flex justify-between">
                      <span className="text-[#64748b]">Time</span>
                      <span className="text-[#94a3b8] font-mono tabular-nums text-right">
                        {formatTimestamp(block.timestamp)}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-[#64748b]">Hash</span>
                      <code className="text-indigo-300 font-mono">
                        {truncateHash(block.emailHash)}
                      </code>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-[#64748b]">Confidence</span>
                      <span className="font-bold text-[#f8fafc]">
                        {Math.round(block.confidence * 100)}%
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Load more controls */}
            {hasMore && (
              <div className="p-4 text-center border-t border-white/[0.06] bg-white/[0.01]">
                <button
                  type="button"
                  onClick={() => setVisibleCount((prev) => prev + 15)}
                  className="inline-flex items-center gap-2 rounded-full px-6 py-2.5 text-xs font-medium text-[#94a3b8] bg-white/[0.03] border border-white/[0.06] hover:bg-white/[0.08] hover:text-white transition-all duration-300 active:scale-95 cursor-pointer"
                >
                  <span>Load More Entries ({blocks.length - visibleCount} remaining)</span>
                  <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M19 9l-7 7-7-7" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}
