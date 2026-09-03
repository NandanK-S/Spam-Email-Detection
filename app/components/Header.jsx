"use client";

export default function Header() {
  return (
    <header className="pt-16 pb-12 md:pt-24 md:pb-16 px-4 text-center animate-fade-up">
      {/* Eyebrow badge */}
      <div className="inline-flex items-center gap-2 rounded-full px-4 py-1.5 text-[11px] uppercase tracking-[0.2em] font-medium bg-white/[0.04] border border-white/[0.06] text-[#94a3b8] mb-6 backdrop-blur-sm">
        <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
        Machine Learning + Blockchain Security
      </div>

      {/* Main title */}
      <h1 className="text-4xl md:text-6xl lg:text-7xl font-extrabold tracking-tight leading-[1.05] mb-4">
        <span className="bg-gradient-to-br from-white via-white/90 to-white/50 bg-clip-text text-transparent">
          AI-Based Spam
        </span>
        <br />
        <span className="bg-gradient-to-r from-violet-400 via-indigo-400 to-emerald-400 bg-clip-text text-transparent">
          Email Detection
        </span>
      </h1>

      {/* Subtitle */}
      <p className="text-base md:text-lg text-[#94a3b8] max-w-xl mx-auto font-light leading-relaxed mt-4">
        Blockchain-Based Tamper-Proof Logging
        <span className="inline-block ml-2 opacity-60">📧🔗</span>
      </p>

      {/* Decorative divider */}
      <div className="mt-10 flex items-center justify-center gap-3">
        <div className="h-px w-16 bg-gradient-to-r from-transparent to-white/10" />
        <div className="w-1 h-1 rounded-full bg-violet-500/50" />
        <div className="h-px w-16 bg-gradient-to-l from-transparent to-white/10" />
      </div>
    </header>
  );
}
