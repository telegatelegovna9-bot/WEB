'use client';

import { useEffect, useState } from 'react';
import { useMarketStore } from '@/store/marketStore';

interface StatsCardProps {
  title: string;
  value: string | number;
  icon: string;
  trend?: 'up' | 'down' | 'neutral';
  trendValue?: string;
  color: 'green' | 'red' | 'blue' | 'purple' | 'yellow';
}

function StatsCard({ title, value, icon, trend, trendValue, color }: StatsCardProps) {
  const colorClasses = {
    green: 'from-green-500/20 to-emerald-500/20 border-green-500/30 text-green-400',
    red: 'from-red-500/20 to-rose-500/20 border-red-500/30 text-red-400',
    blue: 'from-blue-500/20 to-cyan-500/20 border-blue-500/30 text-blue-400',
    purple: 'from-purple-500/20 to-violet-500/20 border-purple-500/30 text-purple-400',
    yellow: 'from-yellow-500/20 to-amber-500/20 border-yellow-500/30 text-yellow-400',
  };

  return (
    <div className={`glass-card rounded-xl border p-4 bg-gradient-to-br ${colorClasses[color]}`}>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs opacity-75 mb-1">{title}</p>
          <p className="text-2xl font-bold">{value}</p>
          {trend && trendValue && (
            <div className={`flex items-center gap-1 text-xs mt-1 ${
              trend === 'up' ? 'text-green-400' : trend === 'down' ? 'text-red-400' : 'text-gray-400'
            }`}>
              <span>{trend === 'up' ? '↑' : trend === 'down' ? '↓' : '→'}</span>
              <span>{trendValue}</span>
            </div>
          )}
        </div>
        <span className="text-3xl opacity-50">{icon}</span>
      </div>
    </div>
  );
}

export function DashboardStats() {
  const signals = useMarketStore((state) => state.signals);
  const tickers = useMarketStore((state) => Object.values(state.tickers));
  const [startTime] = useState(Date.now());

  const stats = {
    totalSignals: signals.length,
    pumpSignals: signals.filter(s => s.type === 'pump').length,
    dumpSignals: signals.filter(s => s.type === 'dump').length,
    orderBookWalls: signals.filter(s => s.type === 'order_book_wall').length,
    breakoutSignals: signals.filter(s => s.type === 'breakout').length,
    avgConfidence: signals.length > 0 
      ? Math.round(signals.reduce((acc, s) => acc + s.intelligence.confidence_score, 0) / signals.length)
      : 0,
    highConfidenceSignals: signals.filter(s => s.intelligence.confidence_score >= 80).length,
    monitoredPairs: tickers.length,
    gainers: tickers.filter(t => t.price_change_percent_24h > 0).length,
    losers: tickers.filter(t => t.price_change_percent_24h < 0).length,
    totalVolume: tickers.reduce((acc, t) => acc + t.volume_24h, 0),
    smartMoneyActive: signals.filter(s => 
      Object.keys(s.intelligence.smart_money_indicators).length > 0
    ).length,
  };

  const uptime = Math.floor((Date.now() - startTime) / 1000);
  const formatUptime = (seconds: number) => {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = seconds % 60;
    return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  const formatVolume = (volume: number) => {
    if (volume >= 1e9) return `${(volume / 1e9).toFixed(2)}B`;
    if (volume >= 1e6) return `${(volume / 1e6).toFixed(2)}M`;
    if (volume >= 1e3) return `${(volume / 1e3).toFixed(2)}K`;
    return volume.toFixed(2);
  };

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-6">
      {/* Total Signals */}
      <StatsCard
        title="Total Signals"
        value={stats.totalSignals}
        icon="📡"
        color="blue"
      />

      {/* Pump Signals */}
      <StatsCard
        title="Pump Signals"
        value={stats.pumpSignals}
        icon="🚀"
        trend={stats.pumpSignals > stats.dumpSignals ? 'up' : 'down'}
        trendValue={`${Math.round(stats.pumpSignals / (stats.pumpSignals + stats.dumpSignals || 1) * 100)}%`}
        color="green"
      />

      {/* Dump Signals */}
      <StatsCard
        title="Dump Signals"
        value={stats.dumpSignals}
        icon="🔻"
        color="red"
      />

      {/* Order Book Walls */}
      <StatsCard
        title="OB Walls"
        value={stats.orderBookWalls}
        icon="🧱"
        color="purple"
      />

      {/* Avg Confidence */}
      <StatsCard
        title="Avg Confidence"
        value={`${stats.avgConfidence}%`}
        icon="🎯"
        trend={stats.avgConfidence >= 70 ? 'up' : stats.avgConfidence >= 50 ? 'neutral' : 'down'}
        trendValue={stats.avgConfidence >= 70 ? 'High' : stats.avgConfidence >= 50 ? 'Medium' : 'Low'}
        color="yellow"
      />

      {/* Smart Money Active */}
      <StatsCard
        title="Smart Money"
        value={stats.smartMoneyActive}
        icon="💰"
        color="purple"
      />
    </div>
  );
}
