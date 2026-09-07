"use client";

export default function FeatureBreakdownTable({ features }) {
  if (!features) return null;

  const rows = [
    {
      label: "Character Count",
      value: features.charCount?.toLocaleString() ?? 0,
      icon: "Aa",
    },
    {
      label: "Word Count",
      value: features.wordCount?.toLocaleString() ?? 0,
      icon: "W",
    },
    {
      label: "Link / URL Count",
      value: features.linkCount ?? 0,
      icon: "🔗",
    },
    {
      label: "Capital Letter Ratio",
      value: `${features.capitalRatio ?? 0}%`,
      icon: "AB",
    },
    {
      label: "Punctuation Count",
      value: features.punctuationCount ?? 0,
      icon: "!?",
    },
    {
      label: "Digit Count",
      value: features.digitCount ?? 0,
      icon: "#",
    },
    {
      label: "Special Characters",
      value: features.specialCharCount ?? 0,
      icon: "@",
    },
    {
      label: "Avg Word Length",
      value: features.avgWordLength ?? 0,
      icon: "μ",
    },
    {
      label: "Exclamation Count",
      value: features.exclamationCount ?? 0,
      icon: "!!",
    },
    {
      label: "Urgency Keywords",
      value: features.urgencyWordCount ?? 0,
      icon: "⚡",
    },
    {
      label: "Suspicious / Sensitive Terms",
      value: features.sensitiveWordCount ?? 0,
      icon: "🛡️",
    },
  ];

  return (
    <section className="px-4 mt-6 animate-fade-up-delay-1">
      <div className="max-w-3xl mx-auto p-1.5 md:p-2 rounded-[2rem] bg-white/[0.02] border border-white/[0.06]">
        <div className="rounded-[calc(2rem-0.375rem)] bg-white/[0.03] p-6 md:p-8 shadow-[inset_0_1px_1px_rgba(255,255,255,0.06)]">
          {/* Section label */}
          <div className="flex items-center gap-2 mb-5">
            <div className="w-2 h-2 rounded-full bg-indigo-500" />
            <span className="text-[11px] uppercase tracking-[0.15em] font-semibold text-[#94a3b8]">
              Structural Features Extracted
            </span>
          </div>

          {/* Feature grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {rows.map((row, i) => (
              <div
                key={row.label}
                className="group flex items-center gap-4 rounded-xl bg-white/[0.02] border border-white/[0.04] px-4 py-3.5 transition-all duration-500 ease-[cubic-bezier(0.32,0.72,0,1)] hover:bg-white/[0.04] hover:border-white/[0.08]"
                style={{ animationDelay: `${i * 60}ms` }}
              >
                {/* Icon badge */}
                <div className="flex-shrink-0 w-9 h-9 rounded-lg bg-white/[0.04] border border-white/[0.06] flex items-center justify-center text-xs font-bold text-[#94a3b8] transition-colors duration-300 group-hover:text-violet-400 group-hover:border-violet-500/20">
                  {row.icon}
                </div>
                <div className="min-w-0">
                  <div className="text-[11px] text-[#64748b] uppercase tracking-wider font-medium">
                    {row.label}
                  </div>
                  <div className="text-lg font-bold text-[#f8fafc] tabular-nums mt-0.5">
                    {row.value}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
