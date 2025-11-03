import { useState, useEffect } from 'react';
import apiClient from '../api/client';

interface PushState {
  supported: boolean;
  subscribed: boolean;
  loading: boolean;
  permission: NotificationPermission;
}

export function usePushNotifications() {
  const [state, setState] = useState<PushState>({
    supported: false,
    subscribed: false,
    loading: false,
    permission: 'default'
  });

  useEffect(() => {
    const supported =
      'serviceWorker' in navigator &&
      'PushManager' in window &&
      'Notification' in window;

    setState(prev => ({
      ...prev,
      supported,
      permission: Notification.permission
    }));

    // Check if already subscribed
    if (supported) {
      checkSubscription();
    }
  }, []);

  const checkSubscription = async () => {
    try {
      const registration = await navigator.serviceWorker.ready;
      const subscription = await registration.pushManager.getSubscription();
      setState(prev => ({ ...prev, subscribed: !!subscription }));
    } catch (error) {
      console.error('Failed to check subscription:', error);
    }
  };

  const subscribe = async () => {
    if (!state.supported) {
      throw new Error('Push notifications not supported');
    }

    setState(prev => ({ ...prev, loading: true }));

    try {
      // Request notification permission
      const permission = await Notification.requestPermission();
      setState(prev => ({ ...prev, permission }));

      if (permission !== 'granted') {
        throw new Error('Notification permission denied');
      }

      // Get VAPID public key from backend
      const { data } = await apiClient.get('/api/v1/push/vapid-public-key');
      const publicKey = data.publicKey;

      // Get service worker registration
      const registration = await navigator.serviceWorker.ready;

      // Subscribe to push service
      const subscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: urlBase64ToUint8Array(publicKey) as BufferSource
      });

      // Send subscription to backend
      const subscriptionJson = subscription.toJSON();
      await apiClient.post('/api/v1/push/subscribe', {
        endpoint: subscription.endpoint,
        p256dh_key: subscriptionJson.keys?.p256dh,
        auth_key: subscriptionJson.keys?.auth,
        user_agent: navigator.userAgent
      });

      setState(prev => ({ ...prev, subscribed: true }));
      console.log('✅ Push subscription successful');
      return true;
    } catch (error) {
      console.error('❌ Push subscription failed:', error);
      throw error;
    } finally {
      setState(prev => ({ ...prev, loading: false }));
    }
  };

  const unsubscribe = async () => {
    setState(prev => ({ ...prev, loading: true }));

    try {
      const registration = await navigator.serviceWorker.ready;
      const subscription = await registration.pushManager.getSubscription();

      if (subscription) {
        // Remove from backend first
        await apiClient.post('/api/v1/push/unsubscribe', {
          endpoint: subscription.endpoint
        });

        // Then unsubscribe from browser
        await subscription.unsubscribe();

        setState(prev => ({ ...prev, subscribed: false }));
        console.log('✅ Push unsubscription successful');
      }
    } catch (error) {
      console.error('❌ Push unsubscribe failed:', error);
      throw error;
    } finally {
      setState(prev => ({ ...prev, loading: false }));
    }
  };

  return {
    ...state,
    subscribe,
    unsubscribe,
    refresh: checkSubscription
  };
}

// Helper function to convert base64 string to Uint8Array
function urlBase64ToUint8Array(base64String: string): Uint8Array {
  const padding = '='.repeat((4 - base64String.length % 4) % 4);
  const base64 = (base64String + padding)
    .replace(/-/g, '+')
    .replace(/_/g, '/');

  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);

  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }

  return outputArray;
}
