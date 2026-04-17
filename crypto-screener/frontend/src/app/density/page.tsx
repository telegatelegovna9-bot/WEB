'use client';

import { useState, useEffect } from 'react';
import { usePathname } from 'next/navigation';
import Link from 'next/link';
import Header from '@/components/Header';
import { useWebSocket } from '@/lib/api';
import { Activity, Layers, PieChart, Settings, Zap, TrendingUp, DollarSign, Users } from 'lucide-react';

const demoDensities = [
  {
    id: 'density-1',
    symbol: 'BTCUSDT',
    exchange: 'binance',
    type: 'buy_wall',
    price_level: 65000,
    total_volume: 1250,
    order_count: 45,
    strength: 'strong',
    description: 'Large buy wall detected - potential support level'
  },
  {
    id: 'density-2',
    symbol: 'ETHUSDT',
    exchange: 'binance',
    type: 'sell_wall',
    price_level: 3600,
    total_volume: 8500,
    order_count: 32,
    strength: 'medium',
    description: 'Sell density forming - resistance expected'
  },
  {
    id: 'density-3',
    symbol: 'SOLUSDT',
    exchange: 'okx',
    type: 'buy_density',
    price_level: 140,
    total_volume: 45000,
    order_count: 78,
    strength: 'strong',
    description: 'Accumulation zone with high order density'
  }
];

export default function DensityPage() {
  const pathname = usePathname();
  const { connected } = useWebSocket();

  const navItems = [
    { href: '/', label: 'Dashboard', icon: Activity },
    { href: '/markets', label: 'Markets', icon: Activity },
    { href: '/signals', label: 'Signals', icon: Zap },
    { href: '/patterns', label: 'Patterns', icon: Layers },
    { href: '/density', label: 'Density', icon: PieChart },
    { href: '/settings', label: 'Settings', icon: Settings },
  ];

  const getDensityColor = (type: string) => {
    switch (type) {
      case 'buy_wall': return 'from-emerald-500/20 to-green-500/20 border-emerald-500/30 text-emerald-400';
      case 'sell_wall': return 'from-red-500/20 to-rose-500/20 border-red-500/30 text-red-400';
      case 'buy_density': return 'from-cyan-500/20 to-blue-500/20 border-cyan-500/30 text-cyan-400';
      default: return 'from-gray-500/20 to-slate-500/20 border-gray-500/30 text-gray-400';
    }
  };

  const getStrengthBadge = (strength: string) => {
    switch (strength) {
      case 'strong': return <span className="px-2 py-1 rounded text-xs font-bold bg-emerald-400/20 text-emerald-400">STRONG</span>;
      case 'medium': return <span className="px-2 py-1 rounded text-xs font-bold bg-yellow-400/20 text-yellow-400">MEDIUM</span>;
      default: return <span className="px-2 py-1 rounded text-xs font-bold bg-gray-400/20 text-gray-400">WEAK</span>;
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
            <h1 className="text-3xl font-bold text-white mb-2">Order Book Density Analysis</h1>
            <p className="text-gray-400">Detect large walls and liquidity zones in real-time</p>
          </div>

          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="glass rounded-xl border border-[#1f2229]/50 p-6">
              <div className="flex items-center gap-4">
                <div className="p-3 rounded-lg bg-emerald-400/10">
                  <DollarSign className="w-6 h-6 text-emerald-400" />
                </div>
                <div>
                  <p className="text-sm text-gray-400">Buy Walls Detected</p>
                  <p className="text-2xl font-bold text-white">12</p>
                </div>
              </div>
            </div>

            <div className="glass rounded-xl border border-[#1f2229]/50 p-6">
              <div className="flex items-center gap-4">
                <div className="p-3 rounded-lg bg-red-400/10">
                  <TrendingUp className="w-6 h-6 text-red-400" />
                </div>
                <div>
                  <p className="text-sm text-gray-400">Sell Walls Detected</p>
                  <p className="text-2xl font-bold text-white">8</p>
                </div>
              </div>
            </div>

            <div className="glass rounded-xl border border-[#1f2229]/50 p-6">
              <div className="flex items-center gap-4">
                <div className="p-3 rounded-lg bg-cyan-400/10">
                  <Users className="w-6 h-6 text-cyan-400" />
                </div>
                <div>
                  <p className="text-sm text-gray-400">Active Density Zones</p>
                  <p className="text-2xl font-bold text-white">24</p>
                </div>
              </div>
            </div>
          </div>

          {/* Density Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {demoDensities.map((density) => (
              <div
                key={density.id}
                className={`glass rounded-xl border p-6 bg-gradient-to-br ${getDensityColor(density.type)} hover:scale-[1.02] transition-transform duration-300`}
              >
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h3 className="text-lg font-bold text-white">{density.symbol}</h3>
                    <p className="text-xs text-gray-400">{density.exchange.toUpperCase()}</p>
                  </div>
                  {getStrengthBadge(density.strength)}
                </div>

                <div className="space-y-3 mb-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-400">Type</span>
                    <span className="text-sm font-medium text-white capitalize">{density.type.replace('_', ' ')}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-400">Price Level</span>
                    <span className="text-sm font-medium text-white">${density.price_level.toLocaleString()}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-400">Total Volume</span>
                    <span className="text-sm font-medium text-white">{density.total_volume.toLocaleString()}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-400">Order Count</span>
                    <span className="text-sm font-medium text-white">{density.order_count}</span>
                  </div>
                </div>

                <div className="pt-4 border-t border-white/10">
                  <p className="text-sm text-gray-300">{density.description}</p>
                </div>
              </div>
            ))}
          </div>

          {/* Order Book Visualization Placeholder */}
          <div className="mt-8 glass rounded-xl border border-[#1f2229]/50 p-8">
            <h3 className="text-xl font-bold text-white mb-4">Live Order Book Heatmap</h3>
            <div className="h-64 bg-[#13151a]/50 rounded-lg flex items-center justify-center">
              <div className="text-center">
                <PieChart className="w-12 h-12 text-gray-600 mx-auto mb-4" />
                <p className="text-gray-400">Real-time order book visualization coming soon</p>
                <p className="text-sm text-gray-500 mt-2">Visualizing liquidity depth across price levels</p>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
