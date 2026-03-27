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
  token?: string | null;
};

function parseAlertPayload(raw: string): ServerAlert[] | null {
  try {
    const data = JSON.parse(raw);

    if (!Array.isArray(data) && (data.type === 'pong' || data.type === 'connection_ack')) {
      if (data.type === 'connection_ack') {
        console.log('Alert connection acknowledged:', data.authenticated ? 'authenticated' : 'anonymous');
      }
      return null;
    }

    return Array.isArray(data) ? data : [data];
  } catch (e) {
    console.error('Failed to parse alert payload:', e);
    return null;
  }
}

function buildWsUrl(url: string, token: string | null | undefined): string {
  if (!token) return url;
  const separator = url.includes('?') ? '&' : '?';
  return `${url}${separator}token=${token}`;
}

export function useRealtimeAlerts({ url, enabled = true, autoReconnect = true, token }: UseRealtimeAlertsOpts) {
  const { add } = useNotifications();
  const wsRef = useRef<WebSocket | null>(null);
  const retryRef = useRef(0);
  const connectingRef = useRef(false);

  const connect = useCallback(() => {
    if (connectingRef.current) return;
    connectingRef.current = true;

    const ws = new WebSocket(buildWsUrl(url, token));
    wsRef.current = ws;

    ws.onopen = () => {
      retryRef.current = 0;
      connectingRef.current = false;
      console.log('Connected to real-time alerts', token ? '(authenticated)' : '(anonymous)');
    };

    ws.onmessage = (ev) => {
      const alerts = parseAlertPayload(ev.data);
      if (!alerts) return;

      alerts.forEach((a) => {
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
  }, [add, autoReconnect, enabled, url, token]);

  useEffect(() => {
    if (!enabled) return;
    connect();
    return () => {
      retryRef.current = 0;
      wsRef.current?.close();
      wsRef.current = null;
    };
  }, [enabled, connect]);

  useEffect(() => {
    const t = setInterval(() => {
      try {
        wsRef.current?.send(JSON.stringify({ type: 'ping', t: Date.now() }));
      } catch {}
    }, 25000);
    return () => clearInterval(t);
  }, []);
}
