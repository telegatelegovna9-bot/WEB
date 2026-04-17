import { useEffect, useState, useCallback } from 'react';
import { useMarketStore } from '@/store/marketStore';
import { Signal, TickerData } from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws';

export function useWebSocket() {
  const { addSignal, updateTicker, setWsConnected } = useMarketStore();
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let ws: WebSocket | null = null;
    let reconnectTimeout: NodeJS.Timeout;
    let reconnectAttempts = 0;
    const MAX_RECONNECT_ATTEMPTS = 10;

    const connect = () => {
      try {
        ws = new WebSocket(WS_URL);

        ws.onopen = () => {
          console.log('WebSocket connected');
          setWsConnected(true);
          setIsConnected(true);
          setError(null);
          reconnectAttempts = 0;
        };

        ws.onmessage = (event) => {
          try {
            const message = JSON.parse(event.data);
            
            switch (message.type) {
              case 'signal':
                addSignal(message.data as Signal);
                break;
              case 'ticker':
                updateTicker(message.data as TickerData);
                break;
              case 'subscribed':
                console.log('Subscribed to:', message.symbol);
                break;
            }
          } catch (error) {
            console.error('Error parsing message:', error);
          }
        };

        ws.onclose = () => {
          console.log('WebSocket disconnected');
          setWsConnected(false);
          setIsConnected(false);
          
          // Reconnect with exponential backoff
          if (reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
            const delay = Math.min(1000 * Math.pow(2, reconnectAttempts), 30000);
            reconnectTimeout = setTimeout(connect, delay);
            reconnectAttempts++;
          } else {
            setError('Failed to connect after multiple attempts. Please refresh the page.');
          }
        };

        ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          setError('Connection error. Retrying...');
        };
      } catch (error) {
        console.error('Failed to connect WebSocket:', error);
        setError('Connection failed. Retrying...');
        reconnectTimeout = setTimeout(connect, 5000);
      }
    };

    connect();

    return () => {
      if (ws) {
        ws.close();
      }
      clearTimeout(reconnectTimeout);
    };
  }, [addSignal, updateTicker, setWsConnected]);

  const subscribe = useCallback((symbol: string) => {
    // Subscription logic can be added here
  }, []);

  return { isConnected, error, subscribe };
}
