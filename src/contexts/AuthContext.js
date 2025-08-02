import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';
import { toast } from 'react-toastify';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState(localStorage.getItem('token'));

  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      fetchCurrentUser();
    } else {
      setLoading(false);
    }
  }, [token]);

  const fetchCurrentUser = async () => {
    try {
      const response = await axios.get('/auth/me');
      setUser(response.data);
    } catch (error) {
      console.error('Failed to fetch user:', error);
      logout();
    } finally {
      setLoading(false);
    }
  };

  const login = async () => {
    try {
      const response = await axios.get('/auth/google');
      window.location.href = response.data.auth_url;
    } catch (error) {
      toast.error('Failed to initiate Google login');
      console.error('Login error:', error);
    }
  };

  const handleCallback = async (code) => {
    try {
      const response = await axios.get(`/auth/callback?code=${code}`);
      const { access_token, user: userData } = response.data;
      
      localStorage.setItem('token', access_token);
      setToken(access_token);
      setUser(userData);
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      toast.success(`Welcome, ${userData.name}!`);
      
      // Clean up URL
      window.history.replaceState({}, document.title, '/');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Authentication failed');
      console.error('Callback error:', error);
    }
  };

  const logout = async () => {
    try {
      await axios.post('/auth/logout');
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      localStorage.removeItem('token');
      setToken(null);
      setUser(null);
      delete axios.defaults.headers.common['Authorization'];
      toast.info('Logged out successfully');
    }
  };

  const updatePreferences = async (preferences) => {
    try {
      await axios.put('/user/preferences', preferences);
      setUser(prevUser => ({
        ...prevUser,
        preferences: { ...prevUser.preferences, ...preferences }
      }));
      toast.success('Preferences updated successfully');
    } catch (error) {
      toast.error('Failed to update preferences');
      console.error('Preferences update error:', error);
    }
  };

  // Handle OAuth callback on page load
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('code');
    
    if (code && !token) {
      handleCallback(code);
    }
  }, []);

  const value = {
    user,
    loading,
    login,
    logout,
    updatePreferences,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}
