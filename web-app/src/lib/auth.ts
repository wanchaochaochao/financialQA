/**
 * Authentication utilities
 */

const TOKEN_KEY = 'auth_token';
const USER_KEY = 'auth_user';

export interface User {
  id: number;
  nickname: string;
  phone?: string;
  email?: string;
  vip_level: number;
  status: boolean;
  vip_active?: boolean;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: User;
}

/**
 * Save authentication token and user info to localStorage
 */
export function saveAuth(tokenResponse: TokenResponse): void {
  if (typeof window !== 'undefined') {
    localStorage.setItem(TOKEN_KEY, tokenResponse.access_token);
    localStorage.setItem(USER_KEY, JSON.stringify(tokenResponse.user));
  }
}

/**
 * Get authentication token from localStorage
 */
export function getToken(): string | null {
  if (typeof window !== 'undefined') {
    return localStorage.getItem(TOKEN_KEY);
  }
  return null;
}

/**
 * Get user info from localStorage
 */
export function getUser(): User | null {
  if (typeof window !== 'undefined') {
    const userStr = localStorage.getItem(USER_KEY);
    if (userStr) {
      try {
        return JSON.parse(userStr);
      } catch {
        return null;
      }
    }
  }
  return null;
}

/**
 * Check if user is authenticated
 */
export function isAuthenticated(): boolean {
  return getToken() !== null;
}

/**
 * Clear authentication data (logout)
 */
export function clearAuth(): void {
  if (typeof window !== 'undefined') {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  }
}

/**
 * Get authorization header for API requests
 */
export function getAuthHeader(): Record<string, string> {
  const token = getToken();
  if (token) {
    return {
      'Authorization': `Bearer ${token}`
    };
  }
  return {};
}
