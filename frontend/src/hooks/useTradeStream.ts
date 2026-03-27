import { useEffect, useRef, useState } from 'react';

type TradeStreamMessage = {
  type: string;
  [key: string]: unknown;
};

type TradeStreamStatus = 'idle' | 'connecting' | 'open' | 'closed';

export function buildTradeStreamUrl(): string {
  const httpBase = (import.meta.env.VITE_API_URL || 'https://api.tradesignal.capital').replace(/\/$/, '');
  const protocol = httpBase.startsWith('https') ? 'wss' : 'ws';
  return httpBase.replace(/^https?/, protocol) + '/api/v1/trades/stream';
}

function parseTradeMessage(raw: string): TradeStreamMessage | null {
  try {
    return JSON.parse(raw);
  } catch (error) {
    console.error('Trade stream message parse error', error);
    return null;
  }
}

function sendHeartbeat(socket: WebSocket | null): void {
  try {
    socket?.send('ping');
  } catch {
    // Ignore send failures during heartbeat
  }
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
        heartbeatInterval = window.setInterval(() => sendHeartbeat(socket), 15000);
      };

      socket.onmessage = (event) => {
        const data = parseTradeMessage(event.data);
        if (data) callbackRef.current?.(data);
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
