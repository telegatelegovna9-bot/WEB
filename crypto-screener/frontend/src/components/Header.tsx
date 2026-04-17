'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { 
  Activity, 
  TrendingUp, 
  Brain, 
  Settings, 
  Bell, 
  Search,
  Menu,
  X,
  Zap,
  Layers,
  Target
} from 'lucide-react';

const navigation = [
  { name: 'Dashboard', href: '/', icon: Activity },
  { name: 'Signals', href: '/signals', icon: Zap },
  { name: 'Market', href: '/market', icon: TrendingUp },
  { name: 'Patterns', href: '/patterns', icon: Brain },
  { name: 'Density Map', href: '/density', icon: Layers },
  { name: 'Settings', href: '/settings', icon: Settings },
];

export default function Header() {
  const pathname = usePathname();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 10);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <header className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
      isScrolled ? 'glass border-b border-[#1f2229]' : ''
    }`}>
      <div className="max-w-[1800px] mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl gradient-crypto flex items-center justify-center">
              <Target className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gradient">CryptoScreener Pro</h1>
              <p className="text-xs text-gray-500 hidden sm:block">Intelligent Market Analysis</p>
            </div>
          </div>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center gap-1">
            {navigation.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href;
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                    isActive
                      ? 'bg-emerald-400/10 text-emerald-400'
                      : 'text-gray-400 hover:text-white hover:bg-[#1f2229]'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {item.name}
                </Link>
              );
            })}
          </nav>

          {/* Right Actions */}
          <div className="flex items-center gap-3">
            <button className="p-2 rounded-lg bg-[#13151a] border border-[#1f2229] text-gray-400 hover:text-emerald-400 hover:border-emerald-400/50 transition-colors">
              <Bell className="w-5 h-5" />
            </button>
            
            <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-[#13151a] border border-[#1f2229]">
              <div className="w-2 h-2 rounded-full bg-emerald-400 live-indicator"></div>
              <span className="text-xs text-gray-400">Live</span>
            </div>

            {/* Mobile menu button */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-2 rounded-lg bg-[#13151a] border border-[#1f2229]"
            >
              {mobileMenuOpen ? (
                <X className="w-5 h-5" />
              ) : (
                <Menu className="w-5 h-5" />
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Navigation */}
      {mobileMenuOpen && (
        <div className="md:hidden glass border-t border-[#1f2229]">
          <nav className="px-4 py-4 space-y-2">
            {navigation.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href;
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  onClick={() => setMobileMenuOpen(false)}
                  className={`flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all ${
                    isActive
                      ? 'bg-emerald-400/10 text-emerald-400'
                      : 'text-gray-400 hover:text-white hover:bg-[#1f2229]'
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  {item.name}
                </Link>
              );
            })}
          </nav>
        </div>
      )}
    </header>
  );
}

// Footer Component
export function Footer() {
  return (
    <footer className="border-t border-[#1f2229] mt-auto">
      <div className="max-w-[1800px] mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
          <div>
            <h4 className="text-sm font-semibold mb-4">Product</h4>
            <ul className="space-y-2 text-sm text-gray-400">
              <li><Link href="/features" className="hover:text-emerald-400">Features</Link></li>
              <li><Link href="/pricing" className="hover:text-emerald-400">Pricing</Link></li>
              <li><Link href="/api" className="hover:text-emerald-400">API</Link></li>
            </ul>
          </div>
          <div>
            <h4 className="text-sm font-semibold mb-4">Resources</h4>
            <ul className="space-y-2 text-sm text-gray-400">
              <li><Link href="/docs" className="hover:text-emerald-400">Documentation</Link></li>
              <li><Link href="/guides" className="hover:text-emerald-400">Guides</Link></li>
              <li><Link href="/support" className="hover:text-emerald-400">Support</Link></li>
            </ul>
          </div>
          <div>
            <h4 className="text-sm font-semibold mb-4">Company</h4>
            <ul className="space-y-2 text-sm text-gray-400">
              <li><Link href="/about" className="hover:text-emerald-400">About</Link></li>
              <li><Link href="/blog" className="hover:text-emerald-400">Blog</Link></li>
              <li><Link href="/contact" className="hover:text-emerald-400">Contact</Link></li>
            </ul>
          </div>
          <div>
            <h4 className="text-sm font-semibold mb-4">Legal</h4>
            <ul className="space-y-2 text-sm text-gray-400">
              <li><Link href="/privacy" className="hover:text-emerald-400">Privacy</Link></li>
              <li><Link href="/terms" className="hover:text-emerald-400">Terms</Link></li>
            </ul>
          </div>
        </div>
        <div className="mt-8 pt-8 border-t border-[#1f2229] text-center text-sm text-gray-500">
          © 2024 CryptoScreener Pro. All rights reserved.
        </div>
      </div>
    </footer>
  );
}
