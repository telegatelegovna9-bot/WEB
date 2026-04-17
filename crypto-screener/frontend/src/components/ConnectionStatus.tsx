'use client';

import { useMarketStore } from '@/store/marketStore';

export function ConnectionStatus() {
  const wsConnected = useMarketStore((state) => state.wsConnected);

  return (
    <div className="flex items-center gap-2 text-sm">
      <div className={`w-2 h-2 rounded-full ${wsConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`} />
      <span className={wsConnected ? 'text-green-500' : 'text-red-500'}>
        {wsConnected ? 'Connected' : 'Disconnected'}
      </span>
    </div>
  );
}
