// frontend/stores/auth.ts
import { defineStore } from 'pinia';
import axios from 'axios';
import type { User } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';


export interface AuthState {
  accessToken: string | null;
  refreshToken: string | null;
  user: User | null;
  isAuthenticated: boolean;
  loading: boolean;
  error: string | null;
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    accessToken: localStorage.getItem('accessToken') || null,
    refreshToken: localStorage.getItem('refreshToken') || null,
    user: null,
    isAuthenticated: !!localStorage.getItem('accessToken'),
    loading: false,
    error: null,
  }),

  getters: {
    userAvatar(): string | null | undefined {
      return this.user?.avatar_url;
    }
  },

  actions: {
    setTokens(access: string, refresh: string) {
      this.accessToken = access;
      this.refreshToken = refresh;
      localStorage.setItem('accessToken', access);
      localStorage.setItem('refreshToken', refresh);
      axios.defaults.headers.common['Authorization'] = `Bearer ${access}`;
      this.isAuthenticated = true;
    },

    clearAuthData() {
      this.accessToken = null;
      this.refreshToken = null;
      this.user = null;
      this.isAuthenticated = false;
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
      delete axios.defaults.headers.common['Authorization'];
    },

    async login(credentials: { email: string; password: any }): Promise<{ success: boolean; errors?: Record<string, any> }> {
      this.loading = true;
      this.error = null; // Общая ошибка
      let apiErrors: Record<string, any> | undefined = undefined;

      try {
        const response = await axios.post(`${API_BASE_URL}/auth/jwt/create/`, credentials);
        const { access, refresh } = response.data;
        this.setTokens(access, refresh);
        await this.fetchUser();
        return { success: true };
      } catch (err: any) {
        this.clearAuthData();
        if (axios.isAxiosError(err) && err.response) {
          apiErrors = err.response.data;
          if (typeof apiErrors === 'object' && apiErrors !== null) {
              const firstErrorKey = Object.keys(apiErrors)[0];
              if (Array.isArray(apiErrors[firstErrorKey])) {
                  this.error = `${firstErrorKey}: ${apiErrors[firstErrorKey][0]}`;
              } else {
                  this.error = String(apiErrors[firstErrorKey] || apiErrors.detail || 'Ошибка входа.');
              }
          } else if (typeof apiErrors === 'string') {
              this.error = apiErrors;
          } else {
               this.error = 'Ошибка входа. Проверьте email и пароль.';
          }
        } else {
          this.error = 'Произошла сетевая ошибка.';
        }
        console.error('Login error:', err);
        return { success: false, errors: apiErrors };
      } finally {
        this.loading = false;
      }
    },
    async socialLogin(payload: { provider: string; code: string; state: string }): Promise<{ success: boolean; }> {
      this.loading = true;
      this.error = null;
      try {
        const response = await axios.post(`${API_BASE_URL}/auth/o/${payload.provider}/`, {
          code: payload.code,
          state: payload.state,
        });
        
        const { access, refresh } = response.data;
        this.setTokens(access, refresh);
        await this.fetchUser();
        return { success: true };
        
      } catch (err: any) {
        this.clearAuthData();
        if (axios.isAxiosError(err) && err.response) {
            this.error = err.response.data?.detail || err.response.data?.non_field_errors?.join(', ') || 'Ошибка социального входа.';
        } else {
            this.error = 'Произошла сетевая ошибка при социальном входе.';
        }
        console.error('Social login error:', err);
        return { success: false };
      } finally {
        this.loading = false;
      }
    },

    async register(userData: any): Promise<{ success: boolean; errors?: Record<string, any> }> {
      this.loading = true;
      this.error = null;
      let apiErrors: Record<string, any> | undefined = undefined;

      try {
        await axios.post(`${API_BASE_URL}/auth/users/`, userData);
        const loginResult = await this.login({ email: userData.email, password: userData.password });
        if (!loginResult.success) {
          return { success: false, errors: loginResult.errors };
        }
        return { success: true };
      } catch (err: any) {
        if (axios.isAxiosError(err) && err.response) {
          apiErrors = err.response.data;
          if (typeof apiErrors === 'object' && apiErrors !== null) {
              const firstErrorKey = Object.keys(apiErrors)[0];
               if (Array.isArray(apiErrors[firstErrorKey])) {
                  this.error = `${firstErrorKey}: ${apiErrors[firstErrorKey][0]}`;
              } else {
                  this.error = String(apiErrors[firstErrorKey] || apiErrors.detail || 'Ошибка регистрации.');
              }
          } else if (typeof apiErrors === 'string') {
              this.error = apiErrors;
          } else {
              this.error = 'Ошибка регистрации. Пожалуйста, проверьте введенные данные.';
          }
        } else {
          this.error = 'Произошла сетевая ошибка при регистрации.';
        }
        console.error('Registration error (during user creation POST):', err);
        return { success: false, errors: apiErrors };
      } finally {
        this.loading = false;
      }
    },

    async fetchUser() {

      if (!this.accessToken) {
        if (this.isAuthenticated) this.clearAuthData();
        return;
      }
      this.loading = true;
      try {
        const response = await axios.get<User>(`${API_BASE_URL}/auth/users/me/`, {
          headers: { Authorization: `Bearer ${this.accessToken}` }
        });
        this.user = response.data;
        this.isAuthenticated = true;
      } catch (err: any) {
        console.error('Fetch user error:', err);
        if (axios.isAxiosError(err) && err.response && (err.response.status === 401 || err.response.status === 403)) {
          await this.tryRefreshTokenAndFetchUser();
        } else {
            this.clearAuthData();
        }
      } finally {
        this.loading = false;
      }
    },

    async tryRefreshTokenAndFetchUser() {

      if (!this.refreshToken) {
        this.clearAuthData();
        return;
      }
      console.log("Attempting to refresh token...");
      try {
        const response = await axios.post(`${API_BASE_URL}/auth/jwt/refresh/`, {
          refresh: this.refreshToken,
        });
        const { access } = response.data;
        const newRefresh = response.data.refresh || this.refreshToken;
        this.setTokens(access, newRefresh);
        await this.fetchUser();
      } catch (refreshErr: any) {
        console.error('Refresh token error:', refreshErr);
        this.clearAuthData();
      }
    },

    logout() {
      this.clearAuthData();
    },

    async initAuth() {
        if (this.accessToken) {
            axios.defaults.headers.common['Authorization'] = `Bearer ${this.accessToken}`;
            await this.fetchUser();
        }
    },
  },
});
