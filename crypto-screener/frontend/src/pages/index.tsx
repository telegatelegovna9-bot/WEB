'use client';

import { SignalCard } from '@/components/SignalCard';
import { TickerList } from '@/components/TickerList';
import { ConnectionStatus } from '@/components/ConnectionStatus';
import { useMarketStore } from '@/store/marketStore';
import { useWebSocket } from '@/hooks/useWebSocket';

export default function Dashboard() {
  const { isConnected, error } = useWebSocket();
  const signals = useMarketStore((state) => state.signals);
  const tickers = useMarketStore((state) => state.tickers);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-slate-900 to-gray-900 text-white">
      {/* Header */}
      <header className="border-b border-white/10 backdrop-blur-sm bg-white/5 sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
                CryptoScreener AI
              </h1>
              <p className="text-sm text-gray-400 mt-1">
                Intelligent Market Analysis & Signal Detection
              </p>
            </div>
            
            <div className="flex items-center gap-4">
              <ConnectionStatus connected={isConnected} />
              <div className="text-right">
                <p className="text-xs text-gray-400">Active Signals</p>
                <p className="text-xl font-bold text-green-400">{signals.length}</p>
              </div>
              <div className="text-right">
                <p className="text-xs text-gray-400">Monitored Pairs</p>
                <p className="text-xl font-bold text-blue-400">{tickers.length}</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-6">
        {/* Error Banner */}
        {error && (
          <div className="mb-6 p-4 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400">
            <p className="flex items-center gap-2">
              <span>⚠️</span>
              {error}
            </p>
          </div>
        )}

        {/* Connection Warning */}
        {!isConnected && !error && (
          <div className="mb-6 p-4 rounded-lg bg-yellow-500/10 border border-yellow-500/30 text-yellow-400">
            <p className="flex items-center gap-2">
              <span>📡</span>
              Connecting to market data...
            </p>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Signals */}
          <div className="lg:col-span-2 space-y-6">
            {/* Signals Panel */}
            <section className="rounded-xl border border-white/10 backdrop-blur-sm bg-white/5 overflow-hidden">
              <div className="p-4 border-b border-white/10">
                <div className="flex items-center justify-between">
                  <h2 className="text-lg font-semibold flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
                    Live Signals
                  </h2>
                  <span className="text-xs text-gray-400">
                    Real-time AI-powered detection
                  </span>
                </div>
              </div>
              <div className="p-4">
                <SignalCard />
              </div>
            </section>

            {/* Market Overview Stats */}
            <section className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="rounded-xl border border-white/10 backdrop-blur-sm bg-white/5 p-4">
                <p className="text-xs text-gray-400 mb-1">Pump Signals (24h)</p>
                <p className="text-2xl font-bold text-green-400">
                  {signals.filter(s => s.type === 'pump').length}
                </p>
              </div>
              <div className="rounded-xl border border-white/10 backdrop-blur-sm bg-white/5 p-4">
                <p className="text-xs text-gray-400 mb-1">Dump Signals (24h)</p>
                <p className="text-2xl font-bold text-red-400">
                  {signals.filter(s => s.type === 'dump').length}
                </p>
              </div>
              <div className="rounded-xl border border-white/10 backdrop-blur-sm bg-white/5 p-4">
                <p className="text-xs text-gray-400 mb-1">Order Book Walls</p>
                <p className="text-2xl font-bold text-blue-400">
                  {signals.filter(s => s.type === 'order_book_wall').length}
                </p>
              </div>
              <div className="rounded-xl border border-white/10 backdrop-blur-sm bg-white/5 p-4">
                <p className="text-xs text-gray-400 mb-1">Avg Confidence</p>
                <p className="text-2xl font-bold text-purple-400">
                  {signals.length > 0 
                    ? Math.round(signals.reduce((acc, s) => acc + s.intelligence.confidence_score, 0) / signals.length)
                    : 0}%
                </p>
              </div>
            </section>
          </div>

          {/* Right Column - Tickers & Info */}
          <div className="space-y-6">
            {/* Ticker List */}
            <section className="rounded-xl border border-white/10 backdrop-blur-sm bg-white/5 overflow-hidden">
              <div className="p-4 border-b border-white/10">
                <h2 className="text-lg font-semibold">Market Watch</h2>
              </div>
              <div className="p-4">
                <TickerList />
              </div>
            </section>

            {/* Intelligence Info */}
            <section className="rounded-xl border border-white/10 backdrop-blur-sm bg-gradient-to-br from-purple-500/10 to-blue-500/10 p-4">
              <h3 className="font-semibold mb-3 flex items-center gap-2">
                <span>🧠</span>
                AI Intelligence
              </h3>
              <div className="space-y-3 text-sm text-gray-300">
                <div className="flex items-start gap-2">
                  <span className="text-green-400 mt-1">✓</span>
                  <p>Real-time pattern recognition across 6+ exchanges</p>
                </div>
                <div className="flex items-start gap-2">
                  <span className="text-green-400 mt-1">✓</span>
                  <p>Smart money flow detection & analysis</p>
                </div>
                <div className="flex items-start gap-2">
                  <span className="text-green-400 mt-1">✓</span>
                  <p>Historical pattern matching with outcome tracking</p>
                </div>
                <div className="flex items-start gap-2">
                  <span className="text-green-400 mt-1">✓</span>
                  <p>Probability scoring based on multiple factors</p>
                </div>
              </div>
            </section>

            {/* Strategy Info */}
            <section className="rounded-xl border border-white/10 backdrop-blur-sm bg-white/5 p-4">
              <h3 className="font-semibold mb-3">Active Strategies</h3>
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-400">Pump/Dump Detector</span>
                  <span className="px-2 py-1 rounded bg-green-500/20 text-green-400 text-xs">Active</span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-400">Order Book Density</span>
                  <span className="px-2 py-1 rounded bg-green-500/20 text-green-400 text-xs">Active</span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-400">Breakout Pattern</span>
                  <span className="px-2 py-1 rounded bg-yellow-500/20 text-yellow-400 text-xs">Beta</span>
                </div>
              </div>
            </section>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-white/10 mt-12 py-6">
        <div className="container mx-auto px-4 text-center text-sm text-gray-500">
          <p>CryptoScreener AI — Professional Market Analysis Platform</p>
          <p className="mt-1 text-xs">
            Data updated in real-time • Latency: &lt;100ms • Accuracy: AI-enhanced
          </p>
        </div>
      </footer>
    </div>
  );
}
