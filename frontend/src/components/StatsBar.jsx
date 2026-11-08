import React from 'react';
import { Target, Zap, Clock, ShieldCheck, DollarSign } from 'lucide-react';

export default function StatsBar({ stats }) {
  const cards = [
    {
      label: 'Accepted Promos',
      value: stats.totalPromos,
      sub: '50 episodes',
      icon: Target,
      tag: 'All ready',
      tagClass: 'text-green-400 bg-green-500/10 border-green-500/20',
    },
    {
      label: 'Top Score',
      value: stats.topScore.toFixed(3),
      sub: '0–5 weighted scale',
      icon: Zap,
      tag: 'Best',
      tagClass: 'text-blue-400 bg-blue-500/10 border-blue-500/20',
    },
    {
      label: 'Avg Duration',
      value: `${stats.avgDuration.toFixed(1)}s`,
      sub: '20–60s window',
      icon: Clock,
      tag: 'Compliant',
      tagClass: 'text-white/40 bg-white/[0.04] border-white/10',
    },
    {
      label: 'Boundary Snap',
      value: '100%',
      sub: '28 micro-adjustments',
      icon: ShieldCheck,
      tag: 'Zero hallucinations',
      tagClass: 'text-green-400 bg-green-500/10 border-green-500/20',
    },
    {
      label: 'Est. Cost / Show',
      value: '$0.014',
      sub: '100 shows ≈ $1.40',
      icon: DollarSign,
      tag: 'Flash tier',
      tagClass: 'text-white/30 bg-white/[0.03] border-white/[0.07]',
    },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mb-5">
      {cards.map((c, idx) => {
        const Icon = c.icon;
        return (
          <div
            key={idx}
            className="p-4 rounded-xl bg-[#111111] border border-white/[0.07] hover:border-white/[0.14] transition-all duration-150 group"
          >
            <div className="flex items-start justify-between gap-2 mb-3">
              <div className="p-1.5 rounded-lg bg-white/[0.05] group-hover:bg-white/[0.08] transition">
                <Icon className="w-3.5 h-3.5 text-white/50" />
              </div>
              <span className={`text-[9px] font-semibold px-1.5 py-0.5 rounded-full border tracking-wide ${c.tagClass}`}>
                {c.tag}
              </span>
            </div>
            <p className="text-xl font-bold text-white tracking-tight font-sans mb-0.5">{c.value}</p>
            <p className="text-[11px] text-white/30 font-medium leading-tight">{c.label}</p>
            <p className="text-[10px] text-white/20 mt-0.5">{c.sub}</p>
          </div>
        );
      })}
    </div>
  );
}
