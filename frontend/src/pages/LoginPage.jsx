import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../context/AuthContext';
import { sendEmailOTPCode, verifyEmailOTPCode, clearPendingOTP } from '../config/firebase';
import { 
  User, Lock, Phone, Eye, EyeOff, ArrowRight, Shield, 
  CheckCircle, AlertCircle, Loader2, KeyRound, Mail, Key
} from 'lucide-react';
import toast from 'react-hot-toast';

const LoginPage = ({ onSwitchToSignup, onLoginSuccess }) => {
  const { login, verifyLoginOTP } = useAuth();
  
  const [step, setStep] = useState('credentials'); // credentials, otp
  const [formData, setFormData] = useState({
    userId: '',
    password: ''
  });
  const [otp, setOtp] = useState(['', '', '', '', '', '']);
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [loginData, setLoginData] = useState(null);
  const [activeTab, setActiveTab] = useState('userId'); // userId, phone

  // Cleanup on unmount
  useEffect(() => {
    return () => clearPendingOTP();
  }, []);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleOtpChange = (index, value) => {
    if (value.length > 1) return;
    const newOtp = [...otp];
    newOtp[index] = value;
    setOtp(newOtp);
    
    // Auto-focus next input
    if (value && index < 5) {
      document.getElementById(`otp-${index + 1}`)?.focus();
    }
  };

  const handleOtpKeyDown = (index, e) => {
    if (e.key === 'Backspace' && !otp[index] && index > 0) {
      document.getElementById(`otp-${index - 1}`)?.focus();
    }
  };

  const handleCredentialsSubmit = async (e) => {
    e.preventDefault();
    if (!formData.userId || !formData.password) {
      toast.error('Please enter both User ID and Password', { duration: 3000 });
      return;
    }

    setLoading(true);
    try {
      const response = await login(formData.userId, formData.password);
      console.log('Full Login Response:', JSON.stringify(response, null, 2)); // Debug log
      
      if (response.requires_otp) {
        setLoginData(response);
        
        // Check if email is available
        const userEmail = response.email;
        console.log('User Email from response:', userEmail); // Debug
        
        if (!userEmail) {
          toast.error('Email not found for this account. Please contact support.', { duration: 4000 });
          return;
        }
        
        // Send OTP to email
        try {
          const result = await sendEmailOTPCode(userEmail);
          setStep('otp');
          toast.success(`OTP sent to ${response.email_masked || userEmail}. Check your inbox!`, { 
            duration: 5000,
            icon: '\ud83d\udce7'
          });
        } catch (emailError) {
          console.error('EmailJS Error:', emailError);
          toast.error(emailError.message || 'Failed to send OTP. Please try again.', { duration: 4000 });
        }
      }
    } catch (error) {
      toast.error(error || 'Login failed. Please check your credentials.', { duration: 4000 });
    } finally {
      setLoading(false);
    }
  };

  const handleOtpSubmit = async (e) => {
    e.preventDefault();
    const otpString = otp.join('');
    if (otpString.length !== 6) {
      toast.error('Please enter all 6 digits of OTP', { duration: 3000 });
      return;
    }

    setLoading(true);
    try {
      // Verify OTP sent to email (stored in frontend)
      const otpResult = await verifyEmailOTPCode(loginData.email, otpString);
      
      if (otpResult.success) {
        // OTP verified via email - now complete login with backend
        // Pass email_verified flag so backend knows OTP was verified via email
        const response = await verifyLoginOTP(loginData.phone, otpString, loginData.temp_token, true);
        if (response.success) {
          toast.success('Welcome back! Login successful.', { 
            duration: 3000,
            icon: '\u2705'
          });
          onLoginSuccess?.();
        }
      }
    } catch (error) {
      toast.error(error.message || 'Invalid OTP. Please try again.', { duration: 4000 });
      setOtp(['', '', '', '', '', '']);
    } finally {
      setLoading(false);
    }
  };

  const resendOtp = async () => {
    setLoading(true);
    try {
      const result = await sendEmailOTPCode(loginData.email);
      setOtp(['', '', '', '', '', '']);
      
      if (result.otp_hint) {
        // Demo mode
        toast.success(`New OTP: ${result.otp_hint}`, { 
          duration: 15000,
          icon: '\ud83d\udd10'
        });
      } else {
        // Production mode
        toast.success('New OTP sent to your email!', { 
          duration: 5000,
          icon: '\ud83d\udce7'
        });
      }
    } catch (error) {
      toast.error(error.message || 'Failed to resend OTP. Please try again.', { duration: 4000 });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex">
      {/* Left Panel - Branding */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-[#004c8c] via-[#0066b3] to-[#0077cc] text-white p-12 flex-col justify-between relative overflow-hidden">
        {/* Decorative Elements */}
        <div className="absolute top-0 right-0 w-96 h-96 bg-white/5 rounded-full -translate-y-1/2 translate-x-1/2" />
        <div className="absolute bottom-0 left-0 w-72 h-72 bg-white/5 rounded-full translate-y-1/2 -translate-x-1/2" />
        
        {/* Logo */}
        <div className="relative z-10">
          <div className="flex items-center gap-3 mb-8">
            <div className="w-12 h-12 bg-white rounded-lg flex items-center justify-center">
              <span className="text-[#004c8c] font-bold text-xl">QL</span>
            </div>
            <div>
              <h1 className="text-2xl font-bold">QuickLoan</h1>
              <p className="text-white/70 text-sm">Your Trusted NBFC Partner</p>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="relative z-10 space-y-8">
          <div>
            <p className="text-lg text-white/80 mb-2">Fast • Online • Paperless</p>
            <h2 className="text-4xl font-bold leading-tight">
              Easy and Simple way<br />
              to apply for a<br />
              <span className="text-[#ffd700]">Personal Loan</span><br />
              online
            </h2>
          </div>

          {/* Trust Indicators */}
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <CheckCircle className="w-5 h-5 text-green-400" />
              <span>100% Digital Process</span>
            </div>
            <div className="flex items-center gap-3">
              <CheckCircle className="w-5 h-5 text-green-400" />
              <span>AI-Powered Instant Decisions</span>
            </div>
            <div className="flex items-center gap-3">
              <CheckCircle className="w-5 h-5 text-green-400" />
              <span>Competitive Interest Rates</span>
            </div>
            <div className="flex items-center gap-3">
              <CheckCircle className="w-5 h-5 text-green-400" />
              <span>Minimal Documentation</span>
            </div>
          </div>
        </div>

        {/* Illustration */}
        <div className="relative z-10">
          <div className="flex items-end gap-4">
            <div className="w-32 h-40 bg-white/10 rounded-2xl backdrop-blur-sm flex items-center justify-center">
              <Shield className="w-16 h-16 text-white/50" />
            </div>
            <div className="text-sm text-white/60">
              <p>Your data is secured with</p>
              <p className="font-semibold text-white">Bank-grade encryption</p>
            </div>
          </div>
        </div>
      </div>

      {/* Right Panel - Login Form */}
      <div className="flex-1 flex items-center justify-center p-8 bg-gray-50">
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="w-full max-w-md"
        >
          {/* Mobile Logo */}
          <div className="lg:hidden text-center mb-8">
            <div className="inline-flex items-center gap-3">
              <div className="w-10 h-10 bg-[#004c8c] rounded-lg flex items-center justify-center">
                <span className="text-white font-bold">QL</span>
              </div>
              <span className="text-xl font-bold text-gray-800">QuickLoan</span>
            </div>
          </div>

          <div className="bg-white rounded-2xl shadow-xl p-8">
            <AnimatePresence mode="wait">
              {step === 'credentials' ? (
                <motion.div
                  key="credentials"
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 20 }}
                >
                  <h2 className="text-2xl font-bold text-gray-800 text-center mb-2">
                    Choose an option to login
                  </h2>

                  {/* Tab Selection */}
                  <div className="flex border-b border-gray-200 mb-6">
                    <button
                      onClick={() => setActiveTab('userId')}
                      className={`flex-1 py-3 text-sm font-medium transition-colors relative ${
                        activeTab === 'userId' 
                          ? 'text-[#004c8c]' 
                          : 'text-gray-500 hover:text-gray-700'
                      }`}
                    >
                      <div className="flex items-center justify-center gap-2">
                        <User className="w-4 h-4" />
                        User ID
                      </div>
                      {activeTab === 'userId' && (
                        <motion.div 
                          layoutId="activeTab"
                          className="absolute bottom-0 left-0 right-0 h-0.5 bg-[#004c8c]"
                        />
                      )}
                    </button>
                    <button
                      onClick={() => setActiveTab('phone')}
                      className={`flex-1 py-3 text-sm font-medium transition-colors relative ${
                        activeTab === 'phone' 
                          ? 'text-[#004c8c]' 
                          : 'text-gray-500 hover:text-gray-700'
                      }`}
                    >
                      <div className="flex items-center justify-center gap-2">
                        <Phone className="w-4 h-4" />
                        Phone Number
                      </div>
                      {activeTab === 'phone' && (
                        <motion.div 
                          layoutId="activeTab"
                          className="absolute bottom-0 left-0 right-0 h-0.5 bg-[#004c8c]"
                        />
                      )}
                    </button>
                  </div>

                  <form onSubmit={handleCredentialsSubmit} className="space-y-5">
                    {/* User ID / Phone Input */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1.5">
                        {activeTab === 'userId' ? 'User ID' : 'Phone Number'}
                        <span className="text-red-500">*</span>
                      </label>
                      <div className="relative">
                        {activeTab === 'phone' && (
                          <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 text-sm border-r pr-2">
                            +91
                          </span>
                        )}
                        <input
                          type="text"
                          name="userId"
                          value={formData.userId}
                          onChange={handleInputChange}
                          placeholder={activeTab === 'userId' ? 'Enter User ID (e.g., QL123456)' : 'Enter 10-digit number'}
                          className={`w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#004c8c] focus:border-transparent transition-all ${
                            activeTab === 'phone' ? 'pl-14' : ''
                          }`}
                        />
                      </div>
                    </div>

                    {/* Password Input */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1.5">
                        Password<span className="text-red-500">*</span>
                      </label>
                      <div className="relative">
                        <input
                          type={showPassword ? 'text' : 'password'}
                          name="password"
                          value={formData.password}
                          onChange={handleInputChange}
                          placeholder="Enter Password"
                          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#004c8c] focus:border-transparent transition-all pr-12"
                        />
                        <button
                          type="button"
                          onClick={() => setShowPassword(!showPassword)}
                          className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
                        >
                          {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                        </button>
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="flex justify-between text-sm">
                      <button type="button" className="text-[#004c8c] hover:underline">
                        Unlock Account
                      </button>
                      <button type="button" className="text-[#004c8c] hover:underline">
                        Forgot Password
                      </button>
                    </div>

                    {/* Login Button */}
                    <button
                      type="submit"
                      id="login-otp-button"
                      disabled={loading}
                      className="w-full bg-[#004c8c] text-white py-3.5 rounded-lg font-semibold hover:bg-[#003d73] transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                    >
                      {loading ? (
                        <Loader2 className="w-5 h-5 animate-spin" />
                      ) : (
                        <>
                          LOGIN
                          <ArrowRight className="w-5 h-5" />
                        </>
                      )}
                    </button>
                  </form>

                  {/* Sign Up Link */}
                  <div className="mt-6 text-center">
                    <p className="text-gray-600">
                      Kindly{' '}
                      <button 
                        onClick={onSwitchToSignup}
                        className="text-[#c8102e] font-semibold hover:underline"
                      >
                        Sign Up
                      </button>
                      {' '}if you are a new user.
                    </p>
                  </div>

                  {/* Security Notice */}
                  <div className="mt-6 p-4 bg-amber-50 rounded-lg border border-amber-200">
                    <div className="flex items-start gap-3">
                      <AlertCircle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
                      <div className="text-sm text-amber-800">
                        <p className="font-medium">Security Notice</p>
                        <p className="mt-1">We never ask for OTP, Password or PIN over calls. Never share these details with anyone.</p>
                      </div>
                    </div>
                  </div>
                </motion.div>
              ) : (
                <motion.div
                  key="otp"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                >
                  <div className="text-center mb-8">
                    <div className="w-16 h-16 bg-[#004c8c]/10 rounded-full flex items-center justify-center mx-auto mb-4">
                      <KeyRound className="w-8 h-8 text-[#004c8c]" />
                    </div>
                    <h2 className="text-2xl font-bold text-gray-800 mb-2">
                      Enter OTP
                    </h2>
                    <p className="text-gray-600">
                      We've sent a 6-digit OTP to your email<br />
                      <span className="font-semibold text-gray-800">{loginData?.email_masked || loginData?.email}</span>
                    </p>
                  </div>

                  <form onSubmit={handleOtpSubmit} className="space-y-6">
                    {/* OTP Input */}
                    <div className="flex justify-center gap-3">
                      {otp.map((digit, index) => (
                        <input
                          key={index}
                          id={`otp-${index}`}
                          type="text"
                          inputMode="numeric"
                          maxLength={1}
                          value={digit}
                          onChange={(e) => handleOtpChange(index, e.target.value.replace(/\D/g, ''))}
                          onKeyDown={(e) => handleOtpKeyDown(index, e)}
                          className="w-12 h-14 text-center text-2xl font-bold border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-[#004c8c] focus:border-transparent transition-all"
                        />
                      ))}
                    </div>

                    {/* Timer & Resend */}
                    <div className="text-center">
                      <button
                        type="button"
                        onClick={resendOtp}
                        disabled={loading}
                        className="text-[#004c8c] hover:underline text-sm font-medium"
                      >
                        Resend OTP
                      </button>
                    </div>

                    {/* Verify Button */}
                    <button
                      type="submit"
                      disabled={loading || otp.join('').length !== 6}
                      className="w-full bg-[#004c8c] text-white py-3.5 rounded-lg font-semibold hover:bg-[#003d73] transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                    >
                      {loading ? (
                        <Loader2 className="w-5 h-5 animate-spin" />
                      ) : (
                        <>
                          VERIFY & LOGIN
                          <ArrowRight className="w-5 h-5" />
                        </>
                      )}
                    </button>

                    {/* Back Button */}
                    <button
                      type="button"
                      onClick={() => {
                        setStep('credentials');
                        setOtp(['', '', '', '', '', '']);
                      }}
                      className="w-full text-gray-600 py-2 text-sm hover:text-gray-800"
                    >
                      ← Back to Login
                    </button>
                  </form>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default LoginPage;
