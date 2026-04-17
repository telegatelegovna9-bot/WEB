import { Activity, Zap, TrendingUp, Wifi, WifiOff } from 'lucide-react';

interface HeaderProps {
  wsConnected: boolean;
}

export default function Header({ wsConnected }: HeaderProps) {
  return (
    <header className="mb-8">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl md:text-4xl font-bold gradient-text">
            CryptoMind AI
          </h1>
          <p className="text-gray-400 mt-2 text-sm md:text-base">
            Intelligent Crypto Signals & Market Analysis
          </p>
        </div>
        
        <div className="flex items-center gap-4">
          {/* Connection Status */}
          <div className={`flex items-center gap-2 px-4 py-2 rounded-lg glass-card ${
            wsConnected ? 'text-emerald-400' : 'text-red-400'
          }`}>
            {wsConnected ? <Wifi size={18} /> : <WifiOff size={18} />}
            <span className="text-sm font-medium">
              {wsConnected ? 'Live' : 'Disconnected'}
            </span>
          </div>
          
          {/* Platform Status */}
          <div className="hidden md:flex items-center gap-2 px-4 py-2 rounded-lg glass-card text-violet-400">
            <Activity size={18} />
            <span className="text-sm font-medium">AI Active</span>
          </div>
        </div>
      </div>
      
      {/* Feature Highlights */}
      <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-3">
        <FeatureBadge 
          icon={<Zap size={16} />}
          label="Real-time Detection"
          color="text-yellow-400"
        />
        <FeatureBadge 
          icon={<TrendingUp size={16} />}
          label="Smart Money Tracking"
          color="text-emerald-400"
        />
        <FeatureBadge 
          icon={<Activity size={16} />}
          label="Pattern Matching"
          color="text-violet-400"
        />
        <FeatureBadge 
          icon={<Zap size={16} />}
          label="Probability Scoring"
          color="text-blue-400"
        />
      </div>
    </header>
  );
}

interface FeatureBadgeProps {
  icon: React.ReactNode;
  label: string;
  color: string;
}

function FeatureBadge({ icon, label, color }: FeatureBadgeProps) {
  return (
    <div className="glass-card p-3 flex items-center gap-2">
      <span className={color}>{icon}</span>
      <span className="text-xs text-gray-300">{label}</span>
    </div>
  );
}
