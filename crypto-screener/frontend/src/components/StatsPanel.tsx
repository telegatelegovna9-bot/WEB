'use client';

import { Stats } from '@/lib/types';
import { Activity, TrendingUp, TrendingDown, Zap, Brain, Target, Layers } from 'lucide-react';

interface StatsPanelProps {
  stats: Stats | null;
}

export default function StatsPanel({ stats }: StatsPanelProps) {
  if (!stats) {
    return (
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="glass rounded-xl p-4 border border-[#1f2229] animate-pulse">
            <div className="h-4 bg-[#1f2229] rounded w-1/2 mb-2"></div>
            <div className="h-8 bg-[#1f2229] rounded w-3/4"></div>
          </div>
        ))}
      </div>
    );
  }

  const statCards = [
    {
      title: 'Active Signals',
      value: stats.total_signals.toString(),
      subValue: `${stats.signals_last_hour} last hour`,
      icon: Zap,
      color: 'text-purple-400',
      bgColor: 'bg-purple-400/10',
      borderColor: 'border-purple-400/20'
    },
    {
      title: 'Tracked Symbols',
      value: stats.tracked_symbols.toString(),
      subValue: `${stats.active_exchanges} exchanges`,
      icon: Layers,
      color: 'text-blue-400',
      bgColor: 'bg-blue-400/10',
      borderColor: 'border-blue-400/20'
    },
    {
      title: 'Signal Accuracy',
      value: `${stats.avg_signal_accuracy.toFixed(1)}%`,
      subValue: 'Historical average',
      icon: Target,
      color: 'text-emerald-400',
      bgColor: 'bg-emerald-400/10',
      borderColor: 'border-emerald-400/20'
    },
    {
      title: 'Market Status',
      value: stats.active_exchanges > 0 ? 'Active' : 'Offline',
      subValue: stats.top_gainers.length > 0 ? `${stats.top_gainers[0].symbol} leading` : 'Loading...',
      icon: Activity,
      color: stats.active_exchanges > 0 ? 'text-emerald-400' : 'text-gray-400',
      bgColor: stats.active_exchanges > 0 ? 'bg-emerald-400/10' : 'bg-gray-400/10',
      borderColor: stats.active_exchanges > 0 ? 'border-emerald-400/20' : 'border-gray-400/20'
    }
  ];

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      {statCards.map((stat, idx) => {
        const Icon = stat.icon;
        return (
          <div 
            key={idx}
            className={`glass rounded-xl p-4 border ${stat.borderColor} card-hover`}
          >
            <div className="flex items-start justify-between mb-3">
              <div>
                <div className="text-xs text-gray-400 uppercase tracking-wider mb-1">
                  {stat.title}
                </div>
                <div className="text-2xl font-bold">{stat.value}</div>
              </div>
              <div className={`p-2 rounded-lg ${stat.bgColor}`}>
                <Icon className={`w-5 h-5 ${stat.color}`} />
              </div>
            </div>
            <div className="text-xs text-gray-500">{stat.subValue}</div>
          </div>
        );
      })}
    </div>
  );
}

// Top Movers Component
export function TopMovers({ stats }: { stats: Stats | null }) {
  if (!stats) return null;

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-6">
      {/* Top Gainers */}
      <div className="glass rounded-xl p-4 border border-[#1f2229]">
        <div className="flex items-center gap-2 mb-3">
          <TrendingUp className="w-5 h-5 text-emerald-400" />
          <h3 className="font-semibold">Top Gainers</h3>
        </div>
        <div className="space-y-2">
          {stats.top_gainers.slice(0, 6).map((ticker, idx) => (
            <div key={idx} className="flex items-center justify-between py-1.5 px-2 rounded hover:bg-[#1f2229]/50">
              <span className="text-sm font-medium">{ticker.symbol}</span>
              <span className="text-sm font-semibold text-emerald-400">
                +{ticker.price_change_percent_24h.toFixed(2)}%
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Top Losers */}
      <div className="glass rounded-xl p-4 border border-[#1f2229]">
        <div className="flex items-center gap-2 mb-3">
          <TrendingDown className="w-5 h-5 text-red-400" />
          <h3 className="font-semibold">Top Losers</h3>
        </div>
        <div className="space-y-2">
          {stats.top_losers.slice(0, 6).map((ticker, idx) => (
            <div key={idx} className="flex items-center justify-between py-1.5 px-2 rounded hover:bg-[#1f2229]/50">
              <span className="text-sm font-medium">{ticker.symbol}</span>
              <span className="text-sm font-semibold text-red-400">
                {ticker.price_change_percent_24h.toFixed(2)}%
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Top Volume */}
      <div className="glass rounded-xl p-4 border border-[#1f2229]">
        <div className="flex items-center gap-2 mb-3">
          <Brain className="w-5 h-5 text-purple-400" />
          <h3 className="font-semibold">Highest Volume</h3>
        </div>
        <div className="space-y-2">
          {stats.top_volume.slice(0, 6).map((ticker, idx) => (
            <div key={idx} className="flex items-center justify-between py-1.5 px-2 rounded hover:bg-[#1f2229]/50">
              <span className="text-sm font-medium">{ticker.symbol}</span>
              <span className="text-sm text-gray-400">
                ${(ticker.quote_volume_24h / 1000000).toFixed(1)}M
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
