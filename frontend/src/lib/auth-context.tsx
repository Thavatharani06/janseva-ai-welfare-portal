"use client";

import React, { createContext, useContext, useState, useEffect } from 'react';
import { authApi } from '@/lib/api';

interface User {
  id: string;
  email: string;
  full_name: string;
  role: string;
  language_preference: string;
  district?: string;
  annual_income?: number;
  age?: number;
  gender?: string;
  occupation?: string;
  disability_status?: boolean;
  community?: string;
  marital_status?: string;
  education_level?: string;
  family_members_count?: number;
  property_owner?: boolean;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  loading: boolean;
  login: (data: any) => Promise<void>;
  register: (data: any) => Promise<void>;
  logout: () => void;
  updateProfile: (data: any) => Promise<void>;
  setLanguage: (lang: string) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const savedToken = localStorage.getItem('janseva_token');
    if (savedToken) {
      setToken(savedToken);
      authApi.getMe()
        .then((userData) => setUser(userData))
        .catch(() => {
          localStorage.removeItem('janseva_token');
          setToken(null);
          setUser(null);
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (credentials: any) => {
    const data = await authApi.login(credentials);
    localStorage.setItem('janseva_token', data.access_token);
    setToken(data.access_token);
    setUser(data.user);
  };

  const register = async (userData: any) => {
    const data = await authApi.register(userData);
    localStorage.setItem('janseva_token', data.access_token);
    setToken(data.access_token);
    setUser(data.user);
  };

  const logout = () => {
    localStorage.removeItem('janseva_token');
    setToken(null);
    setUser(null);
  };

  const updateProfile = async (profileData: any) => {
    const updated = await authApi.updateProfile(profileData);
    setUser(updated);
  };

  const setLanguage = async (lang: string) => {
    if (user) {
      await updateProfile({ language_preference: lang });
    }
  };

  return (
    <AuthContext.Provider value={{ user, token, loading, login, register, logout, updateProfile, setLanguage }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
