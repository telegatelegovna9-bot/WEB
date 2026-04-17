import { TrendingUp, TrendingDown, Brain, Target, History, AlertCircle } from 'lucide-react';

interface Signal {
  signal_id: string;
  signal_type: string;
  symbol: string;
  exchange: string;
  price: number;
  price_change_percent: number;
  volume: number;
  volume_change_percent: number;
  confidence_score: number;
  explanation: {
    reasons: string[];
    market_behavior: string;
    smart_money_activity: boolean;
    large_orders_detected: boolean;
    order_book_changes: string[];
    recommendation?: string;
  };
  historical_analogies: Array<{
    similarity_score: number;
    outcome: string;
    price_change_after: number;
    date: string;
    symbol: string;
    timeframe: string;
  }>;
  probability_assessment?: {
    success_probability: number;
    outlook: string;
    risk_level: string;
    factors: {
      confidence_factor: number;
      historical_factor: number;
    };
  };
  created_at: string;
}

interface SignalCardProps {
  signal: Signal;
}

export default function SignalCard({ signal }: SignalCardProps) {
  const getSignalColor = () => {
    switch (signal.signal_type) {
      case 'pump': return 'text-emerald-400';
      case 'dump': return 'text-red-400';
      case 'volume_spike': return 'text-yellow-400';
      case 'order_book_wall': return 'text-violet-400';
      default: return 'text-gray-400';
    }
  };

  const getSignalIcon = () => {
    switch (signal.signal_type) {
      case 'pump': return <TrendingUp size={20} />;
      case 'dump': return <TrendingDown size={20} />;
      case 'volume_spike': return <AlertCircle size={20} />;
      case 'order_book_wall': return <Brain size={20} />;
      default: return <AlertCircle size={20} />;
    }
  };

  const getConfidenceClass = (score: number) => {
    if (score >= 70) return 'confidence-high';
    if (score >= 40) return 'confidence-medium';
    return 'confidence-low';
  };

  const getBehaviorColor = (behavior: string) => {
    switch (behavior) {
      case 'accumulation': return 'text-emerald-400';
      case 'distribution': return 'text-red-400';
      case 'breakout': return 'text-yellow-400';
      case 'manipulation': return 'text-violet-400';
      default: return 'text-gray-400';
    }
  };

  return (
    <div className={`glass-card p-5 signal-card ${signal.signal_type}`}>
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className={`p-2 rounded-lg glass-card ${getSignalColor()}`}>
            {getSignalIcon()}
          </div>
          <div>
            <h3 className="text-lg font-bold text-white">
              {signal.symbol}
            </h3>
            <p className="text-xs text-gray-400 capitalize">
              {signal.signal_type.replace('_', ' ')} • {signal.exchange}
            </p>
          </div>
        </div>
        <div className="text-right">
          <p className="text-xl font-bold text-white">
            ${signal.price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 6 })}
          </p>
          <p className={`text-sm font-medium ${signal.price_change_percent >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
            {signal.price_change_percent >= 0 ? '+' : ''}{signal.price_change_percent.toFixed(2)}%
          </p>
        </div>
      </div>

      {/* Confidence Meter */}
      <div className="mb-4">
        <div className="flex items-center justify-between mb-1">
          <span className="text-xs text-gray-400">Confidence Score</span>
          <span className="text-sm font-bold text-white">{signal.confidence_score}%</span>
        </div>
        <div className="confidence-meter">
          <div 
            className={`confidence-fill ${getConfidenceClass(signal.confidence_score)}`}
            style={{ width: `${signal.confidence_score}%` }}
          />
        </div>
      </div>

      {/* Explanation */}
      <div className="mb-4">
        <h4 className="text-sm font-semibold text-white mb-2 flex items-center gap-2">
          <Brain size={14} className="text-violet-400" />
          AI Analysis
        </h4>
        <ul className="space-y-1">
          {signal.explanation.reasons.slice(0, 3).map((reason, idx) => (
            <li key={idx} className="text-xs text-gray-300 flex items-start gap-2">
              <span className="text-emerald-400 mt-0.5">•</span>
              {reason}
            </li>
          ))}
        </ul>
      </div>

      {/* Market Behavior & Smart Money */}
      <div className="grid grid-cols-2 gap-3 mb-4">
        <div className="glass-card p-3">
          <p className="text-xs text-gray-400 mb-1">Market Behavior</p>
          <p className={`text-sm font-semibold capitalize ${getBehaviorColor(signal.explanation.market_behavior)}`}>
            {signal.explanation.market_behavior}
          </p>
        </div>
        <div className="glass-card p-3">
          <p className="text-xs text-gray-400 mb-1">Smart Money</p>
          <p className={`text-sm font-semibold ${signal.explanation.smart_money_activity ? 'text-emerald-400' : 'text-gray-500'}`}>
            {signal.explanation.smart_money_activity ? 'Detected ✓' : 'Not Detected'}
          </p>
        </div>
      </div>

      {/* Historical Analogies */}
      {signal.historical_analogies && signal.historical_analogies.length > 0 && (
        <div className="mb-4">
          <h4 className="text-sm font-semibold text-white mb-2 flex items-center gap-2">
            <History size={14} className="text-blue-400" />
            Historical Analogies
          </h4>
          <div className="space-y-2">
            {signal.historical_analogies.slice(0, 2).map((analogy, idx) => (
              <div key={idx} className="glass-card p-2 text-xs">
                <div className="flex items-center justify-between">
                  <span className="text-gray-400">{analogy.symbol} • {analogy.timeframe}</span>
                  <span className={`font-medium ${analogy.outcome === 'success' ? 'text-emerald-400' : analogy.outcome === 'failure' ? 'text-red-400' : 'text-gray-400'}`}>
                    {analogy.outcome} ({analogy.similarity_score * 100}% match)
                  </span>
                </div>
                <p className="text-gray-300 mt-1">
                  After: {analogy.price_change_after >= 0 ? '+' : ''}{analogy.price_change_after}%
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Probability Assessment */}
      {signal.probability_assessment && (
        <div className="glass-card p-3">
          <div className="flex items-center gap-2 mb-2">
            <Target size={14} className="text-violet-400" />
            <span className="text-xs font-semibold text-white">Probability Assessment</span>
          </div>
          <div className="grid grid-cols-3 gap-2 text-center">
            <div>
              <p className="text-xs text-gray-400">Success Rate</p>
              <p className="text-sm font-bold text-white">{signal.probability_assessment.success_probability}%</p>
            </div>
            <div>
              <p className="text-xs text-gray-400">Outlook</p>
              <p className="text-sm font-bold text-white capitalize">{signal.probability_assessment.outlook.replace('_', ' ')}</p>
            </div>
            <div>
              <p className="text-xs text-gray-400">Risk</p>
              <p className={`text-sm font-bold capitalize ${
                signal.probability_assessment.risk_level === 'low' ? 'text-emerald-400' :
                signal.probability_assessment.risk_level === 'medium' ? 'text-yellow-400' : 'text-red-400'
              }`}>
                {signal.probability_assessment.risk_level}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Recommendation */}
      {signal.explanation.recommendation && (
        <div className="mt-4 p-3 bg-gradient-to-r from-emerald-500/10 to-violet-500/10 rounded-lg border border-emerald-500/20">
          <p className="text-xs text-gray-300">
            <span className="font-semibold text-emerald-400">Recommendation:</span> {signal.explanation.recommendation}
          </p>
        </div>
      )}

      {/* Timestamp */}
      <p className="text-xs text-gray-500 mt-3 text-right">
        {new Date(signal.created_at).toLocaleString()}
      </p>
    </div>
  );
}
