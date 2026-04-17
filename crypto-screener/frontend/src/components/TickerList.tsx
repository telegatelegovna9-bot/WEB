'use client';

import { useMarketStore } from '@/store/marketStore';

export function TickerList() {
  const tickers = useMarketStore((state) => state.tickers);
  const tickerArray = Object.values(tickers);

  if (tickerArray.length === 0) {
    return (
      <div className="flex items-center justify-center h-32 text-gray-500">
        No ticker data yet...
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-gray-700">
            <th className="text-left py-2 px-3">Symbol</th>
            <th className="text-right py-2 px-3">Price</th>
            <th className="text-right py-2 px-3">24h Change</th>
            <th className="text-right py-2 px-3">24h Volume</th>
          </tr>
        </thead>
        <tbody>
          {tickerArray.map((ticker) => (
            <tr key={`${ticker.exchange}:${ticker.symbol}`} className="border-b border-gray-800 hover:bg-white/5">
              <td className="py-2 px-3">
                <div className="flex items-center gap-2">
                  <span className="font-medium">{ticker.symbol}</span>
                  <span className="text-xs px-1.5 py-0.5 rounded bg-gray-700 uppercase">
                    {ticker.exchange}
                  </span>
                </div>
              </td>
              <td className="text-right py-2 px-3 font-mono">
                ${ticker.price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 6 })}
              </td>
              <td className={`text-right py-2 px-3 ${
                ticker.price_change_percent_24h >= 0 ? 'text-green-500' : 'text-red-500'
              }`}>
                {ticker.price_change_percent_24h >= 0 ? '+' : ''}
                {ticker.price_change_percent_24h.toFixed(2)}%
              </td>
              <td className="text-right py-2 px-3 text-gray-400">
                ${(ticker.volume_24h / 1000000).toFixed(2)}M
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
