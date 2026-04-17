export interface Signal {
  id: string;
  type: 'pump' | 'dump' | 'order_book_wall' | 'listing' | 'breakout';
  symbol: string;
  exchange: string;
  price: number;
  intelligence: SignalIntelligence;
  created_at: string;
  expires_at?: string;
  is_active: boolean;
}

export interface SignalIntelligence {
  causes: string[];
  market_behavior: 'accumulation' | 'distribution' | 'breakout' | 'manipulation' | 'normal';
  confidence_score: number;
  historical_patterns: HistoricalPattern[];
  smart_money_indicators: Record<string, any>;
  risk_level: 'low' | 'medium' | 'high';
  recommended_action?: string;
}

export interface HistoricalPattern {
  pattern_id: string;
  similarity_score: number;
  date: string;
  outcome: string;
  outcome_percent: number;
  days_to_outcome: number;
}

export interface TickerData {
  symbol: string;
  exchange: string;
  price: number;
  volume_24h: number;
  price_change_24h: number;
  price_change_percent_24h: number;
  high_24h: number;
  low_24h: number;
  timestamp: string;
}

export interface OrderBookEntry {
  price: number;
  quantity: number;
  total?: number;
}

export interface OrderBook {
  symbol: string;
  exchange: string;
  bids: OrderBookEntry[];
  asks: OrderBookEntry[];
  timestamp: string;
}

export interface StrategyInfo {
  name: string;
  enabled: boolean;
  min_confidence: number;
  config: Record<string, any>;
}
