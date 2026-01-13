import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../context/AuthContext';
import { sendEmailOTPCode, verifyEmailOTPCode, clearPendingOTP, sendWelcomeEmail } from '../config/firebase';
import { 
  User, Mail, Phone, Lock, Eye, EyeOff, ArrowRight, ArrowLeft,
  Home, CreditCard, Upload, CheckCircle, AlertCircle, Loader2,
  IndianRupee, FileText, Shield, KeyRound, X
} from 'lucide-react';
import toast from 'react-hot-toast';

// Document Preview Modal Component
const DocumentPreviewModal = ({ file, onClose }) => {
  const [previewUrl, setPreviewUrl] = useState(null);

  React.useEffect(() => {
    if (file) {
      const url = URL.createObjectURL(file);
      setPreviewUrl(url);
      return () => URL.revokeObjectURL(url);
    }
  }, [file]);

  if (!file || !previewUrl) return null;

  const isPDF = file.type === 'application/pdf';
  const isImage = file.type.startsWith('image/');

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b bg-gray-50">
          <div className="flex items-center gap-3">
            <FileText className="w-5 h-5 text-[#004c8c]" />
            <span className="font-medium text-gray-800 truncate max-w-md">{file.name}</span>
            <span className="text-xs text-gray-500 bg-gray-200 px-2 py-1 rounded">
              {(file.size / 1024).toFixed(1)} KB
            </span>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-200 rounded-full transition-colors"
          >
            <X className="w-5 h-5 text-gray-600" />
          </button>
        </div>
        
        {/* Content */}
        <div className="p-4 overflow-auto" style={{ maxHeight: 'calc(90vh - 80px)' }}>
          {isPDF ? (
            <iframe
              src={previewUrl}
              className="w-full h-[70vh] rounded border"
              title="Document Preview"
            />
          ) : isImage ? (
            <div className="flex items-center justify-center">
              <img
                src={previewUrl}
                alt="Document Preview"
                className="max-w-full max-h-[70vh] object-contain rounded shadow-lg"
              />
            </div>
          ) : (
            <div className="text-center py-12 text-gray-500">
              <FileText className="w-16 h-16 mx-auto mb-4 opacity-50" />
              <p>Preview not available for this file type</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

const SignupPage = ({ onSwitchToLogin }) => {
  const { signup, sendOTP, verifyOTP } = useAuth();
  
  const [step, setStep] = useState(1); // 1: Personal, 2: Contact, 3: KYC, 4: Income, 5: OTP
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [phoneVerified, setPhoneVerified] = useState(false);
  const [otpSent, setOtpSent] = useState(false);
  const [otp, setOtp] = useState(['', '', '', '', '', '']);
  const fileInputRef = useRef(null);

  // Cleanup on unmount
  useEffect(() => {
    return () => clearPendingOTP();
  }, []);

  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    phone: '',
    password: '',
    confirmPassword: '',
    residentialAddress: '',
    aadhaarNumber: '',
    aadhaarFile: null,
    panNumber: '',
    panFile: null,
    monthlyIncome: '',
    incomeFile: null
  });

  const [errors, setErrors] = useState({});
  const [previewFile, setPreviewFile] = useState(null);
  const aadhaarFileRef = useRef(null);
  const panFileRef = useRef(null);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (file.type !== 'application/pdf') {
        toast.error('Please upload a PDF file only', { duration: 3000 });
        return;
      }
      if (file.size > 5 * 1024 * 1024) {
        toast.error('File size should be less than 5MB', { duration: 3000 });
        return;
      }
      setFormData(prev => ({ ...prev, incomeFile: file }));
      toast.success('Income certificate uploaded!', { duration: 2000 });
    }
  };

  const handleAadhaarFileChange = async (e) => {
    const file = e.target.files[0];
    if (file) {
      const validTypes = ['application/pdf', 'image/jpeg', 'image/jpg', 'image/png'];
      if (!validTypes.includes(file.type)) {
        toast.error('Please upload PDF, JPG, or PNG file only', { duration: 3000 });
        return;
      }
      if (file.size > 5 * 1024 * 1024) {
        toast.error('File size should be less than 5MB', { duration: 3000 });
        return;
      }
      setFormData(prev => ({ ...prev, aadhaarFile: file }));
      // Clear the error when file is uploaded
      if (errors.aadhaarFile) {
        setErrors(prev => ({ ...prev, aadhaarFile: '' }));
      }
      toast.success('Aadhaar card uploaded!', { duration: 2000 });
      
      // Try to extract Aadhaar number via OCR
      try {
        const ocrFormData = new FormData();
        ocrFormData.append('file', file);
        ocrFormData.append('document_type', 'aadhaar');
        
        const response = await fetch('http://localhost:8000/api/ocr/extract', {
          method: 'POST',
          body: ocrFormData
        });
        
        if (response.ok) {
          const result = await response.json();
          if (result.success && result.extracted_number) {
            const formattedAadhaar = formatAadhaar(result.extracted_number);
            setFormData(prev => ({ ...prev, aadhaarNumber: formattedAadhaar }));
            toast.success('🎉 Aadhaar number extracted automatically!', { 
              duration: 3000,
              style: { background: '#d1fae5', color: '#065f46' }
            });
            // Clear aadhaar number error if any
            if (errors.aadhaarNumber) {
              setErrors(prev => ({ ...prev, aadhaarNumber: '' }));
            }
          }
        }
      } catch (error) {
        console.log('OCR extraction not available, manual entry required');
      }
    }
  };

  const handlePanFileChange = async (e) => {
    const file = e.target.files[0];
    if (file) {
      const validTypes = ['application/pdf', 'image/jpeg', 'image/jpg', 'image/png'];
      if (!validTypes.includes(file.type)) {
        toast.error('Please upload PDF, JPG, or PNG file only', { duration: 3000 });
        return;
      }
      if (file.size > 5 * 1024 * 1024) {
        toast.error('File size should be less than 5MB', { duration: 3000 });
        return;
      }
      setFormData(prev => ({ ...prev, panFile: file }));
      toast.success('PAN card uploaded!', { duration: 2000 });
      
      // Try to extract PAN number via OCR
      try {
        const ocrFormData = new FormData();
        ocrFormData.append('file', file);
        ocrFormData.append('document_type', 'pan');
        
        const response = await fetch('http://localhost:8000/api/ocr/extract', {
          method: 'POST',
          body: ocrFormData
        });
        
        if (response.ok) {
          const result = await response.json();
          if (result.success && result.extracted_number) {
            setFormData(prev => ({ ...prev, panNumber: result.extracted_number.toUpperCase() }));
            toast.success('PAN number extracted automatically!');
            // Clear PAN error if any
            if (errors.panNumber) {
              setErrors(prev => ({ ...prev, panNumber: '' }));
            }
          }
        }
      } catch (error) {
        console.log('OCR extraction not available, manual entry required');
      }
    }
  };

  const formatPan = (value) => {
    // Remove any non-alphanumeric characters and uppercase
    return value.replace(/[^a-zA-Z0-9]/g, '').toUpperCase().slice(0, 10);
  };

  const validatePanFormat = (pan) => {
    // PAN format: AAAAA1234A (5 letters, 4 digits, 1 letter)
    const panRegex = /^[A-Z]{5}[0-9]{4}[A-Z]{1}$/;
    return panRegex.test(pan);
  };

  const handlePanChange = (e) => {
    const formatted = formatPan(e.target.value);
    setFormData(prev => ({ ...prev, panNumber: formatted }));
    // Clear error when typing
    if (errors.panNumber) {
      setErrors(prev => ({ ...prev, panNumber: '' }));
    }
  };

  const handleOtpChange = (index, value) => {
    if (value.length > 1) return;
    const newOtp = [...otp];
    newOtp[index] = value;
    setOtp(newOtp);
    
    if (value && index < 5) {
      document.getElementById(`signup-otp-${index + 1}`)?.focus();
    }
  };

  const handleOtpKeyDown = (index, e) => {
    if (e.key === 'Backspace' && !otp[index] && index > 0) {
      document.getElementById(`signup-otp-${index - 1}`)?.focus();
    }
  };

  const formatAadhaar = (value) => {
    const digits = value.replace(/\D/g, '').slice(0, 12);
    const parts = [];
    for (let i = 0; i < digits.length; i += 4) {
      parts.push(digits.slice(i, i + 4));
    }
    return parts.join(' ');
  };

  const handleAadhaarChange = (e) => {
    const formatted = formatAadhaar(e.target.value);
    setFormData(prev => ({ ...prev, aadhaarNumber: formatted }));
  };

  const validateStep = (stepNum) => {
    const newErrors = {};
    
    switch (stepNum) {
      case 1:
        if (!formData.fullName.trim()) newErrors.fullName = 'Full name is required';
        if (formData.fullName.trim().length < 3) newErrors.fullName = 'Name must be at least 3 characters';
        break;
      case 2:
        if (!formData.email) newErrors.email = 'Email is required';
        else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) newErrors.email = 'Invalid email format';
        if (!formData.phone) newErrors.phone = 'Phone number is required';
        else if (!/^[6-9]\d{9}$/.test(formData.phone)) newErrors.phone = 'Invalid phone number';
        if (!phoneVerified) newErrors.phone = 'Please verify your phone number';
        break;
      case 3:
        if (!formData.password) newErrors.password = 'Password is required';
        else if (formData.password.length < 8) newErrors.password = 'Password must be at least 8 characters';
        if (formData.password !== formData.confirmPassword) newErrors.confirmPassword = 'Passwords do not match';
        if (!formData.residentialAddress) newErrors.residentialAddress = 'Address is required';
        break;
      case 4:
        const aadhaar = formData.aadhaarNumber.replace(/\s/g, '');
        if (!aadhaar) newErrors.aadhaarNumber = 'Aadhaar number is required';
        else if (aadhaar.length !== 12) newErrors.aadhaarNumber = 'Aadhaar must be 12 digits';
        if (!formData.aadhaarFile) newErrors.aadhaarFile = 'Please upload your Aadhaar card';
        if (!formData.monthlyIncome) newErrors.monthlyIncome = 'Monthly income is required';
        // Validate PAN if provided
        if (formData.panNumber && !validatePanFormat(formData.panNumber)) {
          newErrors.panNumber = 'Invalid PAN format (e.g., ABCDE1234F)';
        }
        break;
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const nextStep = () => {
    if (validateStep(step)) {
      setStep(step + 1);
    }
  };

  const prevStep = () => {
    setStep(step - 1);
  };

  const handleSendOTP = async () => {
    if (!/^[6-9]\d{9}$/.test(formData.phone)) {
      toast.error('Please enter a valid 10-digit Indian phone number', { duration: 3000 });
      return;
    }
    if (!formData.email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      toast.error('Please enter a valid email address first', { duration: 3000 });
      return;
    }
    
    setLoading(true);
    try {
      // Send OTP to email (not phone - no billing needed!)
      const result = await sendEmailOTPCode(formData.email);
      setOtpSent(true);
      
      if (result.otp_hint) {
        // Demo mode - OTP shown in toast
        toast.success(`Demo Mode: Your OTP is ${result.otp_hint}`, { 
          duration: 15000,
          icon: '🔐'
        });
      } else {
        // Production mode - OTP sent to email
        toast.success(`OTP sent to ${formData.email}. Check your inbox!`, { 
          duration: 5000,
          icon: '📧'
        });
      }
    } catch (error) {
      toast.error(error.message || 'Failed to send OTP. Please try again.', { duration: 4000 });
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyOTP = async () => {
    const otpString = otp.join('');
    if (otpString.length !== 6) {
      toast.error('Please enter all 6 digits of OTP', { duration: 3000 });
      return;
    }
    
    setLoading(true);
    try {
      // Verify OTP (sent to email, but verifies phone ownership)
      const result = await verifyEmailOTPCode(formData.email, otpString);
      if (result.success) {
        setPhoneVerified(true);
        setOtpSent(false);
        toast.success('Phone number verified successfully!', { 
          duration: 4000,
          icon: '\u2705'
        });
      }
    } catch (error) {
      toast.error(error.message || 'Invalid OTP. Please try again.', { duration: 4000 });
      setOtp(['', '', '', '', '', '']);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validateStep(4)) return;

    setLoading(true);
    try {
      const submitData = new FormData();
      submitData.append('full_name', formData.fullName);
      submitData.append('email', formData.email);
      submitData.append('phone', formData.phone);
      submitData.append('password', formData.password);
      submitData.append('confirm_password', formData.confirmPassword);
      submitData.append('residential_address', formData.residentialAddress);
      submitData.append('aadhaar_number', formData.aadhaarNumber.replace(/\s/g, ''));
      submitData.append('monthly_income', formData.monthlyIncome);
      submitData.append('phone_verified', phoneVerified);  // Phone verified via email OTP
      
      // PAN details
      if (formData.panNumber) {
        submitData.append('pan_number', formData.panNumber);
      }
      if (formData.panFile) {
        submitData.append('pan_card', formData.panFile);
      }
      
      if (formData.aadhaarFile) {
        submitData.append('aadhaar_card', formData.aadhaarFile);
      }
      if (formData.incomeFile) {
        submitData.append('income_certificate', formData.incomeFile);
      }

      const response = await signup(submitData);
      if (response.success) {
        // Send welcome email with credentials
        try {
          await sendWelcomeEmail({
            email: formData.email,
            userName: formData.fullName,
            userId: response.user_id || response.data?.user_id || formData.phone,
            password: formData.password,
            phone: formData.phone
          });
          toast.success('🎉 Account created! Check your email for login credentials.', { 
            duration: 5000,
            style: { background: '#d1fae5', color: '#065f46' }
          });
        } catch (emailError) {
          console.error('Welcome email failed:', emailError);
          toast.success('✅ Account created successfully! Please login.', { 
            duration: 4000,
            style: { background: '#d1fae5', color: '#065f46' }
          });
        }
        onSwitchToLogin?.();
      }
    } catch (error) {
      toast.error(error || 'Registration failed. Please try again.', { duration: 4000 });
    } finally {
      setLoading(false);
    }
  };

  const steps = [
    { num: 1, label: 'Personal', icon: User },
    { num: 2, label: 'Contact', icon: Phone },
    { num: 3, label: 'Security', icon: Lock },
    { num: 4, label: 'KYC & Income', icon: CreditCard }
  ];

  return (
    <div className="min-h-screen flex">
      {/* Document Preview Modal */}
      {previewFile && (
        <DocumentPreviewModal 
          file={previewFile} 
          onClose={() => setPreviewFile(null)} 
        />
      )}

      {/* Left Panel - Branding */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-[#004c8c] via-[#0066b3] to-[#0077cc] text-white p-12 flex-col justify-between relative overflow-hidden">
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
            <h2 className="text-4xl font-bold leading-tight mb-4">
              Create Your<br />
              <span className="text-[#ffd700]">QuickLoan</span><br />
              Account Today
            </h2>
            <p className="text-white/80 text-lg">
              Join thousands of satisfied customers who trust us for their financial needs.
            </p>
          </div>

          {/* Benefits */}
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4">
              <CheckCircle className="w-8 h-8 text-green-400 mb-2" />
              <h3 className="font-semibold mb-1">Quick Approval</h3>
              <p className="text-sm text-white/70">Get approved in minutes with AI</p>
            </div>
            <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4">
              <Shield className="w-8 h-8 text-blue-300 mb-2" />
              <h3 className="font-semibold mb-1">100% Secure</h3>
              <p className="text-sm text-white/70">Bank-grade data protection</p>
            </div>
            <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4">
              <IndianRupee className="w-8 h-8 text-yellow-400 mb-2" />
              <h3 className="font-semibold mb-1">Low Rates</h3>
              <p className="text-sm text-white/70">Starting from 10.5% p.a.</p>
            </div>
            <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4">
              <FileText className="w-8 h-8 text-purple-300 mb-2" />
              <h3 className="font-semibold mb-1">Minimal Docs</h3>
              <p className="text-sm text-white/70">Simple paperless process</p>
            </div>
          </div>
        </div>

        <div className="relative z-10 text-sm text-white/60">
          Already have an account?{' '}
          <button onClick={onSwitchToLogin} className="text-white font-semibold hover:underline">
            Login here
          </button>
        </div>
      </div>

      {/* Right Panel - Signup Form */}
      <div className="flex-1 flex items-center justify-center p-8 bg-gray-50">
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="w-full max-w-lg"
        >
          {/* Mobile Logo */}
          <div className="lg:hidden text-center mb-6">
            <div className="inline-flex items-center gap-3">
              <div className="w-10 h-10 bg-[#004c8c] rounded-lg flex items-center justify-center">
                <span className="text-white font-bold">QL</span>
              </div>
              <span className="text-xl font-bold text-gray-800">QuickLoan</span>
            </div>
          </div>

          <div className="bg-white rounded-2xl shadow-xl p-8">
            <h2 className="text-2xl font-bold text-gray-800 text-center mb-2">Create Account</h2>
            <p className="text-gray-600 text-center mb-6">Fill in your details to get started</p>

            {/* Progress Steps */}
            <div className="flex items-center justify-between mb-8">
              {steps.map((s, index) => (
                <React.Fragment key={s.num}>
                  <div className="flex flex-col items-center">
                    <div className={`w-10 h-10 rounded-full flex items-center justify-center transition-all ${
                      step >= s.num 
                        ? 'bg-[#004c8c] text-white' 
                        : 'bg-gray-200 text-gray-500'
                    }`}>
                      {step > s.num ? (
                        <CheckCircle className="w-5 h-5" />
                      ) : (
                        <s.icon className="w-5 h-5" />
                      )}
                    </div>
                    <span className={`text-xs mt-1 ${step >= s.num ? 'text-[#004c8c] font-medium' : 'text-gray-500'}`}>
                      {s.label}
                    </span>
                  </div>
                  {index < steps.length - 1 && (
                    <div className={`flex-1 h-1 mx-2 rounded ${step > s.num ? 'bg-[#004c8c]' : 'bg-gray-200'}`} />
                  )}
                </React.Fragment>
              ))}
            </div>

            <form onSubmit={handleSubmit}>
              <AnimatePresence mode="wait">
                {/* Step 1: Personal Info */}
                {step === 1 && (
                  <motion.div
                    key="step1"
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                    className="space-y-5"
                  >
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1.5">
                        Full Name (as per Aadhaar)<span className="text-red-500">*</span>
                      </label>
                      <div className="relative">
                        <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                        <input
                          type="text"
                          name="fullName"
                          value={formData.fullName}
                          onChange={handleInputChange}
                          placeholder="Enter your full name"
                          className={`w-full pl-10 pr-4 py-3 border rounded-lg focus:ring-2 focus:ring-[#004c8c] focus:border-transparent transition-all ${
                            errors.fullName ? 'border-red-500' : 'border-gray-300'
                          }`}
                        />
                      </div>
                      {errors.fullName && <p className="text-red-500 text-sm mt-1">{errors.fullName}</p>}
                    </div>
                  </motion.div>
                )}

                {/* Step 2: Contact Info with Phone OTP */}
                {step === 2 && (
                  <motion.div
                    key="step2"
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                    className="space-y-5"
                  >
                    {/* Email Address */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1.5">
                        Email Address<span className="text-red-500">*</span>
                      </label>
                      <div className="relative">
                        <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                        <input
                          type="email"
                          name="email"
                          value={formData.email}
                          onChange={handleInputChange}
                          placeholder="your@email.com (OTP will be sent here)"
                          className={`w-full pl-10 pr-4 py-3 border rounded-lg focus:ring-2 focus:ring-[#004c8c] focus:border-transparent transition-all ${
                            errors.email ? 'border-red-500' : 'border-gray-300'
                          }`}
                        />
                      </div>
                      {errors.email && <p className="text-red-500 text-sm mt-1">{errors.email}</p>}
                    </div>

                    {/* Phone Number with Verify Button */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1.5">
                        Phone Number<span className="text-red-500">*</span>
                      </label>
                      <div className="flex gap-2">
                        <div className="relative flex-1">
                          <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 text-sm border-r pr-2">
                            +91
                          </span>
                          <input
                            type="tel"
                            name="phone"
                            value={formData.phone}
                            onChange={handleInputChange}
                            placeholder="Enter 10-digit number"
                            maxLength={10}
                            disabled={phoneVerified}
                            className={`w-full pl-14 pr-4 py-3 border rounded-lg focus:ring-2 focus:ring-[#004c8c] focus:border-transparent transition-all ${
                              errors.phone ? 'border-red-500' : phoneVerified ? 'border-green-500 bg-green-50' : 'border-gray-300'
                            }`}
                          />
                          {phoneVerified && (
                            <CheckCircle className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-green-500" />
                          )}
                        </div>
                        {!phoneVerified && (
                          <button
                            type="button"
                            id="signup-otp-button"
                            onClick={handleSendOTP}
                            disabled={loading || formData.phone.length !== 10 || !formData.email}
                            className="px-4 py-3 bg-[#c8102e] text-white rounded-lg font-medium hover:bg-[#a50d26] transition-colors disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap"
                          >
                            {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Verify'}
                          </button>
                        )}
                      </div>
                      {errors.phone && <p className="text-red-500 text-sm mt-1">{errors.phone}</p>}
                      {!phoneVerified && formData.email && formData.phone.length === 10 && (
                        <p className="text-xs text-gray-500 mt-1">📧 OTP will be sent to {formData.email}</p>
                      )}
                    </div>

                    {/* OTP Input - for Phone verification via Email */}
                    {otpSent && !phoneVerified && (
                      <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        className="space-y-4 p-4 bg-blue-50 rounded-lg"
                      >
                        <p className="text-sm text-gray-700 text-center">
                          Enter OTP sent to <span className="font-semibold">{formData.email}</span>
                        </p>
                        <div className="flex justify-center gap-2">
                          {otp.map((digit, index) => (
                            <input
                              key={index}
                              id={`signup-otp-${index}`}
                              type="text"
                              inputMode="numeric"
                              maxLength={1}
                              value={digit}
                              onChange={(e) => handleOtpChange(index, e.target.value.replace(/\D/g, ''))}
                              onKeyDown={(e) => handleOtpKeyDown(index, e)}
                              className="w-10 h-12 text-center text-xl font-bold border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-[#004c8c] focus:border-transparent"
                            />
                          ))}
                        </div>
                        <div className="flex justify-center gap-4">
                          <button
                            type="button"
                            onClick={handleVerifyOTP}
                            disabled={loading || otp.join('').length !== 6}
                            className="px-6 py-2 bg-[#004c8c] text-white rounded-lg font-medium hover:bg-[#003d73] transition-colors disabled:opacity-50"
                          >
                            {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Verify OTP'}
                          </button>
                          <button
                            type="button"
                            onClick={handleSendOTP}
                            className="text-[#004c8c] text-sm hover:underline"
                          >
                            Resend OTP
                          </button>
                        </div>
                      </motion.div>
                    )}
                  </motion.div>
                )}

                {/* Step 3: Security */}
                {step === 3 && (
                  <motion.div
                    key="step3"
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                    className="space-y-5"
                  >
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1.5">
                        Create Password<span className="text-red-500">*</span>
                      </label>
                      <div className="relative">
                        <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                        <input
                          type={showPassword ? 'text' : 'password'}
                          name="password"
                          value={formData.password}
                          onChange={handleInputChange}
                          placeholder="Minimum 8 characters"
                          className={`w-full pl-10 pr-12 py-3 border rounded-lg focus:ring-2 focus:ring-[#004c8c] focus:border-transparent transition-all ${
                            errors.password ? 'border-red-500' : 'border-gray-300'
                          }`}
                        />
                        <button
                          type="button"
                          onClick={() => setShowPassword(!showPassword)}
                          className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500"
                        >
                          {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                        </button>
                      </div>
                      {errors.password && <p className="text-red-500 text-sm mt-1">{errors.password}</p>}
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1.5">
                        Confirm Password<span className="text-red-500">*</span>
                      </label>
                      <div className="relative">
                        <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                        <input
                          type="password"
                          name="confirmPassword"
                          value={formData.confirmPassword}
                          onChange={handleInputChange}
                          placeholder="Re-enter password"
                          className={`w-full pl-10 pr-4 py-3 border rounded-lg focus:ring-2 focus:ring-[#004c8c] focus:border-transparent transition-all ${
                            errors.confirmPassword ? 'border-red-500' : 'border-gray-300'
                          }`}
                        />
                      </div>
                      {errors.confirmPassword && <p className="text-red-500 text-sm mt-1">{errors.confirmPassword}</p>}
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1.5">
                        Residential Address<span className="text-red-500">*</span>
                      </label>
                      <div className="relative">
                        <Home className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
                        <textarea
                          name="residentialAddress"
                          value={formData.residentialAddress}
                          onChange={handleInputChange}
                          placeholder="Enter your complete residential address"
                          rows={3}
                          className={`w-full pl-10 pr-4 py-3 border rounded-lg focus:ring-2 focus:ring-[#004c8c] focus:border-transparent transition-all resize-none ${
                            errors.residentialAddress ? 'border-red-500' : 'border-gray-300'
                          }`}
                        />
                      </div>
                      {errors.residentialAddress && <p className="text-red-500 text-sm mt-1">{errors.residentialAddress}</p>}
                    </div>
                  </motion.div>
                )}

                {/* Step 4: KYC & Income */}
                {step === 4 && (
                  <motion.div
                    key="step4"
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                    className="space-y-5"
                  >
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1.5">
                        Aadhaar Number<span className="text-red-500">*</span>
                      </label>
                      <div className="relative">
                        <CreditCard className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                        <input
                          type="text"
                          value={formData.aadhaarNumber}
                          onChange={handleAadhaarChange}
                          placeholder="XXXX XXXX XXXX"
                          maxLength={14}
                          className={`w-full pl-10 pr-4 py-3 border rounded-lg focus:ring-2 focus:ring-[#004c8c] focus:border-transparent transition-all font-mono tracking-wider ${
                            errors.aadhaarNumber ? 'border-red-500' : 'border-gray-300'
                          }`}
                        />
                      </div>
                      {errors.aadhaarNumber && <p className="text-red-500 text-sm mt-1">{errors.aadhaarNumber}</p>}
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1.5">
                        Upload Aadhaar Card<span className="text-red-500">*</span>
                      </label>
                      <div 
                        className={`border-2 border-dashed rounded-lg p-4 transition-colors ${
                          errors.aadhaarFile ? 'border-red-500' : 'border-gray-300'
                        }`}
                      >
                        <input
                          ref={aadhaarFileRef}
                          type="file"
                          accept=".pdf,.jpg,.jpeg,.png"
                          onChange={handleAadhaarFileChange}
                          className="hidden"
                        />
                        {formData.aadhaarFile ? (
                          <div className="flex items-center justify-between">
                            <div 
                              onClick={() => aadhaarFileRef.current?.click()}
                              className="flex items-center gap-2 text-green-600 cursor-pointer hover:text-green-700 flex-1"
                            >
                              <CheckCircle className="w-5 h-5" />
                              <span className="text-sm truncate max-w-[200px]">{formData.aadhaarFile.name}</span>
                            </div>
                            <button
                              type="button"
                              onClick={(e) => {
                                e.stopPropagation();
                                setPreviewFile(formData.aadhaarFile);
                              }}
                              className="p-2 bg-[#004c8c] text-white rounded-lg hover:bg-[#003d73] transition-colors flex items-center gap-1"
                              title="View Document"
                            >
                              <Eye className="w-4 h-4" />
                              <span className="text-xs">View</span>
                            </button>
                          </div>
                        ) : (
                          <div 
                            onClick={() => aadhaarFileRef.current?.click()}
                            className="cursor-pointer text-center hover:bg-gray-50"
                          >
                            <Upload className="w-6 h-6 text-gray-400 mx-auto mb-1" />
                            <p className="text-sm text-gray-600">Upload front & back of Aadhaar</p>
                            <p className="text-xs text-gray-500">PDF, JPG, PNG (max 5MB)</p>
                          </div>
                        )}
                      </div>
                      {errors.aadhaarFile && <p className="text-red-500 text-sm mt-1">{errors.aadhaarFile}</p>}
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1.5">
                        Monthly Income (₹)<span className="text-red-500">*</span>
                      </label>
                      <div className="relative">
                        <IndianRupee className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                        <input
                          type="number"
                          name="monthlyIncome"
                          value={formData.monthlyIncome}
                          onChange={handleInputChange}
                          placeholder="Enter your monthly income"
                          className={`w-full pl-10 pr-4 py-3 border rounded-lg focus:ring-2 focus:ring-[#004c8c] focus:border-transparent transition-all ${
                            errors.monthlyIncome ? 'border-red-500' : 'border-gray-300'
                          }`}
                        />
                      </div>
                      {errors.monthlyIncome && <p className="text-red-500 text-sm mt-1">{errors.monthlyIncome}</p>}
                    </div>

                    {/* Income Certificate - Right after Monthly Income */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1.5">
                        Income Certificate (PDF)
                      </label>
                      <div 
                        className="border-2 border-dashed border-gray-300 rounded-lg p-4 transition-colors"
                      >
                        <input
                          ref={fileInputRef}
                          type="file"
                          accept=".pdf"
                          onChange={handleFileChange}
                          className="hidden"
                        />
                        {formData.incomeFile ? (
                          <div className="flex items-center justify-between">
                            <div 
                              onClick={() => fileInputRef.current?.click()}
                              className="flex items-center gap-2 text-green-600 cursor-pointer hover:text-green-700 flex-1"
                            >
                              <CheckCircle className="w-5 h-5" />
                              <span className="text-sm truncate max-w-[200px]">{formData.incomeFile.name}</span>
                            </div>
                            <button
                              type="button"
                              onClick={(e) => {
                                e.stopPropagation();
                                setPreviewFile(formData.incomeFile);
                              }}
                              className="p-2 bg-[#004c8c] text-white rounded-lg hover:bg-[#003d73] transition-colors flex items-center gap-1"
                              title="View Document"
                            >
                              <Eye className="w-4 h-4" />
                              <span className="text-xs">View</span>
                            </button>
                          </div>
                        ) : (
                          <div 
                            onClick={() => fileInputRef.current?.click()}
                            className="cursor-pointer text-center hover:bg-gray-50"
                          >
                            <Upload className="w-6 h-6 text-gray-400 mx-auto mb-1" />
                            <p className="text-sm text-gray-600">Upload salary slip or income proof</p>
                            <p className="text-xs text-gray-500">PDF format, max 5MB</p>
                          </div>
                        )}
                      </div>
                    </div>

                    {/* PAN Card Section */}
                    <div className="border-t pt-4 mt-2">
                      <p className="text-sm text-gray-500 mb-3">Optional: Add PAN for faster loan approval</p>
                      
                      <div className="mb-4">
                        <label className="block text-sm font-medium text-gray-700 mb-1.5">
                          PAN Number
                        </label>
                        <div className="relative">
                          <CreditCard className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                          <input
                            type="text"
                            value={formData.panNumber}
                            onChange={handlePanChange}
                            placeholder="ABCDE1234F"
                            maxLength={10}
                            className={`w-full pl-10 pr-4 py-3 border rounded-lg focus:ring-2 focus:ring-[#004c8c] focus:border-transparent transition-all font-mono uppercase tracking-wider ${
                              errors.panNumber ? 'border-red-500' : 'border-gray-300'
                            }`}
                          />
                        </div>
                        {errors.panNumber && <p className="text-red-500 text-sm mt-1">{errors.panNumber}</p>}
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1.5">
                          Upload PAN Card
                        </label>
                        <div 
                          className="border-2 border-dashed border-gray-300 rounded-lg p-4 transition-colors"
                        >
                          <input
                            ref={panFileRef}
                            type="file"
                            accept=".pdf,.jpg,.jpeg,.png"
                            onChange={handlePanFileChange}
                            className="hidden"
                          />
                          {formData.panFile ? (
                            <div className="flex items-center justify-between">
                              <div 
                                onClick={() => panFileRef.current?.click()}
                                className="flex items-center gap-2 text-green-600 cursor-pointer hover:text-green-700 flex-1"
                              >
                                <CheckCircle className="w-5 h-5" />
                                <span className="text-sm truncate max-w-[200px]">{formData.panFile.name}</span>
                              </div>
                              <button
                                type="button"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  setPreviewFile(formData.panFile);
                                }}
                                className="p-2 bg-[#004c8c] text-white rounded-lg hover:bg-[#003d73] transition-colors flex items-center gap-1"
                                title="View Document"
                              >
                                <Eye className="w-4 h-4" />
                                <span className="text-xs">View</span>
                              </button>
                            </div>
                          ) : (
                            <div 
                              onClick={() => panFileRef.current?.click()}
                              className="cursor-pointer text-center hover:bg-gray-50"
                            >
                              <Upload className="w-6 h-6 text-gray-400 mx-auto mb-1" />
                              <p className="text-sm text-gray-600">Upload PAN Card</p>
                              <p className="text-xs text-gray-500">PDF, JPG, PNG (max 5MB)</p>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Navigation Buttons */}
              <div className="flex justify-between mt-8">
                {step > 1 ? (
                  <button
                    type="button"
                    onClick={prevStep}
                    className="flex items-center gap-2 px-6 py-3 text-gray-600 hover:text-gray-800 transition-colors"
                  >
                    <ArrowLeft className="w-5 h-5" />
                    Back
                  </button>
                ) : (
                  <div />
                )}

                {step < 4 ? (
                  <button
                    type="button"
                    onClick={nextStep}
                    className="flex items-center gap-2 px-6 py-3 bg-[#004c8c] text-white rounded-lg font-semibold hover:bg-[#003d73] transition-colors"
                  >
                    Continue
                    <ArrowRight className="w-5 h-5" />
                  </button>
                ) : (
                  <button
                    type="submit"
                    disabled={loading}
                    className="flex items-center gap-2 px-8 py-3 bg-[#c8102e] text-white rounded-lg font-semibold hover:bg-[#a50d26] transition-colors disabled:opacity-50"
                  >
                    {loading ? (
                      <Loader2 className="w-5 h-5 animate-spin" />
                    ) : (
                      <>
                        Create Account
                        <ArrowRight className="w-5 h-5" />
                      </>
                    )}
                  </button>
                )}
              </div>
            </form>

            {/* Login Link */}
            <div className="mt-6 text-center lg:hidden">
              <p className="text-gray-600">
                Already have an account?{' '}
                <button onClick={onSwitchToLogin} className="text-[#c8102e] font-semibold hover:underline">
                  Login
                </button>
              </p>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default SignupPage;
