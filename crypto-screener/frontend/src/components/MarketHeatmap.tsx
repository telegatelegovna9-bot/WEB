'use client';

import { useState, useMemo } from 'react';
import { TickerData } from '@/types';
import { useMarketStore } from '@/store/marketStore';

type SortField = 'symbol' | 'price' | 'change' | 'volume';
type SortOrder = 'asc' | 'desc';

export function MarketHeatmap() {
  const tickers = useMarketStore((state) => state.tickers);
  const tickerArray = Object.values(tickers);
  
  const [sortField, setSortField] = useState<SortField>('change');
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc');

  const sortedTickers = useMemo(() => {
    return [...tickerArray].sort((a, b) => {
      let comparison = 0;
      
      switch (sortField) {
        case 'symbol':
          comparison = a.symbol.localeCompare(b.symbol);
          break;
        case 'price':
          comparison = a.price - b.price;
          break;
        case 'change':
          comparison = a.price_change_percent_24h - b.price_change_percent_24h;
          break;
        case 'volume':
          comparison = a.volume_24h - b.volume_24h;
          break;
      }
      
      return sortOrder === 'asc' ? comparison : -comparison;
    });
  }, [tickerArray, sortField, sortOrder]);

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortOrder('desc');
    }
  };

  const getColorIntensity = (value: number, max: number) => {
    const intensity = Math.min(Math.abs(value) / max, 1);
    if (value >= 0) {
      return `rgba(46, 160, 67, ${intensity * 0.8})`;
    }
    return `rgba(218, 54, 51, ${intensity * 0.8})`;
  };

  const maxChange = Math.max(
    ...tickerArray.map(t => Math.abs(t.price_change_percent_24h)),
    1
  );

  const formatPrice = (price: number) => {
    if (price >= 1000) return price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    if (price >= 1) return price.toFixed(4);
    return price.toFixed(6);
  };

  const formatVolume = (volume: number) => {
    if (volume >= 1e9) return `${(volume / 1e9).toFixed(2)}B`;
    if (volume >= 1e6) return `${(volume / 1e6).toFixed(2)}M`;
    if (volume >= 1e3) return `${(volume / 1e3).toFixed(2)}K`;
    return volume.toFixed(2);
  };

  const getSortIcon = (field: SortField) => {
    if (sortField !== field) return '↕️';
    return sortOrder === 'asc' ? '↑' : '↓';
  };

  if (tickerArray.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-500">
        No market data yet...
      </div>
    );
  }

  return (
    <div className="glass-card rounded-xl border border-white/10 overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b border-white/10 flex items-center justify-between">
        <h2 className="text-lg font-semibold flex items-center gap-2">
          <span>🔥</span>
          Market Heatmap
        </h2>
        <div className="flex items-center gap-2 text-xs">
          <span className="px-2 py-1 rounded bg-green-500/20 text-green-400">
            ↑ {tickerArray.filter(t => t.price_change_percent_24h > 0).length} Gainers
          </span>
          <span className="px-2 py-1 rounded bg-red-500/20 text-red-400">
            ↓ {tickerArray.filter(t => t.price_change_percent_24h < 0).length} Losers
          </span>
        </div>
      </div>

      {/* Table Header */}
      <div className="grid grid-cols-12 gap-2 px-4 py-2 bg-white/5 text-xs font-semibold text-gray-400">
        <div 
          className="col-span-3 cursor-pointer hover:text-white transition-colors"
          onClick={() => handleSort('symbol')}
        >
          Symbol {getSortIcon('symbol')}
        </div>
        <div 
          className="col-span-2 text-right cursor-pointer hover:text-white transition-colors"
          onClick={() => handleSort('price')}
        >
          Price {getSortIcon('price')}
        </div>
        <div 
          className="col-span-3 text-right cursor-pointer hover:text-white transition-colors"
          onClick={() => handleSort('change')}
        >
          24h Change {getSortIcon('change')}
        </div>
        <div 
          className="col-span-2 text-right cursor-pointer hover:text-white transition-colors"
          onClick={() => handleSort('volume')}
        >
          Volume {getSortIcon('volume')}
        </div>
        <div className="col-span-2 text-right">Momentum</div>
      </div>

      {/* Table Body */}
      <div className="max-h-96 overflow-y-auto">
        {sortedTickers.map((ticker) => (
          <div 
            key={`${ticker.exchange}:${ticker.symbol}`}
            className="grid grid-cols-12 gap-2 px-4 py-3 border-t border-white/5 hover:bg-white/5 transition-colors items-center"
          >
            {/* Symbol */}
            <div className="col-span-3">
              <div className="flex items-center gap-2">
                <span className="font-semibold">{ticker.symbol}</span>
                <span className="text-xs px-1.5 py-0.5 rounded bg-white/10 uppercase">
                  {ticker.exchange}
                </span>
              </div>
            </div>

            {/* Price */}
            <div className="col-span-2 text-right font-mono">
              ${formatPrice(ticker.price)}
            </div>

            {/* Change */}
            <div 
              className={`col-span-3 text-right font-semibold ${
                ticker.price_change_percent_24h >= 0 ? 'text-green-500' : 'text-red-500'
              }`}
            >
              {ticker.price_change_percent_24h >= 0 ? '+' : ''}
              {ticker.price_change_percent_24h.toFixed(2)}%
            </div>

            {/* Volume */}
            <div className="col-span-2 text-right text-gray-400">
              ${formatVolume(ticker.volume_24h)}
            </div>

            {/* Momentum Bar */}
            <div className="col-span-2 flex items-center justify-end gap-2">
              <div className="w-16 h-2 rounded-full bg-gray-700 overflow-hidden">
                <div 
                  className="h-full rounded-full transition-all duration-300"
                  style={{ 
                    width: `${Math.min(Math.abs(ticker.price_change_percent_24h) / maxChange * 100, 100)}%`,
                    backgroundColor: getColorIntensity(ticker.price_change_percent_24h, maxChange)
                  }}
                />
              </div>
              <span className={`text-xs font-mono ${
                ticker.price_change_percent_24h >= 0 ? 'text-green-500' : 'text-red-500'
              }`}>
                {ticker.price_change_percent_24h >= 0 ? '📈' : '📉'}
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* Footer Stats */}
      <div className="px-4 py-3 border-t border-white/10 bg-white/5 grid grid-cols-3 gap-4 text-xs">
        <div>
          <span className="text-gray-400">Total Pairs:</span>
          <span className="ml-2 font-semibold">{tickerArray.length}</span>
        </div>
        <div>
          <span className="text-gray-400">Avg Change:</span>
          <span className={`ml-2 font-semibold ${
            tickerArray.reduce((acc, t) => acc + t.price_change_percent_24h, 0) / tickerArray.length >= 0 
              ? 'text-green-500' 
              : 'text-red-500'
          }`}>
            {(tickerArray.reduce((acc, t) => acc + t.price_change_percent_24h, 0) / tickerArray.length).toFixed(2)}%
          </span>
        </div>
        <div>
          <span className="text-gray-400">Total Volume:</span>
          <span className="ml-2 font-semibold">${formatVolume(tickerArray.reduce((acc, t) => acc + t.volume_24h, 0))}</span>
        </div>
      </div>
    </div>
  );
}
