import { useCallback } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { api } from '../services/api';
import { useAppStore } from '../store/appStore';
import type { LoginForm, RegisterForm } from '../types';

export const useAuth = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const authStore = useAuthStore();
  const appStore = useAppStore();

  const login = useCallback(async (credentials: LoginForm) => {
    try {
      await authStore.login(credentials);
      
      // Get return URL from location state or default to dashboard
      const from = (location.state as any)?.from || '/dashboard';
      navigate(from, { replace: true });

      appStore.addNotification({
        type: 'success',
        title: 'Welcome back!',
        message: 'You have successfully logged in.',
      });
    } catch (error: any) {
      appStore.addNotification({
        type: 'error',
        title: 'Login Failed',
        message: error.message || 'Invalid credentials. Please try again.',
      });
      throw error;
    }
  }, [authStore, navigate, location.state, appStore]);

  const register = useCallback(async (userData: RegisterForm) => {
    try {
      await authStore.register(userData);
      navigate('/dashboard', { replace: true });

      appStore.addNotification({
        type: 'success',
        title: 'Account Created',
        message: 'Your account has been created successfully. Welcome!',
      });
    } catch (error: any) {
      appStore.addNotification({
        type: 'error',
        title: 'Registration Failed',
        message: error.message || 'Failed to create account. Please try again.',
      });
      throw error;
    }
  }, [authStore, navigate, appStore]);

  const logout = useCallback(() => {
    authStore.logout();
    navigate('/auth/login', { replace: true });
    
    appStore.addNotification({
      type: 'info',
      title: 'Logged Out',
      message: 'You have been logged out successfully.',
    });
  }, [authStore, navigate, appStore]);

  const checkAuth = useCallback(() => {
    // This could be used to validate token on app startup
    if (!authStore.isAuthenticated || !authStore.token) {
      logout();
      return false;
    }
    return true;
  }, [authStore.isAuthenticated, authStore.token, logout]);

  const updateProfile = useCallback(async (userData: Partial<typeof authStore.user>) => {
    try {
      await authStore.updateProfile(userData);
      appStore.addNotification({
        type: 'success',
        title: 'Profile Updated',
        message: 'Your profile has been updated successfully.',
      });
    } catch (error: any) {
      appStore.addNotification({
        type: 'error',
        title: 'Update Failed',
        message: error.message || 'Failed to update profile.',
      });
      throw error;
    }
  }, [authStore, appStore]);

  const hasRole = useCallback((role: string | string[]) => {
    if (!authStore.user) return false;
    
    if (Array.isArray(role)) {
      return role.includes(authStore.user.role);
    }
    
    return authStore.user.role === role;
  }, [authStore.user]);

  const canAccess = useCallback((resource: string, action: string = 'read') => {
    if (!authStore.user) return false;

    // Basic role-based access control
    switch (authStore.user.role) {
      case 'teacher':
        return true; // Teachers can access everything
      case 'student':
        // Students can only read their own data
        return action === 'read' && !resource.includes('admin');
      default:
        return false;
    }
  }, [authStore.user]);

  return {
    // State
    user: authStore.user,
    isAuthenticated: authStore.isAuthenticated,
    isLoading: authStore.isLoading,
    error: authStore.error,
    
    // Actions
    login,
    register,
    logout,
    updateProfile,
    checkAuth,
    clearError: authStore.clearError,
    
    // Utilities
    hasRole,
    canAccess,
  };
};