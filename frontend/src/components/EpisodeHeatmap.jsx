import React from 'react';
import { BarChart2 } from 'lucide-react';

export default function EpisodeHeatmap({ promos, onSelectEpisode, selectedEpisode }) {
  const episodeStats = Array.from({ length: 50 }, (_, i) => {
    const epNum    = i + 1;
    const epPromos = promos.filter(p => p.segments.some(s => s.episode === epNum));
    const count    = epPromos.length;
    const maxScore = count > 0 ? Math.max(...epPromos.map(p => p.calculatedOverall)) : 0;
    const hasTop10 = epPromos.some(p => p.dynamicRank <= 10);
    return { epNum, count, maxScore, hasTop10 };
  });

  // Map score to opacity level (purely white-based — no rainbow)
  const getCell = (ep) => {
    if (ep.count === 0)   return { bg: 'bg-white/[0.03]',   text: 'text-white/15',  ring: '' };
    if (ep.hasTop10)      return { bg: 'bg-white/[0.18]',   text: 'text-white',     ring: 'ring-1 ring-white/30' };
    if (ep.maxScore >= 4.5) return { bg: 'bg-white/[0.12]', text: 'text-white/80',  ring: '' };
    if (ep.maxScore >= 4.0) return { bg: 'bg-white/[0.08]', text: 'text-white/60',  ring: '' };
    return                       { bg: 'bg-white/[0.05]',   text: 'text-white/40',  ring: '' };
  };

  return (
    <div className="bg-[#111111] border border-white/[0.07] rounded-xl p-4 mb-5">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4 pb-3 border-b border-white/[0.06]">
        <div className="flex items-center gap-2.5">
          <div className="p-1.5 rounded-lg bg-white/[0.05]">
            <BarChart2 className="w-3.5 h-3.5 text-white/50" />
          </div>
          <div>
            <span className="text-sm font-semibold text-white">Episode Heatmap</span>
            <span className="text-[11px] text-white/30 ml-2">Click to filter • brightness = virality score</span>
          </div>
        </div>

        <div className="flex items-center gap-4 text-[11px] flex-wrap">
          <div className="flex items-center gap-1.5">
            <div className="w-3 h-3 rounded bg-white/[0.18] ring-1 ring-white/30" />
            <span className="text-white/35">Top 10</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-3 h-3 rounded bg-white/[0.1]" />
            <span className="text-white/35">High (≥4.5)</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-3 h-3 rounded bg-white/[0.05]" />
            <span className="text-white/35">Standard</span>
          </div>
          {selectedEpisode !== 'all' && (
            <button
              onClick={() => onSelectEpisode('all')}
              className="text-[10px] font-semibold px-2 py-0.5 rounded bg-white/[0.08] text-white/60 hover:text-white hover:bg-white/[0.14] transition"
            >
              Clear filter
            </button>
          )}
        </div>
      </div>

      <div className="grid grid-cols-10 gap-1.5">
        {episodeStats.map(ep => {
          const { bg, text, ring } = getCell(ep);
          const isSelected = selectedEpisode === ep.epNum.toString();
          return (
            <button
              key={ep.epNum}
              onClick={() => onSelectEpisode(isSelected ? 'all' : ep.epNum.toString())}
              title={`Ep ${ep.epNum}: ${ep.count} promos · top ${ep.maxScore.toFixed(2)}`}
              className={`aspect-square rounded-lg border border-white/[0.06] flex flex-col items-center justify-center gap-0 transition-all duration-100 ${bg} ${ring} ${
                isSelected ? 'scale-110 ring-2 ring-white/50 z-10' : 'hover:scale-105 hover:border-white/20'
              }`}
            >
              <span className={`text-[9px] font-bold font-mono leading-none ${text}`}>{ep.epNum}</span>
              {ep.count > 0 && (
                <span className="text-[8px] font-mono text-white/25 leading-none mt-0.5">{ep.count}</span>
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
}
