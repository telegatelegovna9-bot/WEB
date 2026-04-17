interface StatsPanelProps {
  stats: {
    pump: number;
    dump: number;
    breakout: number;
  };
  signalsCount: number;
}

export default function StatsPanel({ stats, signalsCount }: StatsPanelProps) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      {/* Total Signals */}
      <div className="card bg-gradient-to-br from-primary/20 to-primary/5 border-primary/30">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-primary/20 rounded-lg flex items-center justify-center">
            <svg className="w-5 h-5 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </div>
          <div>
            <p className="text-xs text-gray-400">Total Signals</p>
            <p className="text-xl font-bold text-white">{signalsCount}</p>
          </div>
        </div>
      </div>

      {/* Pump Signals */}
      <div className="card bg-gradient-to-br from-success/20 to-success/5 border-success/30">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-success/20 rounded-lg flex items-center justify-center">
            <span className="text-xl">🚀</span>
          </div>
          <div>
            <p className="text-xs text-gray-400">Pump Signals</p>
            <p className="text-xl font-bold text-success">{stats.pump}</p>
          </div>
        </div>
      </div>

      {/* Dump Signals */}
      <div className="card bg-gradient-to-br from-danger/20 to-danger/5 border-danger/30">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-danger/20 rounded-lg flex items-center justify-center">
            <span className="text-xl">📉</span>
          </div>
          <div>
            <p className="text-xs text-gray-400">Dump Signals</p>
            <p className="text-xl font-bold text-danger">{stats.dump}</p>
          </div>
        </div>
      </div>

      {/* Breakout Signals */}
      <div className="card bg-gradient-to-br from-accent/20 to-accent/5 border-accent/30">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-accent/20 rounded-lg flex items-center justify-center">
            <span className="text-xl">💥</span>
          </div>
          <div>
            <p className="text-xs text-gray-400">Breakouts</p>
            <p className="text-xl font-bold text-accent">{stats.breakout}</p>
          </div>
        </div>
      </div>
    </div>
  );
}
