import { create } from 'zustand';
import { Signal, TickerData, StrategyInfo } from '@/types';

interface MarketState {
  signals: Signal[];
  tickers: Record<string, TickerData>;
  strategies: StrategyInfo[];
  wsConnected: boolean;
  
  // Actions
  addSignal: (signal: Signal) => void;
  removeSignal: (id: string) => void;
  updateTicker: (ticker: TickerData) => void;
  setStrategies: (strategies: StrategyInfo[]) => void;
  setWsConnected: (connected: boolean) => void;
  clearSignals: () => void;
}

export const useMarketStore = create<MarketState>((set) => ({
  signals: [],
  tickers: {},
  strategies: [],
  wsConnected: false,
  
  addSignal: (signal) =>
    set((state) => ({
      signals: [signal, ...state.signals].slice(0, 100),
    })),
  
  removeSignal: (id) =>
    set((state) => ({
      signals: state.signals.filter((s) => s.id !== id),
    })),
  
  updateTicker: (ticker) =>
    set((state) => ({
      tickers: {
        ...state.tickers,
        [`${ticker.exchange}:${ticker.symbol}`]: ticker,
      },
    })),
  
  setStrategies: (strategies) => set({ strategies }),
  
  setWsConnected: (connected) => set({ wsConnected: connected }),
  
  clearSignals: () => set({ signals: [] }),
}));
