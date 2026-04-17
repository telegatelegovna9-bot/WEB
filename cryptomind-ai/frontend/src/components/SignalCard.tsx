'use client';

import { Signal } from '@/services/api';

interface SignalCardProps {
  signal: Signal;
}

export function SignalCard({ signal }: SignalCardProps) {
  const getSignalColor = (type: string) => {
    switch (type) {
      case 'pump':
        return 'signal-pump';
      case 'dump':
        return 'signal-dump';
      case 'orderbook_wall':
        return 'signal-orderbook';
      case 'volume_spike':
        return 'signal-volume';
      default:
        return 'border-gray-500/30';
    }
  };

  const getConfidenceClass = (score: number) => {
    if (score >= 70) return 'confidence-high';
    if (score >= 50) return 'confidence-medium';
    return 'confidence-low';
  };

  const formatPrice = (price: number) => {
    if (price >= 1000) {
      return price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    }
    return price.toFixed(4);
  };

  return (
    <div className={`glass-card p-4 border-l-4 ${getSignalColor(signal.signal_type)} animate-pulse-signal`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className="text-2xl font-bold">{signal.symbol}</div>
          <span className="px-2 py-1 text-xs rounded bg-white/10 uppercase">
            {signal.exchange}
          </span>
          <span className="px-2 py-1 text-xs rounded bg-white/10 uppercase">
            {signal.signal_type}
          </span>
        </div>
        <div className="text-right">
          <div className="text-lg font-semibold">${formatPrice(signal.price)}</div>
          <div className={`text-sm ${signal.price_change_percent >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            {signal.price_change_percent >= 0 ? '+' : ''}{signal.price_change_percent.toFixed(2)}%
          </div>
        </div>
      </div>

      {/* Confidence Score */}
      <div className="mb-3">
        <div className="flex items-center justify-between text-sm mb-1">
          <span className="text-gray-400">Confidence</span>
          <span className={`font-semibold ${getConfidenceClass(signal.confidence_score)}`}>
            {signal.confidence_score.toFixed(0)}%
          </span>
        </div>
        <div className="w-full h-2 bg-white/10 rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full transition-all ${
              signal.confidence_score >= 70 ? 'bg-green-500' :
              signal.confidence_score >= 50 ? 'bg-yellow-500' :
              'bg-red-500'
            }`}
            style={{ width: `${signal.confidence_score}%` }}
          />
        </div>
      </div>

      {/* Explanation */}
      <div className="mb-3">
        <div className="text-sm text-gray-400 mb-2">Why this signal?</div>
        <ul className="space-y-1">
          {signal.explanation.reasons.map((reason, index) => (
            <li key={index} className="text-sm flex items-start gap-2">
              <span className="text-blue-400 mt-1">•</span>
              <span>{reason}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Market Behavior */}
      <div className="grid grid-cols-2 gap-3 mb-3">
        <div className="bg-white/5 rounded-lg p-2">
          <div className="text-xs text-gray-400">Market Behavior</div>
          <div className="text-sm font-semibold capitalize">
            {signal.explanation.market_behavior}
          </div>
        </div>
        <div className="bg-white/5 rounded-lg p-2">
          <div className="text-xs text-gray-400">Smart Money</div>
          <div className={`text-sm font-semibold ${signal.explanation.smart_money_activity ? 'text-green-400' : 'text-gray-400'}`}>
            {signal.explanation.smart_money_activity ? 'Active' : 'Inactive'}
          </div>
        </div>
      </div>

      {/* Historical Analogies */}
      {signal.historical_analogies && signal.historical_analogies.length > 0 && (
        <div>
          <div className="text-sm text-gray-400 mb-2">Historical Similar Cases</div>
          <div className="space-y-2">
            {signal.historical_analogies.slice(0, 2).map((analogy, index) => (
              <div key={index} className="bg-white/5 rounded-lg p-2 text-sm">
                <div className="flex justify-between items-center">
                  <span className="text-gray-400">
                    {analogy.similarity_score * 100}% similar
                  </span>
                  <span className={analogy.outcome === 'success' ? 'text-green-400' : 'text-red-400'}>
                    {analogy.outcome === 'success' ? '✓' : '✗'} {analogy.price_change_after > 0 ? '+' : ''}{analogy.price_change_after.toFixed(1)}%
                  </span>
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  Timeframe: {analogy.time_frame}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Footer */}
      <div className="mt-3 pt-3 border-t border-white/10 flex justify-between items-center text-xs text-gray-500">
        <span>Volume: {signal.volume_change_percent >= 0 ? '+' : ''}{signal.volume_change_percent.toFixed(0)}%</span>
        <span>{new Date(signal.timestamp).toLocaleString()}</span>
      </div>
    </div>
  );
}
