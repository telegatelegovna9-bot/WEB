'use client';

import { OrderBook, OrderBookEntry } from '@/types';

interface OrderBookVisualizationProps {
  orderbook: OrderBook;
  maxDepth?: number;
}

export function OrderBookVisualization({ orderbook, maxDepth = 10 }: OrderBookVisualizationProps) {
  const maxTotal = Math.max(
    ...orderbook.bids.slice(0, maxDepth).map(b => b.total || 0),
    ...orderbook.asks.slice(0, maxDepth).map(a => a.total || 0)
  );

  const formatPrice = (price: number) => {
    if (price >= 1000) return price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    if (price >= 1) return price.toFixed(4);
    return price.toFixed(6);
  };

  const formatQuantity = (qty: number) => {
    if (qty >= 1000) return `${(qty / 1000).toFixed(2)}K`;
    if (qty >= 1) return qty.toFixed(4);
    return qty.toFixed(6);
  };

  return (
    <div className="glass-card rounded-lg overflow-hidden">
      <div className="p-3 border-b border-white/10">
        <h3 className="font-semibold text-sm flex items-center gap-2">
          <span>📊</span>
          Order Book - {orderbook.symbol}
        </h3>
      </div>
      
      <div className="grid grid-cols-2 divide-x divide-white/10">
        {/* Bids */}
        <div>
          <div className="px-3 py-2 text-xs text-green-500 font-semibold bg-green-500/5">
            BIDS (BUY)
          </div>
          <div className="space-y-0.5 p-2">
            {orderbook.bids.slice(0, maxDepth).reverse().map((bid, idx) => (
              <div key={`bid-${idx}`} className="relative flex items-center justify-between text-xs px-2 py-1 hover:bg-white/5 rounded">
                <div 
                  className="absolute inset-0 bg-green-500/20 rounded"
                  style={{ width: `${((bid.total || 0) / maxTotal) * 100}%`, right: 0, left: 'auto' }}
                />
                <span className="relative z-10 text-green-400 font-mono">{formatPrice(bid.price)}</span>
                <span className="relative z-10 text-gray-300">{formatQuantity(bid.quantity)}</span>
                <span className="relative z-10 text-gray-500 w-12 text-right">{formatQuantity(bid.total || 0)}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Asks */}
        <div>
          <div className="px-3 py-2 text-xs text-red-500 font-semibold bg-red-500/5">
            ASKS (SELL)
          </div>
          <div className="space-y-0.5 p-2">
            {orderbook.asks.slice(0, maxDepth).map((ask, idx) => (
              <div key={`ask-${idx}`} className="relative flex items-center justify-between text-xs px-2 py-1 hover:bg-white/5 rounded">
                <div 
                  className="absolute inset-0 bg-red-500/20 rounded"
                  style={{ width: `${((ask.total || 0) / maxTotal) * 100}%`, right: 0, left: 'auto' }}
                />
                <span className="relative z-10 text-red-400 font-mono">{formatPrice(ask.price)}</span>
                <span className="relative z-10 text-gray-300">{formatQuantity(ask.quantity)}</span>
                <span className="relative z-10 text-gray-500 w-12 text-right">{formatQuantity(ask.total || 0)}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Spread Info */}
      <div className="px-3 py-2 border-t border-white/10 bg-white/5">
        <div className="flex items-center justify-between text-xs">
          <span className="text-gray-400">Spread:</span>
          <span className="font-mono">
            {orderbook.asks.length > 0 && orderbook.bids.length > 0 
              ? formatPrice(orderbook.asks[0].price - orderbook.bids[orderbook.bids.length - 1].price)
              : 'N/A'}
          </span>
        </div>
      </div>
    </div>
  );
}
