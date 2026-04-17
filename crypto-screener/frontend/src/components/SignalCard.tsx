interface Signal {
  id: string;
  type: string;
  symbol: string;
  exchange: string;
  price: number;
  price_change_percent: number;
  volume_change_percent: number;
  intelligence: {
    reasons: Array<{ type: string; description: string; value?: number }>;
    market_behavior: string;
    probability_score: number;
    confidence_level: string;
  };
  created_at: string;
}

interface SignalCardProps {
  signal: Signal;
}

const typeColors = {
  pump: 'bg-success/20 text-success border-success/30',
  dump: 'bg-danger/20 text-danger border-danger/30',
  breakout: 'bg-accent/20 text-accent border-accent/30',
  order_wall: 'bg-warning/20 text-warning border-warning/30',
};

const typeLabels = {
  pump: '🚀 Pump',
  dump: '📉 Dump',
  breakout: '💥 Breakout',
  order_wall: '🧱 Order Wall',
};

export default function SignalCard({ signal }: SignalCardProps) {
  const colorClass = typeColors[signal.type as keyof typeof typeColors] || typeColors.breakout;
  const label = typeLabels[signal.type as keyof typeof typeLabels] || signal.type;

  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleTimeString();
  };

  const getProbabilityColor = (score: number) => {
    if (score >= 75) return 'text-success';
    if (score >= 50) return 'text-warning';
    return 'text-danger';
  };

  const formatBehavior = (behavior: string) => {
    return behavior
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  return (
    <div className="card border-l-4 border-l-primary hover:border-l-accent transition-all duration-300">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <span className={`px-3 py-1 rounded-full text-sm font-semibold ${colorClass}`}>
            {label}
          </span>
          <div>
            <h3 className="text-lg font-bold text-white">{signal.symbol}</h3>
            <p className="text-xs text-gray-400 uppercase">{signal.exchange}</p>
          </div>
        </div>
        <div className="text-right">
          <p className="text-lg font-bold text-white">${signal.price.toLocaleString()}</p>
          <p className={`text-sm ${signal.price_change_percent >= 0 ? 'text-success' : 'text-danger'}`}>
            {signal.price_change_percent >= 0 ? '+' : ''}{signal.price_change_percent.toFixed(2)}%
          </p>
        </div>
      </div>

      {/* Intelligence Section */}
      <div className="bg-surface2 rounded-lg p-4 mb-4">
        <div className="grid grid-cols-2 gap-4 mb-4">
          {/* Probability Score */}
          <div>
            <p className="text-xs text-gray-400 mb-1">Probability Score</p>
            <div className="flex items-center gap-2">
              <div className="flex-1 h-2 bg-background rounded-full overflow-hidden">
                <div 
                  className={`h-full rounded-full ${
                    signal.intelligence.probability_score >= 75 ? 'bg-success' :
                    signal.intelligence.probability_score >= 50 ? 'bg-warning' : 'bg-danger'
                  }`}
                  style={{ width: `${signal.intelligence.probability_score}%` }}
                />
              </div>
              <span className={`text-sm font-bold ${getProbabilityColor(signal.intelligence.probability_score)}`}>
                {signal.intelligence.probability_score.toFixed(0)}%
              </span>
            </div>
          </div>

          {/* Market Behavior */}
          <div>
            <p className="text-xs text-gray-400 mb-1">Market Behavior</p>
            <p className="text-sm font-medium text-white">
              {formatBehavior(signal.intelligence.market_behavior)}
            </p>
          </div>
        </div>

        {/* Reasons */}
        <div className="space-y-2">
          <p className="text-xs text-gray-400">Detected Reasons:</p>
          {signal.intelligence.reasons.map((reason, index) => (
            <div key={index} className="flex items-center gap-2 text-sm">
              <span className="w-1.5 h-1.5 bg-primary rounded-full"></span>
              <span className="text-gray-300">{reason.description}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Footer */}
      <div className="flex items-center justify-between text-xs text-gray-500">
        <span>Volume: {signal.volume_change_percent >= 0 ? '+' : ''}{signal.volume_change_percent.toFixed(0)}%</span>
        <span>{formatTime(signal.created_at)}</span>
      </div>
    </div>
  );
}
