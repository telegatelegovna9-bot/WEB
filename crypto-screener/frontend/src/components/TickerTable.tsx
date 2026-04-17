'use client';

import { Ticker } from '@/lib/types';
import { formatPrice, formatVolume } from '@/lib/api';
import { ArrowUpRight, ArrowDownRight } from 'lucide-react';

interface TickerTableProps {
  tickers: Ticker[];
  onTickerClick?: (ticker: Ticker) => void;
}

export default function TickerTable({ tickers, onTickerClick }: TickerTableProps) {
  return (
    <div className="glass rounded-xl border border-[#1f2229] overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-[#1f2229]">
              <th className="text-left text-xs font-medium text-gray-400 uppercase tracking-wider px-4 py-3">
                Symbol
              </th>
              <th className="text-right text-xs font-medium text-gray-400 uppercase tracking-wider px-4 py-3">
                Price
              </th>
              <th className="text-right text-xs font-medium text-gray-400 uppercase tracking-wider px-4 py-3">
                24h Change
              </th>
              <th className="text-right text-xs font-medium text-gray-400 uppercase tracking-wider px-4 py-3">
                Volume (24h)
              </th>
              <th className="text-right text-xs font-medium text-gray-400 uppercase tracking-wider px-4 py-3 hidden lg:table-cell">
                High
              </th>
              <th className="text-right text-xs font-medium text-gray-400 uppercase tracking-wider px-4 py-3 hidden lg:table-cell">
                Low
              </th>
              <th className="text-center text-xs font-medium text-gray-400 uppercase tracking-wider px-4 py-3">
                Exchange
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#1f2229]">
            {tickers.map((ticker, idx) => (
              <tr 
                key={`${ticker.symbol}-${ticker.exchange}-${idx}`}
                className="table-row-hover cursor-pointer transition-colors"
                onClick={() => onTickerClick?.(ticker)}
              >
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-emerald-400/20 to-purple-400/20 flex items-center justify-center">
                      <span className="text-xs font-bold text-emerald-400">
                        {ticker.symbol.slice(0, 1)}
                      </span>
                    </div>
                    <div>
                      <div className="font-semibold">{ticker.symbol}</div>
                      <div className="text-xs text-gray-500">{ticker.symbol.replace('USDT', '')}/USDT</div>
                    </div>
                  </div>
                </td>
                <td className="px-4 py-3 text-right">
                  <div className="font-mono font-medium">${formatPrice(ticker.price)}</div>
                </td>
                <td className="px-4 py-3 text-right">
                  <div className={`flex items-center justify-end gap-1 ${
                    ticker.price_change_percent_24h >= 0 ? 'text-emerald-400' : 'text-red-400'
                  }`}>
                    {ticker.price_change_percent_24h >= 0 ? (
                      <ArrowUpRight className="w-4 h-4" />
                    ) : (
                      <ArrowDownRight className="w-4 h-4" />
                    )}
                    <span className="font-semibold">
                      {ticker.price_change_percent_24h >= 0 ? '+' : ''}
                      {ticker.price_change_percent_24h.toFixed(2)}%
                    </span>
                  </div>
                </td>
                <td className="px-4 py-3 text-right">
                  <div className="font-medium text-gray-300">
                    {formatVolume(ticker.quote_volume_24h)}
                  </div>
                </td>
                <td className="px-4 py-3 text-right hidden lg:table-cell">
                  <div className="text-sm text-gray-400">${formatPrice(ticker.high_24h)}</div>
                </td>
                <td className="px-4 py-3 text-right hidden lg:table-cell">
                  <div className="text-sm text-gray-400">${formatPrice(ticker.low_24h)}</div>
                </td>
                <td className="px-4 py-3 text-center">
                  <span className="px-2 py-1 rounded text-xs font-medium bg-[#1f2229] text-gray-400 uppercase">
                    {ticker.exchange}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      
      {tickers.length === 0 && (
        <div className="text-center py-12">
          <div className="text-gray-500">No tickers available</div>
        </div>
      )}
    </div>
  );
}
