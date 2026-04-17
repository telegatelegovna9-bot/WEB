'use client';

import { Signal } from '@/types';
import { formatDistanceToNow } from 'date-fns';

interface SignalDetailPanelProps {
  signal: Signal;
  onClose?: () => void;
}

export function SignalDetailPanel({ signal, onClose }: SignalDetailPanelProps) {
  const getSignalColor = (type: string) => {
    switch (type) {
      case 'pump':
        return 'from-green-500/20 to-emerald-500/20 border-green-500/50 text-green-400';
      case 'dump':
        return 'from-red-500/20 to-rose-500/20 border-red-500/50 text-red-400';
      case 'order_book_wall':
        return 'from-blue-500/20 to-cyan-500/20 border-blue-500/50 text-blue-400';
      case 'breakout':
        return 'from-purple-500/20 to-violet-500/20 border-purple-500/50 text-purple-400';
      default:
        return 'from-gray-500/20 to-slate-500/20 border-gray-500/50 text-gray-400';
    }
  };

  const getConfidenceGradient = (score: number) => {
    if (score >= 80) return 'confidence-high';
    if (score >= 60) return 'confidence-medium';
    return 'confidence-low';
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

  return (
    <div className="signal-enter glass-card rounded-xl border border-white/10 overflow-hidden">
      {/* Header */}
      <div className={`p-4 bg-gradient-to-r ${getSignalColor(signal.type)} border-b border-white/10`}>
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-full bg-white/10 flex items-center justify-center text-2xl">
              {signal.type === 'pump' ? '🚀' : signal.type === 'dump' ? '🔻' : '📊'}
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-xl font-bold">{signal.symbol}</h2>
                <span className="px-2 py-0.5 rounded text-xs bg-white/20 uppercase font-semibold">
                  {signal.exchange}
                </span>
              </div>
              <p className="text-sm opacity-75 capitalize mt-0.5">
                {signal.type.replace('_', ' ')} Signal
              </p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-2xl font-mono font-bold">${signal.price.toLocaleString()}</p>
            <p className="text-xs opacity-75">
              {formatDistanceToNow(new Date(signal.created_at), { addSuffix: true })}
            </p>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="p-4 space-y-4">
        {/* Confidence Score */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-400">Confidence Score</span>
            <span className={`text-lg font-bold ${
              signal.intelligence.confidence_score >= 80 ? 'text-green-500' :
              signal.intelligence.confidence_score >= 60 ? 'text-yellow-500' :
              'text-red-500'
            }`}>
              {signal.intelligence.confidence_score.toFixed(0)}%
            </span>
          </div>
          <div className="h-3 rounded-full bg-gray-700 overflow-hidden">
            <div 
              className={`h-full ${getConfidenceGradient(signal.intelligence.confidence_score)} transition-all duration-500`}
              style={{ width: `${signal.intelligence.confidence_score}%` }}
            />
          </div>
        </div>

        {/* Market Behavior */}
        <div className="grid grid-cols-2 gap-3">
          <div className="p-3 rounded-lg bg-white/5 border border-white/10">
            <p className="text-xs text-gray-400 mb-1">Market Behavior</p>
            <div className="flex items-center gap-2">
              <span className="text-xl">{getBehaviorIcon(signal.intelligence.market_behavior)}</span>
              <span className="font-semibold capitalize">{signal.intelligence.market_behavior}</span>
            </div>
          </div>
          <div className="p-3 rounded-lg bg-white/5 border border-white/10">
            <p className="text-xs text-gray-400 mb-1">Risk Level</p>
            <span className={`font-semibold capitalize ${
              signal.intelligence.risk_level === 'low' ? 'text-green-500' :
              signal.intelligence.risk_level === 'medium' ? 'text-yellow-500' :
              'text-red-500'
            }`}>
              {signal.intelligence.risk_level}
            </span>
          </div>
        </div>

        {/* Detected Causes */}
        <div className="p-3 rounded-lg bg-white/5 border border-white/10">
          <p className="text-sm font-semibold mb-2 flex items-center gap-2">
            <span>🔍</span>
            Detected Causes
          </p>
          <ul className="space-y-2">
            {signal.intelligence.causes.map((cause, idx) => (
              <li key={idx} className="flex items-start gap-2 text-sm">
                <span className="text-green-500 mt-0.5">✓</span>
                <span className="text-gray-300">{cause}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Smart Money Indicators */}
        {Object.keys(signal.intelligence.smart_money_indicators).length > 0 && (
          <div className="p-3 rounded-lg bg-purple-500/10 border border-purple-500/30">
            <p className="text-sm font-semibold mb-2 flex items-center gap-2">
              <span>💰</span>
              Smart Money Indicators
            </p>
            <div className="flex flex-wrap gap-2">
              {Object.entries(signal.intelligence.smart_money_indicators).map(([key, value]) => (
                <span 
                  key={key} 
                  className="px-3 py-1.5 rounded-lg bg-purple-500/20 text-purple-300 text-sm font-mono"
                >
                  {key}: {typeof value === 'number' ? value.toLocaleString() : String(value)}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Historical Patterns */}
        {signal.intelligence.historical_patterns.length > 0 && (
          <div className="p-3 rounded-lg bg-blue-500/10 border border-blue-500/30">
            <p className="text-sm font-semibold mb-2 flex items-center gap-2">
              <span>📚</span>
              Historical Patterns ({signal.intelligence.historical_patterns.length} matches)
            </p>
            <div className="space-y-2">
              {signal.intelligence.historical_patterns.slice(0, 3).map((pattern, idx) => (
                <div key={idx} className="flex items-center justify-between text-sm p-2 rounded bg-white/5">
                  <div>
                    <span className="text-blue-400">{(pattern.similarity_score * 100).toFixed(0)}% similar</span>
                    <span className="text-gray-500 ml-2">{pattern.date}</span>
                  </div>
                  <span className={`font-semibold ${
                    pattern.outcome_percent > 0 ? 'text-green-500' : 'text-red-500'
                  }`}>
                    {pattern.outcome_percent > 0 ? '+' : ''}{pattern.outcome_percent.toFixed(2)}%
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Recommended Action */}
        {signal.intelligence.recommended_action && (
          <div className="p-4 rounded-lg bg-yellow-500/10 border border-yellow-500/30">
            <div className="flex items-start gap-3">
              <span className="text-2xl">💡</span>
              <div>
                <p className="text-sm font-semibold text-yellow-500 mb-1">Recommended Action</p>
                <p className="text-sm text-yellow-200">{signal.intelligence.recommended_action}</p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="px-4 py-3 border-t border-white/10 bg-white/5 flex items-center justify-between">
        <div className="flex items-center gap-4 text-xs text-gray-400">
          <span>Signal ID: {signal.id.slice(0, 8)}...</span>
          <span>•</span>
          <span>Expires: {signal.expires_at ? formatDistanceToNow(new Date(signal.expires_at)) : 'N/A'}</span>
        </div>
        {onClose && (
          <button 
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg bg-white/10 hover:bg-white/20 text-sm transition-colors"
          >
            Close
          </button>
        )}
      </div>
    </div>
  );
}
