export interface Ticker {
  symbol: string;
  exchange: string;
  price: number;
  price_change_24h: number;
  price_change_percent_24h: number;
  volume_24h: number;
  quote_volume_24h: number;
  high_24h: number;
  low_24h: number;
  last_update: string;
}

export interface Reason {
  description: string;
  weight: number;
  type: string;
}

export interface HistoricalAnalogy {
  date: string;
  symbol: string;
  outcome: string;
  price_change_percent: number;
  similarity_score: number;
}

export interface SignalIntelligence {
  reasons: Reason[];
  market_behavior: string;
  probability_score: number;
  confidence_level: string;
  historical_analogies: HistoricalAnalogy[];
  explanation: string;
}

export interface Signal {
  id: string;
  type: string;
  symbol: string;
  exchange: string;
  timestamp: string;
  price: number;
  price_change_percent: number;
  volume_change_percent: number;
  intelligence: SignalIntelligence;
  is_new: boolean;
  tags: string[];
}

export interface Stats {
  total_signals: number;
  signals_last_hour: number;
  active_exchanges: number;
  tracked_symbols: number;
  top_gainers: Ticker[];
  top_losers: Ticker[];
  top_volume: Ticker[];
  avg_signal_accuracy: number;
}

export interface Exchange {
  id: string;
  name: string;
  active: boolean;
}
