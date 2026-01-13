import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';
import { sendEmailOTPCode, verifyEmailOTPCode, clearPendingOTP } from '../config/firebase';

const AuthContext = createContext(null);

const API_BASE = 'http://127.0.0.1:8000';

// Use sessionStorage for auto-logout on browser/tab close
// Token will be cleared when the browser session ends
const TOKEN_KEY = 'quickloan_token';

const getToken = () => sessionStorage.getItem(TOKEN_KEY);
const setToken = (token) => sessionStorage.setItem(TOKEN_KEY, token);
const removeToken = () => sessionStorage.removeItem(TOKEN_KEY);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Check for existing session on mount
  useEffect(() => {
    const token = getToken();
    if (token) {
      validateToken(token);
    } else {
      setLoading(false);
    }
  }, []);

  const validateToken = async (token) => {
    try {
      const response = await axios.get(`${API_BASE}/api/auth/me`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (response.data.success) {
        setUser(response.data.user);
        setIsAuthenticated(true);
      } else {
        removeToken();
      }
    } catch (error) {
      console.error('Token validation failed:', error);
      removeToken();
    } finally {
      setLoading(false);
    }
  };

  const login = async (userId, password) => {
    try {
      const response = await axios.post(`${API_BASE}/api/auth/login`, {
        user_id: userId,
        password: password
      });
      return response.data;
    } catch (error) {
      throw error.response?.data?.detail || 'Login failed';
    }
  };

  const verifyLoginOTP = async (phone, otp, sessionToken, emailVerified = false) => {
    try {
      const response = await axios.post(`${API_BASE}/api/auth/verify-login`, {
        phone: phone,
        otp: otp,
        session_token: sessionToken,
        email_verified: emailVerified  // Skip backend OTP check if verified via email
      });
      
      if (response.data.success) {
        setToken(response.data.token);
        setUser(response.data.user);
        setIsAuthenticated(true);
      }
      return response.data;
    } catch (error) {
      throw error.response?.data?.detail || 'OTP verification failed';
    }
  };

  const signup = async (formData) => {
    try {
      const response = await axios.post(`${API_BASE}/api/auth/signup`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      return response.data;
    } catch (error) {
      throw error.response?.data?.detail || 'Signup failed';
    }
  };

  const sendOTP = async (email, purpose = 'signup') => {
    try {
      // Use Email OTP (no billing required)
      const result = await sendEmailOTPCode(email);
      return { success: true, message: result.message, otp_hint: result.otp_hint };
    } catch (error) {
      throw error.message || 'Failed to send OTP';
    }
  };

  const verifyOTP = async (email, otp, purpose = 'signup') => {
    try {
      // Verify Email OTP
      const result = await verifyEmailOTPCode(email, otp);
      
      if (result.success) {
        return { success: true, verified: true };
      }
      throw new Error('Verification failed');
    } catch (error) {
      throw error.message || 'OTP verification failed';
    }
  };

  const logout = async () => {
    try {
      const token = getToken();
      if (token) {
        await axios.post(`${API_BASE}/api/auth/logout`, {}, {
          headers: { Authorization: `Bearer ${token}` }
        });
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      removeToken();
      setUser(null);
      setIsAuthenticated(false);
    }
  };

  const getAuthHeader = () => {
    const token = getToken();
    return token ? { Authorization: `Bearer ${token}` } : {};
  };

  const value = {
    user,
    loading,
    isAuthenticated,
    login,
    verifyLoginOTP,
    signup,
    sendOTP,
    verifyOTP,
    logout,
    getAuthHeader
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default AuthContext;
