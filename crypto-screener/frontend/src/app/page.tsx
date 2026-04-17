'use client';

import { useState, useEffect } from 'react';
import { usePathname } from 'next/navigation';
import Link from 'next/link';
import Header from '@/components/Header';
import SignalCard from '@/components/SignalCard';
import TickerTable from '@/components/TickerTable';
import StatsPanel, { TopMovers } from '@/components/StatsPanel';
import ExchangeSelector, { SignalTypeFilter, SearchInput, ProbabilityFilter } from '@/components/Filters';
import { useWebSocket, fetchExchanges } from '@/lib/api';
import { Signal, Ticker, Exchange } from '@/lib/types';
import { Filter, Grid3X3, List, TrendingUp, Activity, Layers, PieChart, Settings, Zap } from 'lucide-react';

export default function Dashboard() {
  const pathname = usePathname();
  const { connected, tickers, signals, stats } = useWebSocket();
  const [exchanges, setExchanges] = useState<Exchange[]>([]);
  const [selectedExchanges, setSelectedExchanges] = useState<string[]>(['binance', 'okx', 'bybit', 'mexc', 'gate', 'bitget']);
  const [selectedSignalTypes, setSelectedSignalTypes] = useState<string[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [minProbability, setMinProbability] = useState(0);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [showFilters, setShowFilters] = useState(false);

  useEffect(() => {
    fetchExchanges().then(setExchanges).catch(console.error);
  }, []);

  // Filter signals
  const filteredSignals = signals.filter((signal) => {
    if (selectedExchanges.length > 0 && !selectedExchanges.includes(signal.exchange.toLowerCase())) {
      return false;
    }
    if (selectedSignalTypes.length > 0 && !selectedSignalTypes.includes(signal.type)) {
      return false;
    }
    if (searchQuery && !signal.symbol.toLowerCase().includes(searchQuery.toLowerCase())) {
      return false;
    }
    if (minProbability > 0 && signal.intelligence.probability_score < minProbability) {
      return false;
    }
    return true;
  });

  // Filter tickers
  const filteredTickers = tickers.filter((ticker) => {
    if (selectedExchanges.length > 0 && !selectedExchanges.includes(ticker.exchange.toLowerCase())) {
      return false;
    }
    if (searchQuery && !ticker.symbol.toLowerCase().includes(searchQuery.toLowerCase())) {
      return false;
    }
    return true;
  });

  // Top 6 by volume and trades
  const topByVolume = [...filteredTickers].sort((a, b) => b.quote_volume_24h - a.quote_volume_24h).slice(0, 6);
  const topByTrades = [...filteredTickers].sort((a, b) => (a.quote_volume_24h / a.price) - (b.quote_volume_24h / b.price)).slice(0, 6);

  const toggleExchange = (exchangeId: string) => {
    setSelectedExchanges(prev =>
      prev.includes(exchangeId)
        ? prev.filter(e => e !== exchangeId)
        : [...prev, exchangeId]
    );
  };

  const toggleSignalType = (type: string) => {
    setSelectedSignalTypes(prev =>
      prev.includes(type)
        ? prev.filter(t => t !== type)
        : [...prev, type]
    );
  };

  const navItems = [
    { href: '/', label: 'Dashboard', icon: Activity },
    { href: '/markets', label: 'Markets', icon: TrendingUp },
    { href: '/signals', label: 'Signals', icon: Zap },
    { href: '/patterns', label: 'Patterns', icon: Layers },
    { href: '/density', label: 'Density', icon: PieChart },
    { href: '/settings', label: 'Settings', icon: Settings },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#050608] via-[#0a0b0f] to-[#0d0e12]">
      <Header />
      
      {/* Premium Navigation */}
      <nav className="fixed left-0 top-20 h-[calc(100vh-5rem)] w-20 lg:w-64 bg-[#0a0b0f]/80 backdrop-blur-xl border-r border-[#1f2229]/50 z-40">
        <div className="p-4 space-y-2">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-3 px-3 py-3 rounded-xl transition-all duration-300 group ${
                  isActive
                    ? 'bg-gradient-to-r from-emerald-500/20 to-cyan-500/20 border border-emerald-500/30 text-white shadow-lg shadow-emerald-500/10'
                    : 'text-gray-400 hover:bg-[#1f2229]/50 hover:text-white'
                }`}
              >
                <Icon className={`w-5 h-5 ${isActive ? 'text-emerald-400' : 'group-hover:text-emerald-400 transition-colors'}`} />
                <span className="hidden lg:block font-medium">{item.label}</span>
                {isActive && (
                  <div className="hidden lg:flex ml-auto w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                )}
              </Link>
            );
          })}
        </div>
        
        {/* Connection Status in Sidebar */}
        <div className="absolute bottom-8 left-0 right-0 px-4">
          <div className={`flex items-center gap-3 px-3 py-3 rounded-xl ${
            connected ? 'bg-emerald-500/10 border border-emerald-500/20' : 'bg-red-500/10 border border-red-500/20'
          }`}>
            <div className={`w-2 h-2 rounded-full ${connected ? 'bg-emerald-400 live-indicator' : 'bg-red-400'}`}></div>
            <span className={`hidden lg:block text-sm font-medium ${connected ? 'text-emerald-400' : 'text-red-400'}`}>
              {connected ? 'Live Data' : 'Disconnected'}
            </span>
          </div>
        </div>
      </nav>

      <main className="pt-20 pl-20 lg:pl-64 pb-12">
        <div className="max-w-[1800px] mx-auto px-4 sm:px-6 lg:px-8">
          
          {/* Stats Panel */}
          <StatsPanel stats={stats} />

          {/* Top Movers */}
          <TopMovers stats={stats} />

          {/* Top 6 by Volume & Trades */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            <div className="glass rounded-xl border border-[#1f2229]/50 p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-bold text-white flex items-center gap-2">
                  <TrendingUp className="w-5 h-5 text-emerald-400" />
                  Top 6 by Volume
                </h3>
              </div>
              <div className="space-y-3">
                {topByVolume.map((ticker, idx) => (
                  <div key={ticker.symbol} className="flex items-center justify-between p-3 rounded-lg bg-[#13151a]/50 hover:bg-[#1f2229]/50 transition-colors">
                    <div className="flex items-center gap-3">
                      <span className="text-xs font-mono text-gray-500">#{idx + 1}</span>
                      <span className="font-bold text-white">{ticker.symbol}</span>
                      <span className="text-xs text-gray-400">{ticker.exchange.toUpperCase()}</span>
                    </div>
                    <div className="text-right">
                      <div className="text-sm font-medium text-white">${(ticker.quote_volume_24h / 1_000_000).toFixed(2)}M</div>
                      <div className={`text-xs ${ticker.price_change_percent_24h >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                        {ticker.price_change_percent_24h >= 0 ? '+' : ''}{ticker.price_change_percent_24h.toFixed(2)}%
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="glass rounded-xl border border-[#1f2229]/50 p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-bold text-white flex items-center gap-2">
                  <Activity className="w-5 h-5 text-cyan-400" />
                  Top 6 by Trades
                </h3>
              </div>
              <div className="space-y-3">
                {topByTrades.map((ticker, idx) => (
                  <div key={ticker.symbol} className="flex items-center justify-between p-3 rounded-lg bg-[#13151a]/50 hover:bg-[#1f2229]/50 transition-colors">
                    <div className="flex items-center gap-3">
                      <span className="text-xs font-mono text-gray-500">#{idx + 1}</span>
                      <span className="font-bold text-white">{ticker.symbol}</span>
                      <span className="text-xs text-gray-400">{ticker.exchange.toUpperCase()}</span>
                    </div>
                    <div className="text-right">
                      <div className="text-sm font-medium text-white">{(ticker.quote_volume_24h / ticker.price / 1000).toFixed(1)}K trades</div>
                      <div className="text-xs text-gray-400">${ticker.price.toFixed(ticker.price < 1 ? 6 : 2)}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Filters Bar */}
          <div className="glass rounded-xl border border-[#1f2229]/50 p-4 mb-6">
            <div className="flex flex-wrap items-center gap-4">
              <ExchangeSelector
                exchanges={exchanges}
                selectedExchanges={selectedExchanges}
                onExchangeToggle={toggleExchange}
              />
              
              <SearchInput
                value={searchQuery}
                onChange={setSearchQuery}
                placeholder="Search symbols..."
              />
              
              <button
                onClick={() => setShowFilters(!showFilters)}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg border transition-colors ${
                  showFilters || selectedSignalTypes.length > 0 || minProbability > 0
                    ? 'bg-emerald-400/10 border-emerald-400/50 text-emerald-400'
                    : 'bg-[#13151a] border-[#1f2229] text-gray-400 hover:border-gray-600'
                }`}
              >
                <Filter className="w-4 h-4" />
                <span className="text-sm font-medium">Filters</span>
                {(selectedSignalTypes.length > 0 || minProbability > 0) && (
                  <span className="px-2 py-0.5 rounded-full text-xs bg-emerald-400/20 text-emerald-400">
                    {selectedSignalTypes.length + (minProbability > 0 ? 1 : 0)}
                  </span>
                )}
              </button>

              <div className="flex-1"></div>

              <div className="flex items-center gap-2">
                <button
                  onClick={() => setViewMode('grid')}
                  className={`p-2 rounded-lg transition-colors ${
                    viewMode === 'grid'
                      ? 'bg-emerald-400/10 text-emerald-400'
                      : 'text-gray-400 hover:bg-[#1f2229]'
                  }`}
                >
                  <Grid3X3 className="w-5 h-5" />
                </button>
                <button
                  onClick={() => setViewMode('list')}
                  className={`p-2 rounded-lg transition-colors ${
                    viewMode === 'list'
                      ? 'bg-emerald-400/10 text-emerald-400'
                      : 'text-gray-400 hover:bg-[#1f2229]'
                  }`}
                >
                  <List className="w-5 h-5" />
                </button>
              </div>
            </div>

            {/* Expanded Filters */}
            {showFilters && (
              <div className="mt-4 pt-4 border-t border-[#1f2229]/50 space-y-4">
                <SignalTypeFilter
                  selectedTypes={selectedSignalTypes}
                  onTypeToggle={toggleSignalType}
                />
                <ProbabilityFilter
                  value={minProbability}
                  onChange={setMinProbability}
                />
              </div>
            )}
          </div>

          {/* Signals Section */}
          <div className="mb-8">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-white">Live Signals</h2>
              <span className="text-sm text-gray-400">
                {filteredSignals.length} signals
              </span>
            </div>

            {filteredSignals.length > 0 ? (
              viewMode === 'grid' ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {filteredSignals.map((signal) => (
                    <SignalCard key={signal.id} signal={signal} />
                  ))}
                </div>
              ) : (
                <div className="space-y-3">
                  {filteredSignals.map((signal) => (
                    <SignalCard key={signal.id} signal={signal} />
                  ))}
                </div>
              )
            ) : (
              <div className="glass rounded-xl border border-[#1f2229]/50 p-12 text-center">
                <div className="text-gray-500 mb-2">No signals match your filters</div>
                <button
                  onClick={() => {
                    setSelectedSignalTypes([]);
                    setMinProbability(0);
                    setSearchQuery('');
                  }}
                  className="text-emerald-400 hover:text-emerald-300 text-sm font-medium"
                >
                  Clear all filters
                </button>
              </div>
            )}
          </div>

          {/* Market Overview */}
          <div className="mb-8">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-white">Market Overview</h2>
              <span className="text-sm text-gray-400">
                {filteredTickers.length} symbols
              </span>
            </div>
            <TickerTable tickers={filteredTickers.slice(0, 20)} />
          </div>
        </div>
      </main>
    </div>
  );
}
