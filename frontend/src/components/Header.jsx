import React from 'react';
import { Clapperboard, Smartphone, ShieldCheck, Download, Layers, BarChart2, ArrowLeftRight } from 'lucide-react';

export default function Header({ activeTab, setActiveTab, totalPromos }) {
  const navItems = [
    { id: 'catalog',   label: 'Catalog',      icon: Layers },
    { id: 'heatmap',   label: 'Heatmap',      icon: BarChart2 },
    { id: 'simulator', label: 'Mobile Studio', icon: Smartphone },
    { id: 'compare',   label: 'A/B Test',      icon: ArrowLeftRight },
    { id: 'quality',   label: 'Quality',       icon: ShieldCheck },
    { id: 'export',    label: 'Export',         icon: Download },
  ];

  return (
    <header className="sticky top-0 z-50 border-b border-white/[0.07] bg-[#0A0A0A]/90 backdrop-blur-xl">
      <div className="max-w-7xl mx-auto px-5 h-14 flex items-center justify-between gap-6">

        {/* Brand */}
        <div className="flex items-center gap-3 shrink-0">
          <div className="w-8 h-8 rounded-lg bg-[#161616] border border-white/[0.1] flex items-center justify-center">
            <Clapperboard className="w-4 h-4 text-white" />
          </div>
          <div className="hidden sm:flex items-baseline gap-2">
            <span className="font-semibold text-sm text-white tracking-tight">
              Kuku Promo Studio
            </span>
            <span className="text-[11px] font-medium text-white/30 font-mono">v2</span>
          </div>
        </div>

        {/* Segmented Nav — Linear/Vercel style */}
        <nav className="flex items-center gap-0.5 p-1 rounded-xl bg-white/[0.04] border border-white/[0.07]">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-[13px] font-medium transition-all duration-100 whitespace-nowrap ${
                  isActive
                    ? 'bg-white text-black shadow-sm'
                    : 'text-white/40 hover:text-white/80 hover:bg-white/[0.05]'
                }`}
              >
                <Icon className={`w-3.5 h-3.5 shrink-0 ${isActive ? 'text-black' : 'text-white/40'}`} />
                <span className="hidden md:inline">{item.label}</span>
                {item.id === 'catalog' && (
                  <span className={`text-[10px] font-mono px-1 rounded ${
                    isActive ? 'bg-black/10 text-black/60' : 'bg-white/[0.07] text-white/30'
                  }`}>{totalPromos}</span>
                )}
              </button>
            );
          })}
        </nav>

        {/* Right slot — pill */}
        <div className="hidden lg:flex items-center gap-2 shrink-0">
          <span className="text-[11px] font-mono text-white/20">50 eps • 105 promos</span>
          <span className="w-1.5 h-1.5 rounded-full bg-green-500/60 animate-pulse-dot"></span>
        </div>
      </div>
    </header>
  );
}
