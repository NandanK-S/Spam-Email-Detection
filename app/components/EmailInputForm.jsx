"use client";

import { useState } from "react";

export default function EmailInputForm({ onSubmit, isLoading }) {
  const [emailText, setEmailText] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!emailText.trim() || isLoading) return;
    onSubmit(emailText);
  };

  return (
    <section className="px-4 animate-fade-up-delay-1">
      {/* Double-bezel outer shell */}
      <div className="max-w-3xl mx-auto p-1.5 md:p-2 rounded-[2rem] bg-white/[0.02] border border-white/[0.06]">
        {/* Inner core */}
        <div className="rounded-[calc(2rem-0.375rem)] bg-white/[0.03] p-6 md:p-8 shadow-[inset_0_1px_1px_rgba(255,255,255,0.06)]">
          {/* Section label */}
          <div className="flex items-center gap-2 mb-5">
            <div className="w-2 h-2 rounded-full bg-violet-500" />
            <span className="text-[11px] uppercase tracking-[0.15em] font-semibold text-[#94a3b8]">
              Email Analysis
            </span>
          </div>

          <form onSubmit={handleSubmit}>
            <textarea
              id="email-input"
              value={emailText}
              onChange={(e) => setEmailText(e.target.value)}
              placeholder="Paste email content here..."
              rows={6}
              maxLength={50000}
              className="w-full resize-none rounded-2xl bg-white/[0.03] border border-white/[0.06] px-5 py-4 text-sm md:text-base text-[#f8fafc] placeholder-[#64748b] focus:outline-none focus:border-violet-500/40 focus:ring-1 focus:ring-violet-500/20 transition-all duration-500 ease-[cubic-bezier(0.32,0.72,0,1)] font-light leading-relaxed"
            />

            <div className="mt-5 flex items-center gap-4">
              {/* Primary CTA — pill with trailing icon */}
              <button
                type="submit"
                disabled={!emailText.trim() || isLoading}
                className="group relative inline-flex items-center gap-3 rounded-full bg-gradient-to-r from-violet-600 to-indigo-600 px-7 py-3.5 text-sm font-semibold text-white shadow-lg shadow-violet-500/20 transition-all duration-500 ease-[cubic-bezier(0.32,0.72,0,1)] hover:shadow-violet-500/30 hover:scale-[1.02] active:scale-[0.98] disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:scale-100"
              >
                {isLoading ? (
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
                    <span>Analyzing...</span>
                  </>
                ) : (
                  <>
                    <span>Check Email</span>
                    {/* Button-in-button trailing icon */}
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
                        <path d="M5 12h14M12 5l7 7-7 7" />
                      </svg>
                    </span>
                  </>
                )}
              </button>

              {isLoading && (
                <span className="text-xs text-[#64748b] animate-pulse">
                  Running ML prediction model...
                </span>
              )}
            </div>
          </form>
        </div>
      </div>
    </section>
  );
}
