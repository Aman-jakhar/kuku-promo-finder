import React, { useState, useMemo } from 'react';
import Header from './components/Header.jsx';
import StatsBar from './components/StatsBar.jsx';
import WeightTuner from './components/WeightTuner.jsx';
import PromoTable from './components/PromoTable.jsx';
import MobileSimulator from './components/MobileSimulator.jsx';
import QualityCenter from './components/QualityCenter.jsx';
import EdlExporterModal from './components/EdlExporterModal.jsx';
import EpisodeHeatmap from './components/EpisodeHeatmap.jsx';
import CompareView from './components/CompareView.jsx';

import rawPromos from './data/promos.json';
import transcripts from './data/transcripts.json';

export default function App() {
  const [activeTab, setActiveTab] = useState('catalog');
  const [selectedPromoId, setSelectedPromoId] = useState(rawPromos[0]?.promo_id || '');
  const [compareTargetPromo, setCompareTargetPromo] = useState(rawPromos[1] || null);
  const [filterEpisode, setFilterEpisode] = useState('all');
  
  // Scoring weights state
  const [weights, setWeights] = useState({
    hook: 0.35,
    cliffhanger: 0.35,
    standalone: 0.30
  });

  // Dynamically calculate overall scores & ranks based on current weights
  const processedPromos = useMemo(() => {
    const scored = rawPromos.map(p => {
      const calcOverall = Number(
        (weights.hook * p.scores.hook +
         weights.cliffhanger * p.scores.cliffhanger +
         weights.standalone * p.scores.standalone).toFixed(3)
      );
      return {
        ...p,
        calculatedOverall: calcOverall
      };
    });

    // Sort descending by calculatedOverall
    scored.sort((a, b) => b.calculatedOverall - a.calculatedOverall);

    // Assign dynamic ranks
    return scored.map((p, idx) => ({
      ...p,
      dynamicRank: idx + 1
    }));
  }, [weights]);

  // Selected promo object
  const selectedPromo = useMemo(() => {
    return processedPromos.find(p => p.promo_id === selectedPromoId) || processedPromos[0];
  }, [processedPromos, selectedPromoId]);

  // Current promo transcript
  const currentTranscript = transcripts[selectedPromo?.promo_id] || [];

  // Summary stats
  const stats = useMemo(() => {
    const total = processedPromos.length;
    const topScore = processedPromos[0]?.calculatedOverall || 0.0;
    const avgDuration = processedPromos.reduce((acc, p) => acc + p.total_seconds, 0) / (total || 1);
    return {
      totalPromos: total,
      topScore,
      avgDuration
    };
  }, [processedPromos]);

  const handleSelectPromo = (p) => {
    setSelectedPromoId(p.promo_id);
    setActiveTab('simulator');
  };

  const handleComparePromo = (p) => {
    setCompareTargetPromo(p);
    setActiveTab('compare');
  };

  return (
    <div className="min-h-screen bg-[#0A0A0A] text-white flex flex-col" style={{ fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif' }}>
      {/* Navigation Header */}
      <Header
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        totalPromos={processedPromos.length}
      />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-5 md:p-7">
        {/* Top Metric Cards */}
        <StatsBar stats={stats} />

        {/* Dynamic Weight Sliders */}
        <WeightTuner weights={weights} setWeights={setWeights} />

        {/* Tab 1: Catalog & Ranking */}
        {activeTab === 'catalog' && (
          <div className="space-y-6">
            <EpisodeHeatmap
              promos={processedPromos}
              selectedEpisode={filterEpisode}
              onSelectEpisode={setFilterEpisode}
            />
            <PromoTable
              promos={processedPromos}
              onSelectPromo={handleSelectPromo}
              onComparePromo={handleComparePromo}
              selectedPromoId={selectedPromoId}
              filterEpisode={filterEpisode}
              setFilterEpisode={setFilterEpisode}
            />
          </div>
        )}

        {/* Tab 2: 50-Episode Heatmap View */}
        {activeTab === 'heatmap' && (
          <div className="space-y-6">
            <EpisodeHeatmap
              promos={processedPromos}
              selectedEpisode={filterEpisode}
              onSelectEpisode={setFilterEpisode}
            />
            <PromoTable
              promos={processedPromos}
              onSelectPromo={handleSelectPromo}
              onComparePromo={handleComparePromo}
              selectedPromoId={selectedPromoId}
              filterEpisode={filterEpisode}
              setFilterEpisode={setFilterEpisode}
            />
          </div>
        )}

        {/* Tab 3: 9:16 Mobile Simulator */}
        {activeTab === 'simulator' && (
          <MobileSimulator
            promo={selectedPromo}
            transcriptParts={currentTranscript}
          />
        )}

        {/* Tab 4: A/B Split Test View */}
        {activeTab === 'compare' && (
          <CompareView
            promos={processedPromos}
            initialPromoA={selectedPromo}
            initialPromoB={compareTargetPromo}
          />
        )}

        {/* Tab 5: Quality Center & Failure Audit */}
        {activeTab === 'quality' && (
          <QualityCenter />
        )}

        {/* Tab 6: EDL & Finishing Export */}
        {activeTab === 'export' && (
          <EdlExporterModal promos={processedPromos} />
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-white/[0.05] bg-[#060606] py-5 px-6 text-center">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-3">
          <div className="text-[11px] text-white/20">
            Kuku AI Microdrama Studio — Problem 1 Take-Home Submission
          </div>
          <div className="font-mono text-[10px] text-white/15">
            50 Episodes · 105 Promos · 100% Boundary Snapping Compliance
          </div>
        </div>
      </footer>
    </div>
  );
}
