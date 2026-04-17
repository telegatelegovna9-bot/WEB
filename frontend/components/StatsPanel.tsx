import { TrendingUp, TrendingDown, Activity, Layers } from 'lucide-react';

interface StatsPanelProps {
  totalSignals: number;
  pumpCount: number;
  dumpCount: number;
  volumeCount: number;
  orderBookCount: number;
}

export default function StatsPanel({ 
  totalSignals, 
  pumpCount, 
  dumpCount, 
  volumeCount, 
  orderBookCount 
}: StatsPanelProps) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
      <StatCard
        label="Total Signals"
        value={totalSignals}
        icon={<Activity size={20} />}
        color="from-violet-500 to-purple-500"
      />
      <StatCard
        label="Pump Detected"
        value={pumpCount}
        icon={<TrendingUp size={20} />}
        color="from-emerald-500 to-green-500"
      />
      <StatCard
        label="Dump Detected"
        value={dumpCount}
        icon={<TrendingDown size={20} />}
        color="from-red-500 to-rose-500"
      />
      <StatCard
        label="Volume Spikes"
        value={volumeCount}
        icon={<Activity size={20} />}
        color="from-yellow-500 to-orange-500"
      />
      <StatCard
        label="Order Walls"
        value={orderBookCount}
        icon={<Layers size={20} />}
        color="from-blue-500 to-cyan-500"
      />
    </div>
  );
}

interface StatCardProps {
  label: string;
  value: number;
  icon: React.ReactNode;
  color: string;
}

function StatCard({ label, value, icon, color }: StatCardProps) {
  return (
    <div className="glass-card p-4">
      <div className="flex items-center justify-between mb-2">
        <span className={`bg-gradient-to-r ${color} p-2 rounded-lg text-white`}>
          {icon}
        </span>
      </div>
      <p className="text-2xl font-bold text-white">{value}</p>
      <p className="text-xs text-gray-400 mt-1">{label}</p>
    </div>
  );
}
