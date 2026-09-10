import React, { createContext, useContext, useState, useEffect } from 'react';
import { User, UserType } from '../types';
import { api } from '../services/api';

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (credentials: { email: string; password: string }) => Promise<void>;
  register: (userData: any) => Promise<void>;
  logout: () => void;
  setUserType: (type: UserType) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('weathergpt_token'));
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    const initAuth = async () => {
      const storedToken = localStorage.getItem('weathergpt_token');
      if (storedToken) {
        try {
          const profile = await api.getMe(storedToken);
          setUser(profile);
        } catch (e) {
          console.error('Session expired or invalid token', e);
          localStorage.removeItem('weathergpt_token');
          setToken(null);
          setUser(null);
        }
      }
      setIsLoading(false);
    };
    initAuth();
  }, []);

  const login = async (credentials: { email: string; password: string }) => {
    const data = await api.login(credentials);
    setToken(data.access_token);
    setUser(data.user);
    localStorage.setItem('weathergpt_token', data.access_token);
  };

  const register = async (userData: any) => {
    const data = await api.register(userData);
    setToken(data.access_token);
    setUser(data.user);
    localStorage.setItem('weathergpt_token', data.access_token);
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('weathergpt_token');
  };

  const setUserType = async (type: UserType) => {
    if (token) {
      try {
        const updated = await api.updateUserType(type, token);
        setUser(updated);
      } catch (e) {
        console.error('Failed to update user type in backend', e);
      }
    } else if (user) {
      setUser({ ...user, user_type: type });
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!token && !!user,
        isLoading,
        login,
        register,
        logout,
        setUserType,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within an AuthProvider');
  return context;
};
