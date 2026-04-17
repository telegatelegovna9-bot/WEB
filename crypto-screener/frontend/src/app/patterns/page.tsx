'use client';

import { useState, useEffect } from 'react';
import { usePathname } from 'next/navigation';
import Link from 'next/link';
import Header from '@/components/Header';
import { useWebSocket, fetchExchanges } from '@/lib/api';
import { Exchange, PatternDetection } from '@/lib/types';
import { Activity, Layers, PieChart, Settings, Zap, TrendingUp, Triangle, ArrowUpRight, ArrowDownRight } from 'lucide-react';

const demoPatterns: PatternDetection[] = [
  {
    id: 'pattern-1',
    symbol: 'BTCUSDT',
    exchange: 'binance',
    pattern_type: 'breakout',
    confidence: 85,
    timestamp: new Date().toISOString(),
    price_level: 67500,
    volume_confirmation: true,
    description: 'Strong breakout above resistance with volume confirmation'
  },
  {
    id: 'pattern-2',
    symbol: 'ETHUSDT',
    exchange: 'binance',
    pattern_type: 'triangle',
    confidence: 72,
    timestamp: new Date().toISOString(),
    price_level: 3450,
    volume_confirmation: true,
    description: 'Ascending triangle forming, awaiting breakout'
  },
  {
    id: 'pattern-3',
    symbol: 'SOLUSDT',
    exchange: 'okx',
    pattern_type: 'flag',
    confidence: 68,
    timestamp: new Date().toISOString(),
    price_level: 145,
    volume_confirmation: false,
    description: 'Bull flag consolidation after strong move'
  }
];

export default function PatternsPage() {
  const pathname = usePathname();
  const { connected } = useWebSocket();
  const [exchanges, setExchanges] = useState<Exchange[]>([]);
  const [selectedExchanges, setSelectedExchanges] = useState<string[]>(['binance', 'okx', 'bybit', 'mexc', 'gate', 'bitget']);

  useEffect(() => {
    fetchExchanges().then(setExchanges).catch(console.error);
  }, []);

  const toggleExchange = (exchangeId: string) => {
    setSelectedExchanges(prev =>
      prev.includes(exchangeId)
        ? prev.filter(e => e !== exchangeId)
        : [...prev, exchangeId]
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

  const getPatternIcon = (type: string) => {
    switch (type) {
      case 'breakout': return <ArrowUpRight className="w-6 h-6 text-emerald-400" />;
      case 'triangle': return <Triangle className="w-6 h-6 text-cyan-400" />;
      case 'flag': return <TrendingUp className="w-6 h-6 text-purple-400" />;
      default: return <Layers className="w-6 h-6 text-gray-400" />;
    }
  };

  const getPatternColor = (type: string) => {
    switch (type) {
      case 'breakout': return 'from-emerald-500/20 to-green-500/20 border-emerald-500/30';
      case 'triangle': return 'from-cyan-500/20 to-blue-500/20 border-cyan-500/30';
      case 'flag': return 'from-purple-500/20 to-pink-500/20 border-purple-500/30';
      default: return 'from-gray-500/20 to-slate-500/20 border-gray-500/30';
    }
  };

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
            <h1 className="text-3xl font-bold text-white mb-2">Pattern Detection</h1>
            <p className="text-gray-400">Automated technical pattern recognition across all exchanges</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {demoPatterns.map((pattern) => (
              <div
                key={pattern.id}
                className={`glass rounded-xl border p-6 bg-gradient-to-br ${getPatternColor(pattern.pattern_type)} hover:scale-[1.02] transition-transform duration-300`}
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-3">
                    {getPatternIcon(pattern.pattern_type)}
                    <div>
                      <h3 className="text-lg font-bold text-white">{pattern.symbol}</h3>
                      <p className="text-xs text-gray-400">{pattern.exchange.toUpperCase()}</p>
                    </div>
                  </div>
                  <div className={`px-3 py-1 rounded-full text-xs font-bold ${
                    pattern.confidence >= 80 ? 'bg-emerald-400/20 text-emerald-400' :
                    pattern.confidence >= 60 ? 'bg-yellow-400/20 text-yellow-400' :
                    'bg-red-400/20 text-red-400'
                  }`}>
                    {pattern.confidence}% confidence
                  </div>
                </div>

                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-400">Pattern Type</span>
                    <span className="text-sm font-medium text-white capitalize">{pattern.pattern_type}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-400">Price Level</span>
                    <span className="text-sm font-medium text-white">${pattern.price_level.toLocaleString()}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-400">Volume Confirmation</span>
                    <span className={`text-sm font-medium ${pattern.volume_confirmation ? 'text-emerald-400' : 'text-gray-500'}`}>
                      {pattern.volume_confirmation ? '✓ Yes' : '✗ No'}
                    </span>
                  </div>
                </div>

                <div className="mt-4 pt-4 border-t border-white/10">
                  <p className="text-sm text-gray-300">{pattern.description}</p>
                </div>
              </div>
            ))}
          </div>

          <div className="mt-8 glass rounded-xl border border-[#1f2229]/50 p-8 text-center">
            <Layers className="w-12 h-12 text-gray-600 mx-auto mb-4" />
            <h3 className="text-xl font-bold text-white mb-2">More Patterns Coming Soon</h3>
            <p className="text-gray-400 max-w-md mx-auto">
              Our AI is continuously scanning for head & shoulders, double tops/bottoms, wedges, and more complex formations.
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
