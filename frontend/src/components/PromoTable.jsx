import React, { useState } from 'react';
import { Search, SlidersHorizontal, Play, Copy, Check, ArrowLeftRight, Layers } from 'lucide-react';

function ScoreDot({ score }) {
  const pct = (score / 5) * 100;
  return (
    <div className="flex items-center gap-1.5">
      <div className="w-16 h-1 bg-white/[0.08] rounded-full overflow-hidden">
        <div className="h-full bg-white/50 rounded-full" style={{ width: `${pct}%` }} />
      </div>
      <span className="font-mono text-[11px] text-white/50 tabular-nums w-5">{score.toFixed(1)}</span>
    </div>
  );
}

export default function PromoTable({
  promos,
  onSelectPromo,
  selectedPromoId,
  onComparePromo,
  filterEpisode,
  setFilterEpisode
}) {
  const [search, setSearch]     = useState('');
  const [copiedId, setCopiedId] = useState(null);

  const allEpisodes = Array.from(
    new Set(promos.flatMap(p => p.segments.map(s => s.episode)))
  ).sort((a, b) => a - b);

  const filtered = promos.filter(p => {
    const q = search.toLowerCase();
    const matchSearch =
      p.promo_id.toLowerCase().includes(q) ||
      p.hook.toLowerCase().includes(q) ||
      p.cliffhanger.toLowerCase().includes(q) ||
      p.why_it_works.toLowerCase().includes(q);
    const matchEp =
      filterEpisode === 'all' || p.segments.some(s => s.episode === parseInt(filterEpisode));
    return matchSearch && matchEp;
  });

  const handleCopy = (p, e) => {
    e.stopPropagation();
    const text = p.segments.map(s => `Ep${s.episode} [${s.start}–${s.end}]`).join(' + ');
    navigator.clipboard.writeText(text);
    setCopiedId(p.promo_id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <div className="bg-[#111111] border border-white/[0.07] rounded-xl overflow-hidden">

      {/* Toolbar */}
      <div className="px-4 py-3 border-b border-white/[0.06] flex flex-col sm:flex-row gap-3 items-start sm:items-center justify-between">
        <div className="flex items-center gap-2 w-full sm:w-auto">
          {/* Search */}
          <div className="relative flex-1 sm:w-64">
            <Search className="w-3.5 h-3.5 text-white/25 absolute left-2.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search hook, cliffhanger, ID…"
              value={search}
              onChange={e => setSearch(e.target.value)}
              className="w-full pl-8 pr-3 py-1.5 bg-[#1A1A1A] border border-white/[0.07] rounded-lg text-[12px] text-white/80 placeholder-white/20 focus:outline-none focus:border-white/20 transition"
            />
          </div>
          {/* Episode filter */}
          <div className="flex items-center gap-1.5">
            <SlidersHorizontal className="w-3.5 h-3.5 text-white/25" />
            <select
              value={filterEpisode}
              onChange={e => setFilterEpisode(e.target.value)}
              className="bg-[#1A1A1A] border border-white/[0.07] rounded-lg px-2 py-1.5 text-[12px] text-white/70 focus:outline-none focus:border-white/20 transition"
            >
              <option value="all">All eps</option>
              {allEpisodes.map(ep => (
                <option key={ep} value={ep.toString()}>Ep {ep}</option>
              ))}
            </select>
          </div>
        </div>
        <div className="text-[11px] text-white/25">
          <span className="text-white/60 font-semibold">{filtered.length}</span> / {promos.length} promos
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-[12px]">
          <thead>
            <tr className="border-b border-white/[0.05] text-[10px] text-white/25 uppercase tracking-widest font-semibold">
              <th className="py-2.5 px-4">#</th>
              <th className="py-2.5 px-4">Promo</th>
              <th className="py-2.5 px-4">Segments</th>
              <th className="py-2.5 px-3 text-right">Dur</th>
              <th className="py-2.5 px-4">Hook</th>
              <th className="py-2.5 px-4">Cliff</th>
              <th className="py-2.5 px-4">Alone</th>
              <th className="py-2.5 px-4 text-right">Score</th>
              <th className="py-2.5 px-4"></th>
            </tr>
          </thead>
          <tbody>
            {filtered.map(p => {
              const isSelected = p.promo_id === selectedPromoId;
              const isMulti    = p.segments.length > 1;
              const isTop3     = p.dynamicRank <= 3;
              const isTop10    = p.dynamicRank <= 10;

              return (
                <tr
                  key={p.promo_id}
                  onClick={() => onSelectPromo(p)}
                  className={`border-b border-white/[0.04] cursor-pointer transition-colors duration-100 group ${
                    isSelected ? 'bg-white/[0.05]' : 'hover:bg-white/[0.025]'
                  }`}
                >
                  {/* Rank */}
                  <td className="py-3 px-4">
                    <span className={`inline-flex items-center justify-center w-6 h-6 rounded-md text-[11px] font-bold font-mono ${
                      isTop3  ? 'bg-white text-black'
                      : isTop10 ? 'bg-white/[0.1] text-white/80'
                      : 'text-white/25'
                    }`}>
                      {p.dynamicRank}
                    </span>
                  </td>

                  {/* Promo ID + rationale */}
                  <td className="py-3 px-4 max-w-[220px]">
                    <div className="flex items-center gap-1.5 mb-0.5">
                      <span className="font-mono font-semibold text-white/80 text-[12px]">{p.promo_id}</span>
                      {isMulti && (
                        <span className="text-[9px] font-bold px-1.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">
                          STITCHED
                        </span>
                      )}
                    </div>
                    <p className="text-[11px] text-white/30 truncate" title={p.why_it_works}>
                      {p.why_it_works}
                    </p>
                  </td>

                  {/* Segments */}
                  <td className="py-3 px-4 font-mono">
                    <div className="flex items-start gap-2">
                      <div className="space-y-0.5">
                        {p.segments.map((seg, i) => (
                          <div key={i} className="text-[11px] text-white/40 flex items-center gap-1">
                            <span className="text-white/20">Ep{seg.episode}</span>
                            <span className="text-white/60">{seg.start}</span>
                            <span className="text-white/20">→</span>
                            <span className="text-white/60">{seg.end}</span>
                          </div>
                        ))}
                      </div>
                      <button
                        onClick={e => handleCopy(p, e)}
                        className="p-1 rounded text-white/20 hover:text-white hover:bg-white/[0.08] transition opacity-0 group-hover:opacity-100"
                        title="Copy timestamps"
                      >
                        {copiedId === p.promo_id
                          ? <Check className="w-3.5 h-3.5 text-green-400" />
                          : <Copy className="w-3.5 h-3.5" />
                        }
                      </button>
                    </div>
                  </td>

                  {/* Duration */}
                  <td className="py-3 px-3 text-right font-mono text-[11px] text-white/40">
                    {p.total_seconds.toFixed(1)}s
                  </td>

                  {/* Score bars */}
                  <td className="py-3 px-4"><ScoreDot score={p.scores.hook} /></td>
                  <td className="py-3 px-4"><ScoreDot score={p.scores.cliffhanger} /></td>
                  <td className="py-3 px-4"><ScoreDot score={p.scores.standalone} /></td>

                  {/* Overall */}
                  <td className="py-3 px-4 text-right">
                    <span className={`font-mono font-bold text-[13px] ${
                      isTop3 ? 'text-white' : isTop10 ? 'text-white/70' : 'text-white/40'
                    }`}>
                      {p.calculatedOverall.toFixed(3)}
                    </span>
                  </td>

                  {/* Actions */}
                  <td className="py-3 px-4">
                    <div className="flex items-center gap-1.5 opacity-0 group-hover:opacity-100 transition">
                      <button
                        onClick={e => { e.stopPropagation(); onSelectPromo(p); }}
                        className="flex items-center gap-1 px-2 py-1 rounded-lg bg-white text-black text-[11px] font-semibold hover:bg-white/90 transition"
                      >
                        <Play className="w-2.5 h-2.5 fill-current" />
                        Preview
                      </button>
                      <button
                        onClick={e => { e.stopPropagation(); onComparePromo(p); }}
                        className="p-1.5 rounded-lg bg-white/[0.06] text-white/40 hover:text-white hover:bg-white/[0.1] transition border border-white/[0.06]"
                        title="A/B Compare"
                      >
                        <ArrowLeftRight className="w-3 h-3" />
                      </button>
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {filtered.length === 0 && (
        <div className="py-16 text-center text-white/20 text-sm">
          No promos match your filter.
        </div>
      )}
    </div>
  );
}
