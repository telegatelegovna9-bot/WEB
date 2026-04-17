'use client';

import { useState } from 'react';
import { Signal } from '@/types';
import { useMarketStore } from '@/store/marketStore';
import { SignalDetailPanel } from './SignalDetailPanel';

export function EnhancedSignalCard() {
  const signals = useMarketStore((state) => state.signals);
  const [selectedSignal, setSelectedSignal] = useState<Signal | null>(null);
  const [filter, setFilter] = useState<'all' | 'pump' | 'dump' | 'order_book_wall' | 'breakout'>('all');
  const [minConfidence, setMinConfidence] = useState(0);

  const filteredSignals = signals.filter(signal => {
    if (filter !== 'all' && signal.type !== filter) return false;
    if (signal.intelligence.confidence_score < minConfidence) return false;
    return true;
  });

  const getSignalColor = (type: string) => {
    switch (type) {
      case 'pump':
        return 'bg-green-500/10 border-green-500/50 hover:border-green-500';
      case 'dump':
        return 'bg-red-500/10 border-red-500/50 hover:border-red-500';
      case 'order_book_wall':
        return 'bg-blue-500/10 border-blue-500/50 hover:border-blue-500';
      case 'breakout':
        return 'bg-purple-500/10 border-purple-500/50 hover:border-purple-500';
      default:
        return 'bg-gray-500/10 border-gray-500/50 hover:border-gray-500';
    }
  };

  const getConfidenceBadge = (score: number) => {
    if (score >= 80) return 'bg-green-500/20 text-green-400 border-green-500/30';
    if (score >= 60) return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
    return 'bg-red-500/20 text-red-400 border-red-500/30';
  };

  const getBehaviorIcon = (behavior: string) => {
    const icons: Record<string, string> = {
      accumulation: '📈',
      distribution: '📉',
      breakout: '🚀',
      manipulation: '⚠️',
      normal: '➡️',
    };
    return icons[behavior] || '❓';
  };

  if (filteredSignals.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-gray-500">
        <div className="text-4xl mb-4">🔍</div>
        <p>No signals found</p>
        <p className="text-sm mt-2">
          {signals.length === 0 
            ? 'Waiting for market data...' 
            : 'Try adjusting your filters'}
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Filters */}
      <div className="flex flex-wrap items-center gap-3 pb-4 border-b border-white/10">
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-400">Filter:</span>
          {(['all', 'pump', 'dump', 'order_book_wall', 'breakout'] as const).map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-3 py-1 rounded-lg text-xs font-medium transition-colors ${
                filter === f
                  ? 'bg-white/20 text-white'
                  : 'bg-white/5 text-gray-400 hover:bg-white/10'
              }`}
            >
              {f === 'all' ? 'All' : f.replace('_', ' ')}
            </button>
          ))}
        </div>
        
        <div className="flex items-center gap-2 ml-auto">
          <span className="text-sm text-gray-400">Min Confidence:</span>
          <input
            type="range"
            min="0"
            max="100"
            value={minConfidence}
            onChange={(e) => setMinConfidence(Number(e.target.value))}
            className="w-24 accent-blue-500"
          />
          <span className="text-sm font-mono w-12">{minConfidence}%</span>
        </div>
      </div>

      {/* Signals List */}
      <div className="space-y-3">
        {filteredSignals.map((signal, idx) => (
          <div
            key={signal.id}
            onClick={() => setSelectedSignal(signal)}
            className={`signal-enter p-4 rounded-lg border cursor-pointer transition-all hover:scale-[1.01] ${getSignalColor(signal.type)}`}
            style={{ animationDelay: `${idx * 50}ms` }}
          >
            <div className="flex items-start justify-between gap-4">
              {/* Left: Symbol & Type */}
              <div className="flex items-start gap-3 flex-1">
                <div className="w-10 h-10 rounded-lg bg-white/10 flex items-center justify-center text-xl flex-shrink-0">
                  {signal.type === 'pump' ? '🚀' : signal.type === 'dump' ? '🔻' : signal.type === 'breakout' ? '💥' : '📊'}
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="font-bold">{signal.symbol}</h3>
                    <span className="text-xs px-2 py-0.5 rounded bg-white/10 uppercase">
                      {signal.exchange}
                    </span>
                  </div>
                  <p className="text-sm opacity-75 capitalize mt-0.5">
                    {signal.type.replace('_', ' ')}
                  </p>
                  <p className="text-xs text-gray-400 mt-1 line-clamp-1">
                    {signal.intelligence.causes[0]}
                  </p>
                </div>
              </div>

              {/* Center: Market Behavior */}
              <div className="hidden md:flex flex-col items-center">
                <span className="text-2xl mb-1">{getBehaviorIcon(signal.intelligence.market_behavior)}</span>
                <span className="text-xs text-gray-400 capitalize">
                  {signal.intelligence.market_behavior}
                </span>
              </div>

              {/* Right: Price & Confidence */}
              <div className="flex flex-col items-end gap-2">
                <p className="text-lg font-mono font-bold">${signal.price.toLocaleString()}</p>
                <div className={`px-3 py-1 rounded-full border text-sm font-bold ${getConfidenceBadge(signal.intelligence.confidence_score)}`}>
                  {signal.intelligence.confidence_score.toFixed(0)}%
                </div>
              </div>
            </div>

            {/* Bottom: Quick Stats */}
            <div className="mt-3 pt-3 border-t border-white/10 flex items-center justify-between text-xs">
              <div className="flex items-center gap-4">
                <span className="text-gray-400">
                  Risk: <span className={`font-medium ${
                    signal.intelligence.risk_level === 'low' ? 'text-green-500' :
                    signal.intelligence.risk_level === 'medium' ? 'text-yellow-500' :
                    'text-red-500'
                  }`}>{signal.intelligence.risk_level}</span>
                </span>
                {Object.keys(signal.intelligence.smart_money_indicators).length > 0 && (
                  <span className="flex items-center gap-1 text-purple-400">
                    <span>💰</span>
                    Smart Money Active
                  </span>
                )}
              </div>
              <span className="text-gray-500">Click for details →</span>
            </div>
          </div>
        ))}
      </div>

      {/* Detail Modal */}
      {selectedSignal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
          <div 
            className="absolute inset-0"
            onClick={() => setSelectedSignal(null)}
          />
          <div className="relative w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <SignalDetailPanel 
              signal={selectedSignal} 
              onClose={() => setSelectedSignal(null)}
            />
          </div>
        </div>
      )}
    </div>
  );
}
