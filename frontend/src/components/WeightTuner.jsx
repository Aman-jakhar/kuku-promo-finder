import React from 'react';
import { Sliders, RotateCcw } from 'lucide-react';

const PRESETS = [
  { label: 'Balanced', h: 0.35, c: 0.35, s: 0.30 },
  { label: 'Hook-Heavy', h: 0.55, c: 0.25, s: 0.20 },
  { label: 'Cliffhanger', h: 0.30, c: 0.50, s: 0.20 },
  { label: 'Cold Audience', h: 0.35, c: 0.20, s: 0.45 },
];

const SLIDERS = [
  { key: 'hook',        label: 'Hook',         sub: 'First 3 seconds' },
  { key: 'cliffhanger', label: 'Cliffhanger',  sub: 'Cut tension' },
  { key: 'standalone',  label: 'Standalone',   sub: 'No-context clarity' },
];

export default function WeightTuner({ weights, setWeights }) {
  const handleSlider = (key, val) => {
    setWeights(prev => ({ ...prev, [key]: parseFloat(val) }));
  };

  const apply = (h, c, s) => setWeights({ hook: h, cliffhanger: c, standalone: s });

  return (
    <div className="bg-[#111111] border border-white/[0.07] rounded-xl p-4 mb-5">
      {/* Header row */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4 pb-3 border-b border-white/[0.06]">
        <div className="flex items-center gap-2.5">
          <div className="p-1.5 rounded-lg bg-white/[0.05]">
            <Sliders className="w-3.5 h-3.5 text-white/50" />
          </div>
          <div>
            <span className="text-sm font-semibold text-white">Scoring Weights</span>
            <span className="text-xs text-white/30 font-mono ml-2">
              {weights.hook.toFixed(2)}H + {weights.cliffhanger.toFixed(2)}C + {weights.standalone.toFixed(2)}S = 1.00
            </span>
          </div>
        </div>

        {/* Presets */}
        <div className="flex items-center gap-1.5 flex-wrap">
          {PRESETS.map((p) => (
            <button
              key={p.label}
              onClick={() => apply(p.h, p.c, p.s)}
              className="text-[11px] font-medium px-2.5 py-1 rounded-lg bg-white/[0.05] hover:bg-white/[0.1] text-white/50 hover:text-white border border-white/[0.07] transition duration-100"
            >
              {p.label}
            </button>
          ))}
          <button
            onClick={() => apply(0.35, 0.35, 0.30)}
            title="Reset"
            className="p-1.5 rounded-lg bg-white/[0.04] hover:bg-white/[0.09] text-white/30 hover:text-white border border-white/[0.06] transition"
          >
            <RotateCcw className="w-3 h-3" />
          </button>
        </div>
      </div>

      {/* Sliders */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {SLIDERS.map(({ key, label, sub }) => {
          const val = weights[key];
          const pct = Math.round(val * 100);
          return (
            <div key={key}>
              <div className="flex justify-between items-center mb-2">
                <div>
                  <span className="text-xs font-semibold text-white/70">{label}</span>
                  <span className="text-[10px] text-white/25 ml-1.5">{sub}</span>
                </div>
                <span className="text-xs font-mono font-bold text-white/80 tabular-nums">{pct}%</span>
              </div>
              {/* Progress track */}
              <div className="relative">
                <div className="h-[3px] bg-[#2A2A2A] rounded-full overflow-hidden mb-2">
                  <div
                    className="h-full bg-white/70 rounded-full transition-all duration-100"
                    style={{ width: `${pct}%` }}
                  />
                </div>
                <input
                  type="range"
                  min="0.10" max="0.80" step="0.05"
                  value={val}
                  onChange={(e) => handleSlider(key, e.target.value)}
                  className="w-full"
                  style={{ marginTop: '-14px', position: 'relative', background: 'transparent' }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
