import React, { useState } from 'react';
import { Download, FileCode, Check, Copy, Film, Archive } from 'lucide-react';
import JSZip from 'jszip';

export default function EdlExporterModal({ promos }) {
  const [selectedPromo, setSelectedPromo] = useState(promos[0] || null);
  const [copied, setCopied] = useState(false);
  const [isZipping, setIsZipping] = useState(false);

  if (!selectedPromo) return null;

  // Generate CMX 3600 EDL representation
  const generateEdl = (p) => {
    let edl = `TITLE: KUKU_PROMO_${p.promo_id.toUpperCase()}\nFCM: NON-DROP FRAME\n\n`;
    let recordIn = 0.0;
    p.segments.forEach((seg, idx) => {
      const dur = seg.duration_s || (seg.end_s - seg.start_s);
      const recordOut = recordIn + dur;
      edl += `00${idx + 1}  EP${String(seg.episode).padStart(3, '0')}    V     C        ${seg.start}:00 ${seg.end}:00 00:00:00:00 00:00:${Math.floor(dur)}:00\n`;
      edl += `* FROM CLIP: Episode ${seg.episode} [${seg.start} - ${seg.end}]\n`;
      if (idx === 0) edl += `* HOOK: ${p.hook.substring(0, 65)}\n`;
      if (idx === p.segments.length - 1) edl += `* CLIFFHANGER: ${p.cliffhanger.substring(0, 65)}\n`;
      edl += `\n`;
      recordIn = recordOut;
    });
    return edl;
  };

  // Generate SRT format
  const generateSrt = (p) => {
    return (
      `1\n00:00:00,000 --> 00:00:03,000\n[HOOK] ${p.hook}\n\n` +
      `2\n00:00:03,000 --> 00:00:${Math.max(4, Math.floor(p.total_seconds - 4))},000\n[BODY] ${p.why_it_works}\n\n` +
      `3\n00:00:${Math.max(4, Math.floor(p.total_seconds - 4))},000 --> 00:00:${Math.floor(p.total_seconds)},000\n[CLIFFHANGER] ${p.cliffhanger}\n`
    );
  };

  const edlText = generateEdl(selectedPromo);

  const handleCopy = () => {
    navigator.clipboard.writeText(edlText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const downloadFile = (content, filename, type) => {
    const blob = new Blob([content], { type });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  };

  // Batch Zip Generator
  const handleDownloadBatchZip = async () => {
    setIsZipping(true);
    try {
      const zip = new JSZip();
      const edlFolder = zip.folder("edl_cuts");
      const srtFolder = zip.folder("subtitles");

      // Add Top 15 promos
      promos.slice(0, 15).forEach((p) => {
        edlFolder.file(`${p.promo_id}.edl`, generateEdl(p));
        srtFolder.file(`${p.promo_id}.srt`, generateSrt(p));
      });

      // Add promos.json and CSV
      zip.file("promos.json", JSON.stringify(promos, null, 2));

      const csvHeader = "rank,promo_id,episodes,total_seconds,overall_score,hook,cliffhanger\n";
      const csvRows = promos.map(p => 
        `"${p.dynamicRank || p.rank}","${p.promo_id}","${p.segments.map(s=>s.episode).join('+')}","${p.total_seconds}","${p.calculatedOverall || p.scores.overall}","${p.hook.replace(/"/g, '""')}","${p.cliffhanger.replace(/"/g, '""')}"`
      ).join("\n");
      zip.file("promos.csv", csvHeader + csvRows);

      const content = await zip.generateAsync({ type: "blob" });
      const url = URL.createObjectURL(content);
      const a = document.createElement('a');
      a.href = url;
      a.download = "kuku_promos_premiere_package.zip";
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error(err);
    } finally {
      setIsZipping(false);
    }
  };

  return (
    <div className="space-y-5">
      {/* Editorial Header Banner */}
      <div className="p-4 sm:p-5 rounded-xl bg-[#111111] border border-white/[0.07] flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-white/[0.05] border border-white/[0.08]">
            <Film className="w-4 h-4 text-white/70" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-white">NLE Finishing &amp; Export</h3>
            <p className="text-[11px] text-white/40 mt-0.5">
              Direct import for Premiere Pro, DaVinci Resolve, and Final Cut Pro (CMX 3600 EDL + Subtitles).
            </p>
          </div>
        </div>

        {/* Batch Download ZIP Button */}
        <button
          onClick={handleDownloadBatchZip}
          disabled={isZipping}
          className="w-full sm:w-auto py-2 px-3.5 rounded-lg bg-white text-black text-xs font-semibold hover:bg-white/90 transition flex items-center justify-center gap-2 shadow-sm"
        >
          <Archive className="w-3.5 h-3.5" />
          <span>{isZipping ? 'Packaging ZIP…' : 'Download Top 15 (EDL + SRT Package)'}</span>
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        {/* Left: Promo Selector & Single Downloads */}
        <div className="lg:col-span-5 space-y-3.5">
          <div className="p-4 rounded-xl bg-[#111111] border border-white/[0.07]">
            <label className="text-[11px] font-semibold text-white/50 uppercase tracking-widest block mb-2">
              Select Candidate Promo
            </label>
            <select
              value={selectedPromo.promo_id}
              onChange={(e) => {
                const found = promos.find(p => p.promo_id === e.target.value);
                if (found) setSelectedPromo(found);
              }}
              className="w-full bg-[#1A1A1A] border border-white/[0.08] rounded-lg p-2 text-xs text-white/80 focus:outline-none focus:border-white/20 font-mono"
            >
              {promos.slice(0, 30).map(p => (
                <option key={p.promo_id} value={p.promo_id}>
                  #{p.dynamicRank || p.rank} — {p.promo_id} ({p.total_seconds.toFixed(1)}s)
                </option>
              ))}
            </select>
          </div>

          {/* Individual Download Buttons */}
          <div className="p-4 rounded-xl bg-[#111111] border border-white/[0.07] space-y-2">
            <button
              onClick={() => downloadFile(edlText, `${selectedPromo.promo_id}.edl`, 'text/plain')}
              className="w-full py-2 px-3 rounded-lg bg-white/[0.08] hover:bg-white/[0.12] text-white text-xs font-medium transition flex items-center justify-center gap-2 border border-white/[0.08]"
            >
              <Download className="w-3.5 h-3.5 text-white/70" />
              <span>Download `{selectedPromo.promo_id}.edl`</span>
            </button>

            <button
              onClick={() => downloadFile(generateSrt(selectedPromo), `${selectedPromo.promo_id}.srt`, 'text/plain')}
              className="w-full py-2 px-3 rounded-lg bg-white/[0.04] hover:bg-white/[0.08] text-white/70 hover:text-white text-xs font-medium transition flex items-center justify-center gap-2 border border-white/[0.06]"
            >
              <Download className="w-3.5 h-3.5 text-white/40" />
              <span>Download Subtitle (`.srt`)</span>
            </button>

            <button
              onClick={() => downloadFile(JSON.stringify(promos, null, 2), 'promos.json', 'application/json')}
              className="w-full py-2 px-3 rounded-lg bg-white/[0.04] hover:bg-white/[0.08] text-white/70 hover:text-white text-xs font-medium transition flex items-center justify-center gap-2 border border-white/[0.06]"
            >
              <Download className="w-3.5 h-3.5 text-white/40" />
              <span>Download Full `promos.json` (105 clips)</span>
            </button>
          </div>
        </div>

        {/* Right: Live EDL Preview */}
        <div className="lg:col-span-7">
          <div className="p-4 rounded-xl bg-[#111111] border border-white/[0.07]">
            <div className="flex items-center justify-between mb-2 pb-2 border-b border-white/[0.05]">
              <span className="text-[11px] font-semibold text-white/60 font-mono flex items-center gap-2">
                <FileCode className="w-3.5 h-3.5 text-white/40" />
                <span>{selectedPromo.promo_id}.edl (CMX 3600 Specification)</span>
              </span>
              <button
                onClick={handleCopy}
                className="text-[11px] font-medium text-white/40 hover:text-white flex items-center gap-1.5 transition"
              >
                {copied ? <Check className="w-3 h-3 text-green-400" /> : <Copy className="w-3 h-3" />}
                <span>{copied ? 'Copied' : 'Copy'}</span>
              </button>
            </div>
            <pre className="text-[11px] font-mono text-white/70 p-3 bg-[#0A0A0A] rounded-lg border border-white/[0.05] overflow-x-auto max-h-72 leading-relaxed">
              {edlText}
            </pre>
          </div>
        </div>
      </div>
    </div>
  );
}
