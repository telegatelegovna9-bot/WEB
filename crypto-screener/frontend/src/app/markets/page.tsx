'use client';

import { useState, useEffect } from 'react';
import { usePathname } from 'next/navigation';
import Link from 'next/link';
import Header from '@/components/Header';
import TickerTable from '@/components/TickerTable';
import ExchangeSelector, { SearchInput } from '@/components/Filters';
import { useWebSocket, fetchExchanges } from '@/lib/api';
import { Ticker, Exchange } from '@/lib/types';
import { TrendingUp, Activity, Layers, PieChart, Settings, Zap, ArrowUpDown } from 'lucide-react';

export default function MarketsPage() {
  const pathname = usePathname();
  const { connected, tickers } = useWebSocket();
  const [exchanges, setExchanges] = useState<Exchange[]>([]);
  const [selectedExchanges, setSelectedExchanges] = useState<string[]>(['binance', 'okx', 'bybit', 'mexc', 'gate', 'bitget']);
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState<'volume' | 'price' | 'change'>('volume');

  useEffect(() => {
    fetchExchanges().then(setExchanges).catch(console.error);
  }, []);

  const filteredTickers = tickers.filter((ticker) => {
    if (selectedExchanges.length > 0 && !selectedExchanges.includes(ticker.exchange.toLowerCase())) {
      return false;
    }
    if (searchQuery && !ticker.symbol.toLowerCase().includes(searchQuery.toLowerCase())) {
      return false;
    }
    return true;
  });

  const sortedTickers = [...filteredTickers].sort((a, b) => {
    if (sortBy === 'volume') return b.quote_volume_24h - a.quote_volume_24h;
    if (sortBy === 'price') return b.price - a.price;
    if (sortBy === 'change') return b.price_change_percent_24h - a.price_change_percent_24h;
    return 0;
  });

  const toggleExchange = (exchangeId: string) => {
    setSelectedExchanges(prev =>
      prev.includes(exchangeId)
        ? prev.filter(e => e !== exchangeId)
        : [...prev, exchangeId]
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
            <h1 className="text-3xl font-bold text-white mb-2">Markets</h1>
            <p className="text-gray-400">Real-time market data across all exchanges</p>
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
              
              <div className="flex-1"></div>
              
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-400">Sort by:</span>
                <button
                  onClick={() => setSortBy('volume')}
                  className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                    sortBy === 'volume'
                      ? 'bg-emerald-400/10 text-emerald-400 border border-emerald-400/30'
                      : 'text-gray-400 hover:bg-[#1f2229]'
                  }`}
                >
                  Volume
                </button>
                <button
                  onClick={() => setSortBy('price')}
                  className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                    sortBy === 'price'
                      ? 'bg-emerald-400/10 text-emerald-400 border border-emerald-400/30'
                      : 'text-gray-400 hover:bg-[#1f2229]'
                  }`}
                >
                  Price
                </button>
                <button
                  onClick={() => setSortBy('change')}
                  className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                    sortBy === 'change'
                      ? 'bg-emerald-400/10 text-emerald-400 border border-emerald-400/30'
                      : 'text-gray-400 hover:bg-[#1f2229]'
                  }`}
                >
                  Change %
                </button>
              </div>
            </div>
          </div>

          <TickerTable tickers={sortedTickers} />
        </div>
      </main>
    </div>
  );
}
