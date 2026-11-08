import React, { useState } from 'react';
import { ArrowLeftRight, Trophy } from 'lucide-react';

function ScoreBar({ value }) {
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 h-1.5 bg-white/[0.07] rounded-full overflow-hidden">
        <div className="h-full bg-white/50 rounded-full" style={{ width: `${(value / 5) * 100}%` }} />
      </div>
      <span className="font-mono text-xs text-white/50 w-6 text-right">{value.toFixed(1)}</span>
    </div>
  );
}

function PromoCard({ promo, label, promos, onSelect }) {
  const isWinner = label === 'A';
  return (
    <div className="bg-[#111111] border border-white/[0.07] rounded-xl p-4 space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b border-white/[0.05]">
        <div className="flex items-center gap-2">
          <span className="text-[10px] font-bold tracking-widest text-white/30 font-mono border border-white/[0.1] px-2 py-0.5 rounded">
            VARIANT {label}
          </span>
          <span className="font-mono text-sm font-bold text-white">#{promo.dynamicRank}</span>
        </div>
        <select
          value={promo.promo_id}
          onChange={e => onSelect(e.target.value)}
          className="bg-[#1A1A1A] border border-white/[0.07] rounded-lg px-2 py-1 text-[11px] text-white/60 focus:outline-none focus:border-white/20 max-w-[160px]"
        >
          {promos.map(p => (
            <option key={p.promo_id} value={p.promo_id}>
              #{p.dynamicRank} {p.promo_id} ({p.total_seconds.toFixed(0)}s)
            </option>
          ))}
        </select>
      </div>

      {/* Big score */}
      <div>
        <p className="text-[10px] text-white/25 font-semibold uppercase tracking-widest mb-1">Overall Score</p>
        <p className="text-3xl font-black text-white font-mono">{promo.calculatedOverall.toFixed(3)}</p>
      </div>

      {/* Score bars */}
      <div className="space-y-2.5">
        {[
          { label: 'Hook',         val: promo.scores.hook },
          { label: 'Cliffhanger',  val: promo.scores.cliffhanger },
          { label: 'Standalone',   val: promo.scores.standalone },
        ].map(({ label: l, val }) => (
          <div key={l}>
            <div className="flex justify-between mb-1">
              <span className="text-[10px] text-white/35 font-semibold">{l}</span>
            </div>
            <ScoreBar value={val} />
          </div>
        ))}
      </div>

      {/* Hook / Cliff text */}
      <div className="space-y-2">
        {[
          { key: 'Hook',        text: promo.hook },
          { key: 'Cliffhanger', text: promo.cliffhanger },
        ].map(({ key, text }) => (
          <div key={key} className="p-3 rounded-lg bg-[#0D0D0D] border border-white/[0.05]">
            <span className="text-[9px] font-bold text-white/25 uppercase tracking-widest block mb-1">{key}</span>
            <p className="text-[12px] text-white/60 italic">"{text}"</p>
          </div>
        ))}
      </div>

      <div className="p-3 rounded-lg bg-[#0D0D0D] border border-white/[0.05]">
        <span className="text-[9px] font-bold text-white/25 uppercase tracking-widest block mb-1">Rationale</span>
        <p className="text-[12px] text-white/50">{promo.why_it_works}</p>
      </div>
    </div>
  );
}

export default function CompareView({ promos, initialPromoA, initialPromoB }) {
  const [aId, setAId] = useState(initialPromoA?.promo_id || promos[0]?.promo_id || '');
  const [bId, setBId] = useState(initialPromoB?.promo_id || promos[1]?.promo_id || '');

  const promoA = promos.find(p => p.promo_id === aId) || promos[0];
  const promoB = promos.find(p => p.promo_id === bId) || promos[1];

  if (!promoA || !promoB) return null;

  const winner = promoA.calculatedOverall >= promoB.calculatedOverall ? promoA : promoB;

  return (
    <div className="space-y-5">
      {/* Banner */}
      <div className="bg-[#111111] border border-white/[0.07] rounded-xl p-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="p-1.5 rounded-lg bg-white/[0.05]">
            <ArrowLeftRight className="w-4 h-4 text-white/40" />
          </div>
          <div>
            <p className="text-sm font-semibold text-white">A/B Split Test</p>
            <p className="text-[11px] text-white/30 mt-0.5">Side-by-side candidate comparison</p>
          </div>
        </div>

        <div className="flex items-center gap-2 px-3 py-2 rounded-xl bg-white/[0.04] border border-white/[0.07]">
          <Trophy className="w-3.5 h-3.5 text-white/40" />
          <span className="text-[12px] text-white/50">Winner: </span>
          <span className="text-[12px] font-semibold text-white font-mono">
            #{winner.dynamicRank} · {winner.promo_id}
          </span>
          <span className="font-mono text-[12px] font-bold text-white/70">{winner.calculatedOverall.toFixed(3)}</span>
        </div>
      </div>

      {/* Delta bar */}
      <div className="bg-[#111111] border border-white/[0.07] rounded-xl px-4 py-3 flex items-center gap-4">
        <span className="text-[10px] text-white/25 font-semibold uppercase tracking-widest shrink-0">Score Δ</span>
        <div className="flex-1 relative h-1.5 bg-white/[0.06] rounded-full overflow-hidden">
          <div
            className="absolute inset-y-0 bg-white/40 rounded-full"
            style={{
              left: promoA.calculatedOverall >= promoB.calculatedOverall ? '50%' : `${50 - ((promoB.calculatedOverall - promoA.calculatedOverall) / 5) * 100 / 2}%`,
              width: `${Math.abs(promoA.calculatedOverall - promoB.calculatedOverall) / 5 * 100}%`,
            }}
          />
          <div className="absolute inset-y-0 left-1/2 w-px bg-white/20" />
        </div>
        <span className="font-mono text-xs text-white/50 shrink-0">
          {Math.abs(promoA.calculatedOverall - promoB.calculatedOverall).toFixed(3)}
        </span>
      </div>

      {/* Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <PromoCard promo={promoA} label="A" promos={promos} onSelect={setAId} />
        <PromoCard promo={promoB} label="B" promos={promos} onSelect={setBId} />
      </div>
    </div>
  );
}
