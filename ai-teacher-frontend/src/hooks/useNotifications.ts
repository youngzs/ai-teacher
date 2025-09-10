import { useCallback } from 'react';
import { useAppStore } from '../store/appStore';
import type { NotificationItem } from '../types';

export const useNotifications = () => {
  const appStore = useAppStore();

  const showSuccess = useCallback((title: string, message: string, duration?: number) => {
    appStore.addNotification({
      type: 'success',
      title,
      message,
      duration,
    });
  }, [appStore]);

  const showError = useCallback((title: string, message: string, duration?: number) => {
    appStore.addNotification({
      type: 'error',
      title,
      message,
      duration,
    });
  }, [appStore]);

  const showWarning = useCallback((title: string, message: string, duration?: number) => {
    appStore.addNotification({
      type: 'warning',
      title,
      message,
      duration,
    });
  }, [appStore]);

  const showInfo = useCallback((title: string, message: string, duration?: number) => {
    appStore.addNotification({
      type: 'info',
      title,
      message,
      duration,
    });
  }, [appStore]);

  const removeNotification = useCallback((id: string) => {
    appStore.removeNotification(id);
  }, [appStore]);

  const clearAll = useCallback(() => {
    appStore.clearNotifications();
  }, [appStore]);

  return {
    notifications: appStore.notifications,
    showSuccess,
    showError,
    showWarning,
    showInfo,
    remove: removeNotification,
    clearAll,
  };
};