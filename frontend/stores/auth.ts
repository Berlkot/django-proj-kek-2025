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

    async login(credentials: { email: string; password: any }) {
      this.loading = true;
      this.error = null;
      try {
        const response = await axios.post(`${API_BASE_URL}/auth/jwt/create/`, credentials);
        const { access, refresh } = response.data;
        this.setTokens(access, refresh);
        await this.fetchUser();
        return true;
      } catch (err: any) {
        this.clearAuthData();
        let errorMessagesArray: string[] = [];
        if (axios.isAxiosError(err) && err.response) {
            const errors = err.response.data;
            if (typeof errors === 'object' && errors !== null) {
                Object.values(errors).forEach(messagesForField => {
                    if (Array.isArray(messagesForField)) {
                        errorMessagesArray.push(...messagesForField.map(msg => String(msg)));
                    } else {
                        errorMessagesArray.push(String(messagesForField));
                    }
                });
            } else if (typeof errors === 'string') {
                errorMessagesArray.push(errors);
            }
        }
        if (errorMessagesArray.length > 0) {
            this.error = errorMessagesArray.join('; ');
        } else {
            this.error = 'Ошибка входа. Проверьте email и пароль или попробуйте позже.';
        }
        console.error('Login error:', err);
        return false;
      } finally {
        this.loading = false;
      }
    },

    async register(userData: any) {
      this.loading = true;
      this.error = null;
      try {
        await axios.post(`${API_BASE_URL}/auth/users/`, userData);
        // После успешной регистрации автоматически логиним пользователя
        // Djoser не возвращает токены при регистрации, поэтому вызываем login
        console.log(`Registration successful for ${userData.email}. Attempting to login...`);
        // Важно: передаем email и password из исходных данных регистрации
        const loginSuccess = await this.login({ email: userData.email, password: userData.password });
        if (!loginSuccess) {
            // Если логин после регистрации не удался, возможно, стоит установить специфическую ошибку
            // this.error все еще будет содержать ошибку от вызова this.login()
            console.warn(`Auto-login after registration failed for ${userData.email}. User might need to login manually.`);
            // Не возвращаем false, так как регистрация прошла, но авто-логин нет.
            // Фронтенд сам решит, что делать (например, показать сообщение о необходимости ручного входа)
            // Однако, если мы хотим, чтобы RegisterPage.vue считал это неудачей регистрации, то return false
            // Но тогда registrationSuccess не установится в true.
            // Давайте считать, что если авто-логин не удался, то это ошибка для процесса регистрации в целом.
            return false; // Указываем, что общий процесс (регистрация + автологин) не завершился идеально
        }
        return true; // Успешная регистрация И авто-логин
      } catch (err: any) {
         let errorMessagesArray: string[] = [];
        if (axios.isAxiosError(err) && err.response) {
            const errors = err.response.data;
            if (typeof errors === 'object' && errors !== null) {
                Object.values(errors).forEach(messagesForField => {
                    if (Array.isArray(messagesForField)) {
                        errorMessagesArray.push(...messagesForField.map(msg => String(msg)));
                    } else {
                        errorMessagesArray.push(String(messagesForField));
                    }
                });
            } else if (typeof errors === 'string') {
                errorMessagesArray.push(errors);
            }
        }
        if (errorMessagesArray.length > 0) {
            this.error = errorMessagesArray.join('; ');
        } else {
            this.error = 'Ошибка регистрации. Пожалуйста, проверьте введенные данные.';
        }
        console.error('Registration error (during user creation POST):', err);
        return false;
      } finally {
        this.loading = false;
      }
    },

    async fetchUser() {
      // ... (код без изменений) ...
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
      // ... (код без изменений) ...
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
    }
  },
});