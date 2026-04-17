'use client';

import { useState } from 'react';
import { Exchange } from '@/lib/types';
import { Check, ChevronDown } from 'lucide-react';

interface ExchangeSelectorProps {
  exchanges: Exchange[];
  selectedExchanges: string[];
  onExchangeToggle: (exchangeId: string) => void;
}

export default function ExchangeSelector({ 
  exchanges, 
  selectedExchanges, 
  onExchangeToggle 
}: ExchangeSelectorProps) {
  const [isOpen, setIsOpen] = useState(false);

  const activeCount = selectedExchanges.length;

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-4 py-2 rounded-lg bg-[#13151a] border border-[#1f2229] hover:border-emerald-400/50 transition-colors"
      >
        <span className="text-sm font-medium">Exchanges</span>
        {activeCount > 0 && (
          <span className="px-2 py-0.5 rounded-full text-xs bg-emerald-400/20 text-emerald-400">
            {activeCount}
          </span>
        )}
        <ChevronDown className={`w-4 h-4 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {isOpen && (
        <>
          <div 
            className="fixed inset-0 z-10" 
            onClick={() => setIsOpen(false)}
          />
          <div className="absolute top-full left-0 mt-2 w-56 glass rounded-xl border border-[#1f2229] p-2 z-20 shadow-xl">
            <div className="space-y-1">
              {exchanges.map((exchange) => {
                const isSelected = selectedExchanges.includes(exchange.id);
                return (
                  <button
                    key={exchange.id}
                    onClick={() => {
                      if (exchange.active) {
                        onExchangeToggle(exchange.id);
                      }
                    }}
                    disabled={!exchange.active}
                    className={`w-full flex items-center justify-between px-3 py-2 rounded-lg text-sm transition-colors ${
                      !exchange.active
                        ? 'opacity-50 cursor-not-allowed'
                        : isSelected
                        ? 'bg-emerald-400/10 text-emerald-400'
                        : 'hover:bg-[#1f2229]'
                    }`}
                  >
                    <span>{exchange.name}</span>
                    {isSelected && (
                      <Check className="w-4 h-4" />
                    )}
                  </button>
                );
              })}
            </div>
            <div className="mt-2 pt-2 border-t border-[#1f2229]">
              <button
                onClick={() => {
                  exchanges.forEach(e => e.active && onExchangeToggle(e.id));
                }}
                className="w-full text-xs text-center text-gray-400 hover:text-emerald-400 py-1"
              >
                Select All Active
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

// Signal Type Filter
interface SignalTypeFilterProps {
  selectedTypes: string[];
  onTypeToggle: (type: string) => void;
}

const signalTypes = [
  { id: 'pump', label: 'Pump', color: 'text-emerald-400' },
  { id: 'dump', label: 'Dump', color: 'text-red-400' },
  { id: 'volume_spike', label: 'Volume Spike', color: 'text-purple-400' },
  { id: 'breakout', label: 'Breakout', color: 'text-blue-400' },
];

export function SignalTypeFilter({ selectedTypes, onTypeToggle }: SignalTypeFilterProps) {
  return (
    <div className="flex flex-wrap gap-2">
      {signalTypes.map((type) => {
        const isSelected = selectedTypes.includes(type.id);
        return (
          <button
            key={type.id}
            onClick={() => onTypeToggle(type.id)}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              isSelected
                ? `bg-${type.color.split('-')[1]}-400/20 ${type.color} border border-${type.color.split('-')[1]}-400/30`
                : 'bg-[#13151a] border border-[#1f2229] text-gray-400 hover:border-gray-600'
            }`}
          >
            {type.label}
          </button>
        );
      })}
    </div>
  );
}

// Search Input
interface SearchInputProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
}

export function SearchInput({ value, onChange, placeholder = 'Search...' }: SearchInputProps) {
  return (
    <div className="relative">
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className="w-full md:w-64 px-4 py-2 pl-10 rounded-lg bg-[#13151a] border border-[#1f2229] focus:border-emerald-400/50 focus:outline-none text-sm"
      />
      <svg
        className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
        />
      </svg>
    </div>
  );
}

// Probability Filter Slider
interface ProbabilityFilterProps {
  value: number;
  onChange: (value: number) => void;
}

export function ProbabilityFilter({ value, onChange }: ProbabilityFilterProps) {
  return (
    <div className="flex items-center gap-3">
      <span className="text-xs text-gray-400 whitespace-nowrap">Min Probability:</span>
      <input
        type="range"
        min="0"
        max="100"
        step="10"
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="w-32 h-1 bg-[#1f2229] rounded-lg appearance-none cursor-pointer accent-emerald-400"
      />
      <span className="text-xs font-medium text-emerald-400 w-8">{value}%</span>
    </div>
  );
}
