import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from 'react';
import type { User } from '../types';
import { getMe, login as apiLogin } from '../api/auth';

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  loading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(() =>
    localStorage.getItem('token'),
  );
  const [loading, setLoading] = useState(true);

  const refreshUser = useCallback(async () => {
    if (!token) {
      setUser(null);
      setLoading(false);
      return;
    }
    try {
      const me = await getMe();
      setUser(me);
    } catch {
      localStorage.removeItem('token');
      setToken(null);
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    refreshUser();
  }, [refreshUser]);

  const login = useCallback(async (username: string, password: string) => {
    const res = await apiLogin(username, password);
    localStorage.setItem('token', res.access_token);
    setToken(res.access_token);
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!user,
        loading,
        login,
        logout,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be inside AuthProvider');
  return ctx;
}
