interface Ticker {
  symbol: string;
  exchange: string;
  price: number;
  price_change_percent_24h: number;
  volume_24h: number;
}

interface TickerTableProps {
  tickers: Ticker[];
}

export default function TickerTable({ tickers }: TickerTableProps) {
  const sortedTickers = [...tickers].sort((a, b) => 
    Math.abs(b.price_change_percent_24h) - Math.abs(a.price_change_percent_24h)
  ).slice(0, 15);

  return (
    <div className="card">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="text-xs text-gray-400 border-b border-surface2">
              <th className="text-left py-3 px-2 font-medium">Symbol</th>
              <th className="text-right py-3 px-2 font-medium">Price</th>
              <th className="text-right py-3 px-2 font-medium\">24h %</th>
            </tr>
          </thead>
          <tbody>
            {sortedTickers.map(ticker => (
              <tr key={`${ticker.exchange}-${ticker.symbol}`} className="border-b border-surface2/50 hover:bg-surface2/50 transition-colors">
                <td className="py-3 px-2">
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-white text-sm">{ticker.symbol.replace('USDT', '')}</span>
                    <span className="text-xs text-gray-500 uppercase">{ticker.exchange}</span>
                  </div>
                </td>
                <td className="text-right py-3 px-2 text-sm text-white">
                  ${ticker.price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 6 })}
                </td>
                <td className={`text-right py-3 px-2 text-sm font-medium ${
                  ticker.price_change_percent_24h >= 0 ? 'text-success' : 'text-danger'
                }`}>
                  {ticker.price_change_percent_24h >= 0 ? '+' : ''}{ticker.price_change_percent_24h.toFixed(2)}%
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      
      {tickers.length === 0 && (
        <div className="text-center py-8 text-gray-500 text-sm">
          Loading market data...
        </div>
      )}
    </div>
  );
}
