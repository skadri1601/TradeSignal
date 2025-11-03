import { useCallback, useEffect, useRef } from 'react';
import { useNotifications, NotificationKind } from '../contexts/NotificationContext';

export type ServerAlert = {
  id?: string;
  title?: string;
  message: string;
  kind?: NotificationKind;
  duration?: number;
  meta?: Record<string, any>;
};

type UseRealtimeAlertsOpts = {
  url: string;
  enabled?: boolean;
  autoReconnect?: boolean;
};

export function useRealtimeAlerts({ url, enabled = true, autoReconnect = true }: UseRealtimeAlertsOpts) {
  const { add } = useNotifications();
  const wsRef = useRef<WebSocket | null>(null);
  const retryRef = useRef(0);
  const connectingRef = useRef(false);

  const connect = useCallback(() => {
    if (connectingRef.current) return;
    connectingRef.current = true;

    try {
      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        retryRef.current = 0;
        connectingRef.current = false;
        console.log('✅ Connected to real-time alerts');
      };

      ws.onmessage = (ev) => {
        try {
          const data = JSON.parse(ev.data);

          // Ignore pong messages from keepalive
          if (!Array.isArray(data) && data.type === 'pong') {
            return;
          }

          const list = Array.isArray(data) ? data : [data];
          list.forEach((a) => {
            // Only show notifications with actual message content
            if (!a.message) return;

            add({
              id: a.id,
              title: a.title,
              message: a.message,
              kind: a.kind ?? 'info',
              duration: a.duration ?? 6000,
              meta: a.meta,
            });
          });
        } catch (e) {
          console.error('Failed to parse alert payload:', e);
        }
      };

      ws.onerror = (err) => {
        console.error('Alert WebSocket error:', err);
      };

      ws.onclose = () => {
        wsRef.current = null;
        connectingRef.current = false;
        if (autoReconnect && enabled) {
          const backoff = Math.min(30000, 1000 * Math.pow(2, retryRef.current++));
          console.log(`Reconnecting to alerts in ${backoff}ms...`);
          setTimeout(connect, backoff);
        }
      };
    } catch (e) {
      console.error('Failed to connect to alerts:', e);
      connectingRef.current = false;
    }
  }, [add, autoReconnect, enabled, url]);

  useEffect(() => {
    if (!enabled) return;
    connect();
    return () => {
      retryRef.current = 0;
      wsRef.current?.close();
      wsRef.current = null;
    };
  }, [enabled, connect]);

  // Send heartbeat every 25s to keep connection alive
  useEffect(() => {
    const t = setInterval(() => {
      try {
        wsRef.current?.send(JSON.stringify({ type: 'ping', t: Date.now() }));
      } catch {}
    }, 25000);
    return () => clearInterval(t);
  }, []);
}
