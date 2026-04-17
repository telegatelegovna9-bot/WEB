import { useEffect, useCallback } from 'react';
import { useMarketStore } from '@/store/marketStore';
import { Signal, TickerData } from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws';

export function useWebSocket() {
  const { addSignal, updateTicker, setWsConnected } = useMarketStore();

  useEffect(() => {
    let ws: WebSocket | null = null;
    let reconnectTimeout: NodeJS.Timeout;

    const connect = () => {
      try {
        ws = new WebSocket(WS_URL);

        ws.onopen = () => {
          console.log('WebSocket connected');
          setWsConnected(true);
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
          
          // Reconnect after 5 seconds
          reconnectTimeout = setTimeout(connect, 5000);
        };

        ws.onerror = (error) => {
          console.error('WebSocket error:', error);
        };
      } catch (error) {
        console.error('Failed to connect WebSocket:', error);
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

  return { subscribe };
}
