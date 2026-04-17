'use client';

import { useState, useEffect } from 'react';
import SignalCard from '@/components/SignalCard';
import StatsPanel from '@/components/StatsPanel';
import Header from '@/components/Header';

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

export default function Home() {
  const [signals, setSignals] = useState<Signal[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>('all');
  const [wsConnected, setWsConnected] = useState(false);

  useEffect(() => {
    fetchSignals();
    connectWebSocket();
  }, []);

  const fetchSignals = async () => {
    try {
      const res = await fetch('/api/signals?limit=50');
      if (res.ok) {
        const data = await res.json();
        setSignals(data);
      }
    } catch (error) {
      console.error('Error fetching signals:', error);
    } finally {
      setLoading(false);
    }
  };

  const connectWebSocket = () => {
    const ws = new WebSocket('ws://localhost:8000/ws/signals');

    ws.onopen = () => {
      setWsConnected(true);
      console.log('WebSocket connected');
    };

    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        if (message.type === 'new_signal') {
          setSignals((prev) => [message.data, ...prev.slice(0, 49)]);
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };

    ws.onclose = () => {
      setWsConnected(false);
      console.log('WebSocket disconnected');
      setTimeout(connectWebSocket, 5000);
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    // Keep connection alive
    const pingInterval = setInterval(() => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send('ping');
      }
    }, 30000);

    return () => clearInterval(pingInterval);
  };

  const filteredSignals = filter === 'all' 
    ? signals 
    : signals.filter(s => s.signal_type === filter);

  const getSignalTypeCount = (type: string) => {
    return signals.filter(s => s.signal_type === type).length;
  };

  return (
    <main className="min-h-screen p-4 md:p-8">
      <Header wsConnected={wsConnected} />
      
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Stats Panel */}
        <StatsPanel 
          totalSignals={signals.length}
          pumpCount={getSignalTypeCount('pump')}
          dumpCount={getSignalTypeCount('dump')}
          volumeCount={getSignalTypeCount('volume_spike')}
          orderBookCount={getSignalTypeCount('order_book_wall')}
        />

        {/* Filter Buttons */}
        <div className="flex flex-wrap gap-2">
          {['all', 'pump', 'dump', 'volume_spike', 'order_book_wall'].map((type) => (
            <button
              key={type}
              onClick={() => setFilter(type)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                filter === type
                  ? 'bg-gradient-to-r from-emerald-500 to-violet-500 text-white'
                  : 'glass-card text-gray-400 hover:text-white'
              }`}
            >
              {type === 'all' ? 'All Signals' : type.replace('_', ' ')}
              {type !== 'all' && (
                <span className="ml-2 opacity-70">({getSignalTypeCount(type)})</span>
              )}
            </button>
          ))}
        </div>

        {/* Signals Grid */}
        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-500"></div>
            <p className="mt-4 text-gray-400">Loading signals...</p>
          </div>
        ) : filteredSignals.length === 0 ? (
          <div className="glass-card p-12 text-center">
            <p className="text-gray-400 text-lg">No signals yet</p>
            <p className="text-gray-500 text-sm mt-2">Waiting for market opportunities...</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {filteredSignals.map((signal) => (
              <SignalCard key={signal.signal_id} signal={signal} />
            ))}
          </div>
        )}
      </div>
    </main>
  );
}
