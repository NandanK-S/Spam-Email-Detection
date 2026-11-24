"use client";

import { useState } from "react";
import { verifyChain } from "../lib/api";

export default function ChainVerifyPanel() {
  const [verifyResult, setVerifyResult] = useState(null);
  const [errorMsg, setErrorMsg] = useState(null);
  const [isVerifying, setIsVerifying] = useState(false);
  const [simulateTamper, setSimulateTamper] = useState(false);

  const handleVerify = async () => {
    setIsVerifying(true);
    setVerifyResult(null);
    setErrorMsg(null);

    try {
      const result = await verifyChain(simulateTamper);
      setVerifyResult(result);
    } catch (err) {
      setErrorMsg(err.message || "Failed to connect to backend server");
    } finally {
      setIsVerifying(false);
    }
  };

  return (
    <section className="px-4 mt-16 md:mt-24 animate-fade-up-delay-3">
      <div className="max-w-3xl mx-auto">
        {/* Section header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-2 rounded-full px-4 py-1.5 text-[11px] uppercase tracking-[0.2em] font-medium bg-white/[0.04] border border-white/[0.06] text-[#94a3b8] mb-4">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
            Integrity Check
          </div>
          <h2 className="text-2xl md:text-3xl font-bold tracking-tight">
            <span className="bg-gradient-to-r from-white to-white/60 bg-clip-text text-transparent">
              Chain Verification
            </span>
          </h2>
        </div>

        {/* Double-bezel card */}
        <div className="p-1.5 md:p-2 rounded-[2rem] bg-white/[0.02] border border-white/[0.06]">
          <div className="rounded-[calc(2rem-0.375rem)] bg-white/[0.03] p-6 md:p-8 shadow-[inset_0_1px_1px_rgba(255,255,255,0.06)]">
            <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4">
              {/* Verify button */}
              <button
                onClick={handleVerify}
                disabled={isVerifying}
                className="group inline-flex items-center gap-3 rounded-full bg-gradient-to-r from-emerald-600 to-emerald-500 px-7 py-3.5 text-sm font-semibold text-white shadow-lg shadow-emerald-500/15 transition-all duration-500 ease-[cubic-bezier(0.32,0.72,0,1)] hover:shadow-emerald-500/25 hover:scale-[1.02] active:scale-[0.98] disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:scale-100"
              >
                {isVerifying ? (
                  <>
                    <svg
                      className="animate-spin-slow w-4 h-4"
                      viewBox="0 0 24 24"
                      fill="none"
                    >
                      <circle
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        strokeWidth="2.5"
                        strokeLinecap="round"
                        className="opacity-20"
                      />
                      <path
                        d="M12 2a10 10 0 0 1 10 10"
                        stroke="currentColor"
                        strokeWidth="2.5"
                        strokeLinecap="round"
                      />
                    </svg>
                    <span>Verifying...</span>
                  </>
                ) : (
                  <>
                    <span>Verify Chain Integrity</span>
                    <span className="inline-flex items-center justify-center w-7 h-7 rounded-full bg-white/10 transition-transform duration-500 ease-[cubic-bezier(0.32,0.72,0,1)] group-hover:translate-x-0.5 group-hover:-translate-y-px group-hover:scale-105">
                      <svg
                        className="w-3.5 h-3.5"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      >
                        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
                      </svg>
                    </span>
                  </>
                )}
              </button>

              {/* Simulate Tampering toggle */}
              <button
                onClick={() => setSimulateTamper((prev) => !prev)}
                className={`inline-flex items-center gap-2.5 rounded-full px-5 py-2.5 text-xs font-medium border transition-all duration-500 ease-[cubic-bezier(0.32,0.72,0,1)] active:scale-[0.98] ${
                  simulateTamper
                    ? "bg-red-500/10 border-red-500/25 text-red-400"
                    : "bg-white/[0.03] border-white/[0.06] text-[#94a3b8] hover:border-white/[0.12] hover:text-[#f8fafc]"
                }`}
              >
                {/* Toggle pill */}
                <span
                  className={`relative inline-flex h-5 w-9 rounded-full transition-colors duration-300 ${
                    simulateTamper ? "bg-red-500/30" : "bg-white/[0.08]"
                  }`}
                >
                  <span
                    className={`absolute top-0.5 left-0.5 h-4 w-4 rounded-full transition-all duration-300 ease-[cubic-bezier(0.32,0.72,0,1)] ${
                      simulateTamper
                        ? "translate-x-4 bg-red-400"
                        : "translate-x-0 bg-[#64748b]"
                    }`}
                  />
                </span>
                Simulate Tampering
              </button>
            </div>

            {/* Verification result */}
            {verifyResult && (
              <div
                className={`mt-6 rounded-2xl px-6 py-4 border animate-fade-up ${
                  verifyResult.valid
                    ? "bg-emerald-500/8 border-emerald-500/20"
                    : "bg-red-500/8 border-red-500/20"
                }`}
              >
                <div className="flex items-center gap-3">
                  <span className="text-xl">
                    {verifyResult.valid ? "✅" : "❌"}
                  </span>
                  <div>
                    <div
                      className={`text-sm font-bold ${
                        verifyResult.valid
                          ? "text-emerald-400"
                          : "text-red-400"
                      }`}
                    >
                      {verifyResult.valid
                        ? "Chain Verified — No Tampering Detected"
                        : `Tampering Detected in Block #${verifyResult.tamperedBlock ?? verifyResult.tampered_block}`}
                    </div>
                    <div className="text-xs text-[#64748b] mt-1">
                      {verifyResult.valid
                        ? "All block hashes match their predecessors. Integrity confirmed."
                        : "Hash mismatch found. The chain has been compromised at the indicated block."}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Backend connection error */}
            {errorMsg && (
              <div className="mt-6 rounded-2xl px-6 py-4 border bg-amber-500/10 border-amber-500/20 animate-fade-up">
                <div className="flex items-center gap-3">
                  <span className="text-xl">⚠️</span>
                  <div>
                    <div className="text-sm font-bold text-amber-400">
                      Cannot connect to Python backend
                    </div>
                    <div className="text-xs text-[#94a3b8] mt-1">
                      Please start the FastAPI server:{" "}
                      <code className="bg-white/10 px-1.5 py-0.5 rounded text-amber-300 font-mono text-[11px]">
                        uvicorn backend:app --reload --port 8000
                      </code>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}
