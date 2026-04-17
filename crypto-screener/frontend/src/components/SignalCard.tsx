'use client';

import { Signal } from '@/lib/types';
import { getSignalBadgeClass, getBehaviorLabel, getConfidenceColor, formatPrice } from '@/lib/api';
import { TrendingUp, TrendingDown, Zap, Brain, Target, Clock, ChevronRight } from 'lucide-react';

interface SignalCardProps {
  signal: Signal;
  onClick?: () => void;
}

export default function SignalCard({ signal, onClick }: SignalCardProps) {
  const { intelligence } = signal;
  
  const getTypeIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'pump':
        return <TrendingUp className="w-5 h-5 text-emerald-400" />;
      case 'dump':
        return <TrendingDown className="w-5 h-5 text-red-400" />;
      case 'volume_spike':
        return <Zap className="w-5 h-5 text-purple-400" />;
      default:
        return <Brain className="w-5 h-5 text-blue-400" />;
    }
  };

  const getTimeAgo = (timestamp: string) => {
    const now = new Date();
    const time = new Date(timestamp);
    const diff = Math.floor((now.getTime() - time.getTime()) / 1000);
    
    if (diff < 60) return 'Just now';
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    return `${Math.floor(diff / 3600)}h ago`;
  };

  return (
    <div 
      className="glass rounded-xl p-4 card-hover cursor-pointer border border-[#1f2229]"
      onClick={onClick}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-[#13151a] border border-[#1f2229]">
            {getTypeIcon(signal.type)}
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="font-bold text-lg">{signal.symbol}</h3>
              <span className={`px-2 py-0.5 rounded-full text-xs font-medium uppercase ${getSignalBadgeClass(signal.type)}`}>
                {signal.type.replace('_', ' ')}
              </span>
            </div>
            <div className="flex items-center gap-2 mt-1">
              <span className="text-xs text-gray-500 uppercase">{signal.exchange}</span>
              <span className="text-xs text-gray-600">•</span>
              <span className="text-xs text-gray-500 flex items-center gap-1">
                <Clock className="w-3 h-3" />
                {getTimeAgo(signal.timestamp)}
              </span>
            </div>
          </div>
        </div>
        <div className="text-right">
          <div className="text-xl font-bold">${formatPrice(signal.price)}</div>
          <div className={`text-sm font-semibold ${signal.price_change_percent >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
            {signal.price_change_percent >= 0 ? '+' : ''}{signal.price_change_percent.toFixed(2)}%
          </div>
        </div>
      </div>

      {/* Intelligence Section */}
      <div className="space-y-3">
        {/* Probability Score */}
        <div>
          <div className="flex items-center justify-between mb-1.5">
            <span className="text-xs text-gray-400 flex items-center gap-1">
              <Target className="w-3 h-3" />
              Success Probability
            </span>
            <span 
              className="text-sm font-bold"
              style={{ color: getConfidenceColor(intelligence.confidence_level) }}
            >
              {intelligence.probability_score.toFixed(0)}%
            </span>
          </div>
          <div className="h-1.5 bg-[#1f2229] rounded-full overflow-hidden">
            <div 
              className="h-full rounded-full transition-all duration-500"
              style={{ 
                width: `${intelligence.probability_score}%`,
                background: `linear-gradient(90deg, #ef4444 0%, #f59e0b 50%, #10b981 100%)`,
                backgroundPosition: `${intelligence.probability_score}% 0`
              }}
            />
          </div>
        </div>

        {/* Market Behavior */}
        <div className="flex items-center gap-2 p-2 rounded-lg bg-[#13151a]/50 border border-[#1f2229]">
          <Brain className="w-4 h-4 text-amber-400" />
          <span className="text-xs text-gray-400">Market Behavior:</span>
          <span className="text-xs font-medium text-amber-400">
            {getBehaviorLabel(intelligence.market_behavior)}
          </span>
        </div>

        {/* Key Reasons */}
        <div className="space-y-1.5">
          <div className="text-xs text-gray-400 font-medium">Key Factors:</div>
          {intelligence.reasons.slice(0, 2).map((reason, idx) => (
            <div key={idx} className="text-xs text-gray-300 flex items-start gap-1.5">
              <span className="text-emerald-400 mt-0.5">•</span>
              <span>{reason.description}</span>
            </div>
          ))}
        </div>

        {/* Historical Analogies */}
        {intelligence.historical_analogies.length > 0 && (
          <div className="pt-2 border-t border-[#1f2229]">
            <div className="text-xs text-gray-400 mb-1.5">Historical Patterns:</div>
            <div className="flex gap-2">
              {intelligence.historical_analogies.slice(0, 3).map((analogy, idx) => (
                <div 
                  key={idx}
                  className={`px-2 py-1 rounded text-xs font-medium ${
                    analogy.outcome === 'bullish' 
                      ? 'bg-emerald-400/10 text-emerald-400' 
                      : analogy.outcome === 'bearish'
                      ? 'bg-red-400/10 text-red-400'
                      : 'bg-gray-400/10 text-gray-400'
                  }`}
                >
                  {analogy.price_change_percent >= 0 ? '+' : ''}{analogy.price_change_percent}%
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Footer with Tags */}
      <div className="flex items-center justify-between mt-4 pt-3 border-t border-[#1f2229]">
        <div className="flex gap-1.5">
          {signal.tags.slice(0, 3).map((tag, idx) => (
            <span 
              key={idx}
              className="px-2 py-0.5 rounded text-xs bg-[#1f2229] text-gray-400"
            >
              #{tag}
            </span>
          ))}
        </div>
        <ChevronRight className="w-4 h-4 text-gray-500" />
      </div>
    </div>
  );
}
