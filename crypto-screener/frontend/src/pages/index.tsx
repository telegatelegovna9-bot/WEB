'use client';

import { EnhancedSignalCard } from '@/components/EnhancedSignalCard';
import { MarketHeatmap } from '@/components/MarketHeatmap';
import { DashboardStats } from '@/components/DashboardStats';
import { ConnectionStatus } from '@/components/ConnectionStatus';
import { useMarketStore } from '@/store/marketStore';
import { useWebSocket } from '@/hooks/useWebSocket';
import { useState } from 'react';

type Tab = 'signals' | 'heatmap' | 'overview';

export default function Dashboard() {
  const { isConnected, error } = useWebSocket();
  const signals = useMarketStore((state) => state.signals);
  const tickers = useMarketStore((state) => state.tickers);
  const [activeTab, setActiveTab] = useState<Tab>('signals');

  return (
    <div className="min-h-screen bg-gradient-to-br from-crypto-dark via-slate-900 to-crypto-card text-white">
      {/* Header */}
      <header className="border-b border-white/10 backdrop-blur-sm bg-white/5 sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 via-purple-500 to-pink-500 bg-clip-text text-transparent">
                CryptoScreener AI
              </h1>
              <p className="text-sm text-gray-400 mt-1">
                Intelligent Market Analysis & Signal Detection Platform
              </p>
            </div>
            
            <div className="flex items-center gap-6">
              <div className="hidden md:block text-right">
                <p className="text-xs text-gray-400">Active Signals</p>
                <p className="text-xl font-bold text-green-400">{signals.length}</p>
              </div>
              <div className="hidden md:block text-right">
                <p className="text-xs text-gray-400">Monitored Pairs</p>
                <p className="text-xl font-bold text-blue-400">{Object.keys(tickers).length}</p>
              </div>
              <ConnectionStatus connected={isConnected} />
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-6">
        {/* Error Banner */}
        {error && (
          <div className="mb-6 p-4 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 animate-pulse">
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

        {/* Stats Overview */}
        <DashboardStats />

        {/* Tab Navigation */}
        <div className="flex items-center gap-2 mb-6 border-b border-white/10">
          <button
            onClick={() => setActiveTab('signals')}
            className={`px-4 py-2 rounded-t-lg font-medium transition-colors ${
              activeTab === 'signals'
                ? 'bg-white/10 text-white border-t border-l border-r border-white/20'
                : 'text-gray-400 hover:text-white hover:bg-white/5'
            }`}
          >
            📡 Live Signals
          </button>
          <button
            onClick={() => setActiveTab('heatmap')}
            className={`px-4 py-2 rounded-t-lg font-medium transition-colors ${
              activeTab === 'heatmap'
                ? 'bg-white/10 text-white border-t border-l border-r border-white/20'
                : 'text-gray-400 hover:text-white hover:bg-white/5'
            }`}
          >
            🔥 Market Heatmap
          </button>
        </div>

        {/* Tab Content */}
        {activeTab === 'signals' && (
          <section className="glass-panel rounded-xl border border-white/10 overflow-hidden">
            <div className="p-4 border-b border-white/10 bg-gradient-to-r from-blue-500/10 to-purple-500/10">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
                  Real-Time AI Signals
                </h2>
                <span className="text-xs text-gray-400 flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-blue-500 animate-pulse"></span>
                  Updated live
                </span>
              </div>
            </div>
            <div className="p-4">
              <EnhancedSignalCard />
            </div>
          </section>
        )}

        {activeTab === 'heatmap' && (
          <section className="space-y-6">
            <MarketHeatmap />
            
            {/* Quick Info Panel */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="glass-panel rounded-xl border border-white/10 p-4">
                <h3 className="font-semibold mb-2 flex items-center gap-2">
                  <span>🧠</span>
                  AI Intelligence
                </h3>
                <ul className="space-y-2 text-sm text-gray-300">
                  <li className="flex items-start gap-2">
                    <span className="text-green-400 mt-0.5">✓</span>
                    Real-time pattern recognition across 6+ exchanges
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-green-400 mt-0.5">✓</span>
                    Smart money flow detection & analysis
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-green-400 mt-0.5">✓</span>
                    Historical pattern matching with outcome tracking
                  </li>
                </ul>
              </div>

              <div className="glass-panel rounded-xl border border-white/10 p-4">
                <h3 className="font-semibold mb-2 flex items-center gap-2">
                  <span>⚙️</span>
                  Active Strategies
                </h3>
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-400">Pump/Dump Detector</span>
                    <span className="px-2 py-0.5 rounded bg-green-500/20 text-green-400 text-xs">Active</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-400">Order Book Density</span>
                    <span className="px-2 py-0.5 rounded bg-green-500/20 text-green-400 text-xs">Active</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-400">Breakout Pattern</span>
                    <span className="px-2 py-0.5 rounded bg-yellow-500/20 text-yellow-400 text-xs">Beta</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-400">Listing Detector</span>
                    <span className="px-2 py-0.5 rounded bg-gray-500/20 text-gray-400 text-xs">Coming Soon</span>
                  </div>
                </div>
              </div>

              <div className="glass-panel rounded-xl border border-white/10 p-4 bg-gradient-to-br from-purple-500/10 to-blue-500/10">
                <h3 className="font-semibold mb-2 flex items-center gap-2">
                  <span>📊</span>
                  Platform Metrics
                </h3>
                <div className="space-y-3 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-400">Avg Latency</span>
                    <span className="text-green-400 font-mono">&lt;100ms</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Signal Accuracy</span>
                    <span className="text-blue-400 font-mono">AI-Enhanced</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Exchanges</span>
                    <span className="text-purple-400 font-mono">6 Connected</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Update Frequency</span>
                    <span className="text-yellow-400 font-mono">Real-time</span>
                  </div>
                </div>
              </div>
            </div>
          </section>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-white/10 mt-12 py-6">
        <div className="container mx-auto px-4">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4 text-sm text-gray-500">
            <div>
              <p className="font-medium text-gray-400">CryptoScreener AI — Professional Market Analysis Platform</p>
              <p className="text-xs mt-1">
                Data updated in real-time • Multi-exchange support • AI-powered insights
              </p>
            </div>
            <div className="flex items-center gap-4">
              <span className="flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
                System Operational
              </span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
