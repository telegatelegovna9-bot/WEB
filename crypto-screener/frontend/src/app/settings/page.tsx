'use client';

import { useState } from 'react';
import { usePathname } from 'next/navigation';
import Link from 'next/link';
import Header from '@/components/Header';
import { useWebSocket } from '@/lib/api';
import { Activity, Layers, PieChart, Settings, Zap, Bell, Moon, Sun, Globe, Shield, Database } from 'lucide-react';

export default function SettingsPage() {
  const pathname = usePathname();
  const { connected } = useWebSocket();
  const [notificationsEnabled, setNotificationsEnabled] = useState(true);
  const [darkMode, setDarkMode] = useState(true);
  const [minProbabilityAlert, setMinProbabilityAlert] = useState(70);

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
        <div className="max-w-[1200px] mx-auto px-4 sm:px-6 lg:px-8">
          <div className="mb-6">
            <h1 className="text-3xl font-bold text-white mb-2">Settings</h1>
            <p className="text-gray-400">Configure your trading preferences and notifications</p>
          </div>

          <div className="space-y-6">
            {/* Notifications */}
            <div className="glass rounded-xl border border-[#1f2229]/50 p-6">
              <div className="flex items-center gap-3 mb-6">
                <Bell className="w-6 h-6 text-emerald-400" />
                <h2 className="text-xl font-bold text-white">Notifications</h2>
              </div>

              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 rounded-lg bg-[#13151a]/50">
                  <div>
                    <p className="font-medium text-white">Enable Notifications</p>
                    <p className="text-sm text-gray-400">Receive real-time alerts for high-probability signals</p>
                  </div>
                  <button
                    onClick={() => setNotificationsEnabled(!notificationsEnabled)}
                    className={`relative w-14 h-7 rounded-full transition-colors ${
                      notificationsEnabled ? 'bg-emerald-400' : 'bg-gray-600'
                    }`}
                  >
                    <div
                      className={`absolute top-1 w-5 h-5 rounded-full bg-white transition-transform ${
                        notificationsEnabled ? 'left-8' : 'left-1'
                      }`}
                    />
                  </button>
                </div>

                <div className="p-4 rounded-lg bg-[#13151a]/50">
                  <div className="flex items-center justify-between mb-3">
                    <div>
                      <p className="font-medium text-white">Minimum Probability Alert</p>
                      <p className="text-sm text-gray-400">Only notify for signals above this probability</p>
                    </div>
                    <span className="text-emerald-400 font-bold">{minProbabilityAlert}%</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={minProbabilityAlert}
                    onChange={(e) => setMinProbabilityAlert(Number(e.target.value))}
                    className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-emerald-400"
                  />
                  <div className="flex justify-between mt-2 text-xs text-gray-500">
                    <span>0%</span>
                    <span>50%</span>
                    <span>100%</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Appearance */}
            <div className="glass rounded-xl border border-[#1f2229]/50 p-6">
              <div className="flex items-center gap-3 mb-6">
                <Moon className="w-6 h-6 text-cyan-400" />
                <h2 className="text-xl font-bold text-white">Appearance</h2>
              </div>

              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 rounded-lg bg-[#13151a]/50">
                  <div>
                    <p className="font-medium text-white">Dark Mode</p>
                    <p className="text-sm text-gray-400">Use dark theme for the interface</p>
                  </div>
                  <button
                    onClick={() => setDarkMode(!darkMode)}
                    className={`relative w-14 h-7 rounded-full transition-colors ${
                      darkMode ? 'bg-emerald-400' : 'bg-gray-600'
                    }`}
                  >
                    <div
                      className={`absolute top-1 w-5 h-5 rounded-full bg-white transition-transform ${
                        darkMode ? 'left-8' : 'left-1'
                      }`}
                    />
                  </button>
                </div>
              </div>
            </div>

            {/* Exchange Connections */}
            <div className="glass rounded-xl border border-[#1f2229]/50 p-6">
              <div className="flex items-center gap-3 mb-6">
                <Globe className="w-6 h-6 text-purple-400" />
                <h2 className="text-xl font-bold text-white">Connected Exchanges</h2>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {[
                  { name: 'Binance', status: 'connected', latency: '45ms' },
                  { name: 'OKX', status: 'connected', latency: '62ms' },
                  { name: 'Bybit', status: 'connected', latency: '58ms' },
                  { name: 'MEXC', status: 'connected', latency: '71ms' },
                  { name: 'Gate.io', status: 'connected', latency: '89ms' },
                  { name: 'Bitget', status: 'connected', latency: '53ms' }
                ].map((exchange) => (
                  <div
                    key={exchange.name}
                    className="p-4 rounded-lg bg-[#13151a]/50 border border-[#1f2229]/50"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium text-white">{exchange.name}</span>
                      <div className="flex items-center gap-2">
                        <div className="w-2 h-2 rounded-full bg-emerald-400 live-indicator" />
                        <span className="text-xs text-emerald-400">{exchange.latency}</span>
                      </div>
                    </div>
                    <p className="text-xs text-gray-400 capitalize">{exchange.status}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Data & Privacy */}
            <div className="glass rounded-xl border border-[#1f2229]/50 p-6">
              <div className="flex items-center gap-3 mb-6">
                <Shield className="w-6 h-6 text-yellow-400" />
                <h2 className="text-xl font-bold text-white">Data & Privacy</h2>
              </div>

              <div className="space-y-4">
                <div className="p-4 rounded-lg bg-[#13151a]/50">
                  <div className="flex items-center gap-3 mb-2">
                    <Database className="w-5 h-5 text-gray-400" />
                    <p className="font-medium text-white">Data Retention</p>
                  </div>
                  <p className="text-sm text-gray-400">
                    Signal history is stored for 30 days. Historical data is used for pattern matching and accuracy analysis.
                  </p>
                </div>

                <div className="p-4 rounded-lg bg-[#13151a]/50">
                  <p className="font-medium text-white mb-2">API Security</p>
                  <p className="text-sm text-gray-400">
                    All API keys are encrypted at rest. We never store withdrawal permissions. Read-only access recommended.
                  </p>
                </div>
              </div>
            </div>

            {/* Save Button */}
            <div className="flex justify-end gap-4">
              <button className="px-6 py-3 rounded-lg border border-[#1f2229] text-gray-400 hover:text-white hover:border-gray-600 transition-colors">
                Reset to Defaults
              </button>
              <button className="px-6 py-3 rounded-lg bg-gradient-to-r from-emerald-500 to-cyan-500 text-white font-medium hover:opacity-90 transition-opacity shadow-lg shadow-emerald-500/25">
                Save Changes
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
