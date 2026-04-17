'use client';

import { useEffect, useState } from 'react';
import { SignalCard } from '@/components/SignalCard';
import { StatsDashboard } from '@/components/StatsDashboard';
import { useWebSocket } from '@/hooks/useWebSocket';
import { Signal, apiService } from '@/services/api';
import { WS_URL } from '@/services/api';
import { Activity, Zap, Brain, TrendingUp } from 'lucide-react';

export default function Home() {
  const [signals, setSignals] = useState<Signal[]>([]);
  const [filter, setFilter] = useState<string>('all');
  
  // Connect to WebSocket for real-time signals
  const { isConnected, lastMessage } = useWebSocket(`${WS_URL}/signals`);

  // Load initial signals
  useEffect(() => {
    const loadSignals = async () => {
      try {
        const data = await apiService.getSignals({ limit: 50 });
        setSignals(data);
      } catch (error) {
        console.error('Failed to load signals:', error);
      }
    };

    loadSignals();
  }, []);

  // Handle new signals from WebSocket
  useEffect(() => {
    if (lastMessage && lastMessage.type === 'signal') {
      setSignals(prev => [lastMessage.data, ...prev].slice(0, 100));
    }
  }, [lastMessage]);

  // Filter signals
  const filteredSignals = signals.filter(signal => {
    if (filter === 'all') return true;
    return signal.signal_type === filter;
  });

  const getConfidenceBadge = (score: number) => {
    if (score >= 70) return '🟢 High';
    if (score >= 50) return '🟡 Medium';
    return '🔴 Low';
  };

  return (
    <main className="min-h-screen p-6">
      {/* Header */}
      <header className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
              CryptoMind AI
            </h1>
            <p className="text-gray-400 mt-2">
              Intelligent crypto signals with market behavior analysis
            </p>
          </div>
          
          <div className="flex items-center gap-4">
            <div className={`flex items-center gap-2 px-4 py-2 rounded-lg ${isConnected ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
              <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-400 animate-pulse' : 'bg-red-400'}`} />
              <span className="text-sm">{isConnected ? 'Live' : 'Disconnected'}</span>
            </div>
          </div>
        </div>

        {/* Feature badges */}
        <div className="flex gap-3 flex-wrap">
          <div className="flex items-center gap-2 px-3 py-1.5 bg-blue-500/10 border border-blue-500/30 rounded-full text-sm text-blue-400">
            <Brain size={16} />
            <span>AI Explanations</span>
          </div>
          <div className="flex items-center gap-2 px-3 py-1.5 bg-purple-500/10 border border-purple-500/30 rounded-full text-sm text-purple-400">
            <Zap size={16} />
            <span>Real-time Detection</span>
          </div>
          <div className="flex items-center gap-2 px-3 py-1.5 bg-green-500/10 border border-green-500/30 rounded-full text-sm text-green-400">
            <TrendingUp size={16} />
            <span>Pattern Matching</span>
          </div>
          <div className="flex items-center gap-2 px-3 py-1.5 bg-yellow-500/10 border border-yellow-500/30 rounded-full text-sm text-yellow-400">
            <Activity size={16} />
            <span>Smart Money Tracking</span>
          </div>
        </div>
      </header>

      {/* Stats Dashboard */}
      <StatsDashboard />

      {/* Filters */}
      <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
        {['all', 'pump', 'dump', 'orderbook_wall', 'volume_spike'].map(type => (
          <button
            key={type}
            onClick={() => setFilter(type)}
            className={`px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-colors ${
              filter === type
                ? 'bg-blue-500 text-white'
                : 'bg-white/5 text-gray-400 hover:bg-white/10'
            }`}
          >
            {type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
          </button>
        ))}
      </div>

      {/* Signals Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4">
        {filteredSignals.length === 0 ? (
          <div className="col-span-full text-center py-12 text-gray-400">
            <p>No signals yet. Waiting for market opportunities...</p>
          </div>
        ) : (
          filteredSignals.map((signal, index) => (
            <SignalCard key={signal.id || index} signal={signal} />
          ))
        )}
      </div>

      {/* Footer */}
      <footer className="mt-12 pt-6 border-t border-white/10 text-center text-sm text-gray-500">
        <p>CryptoMind AI © 2024 - Advanced Crypto Intelligence Platform</p>
        <p className="mt-1">Powered by real-time data from Binance, OKX, Bybit, MEXC, Gate, and Bitget</p>
      </footer>
    </main>
  );
}
