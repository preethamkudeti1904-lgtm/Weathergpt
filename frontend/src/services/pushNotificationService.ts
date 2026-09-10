import { api } from './api';

function urlBase64ToUint8Array(base64String: string): Uint8Array {
  const padding = '='.repeat((4 - (base64String.length % 4)) % 4);
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);
  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }
  return outputArray;
}

export class PushNotificationService {
  public isSupported(): boolean {
    return (
      typeof window !== 'undefined' &&
      'serviceWorker' in navigator &&
      'PushManager' in window &&
      'Notification' in window
    );
  }

  public getPermissionState(): NotificationPermission {
    if (typeof window === 'undefined' || !('Notification' in window)) {
      return 'denied';
    }
    return Notification.permission;
  }

  public async registerServiceWorker(): Promise<ServiceWorkerRegistration | null> {
    if (!this.isSupported()) return null;
    try {
      const reg = await navigator.serviceWorker.register('/sw.js', { scope: '/' });
      await navigator.serviceWorker.ready;
      return reg;
    } catch (e) {
      console.warn('Service worker registration failed:', e);
      return null;
    }
  }

  public async subscribeToPush(): Promise<{ success: boolean; error?: string }> {
    if (!this.isSupported()) {
      return { success: false, error: 'Web Push notifications are not supported in this browser.' };
    }

    try {
      // 1. Request permission
      const permission = await Notification.requestPermission();
      if (permission !== 'granted') {
        return { success: false, error: 'Notification permission was denied by the user.' };
      }

      // 2. Register Service Worker
      const reg = await this.registerServiceWorker();
      if (!reg) {
        return { success: false, error: 'Failed to initialize service worker.' };
      }

      // 3. Get VAPID public key from backend
      const keyData = await api.getVapidPublicKey();
      if (!keyData?.publicKey) {
        return { success: false, error: 'Could not retrieve VAPID key from server.' };
      }

      const convertedKey = urlBase64ToUint8Array(keyData.publicKey);

      // 4. Subscribe via PushManager
      const subscription = await reg.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: convertedKey as unknown as BufferSource
      });

      const subJson = subscription.toJSON();
      if (!subJson.endpoint || !subJson.keys?.p256dh || !subJson.keys?.auth) {
        return { success: false, error: 'Incomplete push subscription generated.' };
      }

      // 5. Send to backend
      await api.savePushSubscription({
        endpoint: subJson.endpoint,
        p256dh: subJson.keys.p256dh,
        auth: subJson.keys.auth,
        user_agent: navigator.userAgent
      });

      return { success: true };
    } catch (err: any) {
      console.error('Push subscription error:', err);
      return { success: false, error: err.message || 'Error enabling notifications' };
    }
  }

  public async unsubscribe(): Promise<boolean> {
    if (!this.isSupported()) return false;
    try {
      const reg = await navigator.serviceWorker.getRegistration();
      if (reg) {
        const sub = await reg.pushManager.getSubscription();
        if (sub) {
          const endpoint = sub.endpoint;
          await sub.unsubscribe();
          await api.deletePushSubscription(endpoint);
        }
      }
      return true;
    } catch (e) {
      console.error('Error unsubscribing:', e);
      return false;
    }
  }
}

export const pushNotificationService = new PushNotificationService();
