'use client';

import { useState, useEffect, useCallback } from 'react';
import SignalCard from '../components/SignalCard';
import TickerTable from '../components/TickerTable';
import Header from '../components/Header';
import StatsPanel from '../components/StatsPanel';

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

interface Ticker {
  symbol: string;
  exchange: string;
  price: number;
  price_change_percent_24h: number;
  volume_24h: number;
}

export default function Home() {
  const [signals, setSignals] = useState<Signal[]>([]);
  const [tickers, setTickers] = useState<Ticker[]>([]);
  const [connected, setConnected] = useState(false);
  const [stats, setStats] = useState({ pump: 0, dump: 0, breakout: 0 });

  const connectWebSocket = useCallback(() => {
    const ws = new WebSocket('ws://localhost:8000/ws');

    ws.onopen = () => {
      setConnected(true);
      console.log('Connected to server');
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.type === 'init') {
        setSignals(data.data.signals || []);
        setTickers(data.data.tickers || []);
      } else if (data.type === 'signal') {
        setSignals(prev => [data.data, ...prev].slice(0, 50));
      } else if (data.type === 'tickers') {
        setTickers(data.data || []);
      }
    };

    ws.onclose = () => {
      setConnected(false);
      setTimeout(connectWebSocket, 3000);
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    return ws;
  }, []);

  useEffect(() => {
    const ws = connectWebSocket();
    
    // Fetch initial data
    fetch('/api/signals?limit=20')
      .then(res => res.json())
      .then(data => setSignals(data))
      .catch(console.error);

    fetch('/api/tickers')
      .then(res => res.json())
      .then(data => setTickers(data))
      .catch(console.error);

    return () => ws.close();
  }, [connectWebSocket]);

  useEffect(() => {
    setStats({
      pump: signals.filter(s => s.type === 'pump').length,
      dump: signals.filter(s => s.type === 'dump').length,
      breakout: signals.filter(s => s.type === 'breakout').length,
    });
  }, [signals]);

  return (
    <div className="min-h-screen bg-background">
      <Header connected={connected} />
      
      <main className="container mx-auto px-4 py-6">
        {/* Stats Panel */}
        <StatsPanel stats={stats} signalsCount={signals.length} />

        {/* Main Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-6">
          {/* Signals Column */}
          <div className="lg:col-span-2 space-y-4">
            <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
              <span className="w-2 h-2 bg-primary rounded-full animate-pulse"></span>
              Live Signals
            </h2>
            
            {signals.length === 0 ? (
              <div className="card text-center py-12">
                <p className="text-gray-400">Waiting for signals...</p>
                <p className="text-sm text-gray-500 mt-2">Signals will appear here when detected</p>
              </div>
            ) : (
              signals.map(signal => (
                <SignalCard key={signal.id} signal={signal} />
              ))
            )}
          </div>

          {/* Tickers Column */}
          <div className="lg:col-span-1">
            <h2 className="text-xl font-bold text-white mb-4">Market Overview</h2>
            <TickerTable tickers={tickers} />
          </div>
        </div>
      </main>
    </div>
  );
}
