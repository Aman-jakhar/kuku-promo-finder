import React, { useState, useEffect } from 'react';
import { Play, Pause, RotateCcw, Heart, MessageCircle, Share2, Music, Copy, Check, ChevronRight } from 'lucide-react';

export default function MobileSimulator({ promo, transcriptParts }) {
  const [isPlaying, setIsPlaying]       = useState(false);
  const [currentSec, setCurrentSec]     = useState(0);
  const [speed, setSpeed]               = useState(1.0);
  const [copiedEdl, setCopiedEdl]       = useState(false);

  const totalDuration = promo?.total_seconds || 30;

  useEffect(() => {
    setCurrentSec(0);
    setIsPlaying(false);
  }, [promo?.promo_id]);

  useEffect(() => {
    if (!isPlaying) return;
    const iv = setInterval(() => {
      setCurrentSec(prev => {
        const next = prev + 0.5 * speed;
        if (next >= totalDuration) { setIsPlaying(false); return 0; }
        return next;
      });
    }, 500);
    return () => clearInterval(iv);
  }, [isPlaying, totalDuration, speed]);

  if (!promo) {
    return (
      <div className="py-24 text-center text-white/20 text-sm bg-[#111111] rounded-xl border border-white/[0.07]">
        Select a promo from Catalog to open the Mobile Studio.
      </div>
    );
  }

  const isHook  = currentSec <= 3.0;
  const isCliff = currentSec >= totalDuration - 4.0;
  const pct     = Math.min((currentSec / totalDuration) * 100, 100);

  const transcript = transcriptParts?.length
    ? transcriptParts.map(t => t.text).join('\n\n')
    : promo.why_it_works;

  const copyEdl = () => {
    const txt = `TITLE: ${promo.promo_id}\n` +
      promo.segments.map((s, i) => `00${i+1} EP${s.episode} V C [${s.start} -> ${s.end}]`).join('\n');
    navigator.clipboard.writeText(txt);
    setCopiedEdl(true);
    setTimeout(() => setCopiedEdl(false), 2000);
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">

      {/* ── Phone mockup ── */}
      <div className="lg:col-span-5 flex flex-col items-center gap-4">
        {/* Device frame — neutral black, clean titanium edges */}
        <div className="w-[300px] h-[600px] bg-[#0A0A0A] rounded-[48px] relative flex flex-col overflow-hidden"
          style={{
            boxShadow: '0 0 0 1.5px rgba(255,255,255,0.14), 0 0 0 4px rgba(255,255,255,0.04), 0 32px 64px rgba(0,0,0,0.8)',
          }}
        >
          {/* Dynamic Island */}
          <div className="absolute top-4 left-1/2 -translate-x-1/2 w-[88px] h-[26px] bg-black rounded-full z-30 flex items-center justify-end px-3 gap-1.5">
            <div className="w-1.5 h-1.5 rounded-full bg-green-500/60" style={{ animation: isPlaying ? 'pulse-dot 1.2s ease-in-out infinite' : 'none' }} />
            <div className="w-2 h-2 rounded-full bg-[#1A1A1A] border border-white/10" />
          </div>

          {/* Screen content */}
          <div className="flex-1 bg-gradient-to-b from-[#0A0A0A] via-[#0D0D0D] to-[#000] flex flex-col pt-14 pb-0 relative">

            {/* Top bar */}
            <div className="flex justify-between px-5 items-center text-[10px] text-white/40 font-mono">
              <span className="font-semibold text-white/60 flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-white/40" />
                KUKU
              </span>
              <span className="bg-white/[0.07] px-2 py-0.5 rounded-full">
                Ep {promo.segments.map(s => s.episode).join('+')}
              </span>
            </div>

            {/* Phase badge + text */}
            <div className="flex-1 flex flex-col items-center justify-center px-5 gap-3">
              <span className={`text-[9px] font-bold uppercase tracking-widest px-2.5 py-1 rounded-full border ${
                isHook  ? 'text-orange-400 bg-orange-500/10 border-orange-500/20'
                : isCliff ? 'text-violet-400 bg-violet-500/10 border-violet-500/20'
                : 'text-white/30 bg-white/[0.04] border-white/[0.08]'
              }`}>
                {isHook ? 'Opening Hook' : isCliff ? 'Cliffhanger' : 'Body'}
              </span>

              <div className="bg-black/70 backdrop-blur-xl p-4 rounded-2xl border border-white/[0.08] w-full text-left">
                <p className="text-[9px] text-white/30 font-semibold uppercase tracking-widest mb-1.5">
                  {isHook ? 'First 3s' : isCliff ? 'Unresolved cut' : 'Scene context'}
                </p>
                <p className="text-[13px] font-semibold text-white leading-snug">
                  {isHook ? promo.hook : isCliff ? promo.cliffhanger : promo.why_it_works}
                </p>
              </div>
            </div>

            {/* Right-rail social buttons */}
            <div className="absolute right-4 bottom-24 flex flex-col items-center gap-4">
              {[
                { icon: Heart,         label: '48k', filled: true },
                { icon: MessageCircle, label: '1.8k' },
                { icon: Share2,        label: 'Share' },
              ].map(({ icon: Icon, label, filled }) => (
                <div key={label} className="flex flex-col items-center gap-0.5">
                  <div className="w-9 h-9 rounded-full bg-black/60 border border-white/[0.1] flex items-center justify-center cursor-pointer hover:bg-white/10 transition">
                    <Icon className={`w-4 h-4 ${filled ? 'fill-current text-white' : 'text-white/60'}`} />
                  </div>
                  <span className="text-[9px] text-white/40 font-semibold">{label}</span>
                </div>
              ))}
              <div className={`w-8 h-8 rounded-full bg-[#111] border border-white/15 flex items-center justify-center ${isPlaying ? 'animate-spin-slow' : ''}`}>
                <Music className="w-3.5 h-3.5 text-white/40" />
              </div>
            </div>

            {/* Bottom caption */}
            <div className="px-5 pb-3 pr-16">
              <p className="text-[11px] font-bold text-white">@kuku.microdrama</p>
              <p className="text-[10px] text-white/40 line-clamp-1 mt-0.5">{promo.why_it_works}</p>
            </div>
          </div>

          {/* Timeline scrubber */}
          <div className="bg-black px-4 pt-2.5 pb-4 rounded-b-[48px] border-t border-white/[0.06]">
            {/* Track */}
            <div className="relative h-[3px] bg-white/[0.1] rounded-full mb-3 overflow-hidden">
              {/* Hook zone */}
              <div className="absolute left-0 inset-y-0 bg-orange-500/60 rounded-full"
                style={{ width: `${(3 / totalDuration) * 100}%` }} />
              {/* Cliffhanger zone */}
              <div className="absolute right-0 inset-y-0 bg-violet-500/50 rounded-full"
                style={{ width: `${(4 / totalDuration) * 100}%` }} />
              {/* Progress */}
              <div className="absolute left-0 inset-y-0 bg-white/60 rounded-full transition-all duration-100"
                style={{ width: `${pct}%` }} />
            </div>

            {/* Controls */}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setIsPlaying(p => !p)}
                  className="w-7 h-7 rounded-full bg-white flex items-center justify-center hover:bg-white/90 transition"
                >
                  {isPlaying
                    ? <Pause className="w-3 h-3 fill-black text-black" />
                    : <Play  className="w-3 h-3 fill-black text-black ml-0.5" />
                  }
                </button>
                <button
                  onClick={() => { setIsPlaying(false); setCurrentSec(0); }}
                  className="w-6 h-6 rounded-full bg-white/[0.07] flex items-center justify-center hover:bg-white/15 transition"
                >
                  <RotateCcw className="w-2.5 h-2.5 text-white/60" />
                </button>
                <button
                  onClick={() => setSpeed(s => s === 1 ? 1.5 : s === 1.5 ? 2 : 1)}
                  className="px-2 py-0.5 rounded bg-white/[0.07] text-[9px] font-mono font-bold text-white/50 hover:text-white transition"
                >
                  {speed}×
                </button>
              </div>
              <span className="font-mono text-[10px] text-white/30 tabular-nums">
                {currentSec.toFixed(1)} / {totalDuration.toFixed(1)}s
              </span>
            </div>
          </div>
        </div>

        {/* Jump buttons */}
        <div className="flex gap-2">
          <button
            onClick={() => { setCurrentSec(0); setIsPlaying(true); }}
            className="text-[11px] font-medium px-3 py-1.5 rounded-lg bg-white/[0.06] text-white/50 hover:text-white hover:bg-white/[0.1] border border-white/[0.07] transition flex items-center gap-1"
          >
            <ChevronRight className="w-3 h-3 text-orange-400" />
            Hook (0–3s)
          </button>
          <button
            onClick={() => { setCurrentSec(Math.max(0, totalDuration - 4)); setIsPlaying(true); }}
            className="text-[11px] font-medium px-3 py-1.5 rounded-lg bg-white/[0.06] text-white/50 hover:text-white hover:bg-white/[0.1] border border-white/[0.07] transition flex items-center gap-1"
          >
            <ChevronRight className="w-3 h-3 text-violet-400" />
            Cliffhanger
          </button>
        </div>
      </div>

      {/* ── Detail panel ── */}
      <div className="lg:col-span-7 space-y-3.5">

        {/* Title row */}
        <div className="p-4 rounded-xl bg-[#111111] border border-white/[0.07]">
          <div className="flex items-center justify-between gap-3 mb-2">
            <div className="flex items-baseline gap-2">
              <span className="text-lg font-bold text-white/30 font-mono">#{promo.dynamicRank}</span>
              <span className="text-base font-semibold text-white font-mono">{promo.promo_id}</span>
            </div>
            <span className="font-mono font-bold text-lg text-white bg-white/[0.05] px-3 py-1 rounded-lg border border-white/[0.07]">
              {promo.calculatedOverall.toFixed(3)}
            </span>
          </div>
          <p className="text-[12px] text-white/40 leading-relaxed">{promo.why_it_works}</p>
          <div className="mt-3 pt-3 border-t border-white/[0.05] flex flex-wrap gap-2">
            {promo.segments.map((seg, i) => (
              <span key={i} className="text-[11px] font-mono px-2 py-1 rounded-lg bg-white/[0.04] text-white/50 border border-white/[0.06]">
                Ep {seg.episode}: {seg.start} → {seg.end}
              </span>
            ))}
          </div>
        </div>

        {/* Hook / Cliff */}
        <div className="grid grid-cols-2 gap-3">
          {[
            { label: 'Opening Hook (0–3s)', text: promo.hook, score: promo.scores.hook, color: 'text-orange-400' },
            { label: 'Cliffhanger Cut',     text: promo.cliffhanger, score: promo.scores.cliffhanger, color: 'text-violet-400' },
          ].map(({ label, text, score, color }) => (
            <div key={label} className="p-3.5 rounded-xl bg-[#111111] border border-white/[0.07]">
              <div className="flex items-center justify-between mb-2">
                <span className={`text-[10px] font-bold uppercase tracking-widest ${color}`}>{label}</span>
                <span className="text-[11px] font-mono font-bold text-white/60">{score.toFixed(1)}/5</span>
              </div>
              <p className="text-[12px] text-white/60 italic leading-relaxed">"{text}"</p>
            </div>
          ))}
        </div>

        {/* Standalone */}
        <div className="p-3.5 rounded-xl bg-[#111111] border border-white/[0.07]">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[10px] font-bold uppercase tracking-widest text-white/30">Pass 3 — Standalone Clarity</span>
            <span className="text-[11px] font-mono font-bold text-white/60">{promo.scores.standalone.toFixed(1)}/5</span>
          </div>
          <p className="text-[12px] text-white/50 leading-relaxed">{promo.standalone_note}</p>
        </div>

        {/* Transcript */}
        <div className="p-4 rounded-xl bg-[#0D0D0D] border border-white/[0.06]">
          <div className="flex items-center justify-between mb-2.5">
            <span className="text-[11px] font-semibold text-white/40">Screenplay Transcript</span>
            <button
              onClick={copyEdl}
              className="flex items-center gap-1 text-[11px] font-medium px-2.5 py-1 rounded-lg bg-white/[0.05] text-white/40 hover:text-white hover:bg-white/[0.1] border border-white/[0.06] transition"
            >
              {copiedEdl ? <Check className="w-3 h-3 text-green-400" /> : <Copy className="w-3 h-3" />}
              {copiedEdl ? 'Copied' : 'Copy EDL'}
            </button>
          </div>
          <pre className="text-[11px] font-mono text-white/35 whitespace-pre-wrap leading-relaxed max-h-48 overflow-y-auto bg-black/30 p-3 rounded-lg border border-white/[0.04]">
            {transcript}
          </pre>
        </div>
      </div>
    </div>
  );
}
