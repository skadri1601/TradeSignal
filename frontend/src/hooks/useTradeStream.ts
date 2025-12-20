import { useEffect, useRef, useState } from 'react';

type TradeStreamMessage = {
  type: string;
  [key: string]: unknown;
};

type TradeStreamStatus = 'idle' | 'connecting' | 'open' | 'closed';

export function buildTradeStreamUrl(): string {
  const httpBase = (import.meta.env.VITE_API_URL || 'https://api.yourdomain.com').replace(/\/$/, '');
  const protocol = httpBase.startsWith('https') ? 'wss' : 'ws';
  return httpBase.replace(/^https?/, protocol) + '/api/v1/trades/stream';
}

export default function useTradeStream(
  onMessage: (payload: TradeStreamMessage) => void,
  enabled: boolean = true
): TradeStreamStatus {
  const callbackRef = useRef(onMessage);
  const [status, setStatus] = useState<TradeStreamStatus>('idle');

  useEffect(() => {
    callbackRef.current = onMessage;
  }, [onMessage]);

  useEffect(() => {
    if (!enabled) {
      return;
    }

    let socket: WebSocket | null = null;
    let reconnectTimeout: number | undefined;
    let heartbeatInterval: number | undefined;
    let shouldReconnect = true;

    const connect = () => {
      const url = buildTradeStreamUrl();
      setStatus('connecting');

      try {
        socket = new WebSocket(url);
      } catch (err) {
        setStatus('closed');
        reconnectTimeout = window.setTimeout(connect, 3000);
        return;
      }

      socket.onopen = () => {
        setStatus('open');
        heartbeatInterval = window.setInterval(() => {
          try {
            socket?.send('ping');
          } catch (error) {
            // Ignore send failures during heartbeat
          }
        }, 15000);
      };

      socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          callbackRef.current?.(data);
        } catch (error) {
          console.error('Trade stream message parse error', error);
        }
      };

      socket.onerror = () => {
        setStatus('closed');
      };

      socket.onclose = () => {
        setStatus('closed');
        if (heartbeatInterval) {
          window.clearInterval(heartbeatInterval);
        }
        if (shouldReconnect) {
          reconnectTimeout = window.setTimeout(connect, 3000);
        }
      };
    };

    connect();

    return () => {
      shouldReconnect = false;
      if (reconnectTimeout) {
        window.clearTimeout(reconnectTimeout);
      }
      if (heartbeatInterval) {
        window.clearInterval(heartbeatInterval);
      }
      if (socket && (socket.readyState === WebSocket.OPEN || socket.readyState === WebSocket.CONNECTING)) {
        socket.close();
      }
    };
  }, [enabled]);

  return status;
}

