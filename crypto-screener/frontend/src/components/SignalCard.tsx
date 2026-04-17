'use client';

import { useMarketStore } from '@/store/marketStore';
import { formatDistanceToNow } from 'date-fns';

export function SignalCard() {
  const signals = useMarketStore((state) => state.signals);

  const getSignalColor = (type: string) => {
    switch (type) {
      case 'pump':
        return 'bg-green-500/10 border-green-500 text-green-500';
      case 'dump':
        return 'bg-red-500/10 border-red-500 text-red-500';
      case 'order_book_wall':
        return 'bg-blue-500/10 border-blue-500 text-blue-500';
      default:
        return 'bg-gray-500/10 border-gray-500 text-gray-500';
    }
  };

  const getConfidenceColor = (score: number) => {
    if (score >= 80) return 'text-green-500';
    if (score >= 60) return 'text-yellow-500';
    return 'text-red-500';
  };

  const getBehaviorBadge = (behavior: string) => {
    const colors: Record<string, string> = {
      accumulation: 'bg-green-500/20 text-green-400',
      distribution: 'bg-red-500/20 text-red-400',
      breakout: 'bg-blue-500/20 text-blue-400',
      manipulation: 'bg-purple-500/20 text-purple-400',
      normal: 'bg-gray-500/20 text-gray-400',
    };
    return colors[behavior] || colors.normal;
  };

  if (signals.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-500">
        No signals yet. Waiting for market data...
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {signals.map((signal) => (
        <div
          key={signal.id}
          className={`p-4 rounded-lg border ${getSignalColor(signal.type)} transition-all hover:scale-[1.02]`}
        >
          {/* Header */}
          <div className="flex items-start justify-between mb-3">
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-lg font-bold">
                  {signal.symbol}
                </h3>
                <span className="text-xs px-2 py-1 rounded-full bg-white/10 uppercase">
                  {signal.exchange}
                </span>
              </div>
              <p className="text-sm opacity-75 capitalize">
                {signal.type.replace('_', ' ')}
              </p>
            </div>
            <div className="text-right">
              <p className="text-xl font-mono">${signal.price.toLocaleString()}</p>
              <p className="text-xs opacity-75">
                {formatDistanceToNow(new Date(signal.created_at), { addSuffix: true })}
              </p>
            </div>
          </div>

          {/* Intelligence */}
          <div className="grid grid-cols-2 gap-4 mb-3">
            <div>
              <p className="text-xs opacity-75 mb-1">Confidence</p>
              <p className={`text-2xl font-bold ${getConfidenceColor(signal.intelligence.confidence_score)}`}>
                {signal.intelligence.confidence_score.toFixed(0)}%
              </p>
            </div>
            <div>
              <p className="text-xs opacity-75 mb-1">Market Behavior</p>
              <span className={`text-sm px-2 py-1 rounded ${getBehaviorBadge(signal.intelligence.market_behavior)}`}>
                {signal.intelligence.market_behavior.toUpperCase()}
              </span>
            </div>
          </div>

          {/* Causes */}
          <div className="mb-3">
            <p className="text-xs opacity-75 mb-2">Detected Causes:</p>
            <ul className="space-y-1">
              {signal.intelligence.causes.slice(0, 3).map((cause, idx) => (
                <li key={idx} className="text-sm flex items-start gap-2">
                  <span className="text-green-500 mt-1">•</span>
                  {cause}
                </li>
              ))}
            </ul>
          </div>

          {/* Smart Money Indicators */}
          {Object.keys(signal.intelligence.smart_money_indicators).length > 0 && (
            <div className="mb-3 p-2 rounded bg-white/5">
              <p className="text-xs opacity-75 mb-1">Smart Money Indicators:</p>
              <div className="flex flex-wrap gap-2">
                {Object.entries(signal.intelligence.smart_money_indicators).map(([key, value]) => (
                  <span key={key} className="text-xs px-2 py-1 rounded bg-purple-500/20 text-purple-400">
                    {key}: {typeof value === 'number' ? value.toLocaleString() : String(value)}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Recommended Action */}
          {signal.intelligence.recommended_action && (
            <div className="p-2 rounded bg-yellow-500/10 border border-yellow-500/30">
              <p className="text-xs text-yellow-500">
                💡 {signal.intelligence.recommended_action}
              </p>
            </div>
          )}

          {/* Risk Level */}
          <div className="mt-3 flex items-center justify-between text-xs">
            <span className="opacity-75">Risk Level:</span>
            <span className={`font-medium capitalize ${
              signal.intelligence.risk_level === 'low' ? 'text-green-500' :
              signal.intelligence.risk_level === 'medium' ? 'text-yellow-500' :
              'text-red-500'
            }`}>
              {signal.intelligence.risk_level}
            </span>
          </div>
        </div>
      ))}
    </div>
  );
}
