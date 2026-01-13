// Firebase Configuration for Email OTP Authentication
// Uses EmailJS to send real OTP emails

import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';
import emailjs from '@emailjs/browser';

// Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyCCn8gu-8xEYMQhX14kcvnKU-FeJa3TDqE",
  authDomain: "loan-assistant-quickbot.firebaseapp.com",
  projectId: "loan-assistant-quickbot",
  storageBucket: "loan-assistant-quickbot.firebasestorage.app",
  messagingSenderId: "393867807498",
  appId: "1:393867807498:web:8ae04cf461bc29d6d2e16f",
  measurementId: "G-06TV36WN7G"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

// EmailJS Configuration - Get these from https://www.emailjs.com/
// 1. Create free account at emailjs.com
// 2. Add email service (Gmail, Outlook, etc.)
// 3. Create email template with variables: {{to_email}}, {{otp_code}}, {{app_name}}
const EMAILJS_SERVICE_ID = import.meta.env.VITE_EMAILJS_SERVICE_ID || 'service_quickloan';
const EMAILJS_TEMPLATE_ID = import.meta.env.VITE_EMAILJS_TEMPLATE_ID || 'template_otp';
const EMAILJS_WELCOME_TEMPLATE_ID = import.meta.env.VITE_EMAILJS_WELCOME_TEMPLATE_ID || 'template_welcome';
const EMAILJS_PUBLIC_KEY = import.meta.env.VITE_EMAILJS_PUBLIC_KEY || '';

// Initialize EmailJS
if (EMAILJS_PUBLIC_KEY) {
  emailjs.init(EMAILJS_PUBLIC_KEY);
}

// In-memory OTP storage
let pendingOTP = {};

/**
 * Send OTP to email using EmailJS
 * @param {string} email - Email address to send OTP to
 * @returns {Promise<{success: boolean, message: string}>}
 */
export const sendEmailOTPCode = async (email) => {
  try {
    // Generate 6-digit OTP
    const otp = Math.floor(100000 + Math.random() * 900000).toString();
    
    // Store OTP with expiry (5 minutes)
    pendingOTP[email] = {
      otp: otp,
      expiry: Date.now() + 5 * 60 * 1000
    };
    
    console.log(`🔐 OTP for ${email}: ${otp}`);
    
    // Send email via EmailJS
    if (!EMAILJS_PUBLIC_KEY) {
      throw new Error('Email service not configured. Please contact support.');
    }
    
    // Use 'email' to match EmailJS template variable {{email}}
    await emailjs.send(EMAILJS_SERVICE_ID, EMAILJS_TEMPLATE_ID, {
      email: email,           // For "To Email" field in template
      to_email: email,        // Alternative variable name
      otp_code: otp,
      app_name: 'QuickLoan',
      expiry_time: '5 minutes'
    });
    
    console.log(`✅ OTP ${otp} sent to email: ${email}`);
    
    return {
      success: true,
      otp_hint: null,
      message: `OTP sent to ${email}. Check your inbox!`
    };
  } catch (error) {
    console.error('Error sending OTP email:', error);
    throw new Error(error.message || 'Failed to send OTP. Please try again.');
  }
};

/**
 * Verify the OTP entered by user
 * @param {string} email - Email address the OTP was sent to
 * @param {string} enteredOTP - OTP entered by user
 * @returns {Promise<{success: boolean, verified: boolean}>}
 */
export const verifyEmailOTPCode = async (email, enteredOTP) => {
  try {
    const stored = pendingOTP[email];
    
    if (!stored) {
      throw new Error('No OTP found. Please request a new one.');
    }
    
    if (Date.now() > stored.expiry) {
      delete pendingOTP[email];
      throw new Error('OTP expired. Please request a new one.');
    }
    
    if (stored.otp !== enteredOTP) {
      throw new Error('Invalid OTP. Please try again.');
    }
    
    // OTP verified successfully
    delete pendingOTP[email];
    console.log('✅ OTP verified successfully');
    
    return { success: true, verified: true };
  } catch (error) {
    console.error('OTP Verification Error:', error);
    throw error;
  }
};

/**
 * Clear pending OTP for an email
 * @param {string} email - Email address to clear OTP for
 */
export const clearPendingOTP = (email) => {
  if (email && pendingOTP[email]) {
    delete pendingOTP[email];
  }
};

/**
 * Send Welcome/Onboarding email after successful signup
 * @param {object} params - Email parameters
 * @param {string} params.email - User's email address
 * @param {string} params.userName - User's name
 * @param {string} params.userId - Generated User ID
 * @param {string} params.password - User's password (for their reference)
 * @param {string} params.phone - User's phone number
 * @returns {Promise<{success: boolean, message: string}>}
 */
export const sendWelcomeEmail = async ({ email, userName, userId, password, phone }) => {
  try {
    if (!EMAILJS_PUBLIC_KEY) {
      console.warn('EmailJS not configured, skipping welcome email');
      return { success: false, message: 'Email service not configured' };
    }

    const loginUrl = window.location.origin + '/login';
    
    await emailjs.send(EMAILJS_SERVICE_ID, EMAILJS_WELCOME_TEMPLATE_ID, {
      to_email: email,
      user_name: userName || 'Valued Customer',
      user_id: userId,
      password: password,
      phone_number: phone,
      login_url: loginUrl,
      app_name: 'QuickLoan'
    });
    
    console.log('✅ Welcome email sent successfully to:', email);
    return { success: true, message: 'Welcome email sent!' };
  } catch (error) {
    console.error('Failed to send welcome email:', error);
    return { success: false, message: 'Failed to send welcome email' };
  }
};

export { auth };
export default app;