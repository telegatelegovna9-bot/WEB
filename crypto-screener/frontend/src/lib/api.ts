'use client';

import { useEffect, useState, useCallback } from 'react';
import { Signal, Ticker, Stats, Exchange } from '@/lib/types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export function useWebSocket() {
  const [connected, setConnected] = useState(false);
  const [tickers, setTickers] = useState<Ticker[]>([]);
  const [signals, setSignals] = useState<Signal[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);

  useEffect(() => {
    let ws: WebSocket | null = null;
    let reconnectTimeout: NodeJS.Timeout;

    const connect = () => {
      try {
        ws = new WebSocket(`ws://${window.location.hostname}:8000/ws`);

        ws.onopen = () => {
          console.log('✅ WebSocket connected');
          setConnected(true);
        };

        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            
            if (data.type === 'initial') {
              setTickers(data.tickers || []);
              setSignals(data.signals || []);
              setStats(data.stats || null);
            } else if (data.type === 'update') {
              setTickers(data.tickers || tickers);
              setSignals(data.signals || signals);
            }
          } catch (e) {
            console.error('WebSocket message error:', e);
          }
        };

        ws.onclose = () => {
          console.log('❌ WebSocket disconnected, reconnecting...');
          setConnected(false);
          reconnectTimeout = setTimeout(connect, 3000);
        };

        ws.onerror = (error) => {
          console.error('WebSocket error:', error);
        };
      } catch (e) {
        console.error('WebSocket connection error:', e);
        reconnectTimeout = setTimeout(connect, 3000);
      }
    };

    connect();

    return () => {
      if (ws) {
        ws.close();
      }
      if (reconnectTimeout) {
        clearTimeout(reconnectTimeout);
      }
    };
  }, []);

  return { connected, tickers, signals, stats };
}

export async function fetchTickers(params?: {
  exchange?: string;
  search?: string;
  sort_by?: string;
  limit?: number;
}): Promise<Ticker[]> {
  const url = new URL(`${API_BASE}/api/tickers`);
  if (params?.exchange) url.searchParams.set('exchange', params.exchange);
  if (params?.search) url.searchParams.set('search', params.search);
  if (params?.sort_by) url.searchParams.set('sort_by', params.sort_by);
  if (params?.limit) url.searchParams.set('limit', params.limit.toString());

  const res = await fetch(url.toString());
  if (!res.ok) throw new Error('Failed to fetch tickers');
  const data = await res.json();
  return data.tickers;
}

export async function fetchSignals(params?: {
  exchange?: string;
  signal_type?: string;
  min_probability?: number;
  search?: string;
  limit?: number;
}): Promise<Signal[]> {
  const url = new URL(`${API_BASE}/api/signals`);
  if (params?.exchange) url.searchParams.set('exchange', params.exchange);
  if (params?.signal_type) url.searchParams.set('signal_type', params.signal_type);
  if (params?.min_probability) url.searchParams.set('min_probability', params.min_probability.toString());
  if (params?.search) url.searchParams.set('search', params.search);
  if (params?.limit) url.searchParams.set('limit', params.limit.toString());

  const res = await fetch(url.toString());
  if (!res.ok) throw new Error('Failed to fetch signals');
  const data = await res.json();
  return data.signals;
}

export async function fetchStats(): Promise<Stats> {
  const res = await fetch(`${API_BASE}/api/stats`);
  if (!res.ok) throw new Error('Failed to fetch stats');
  return res.json();
}

export async function fetchExchanges(): Promise<Exchange[]> {
  const res = await fetch(`${API_BASE}/api/exchanges`);
  if (!res.ok) throw new Error('Failed to fetch exchanges');
  const data = await res.json();
  return data.exchanges;
}

export function formatPrice(price: number): string {
  if (price >= 1000) {
    return price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  } else if (price >= 1) {
    return price.toFixed(4);
  } else {
    return price.toFixed(6);
  }
}

export function formatVolume(volume: number): string {
  if (volume >= 1_000_000_000) {
    return `$${(volume / 1_000_000_000).toFixed(2)}B`;
  } else if (volume >= 1_000_000) {
    return `$${(volume / 1_000_000).toFixed(2)}M`;
  } else if (volume >= 1_000) {
    return `$${(volume / 1_000).toFixed(2)}K`;
  }
  return `$${volume.toFixed(2)}`;
}

export function getSignalBadgeClass(type: string): string {
  switch (type.toLowerCase()) {
    case 'pump':
      return 'badge-pump';
    case 'dump':
      return 'badge-dump';
    case 'volume_spike':
      return 'badge-volume';
    default:
      return 'badge-volume';
  }
}

export function getBehaviorLabel(behavior: string): string {
  const labels: Record<string, string> = {
    smart_money_accumulation: 'Smart Money Accumulation',
    distribution: 'Distribution',
    fomo: 'FOMO Rally',
    manipulation: 'Potential Manipulation',
    breakout_confirmed: 'Breakout Confirmed',
    false_breakout: 'False Breakout Risk'
  };
  return labels[behavior] || behavior;
}

export function getConfidenceColor(confidence: string): string {
  switch (confidence.toLowerCase()) {
    case 'very_high':
      return '#10b981';
    case 'high':
      return '#00d4aa';
    case 'medium':
      return '#f59e0b';
    case 'low':
      return '#ef4444';
    default:
      return '#6b7280';
  }
}
