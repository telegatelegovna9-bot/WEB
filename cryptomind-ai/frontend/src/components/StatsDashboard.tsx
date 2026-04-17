'use client';

import { useEffect, useState } from 'react';
import { SignalStats } from '@/services/api';
import { apiService } from '@/services/api';

interface StatsCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  trend?: 'up' | 'down' | 'neutral';
}

function StatCard({ title, value, subtitle, trend }: StatsCardProps) {
  return (
    <div className="glass-card p-4">
      <div className="text-sm text-gray-400 mb-1">{title}</div>
      <div className="text-2xl font-bold">{value}</div>
      {subtitle && (
        <div className={`text-xs mt-1 ${trend === 'up' ? 'text-green-400' : trend === 'down' ? 'text-red-400' : 'text-gray-500'}`}>
          {subtitle}
        </div>
      )}
    </div>
  );
}

export function StatsDashboard() {
  const [stats, setStats] = useState<SignalStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const data = await apiService.getSignalStats(24);
        setStats(data);
      } catch (error) {
        console.error('Failed to fetch stats:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
    
    // Refresh every minute
    const interval = setInterval(fetchStats, 60000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="glass-card p-4 animate-pulse">
            <div className="h-4 bg-white/10 rounded w-24 mb-2"></div>
            <div className="h-8 bg-white/10 rounded w-16"></div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      <StatCard
        title="Total Signals (24h)"
        value={stats?.total_signals || 0}
        subtitle="Last 24 hours"
      />
      <StatCard
        title="Accuracy Rate"
        value={`${(stats?.accuracy_rate || 0).toFixed(1)}%`}
        trend={stats && stats.accuracy_rate >= 60 ? 'up' : 'down'}
        subtitle={stats && stats.accuracy_rate >= 60 ? 'Good performance' : 'Needs improvement'}
      />
      <StatCard
        title="Win Rate"
        value={`${(stats?.win_rate || 0).toFixed(1)}%`}
        trend={stats && stats.win_rate >= 50 ? 'up' : 'down'}
      />
      <StatCard
        title="Avg Confidence"
        value={`${(stats?.avg_confidence || 0).toFixed(0)}%`}
        trend={stats && stats.avg_confidence >= 60 ? 'up' : 'neutral'}
      />
    </div>
  );
}
