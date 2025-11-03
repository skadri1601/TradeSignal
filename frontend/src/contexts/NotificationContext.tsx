import React, { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState } from 'react';

// ------------------------------
// Types
// ------------------------------
export type NotificationKind = 'info' | 'success' | 'warning' | 'error';

export type NotificationItem = {
  id: string;
  title?: string;
  message: string;
  kind?: NotificationKind;
  createdAt?: number;
  meta?: Record<string, any>;
  duration?: number;
};

// ------------------------------
// Notification Context
// ------------------------------

type NotificationContextValue = {
  items: NotificationItem[];
  add: (n: Omit<NotificationItem, 'id' | 'createdAt'> & { id?: string }) => string;
  remove: (id: string) => void;
  clear: () => void;
};

const NotificationContext = createContext<NotificationContextValue | null>(null);

function useId() {
  const c = useRef(0);
  return () => `${Date.now()}_${c.current++}`;
}

export const NotificationProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [items, setItems] = useState<NotificationItem[]>([]);
  const genId = useId();

  const add: NotificationContextValue['add'] = useCallback((n) => {
    const id = n.id ?? genId();
    const createdAt = Date.now();
    setItems((prev) => [...prev, { id, createdAt, kind: 'info', duration: 6000, ...n }]);
    return id;
  }, []);

  const remove: NotificationContextValue['remove'] = useCallback((id) => {
    setItems((prev) => prev.filter((x) => x.id !== id));
  }, []);

  const clear = useCallback(() => setItems([]), []);

  const value = useMemo(() => ({ items, add, remove, clear }), [items, add, remove, clear]);

  return (
    <NotificationContext.Provider value={value}>
      {children}
      <ToastViewport items={items} onClose={remove} />
    </NotificationContext.Provider>
  );
};

export function useNotifications() {
  const ctx = useContext(NotificationContext);
  if (!ctx) throw new Error('useNotifications must be used within NotificationProvider');
  return ctx;
}

// ------------------------------
// Toast Components
// ------------------------------

const kindStyles: Record<NotificationKind, string> = {
  info: 'bg-blue-600 text-white border-blue-500',
  success: 'bg-emerald-600 text-white border-emerald-500',
  warning: 'bg-amber-500 text-white border-amber-400',
  error: 'bg-rose-600 text-white border-rose-500',
};

const Icon: React.FC<{ kind: NotificationKind }> = ({ kind }) => {
  const common = 'w-4 h-4 flex-none';
  switch (kind) {
    case 'success':
      return (
        <svg className={common} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M20 6L9 17l-5-5" />
        </svg>
      );
    case 'warning':
      return (
        <svg className={common} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
          <path d="M12 9v4" />
          <path d="M12 17h.01" />
        </svg>
      );
    case 'error':
      return (
        <svg className={common} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M18 6L6 18M6 6l12 12" />
        </svg>
      );
    default:
      return (
        <svg className={common} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <circle cx="12" cy="12" r="10" />
          <path d="M12 8v4m0 4h.01" />
        </svg>
      );
  }
};

const Toast: React.FC<{ item: NotificationItem; onClose: (id: string) => void }> = ({ item, onClose }) => {
  const [hovered, setHovered] = useState(false);

  useEffect(() => {
    const duration = item.duration ?? 6000;
    if (duration <= 0) return;
    let id: number;
    const start = () => {
      id = window.setTimeout(() => onClose(item.id), duration);
    };
    start();
    return () => window.clearTimeout(id);
  }, [item.id, item.duration, onClose]);

  const kind = item.kind ?? 'info';

  return (
    <div
      role="status"
      aria-live="polite"
      className={`pointer-events-auto w-96 max-w-[92vw] overflow-hidden rounded-2xl border shadow-lg ${kindStyles[kind]} transition-all`}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
    >
      <div className="p-4 flex gap-3 items-start">
        <div className="mt-1">
          <Icon kind={kind} />
        </div>
        <div className="flex-1">
          {item.title ? <div className="font-semibold leading-tight">{item.title}</div> : null}
          <div className="text-sm opacity-90 whitespace-pre-wrap">{item.message}</div>
          {item.meta?.link ? (
            <a
              href={item.meta.link}
              className="inline-block mt-2 text-xs underline underline-offset-4 hover:opacity-80"
            >
              View Details
            </a>
          ) : null}
        </div>
        <button
          aria-label="Close"
          className="opacity-80 hover:opacity-100 focus:outline-none"
          onClick={() => onClose(item.id)}
        >
          <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M18 6L6 18M6 6l12 12" />
          </svg>
        </button>
      </div>
      {hovered ? (
        <div className="h-1 w-full bg-black/10">
          <div className="h-1 w-full bg-white/40 animate-pulse" />
        </div>
      ) : null}
    </div>
  );
};

const ToastViewport: React.FC<{
  items: NotificationItem[];
  onClose: (id: string) => void;
}> = ({ items, onClose }) => {
  return (
    <div
      aria-live="polite"
      className="pointer-events-none fixed bottom-4 right-4 z-[1000] flex flex-col gap-3"
    >
      {items.map((it) => (
        <Toast key={it.id} item={it} onClose={onClose} />
      ))}
    </div>
  );
};
