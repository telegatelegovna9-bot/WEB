export const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
export const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws';

export interface Signal {
  id: string | null;
  signal_type: string;
  symbol: string;
  exchange: string;
  price: number;
  price_change_percent: number;
  volume_change_percent: number;
  confidence_score: number;
  explanation: {
    reasons: string[];
    market_behavior: string;
    smart_money_activity: boolean;
    unusual_volume: boolean;
    orderbook_changes: string[];
  };
  historical_analogies: Array<{
    date: string;
    symbol: string;
    similarity_score: number;
    outcome: string;
    price_change_after: number;
    time_frame: string;
  }>;
  timestamp: string;
}

export interface SignalStats {
  total_signals: number;
  accuracy_rate: number;
  win_rate: number;
  avg_confidence: number;
  signals_by_type: Record<string, number>;
  signals_by_exchange: Record<string, number>;
}

class ApiService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = API_URL;
  }

  async getSignals(params?: {
    limit?: number;
    offset?: number;
    signal_type?: string;
    exchange?: string;
    symbol?: string;
    min_confidence?: number;
  }): Promise<Signal[]> {
    const url = new URL(`${this.baseUrl}/signals`);
    
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          url.searchParams.append(key, value.toString());
        }
      });
    }

    const response = await fetch(url.toString());
    
    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`);
    }

    return response.json();
  }

  async getSignalStats(hours: number = 24): Promise<SignalStats> {
    const response = await fetch(`${this.baseUrl}/signals/stats?hours=${hours}`);
    
    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`);
    }

    return response.json();
  }

  async getHealth(): Promise<{ status: string; service: string; version: string }> {
    const response = await fetch(`${this.baseUrl}/health`);
    
    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`);
    }

    return response.json();
  }
}

export const apiService = new ApiService();
