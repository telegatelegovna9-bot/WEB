'use client';

import { useState, useEffect } from 'react';
import { usePathname } from 'next/navigation';
import Link from 'next/link';
import Header from '@/components/Header';
import SignalCard from '@/components/SignalCard';
import ExchangeSelector, { SignalTypeFilter, SearchInput, ProbabilityFilter } from '@/components/Filters';
import { useWebSocket, fetchExchanges } from '@/lib/api';
import { Signal, Exchange } from '@/lib/types';
import { Activity, Layers, PieChart, Settings, Zap, Filter } from 'lucide-react';

export default function SignalsPage() {
  const pathname = usePathname();
  const { connected, signals } = useWebSocket();
  const [exchanges, setExchanges] = useState<Exchange[]>([]);
  const [selectedExchanges, setSelectedExchanges] = useState<string[]>(['binance', 'okx', 'bybit', 'mexc', 'gate', 'bitget']);
  const [selectedSignalTypes, setSelectedSignalTypes] = useState<string[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [minProbability, setMinProbability] = useState(0);
  const [showFilters, setShowFilters] = useState(false);

  useEffect(() => {
    fetchExchanges().then(setExchanges).catch(console.error);
  }, []);

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
    { href: '/markets', label: 'Markets', icon: Activity },
    { href: '/signals', label: 'Signals', icon: Zap },
    { href: '/patterns', label: 'Patterns', icon: Layers },
    { href: '/density', label: 'Density', icon: PieChart },
    { href: '/settings', label: 'Settings', icon: Settings },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#050608] via-[#0a0b0f] to-[#0d0e12]">
      <Header />
      
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
          <div className="mb-6">
            <h1 className="text-3xl font-bold text-white mb-2">Intelligent Signals</h1>
            <p className="text-gray-400">AI-powered market analysis with probability scoring</p>
          </div>

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

              <span className="text-sm text-gray-400">
                {filteredSignals.length} signals found
              </span>
            </div>

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

          {filteredSignals.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filteredSignals.map((signal) => (
                <SignalCard key={signal.id} signal={signal} />
              ))}
            </div>
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
      </main>
    </div>
  );
}
