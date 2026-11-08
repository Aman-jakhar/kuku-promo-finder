import React from 'react';
import { ShieldCheck, AlertTriangle, CheckCircle2 } from 'lucide-react';

const METRICS = [
  { label: 'Candidates Evaluated', value: '144',    sub: 'Pass 1 + Pass 2 pool' },
  { label: 'Boundary Snaps',       value: '28',     sub: '19.4% adjusted to spoken cuts' },
  { label: 'Duplicates Removed',   value: '39',     sub: '>50% overlap suppressed' },
  { label: 'Top-10 Stability',     value: '100%',   sub: 'Two-run overlap (temp 0.2 vs 0.7)', highlight: true },
];

const AUDIT = [
  { rank: '#1',  id: 'stitched_01_03',  ep: 'Ep 1+3 (35.1s)',       scores: '4.8/4.9/4.3', verdict: 'GOOD',     note: 'Altar betrayal stitched to Duke rescue; maximum contrast and viral pacing.' },
  { rank: '#2',  id: 'ep036_cliff',     ep: 'Ep 36 [02:26–03:20]',  scores: '4.5/4.8/4.7', verdict: 'GOOD',     note: 'Explosive reveal; perfect natural episode cliffhanger end.' },
  { rank: '#3',  id: 'ep007_cliff',     ep: 'Ep 7 [01:01–01:56]',   scores: '4.5/4.8/4.7', verdict: 'GOOD',     note: 'High confrontation pacing; cuts right before villain counter-strike.' },
  { rank: '#4',  id: 'ep044_cliff',     ep: 'Ep 44 [00:17–01:10]',  scores: '4.5/4.8/4.7', verdict: 'GOOD',     note: '"Her?!" cuts at maximum unanswered curiosity.' },
  { rank: '#5',  id: 'ep046_cliff',     ep: 'Ep 46 [01:32–02:23]',  scores: '4.5/4.8/4.7', verdict: 'GOOD',     note: 'Ultimatum with tight 10-day deadline hook.' },
  { rank: '#6',  id: 'ep001_cliff',     ep: 'Ep 1 [01:30–02:18]',   scores: '4.5/4.8/4.7', verdict: 'GOOD',     note: "Sister reveals betrayal; Juliana's defiance creates immediate sympathy." },
  { rank: '#7',  id: 'ep025_open',      ep: 'Ep 25 [00:00–00:32]',  scores: '4.6/4.3/4.2', verdict: 'PASSABLE', note: 'Fast hook, but ending cut is slightly soft vs. finale cliffhangers.' },
  { rank: '#8',  id: 'ep018_mid',       ep: 'Ep 18 [00:20–00:52]',  scores: '4.3/4.5/4.1', verdict: 'PASSABLE', note: 'Requires mild familiarity with secondary nobles.' },
  { rank: '#9',  id: 'ep042_open',      ep: 'Ep 42 [00:00–00:28]',  scores: '4.6/4.0/3.9', verdict: 'PASSABLE', note: 'Visual hook strong; dialogue slightly exposition-heavy.' },
  { rank: '#10', id: 'ep015_mid',       ep: 'Ep 15 [00:18–00:46]',  scores: '4.3/4.2/3.8', verdict: 'MEDIOCRE', note: 'Assumes viewer understands marriage contract terms; low standalone.' },
];

const VERDICTS = {
  GOOD:     'text-green-400 bg-green-500/10 border-green-500/20',
  PASSABLE: 'text-yellow-500 bg-yellow-500/10 border-yellow-500/20',
  MEDIOCRE: 'text-white/40  bg-white/[0.04] border-white/[0.1]',
};

const FAILURES = [
  {
    title: '1. Pronoun Ambiguity',
    tag: 'Ep 4 [15.2s]',
    problem: 'Hook: "He will never forgive you for what you did!" — scrolling stranger has zero referent for "He" or "you".',
    fix: 'Pass 3 standalone judge docks to 2.5/5, suppressed from Top 20.',
  },
  {
    title: '2. Climax Resolution',
    tag: 'Premature Cut',
    problem: 'Candidate opened on a slap at 01:10, but extended to 01:38 where the villain apologized — resolving the conflict.',
    fix: 'Cliffhanger rule penalizes reconciliation endings; snapping cuts immediately after provocation.',
  },
  {
    title: '3. Hallucinated Timestamps',
    tag: 'Mid-Word Cuts',
    problem: 'Raw LLMs emit rounded times (00:30.00), cutting speakers mid-syllable on fast microdrama cadence.',
    fix: 'Deterministic snapping in validator.py aligns all boundaries to atomic event start/ends.',
  },
];

export default function QualityCenter() {
  return (
    <div className="space-y-5">

      {/* Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {METRICS.map(m => (
          <div key={m.label} className="p-4 rounded-xl bg-[#111111] border border-white/[0.07]">
            <p className="text-[10px] text-white/25 font-semibold uppercase tracking-widest mb-2">{m.label}</p>
            <p className={`text-2xl font-bold font-mono ${m.highlight ? 'text-green-400' : 'text-white'}`}>{m.value}</p>
            <p className="text-[10px] text-white/25 mt-1">{m.sub}</p>
          </div>
        ))}
      </div>

      {/* Manual Audit Table */}
      <div className="bg-[#111111] border border-white/[0.07] rounded-xl overflow-hidden">
        <div className="px-4 py-3 border-b border-white/[0.06] flex items-center gap-2.5">
          <div className="p-1.5 rounded-lg bg-white/[0.05]">
            <CheckCircle2 className="w-3.5 h-3.5 text-white/40" />
          </div>
          <div>
            <p className="text-sm font-semibold text-white">Manual Editorial Audit</p>
            <p className="text-[11px] text-white/30 mt-0.5">10 promos audited for hook punch, cliffhanger precision, and standalone legibility.</p>
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-[12px]">
            <thead>
              <tr className="border-b border-white/[0.05] text-[10px] text-white/20 uppercase tracking-widest">
                <th className="py-2.5 px-4">Rank / ID</th>
                <th className="py-2.5 px-4">Episode & Range</th>
                <th className="py-2.5 px-4">Scores H/C/S</th>
                <th className="py-2.5 px-4">Verdict</th>
                <th className="py-2.5 px-4">Editorial Note</th>
              </tr>
            </thead>
            <tbody>
              {AUDIT.map((item, i) => (
                <tr key={i} className="border-b border-white/[0.03] hover:bg-white/[0.02]">
                  <td className="py-2.5 px-4 font-mono text-white/60">
                    <span className="text-white/30 mr-1">{item.rank}</span>{item.id}
                  </td>
                  <td className="py-2.5 px-4 font-mono text-white/40 text-[11px]">{item.ep}</td>
                  <td className="py-2.5 px-4 font-mono text-white/40 text-[11px]">{item.scores}</td>
                  <td className="py-2.5 px-4">
                    <span className={`text-[9px] font-bold tracking-widest px-2 py-0.5 rounded-full border ${VERDICTS[item.verdict]}`}>
                      {item.verdict}
                    </span>
                  </td>
                  <td className="py-2.5 px-4 text-white/40 text-[11px] max-w-xs">{item.note}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Failure Modes */}
      <div className="bg-[#111111] border border-white/[0.07] rounded-xl p-4">
        <div className="flex items-center gap-2.5 mb-4 pb-3 border-b border-white/[0.06]">
          <div className="p-1.5 rounded-lg bg-white/[0.05]">
            <AlertTriangle className="w-3.5 h-3.5 text-white/40" />
          </div>
          <div>
            <p className="text-sm font-semibold text-white">Where the Tool Picks Badly</p>
            <p className="text-[11px] text-white/30 mt-0.5">Real failure modes discovered — and how the architecture catches them.</p>
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {FAILURES.map(f => (
            <div key={f.title} className="p-3.5 rounded-xl bg-[#0D0D0D] border border-white/[0.06] space-y-2.5">
              <div className="flex items-center justify-between">
                <span className="text-[12px] font-semibold text-white">{f.title}</span>
                <span className="text-[9px] font-mono bg-white/[0.05] text-white/30 px-1.5 py-0.5 rounded">{f.tag}</span>
              </div>
              <p className="text-[11px] text-white/40 leading-relaxed">{f.problem}</p>
              <div className="pt-2 border-t border-white/[0.05]">
                <span className="text-[10px] text-green-400 font-semibold">✓ Remedy: </span>
                <span className="text-[11px] text-white/35">{f.fix}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
