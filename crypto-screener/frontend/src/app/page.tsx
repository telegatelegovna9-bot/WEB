'use client';

import { useState, useEffect } from 'react';
import Header, { Footer } from '@/components/Header';
import SignalCard from '@/components/SignalCard';
import TickerTable from '@/components/TickerTable';
import StatsPanel, { TopMovers } from '@/components/StatsPanel';
import ExchangeSelector, { SignalTypeFilter, SearchInput, ProbabilityFilter } from '@/components/Filters';
import { useWebSocket, fetchExchanges } from '@/lib/api';
import { Signal, Ticker, Exchange } from '@/lib/types';
import { Filter, Grid3X3, List } from 'lucide-react';

export default function Dashboard() {
  const { connected, tickers, signals, stats } = useWebSocket();
  const [exchanges, setExchanges] = useState<Exchange[]>([]);
  const [selectedExchanges, setSelectedExchanges] = useState<string[]>(['binance', 'okx', 'bybit']);
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

  return (
    <div className="min-h-screen bg-[#0a0b0f]">
      <Header />
      
      <main className="pt-20 pb-12">
        <div className="max-w-[1800px] mx-auto px-4 sm:px-6 lg:px-8">
          {/* Connection Status */}
          <div className="mb-6 flex items-center gap-3">
            <div className={`w-2 h-2 rounded-full ${connected ? 'bg-emerald-400 live-indicator' : 'bg-red-400'}`}></div>
            <span className="text-sm text-gray-400">
              {connected ? 'Connected to real-time data' : 'Connecting...'}
            </span>
          </div>

          {/* Stats Panel */}
          <StatsPanel stats={stats} />

          {/* Top Movers */}
          <TopMovers stats={stats} />

          {/* Filters Bar */}
          <div className="glass rounded-xl border border-[#1f2229] p-4 mb-6">
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
              <div className="mt-4 pt-4 border-t border-[#1f2229] space-y-4">
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
              <h2 className="text-xl font-bold">Live Signals</h2>
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
              <div className="glass rounded-xl border border-[#1f2229] p-12 text-center">
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
              <h2 className="text-xl font-bold">Market Overview</h2>
              <span className="text-sm text-gray-400">
                {filteredTickers.length} symbols
              </span>
            </div>
            <TickerTable tickers={filteredTickers.slice(0, 20)} />
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}
