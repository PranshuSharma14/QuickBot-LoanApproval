import React, { useState, useRef, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Send, MessageCircle, User, Bot, Download, Upload, FileText, 
  CheckCircle, XCircle, ArrowLeft, Home, Phone, Shield,
  IndianRupee, Clock, Sparkles
} from 'lucide-react';
import { toast } from 'react-hot-toast';
import axios from 'axios';
import LoanApprovalCelebration from './LoanApprovalCelebration';

const API_BASE_URL = 'http://127.0.0.1:8000/api';

const BankChatInterface = ({ onBack, userInfo, loanId }) => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [currentStage, setCurrentStage] = useState('greeting');
  const [showFileUpload, setShowFileUpload] = useState(false);
  const [loanDetails, setLoanDetails] = useState({});
  const [conversationStarted, setConversationStarted] = useState(false);
  const [isCompleted, setIsCompleted] = useState(false);
  const [isSending, setIsSending] = useState(false);  // Debounce flag
  const [showCelebration, setShowCelebration] = useState(false);  // Celebration screen
  
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const fileInputRef = useRef(null);
  const lastMessageRef = useRef('');  // Track last message to prevent duplicates

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Auto-focus input when not loading
    if (!isLoading && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isLoading, messages]);

  useEffect(() => {
    // Auto-start conversation
    if (!conversationStarted) {
      startConversation();
    }
  }, []);

  const startConversation = async () => {
    setConversationStarted(true);
    // Include user info in first message if available
    const greeting = userInfo 
      ? `Hello, I'm ${userInfo.full_name}. I want to apply for a loan.`
      : 'Hello, I need a loan';
    await sendMessage(greeting);
  };

  const sendMessage = async (message) => {
    if (!message.trim()) return;
    
    // Prevent duplicate sends
    if (isSending) return;
    if (message === lastMessageRef.current && Date.now() - (window.lastSendTime || 0) < 2000) {
      console.log('Duplicate message blocked');
      return;
    }
    
    setIsSending(true);
    lastMessageRef.current = message;
    window.lastSendTime = Date.now();

    const userMessage = {
      id: Date.now(),
      text: message,
      sender: 'user',
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await axios.post(`${API_BASE_URL}/chat`, {
        message: message,
        session_id: sessionId,
        phone: userInfo?.phone || null
      });

      const { data } = response;

      if (data.session_id && !sessionId) {
        setSessionId(data.session_id);
      }

      setCurrentStage(data.stage);

      // Check for file upload requirement
      if (data.file_upload) {
        setShowFileUpload(true);
      }

      // Check if completed
      if (data.final || data.stage === 'approved' || data.stage === 'rejected') {
        setIsCompleted(true);
        // Show celebration only for approved loans
        if (data.stage === 'approved' || (data.final && data.stage !== 'rejected')) {
          // Extract loan details from response for celebration
          if (data.metadata) {
            setLoanDetails(prev => ({ 
              ...prev, 
              ...data.metadata,
              customerName: userInfo?.full_name || data.metadata.customer_name || 'Customer'
            }));
          }
          // Show celebration after a short delay for dramatic effect
          setTimeout(() => setShowCelebration(true), 1500);
        }
      }

      // Extract loan details
      if (data.metadata) {
        setLoanDetails(prev => ({ ...prev, ...data.metadata }));
      }

      // Add bot response
      const botMessage = {
        id: Date.now() + 1,
        text: data.message,
        sender: 'bot',
        timestamp: new Date(),
        options: data.options,
        stage: data.stage,
        metadata: data.metadata
      };
      setMessages(prev => [...prev, botMessage]);

    } catch (error) {
      console.error('Chat error:', error);
      toast.error('Connection error. Please try again.');
      const errorMessage = {
        id: Date.now() + 1,
        text: 'Sorry, there was an error. Please try again.',
        sender: 'bot',
        timestamp: new Date(),
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      setIsSending(false);  // Reset debounce flag
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (inputValue.trim() && !isLoading && !isSending) {
      sendMessage(inputValue);
    }
  };

  const handleOptionClick = (option) => {
    sendMessage(option);
  };

  const handleFileUpload = async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('phone', userInfo?.phone || '9999999999');

    try {
      setIsLoading(true);
      const response = await axios.post(`${API_BASE_URL}/upload/salary-slip`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      if (response.data.uploaded) {
        toast.success('Document uploaded successfully!');
        setShowFileUpload(false);
        sendMessage('I have uploaded my salary slip');
      } else {
        toast.error('Failed to upload document');
      }
    } catch (error) {
      console.error('Upload error:', error);
      toast.error('Failed to upload document');
    } finally {
      setIsLoading(false);
    }
  };

  const downloadSanctionLetter = async () => {
    try {
      window.open(`${API_BASE_URL}/download-sanction-letter/${sessionId}`, '_blank');
    } catch (error) {
      toast.error('Failed to download sanction letter');
    }
  };

  const getStageInfo = () => {
    const stages = {
      greeting: { label: 'Welcome', progress: 10, color: 'blue' },
      sales: { label: 'Requirements', progress: 25, color: 'blue' },
      verification: { label: 'Verification', progress: 50, color: 'yellow' },
      underwriting: { label: 'Processing', progress: 75, color: 'purple' },
      salary_slip: { label: 'Documents', progress: 80, color: 'purple' },
      approved: { label: 'Approved', progress: 100, color: 'green' },
      rejected: { label: 'Rejected', progress: 100, color: 'red' },
      completed: { label: 'Completed', progress: 100, color: 'green' }
    };
    return stages[currentStage] || stages.greeting;
  };

  const stageInfo = getStageInfo();

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <header className="bg-white shadow-sm border-b sticky top-0 z-10">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={onBack}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <ArrowLeft className="w-5 h-5 text-gray-600" />
              </button>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-[#004c8c] rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold text-sm">QL</span>
                </div>
                <div>
                  <h1 className="font-semibold text-gray-800">QuickLoan Assistant</h1>
                  <p className="text-xs text-gray-500">AI-Powered Loan Processing</p>
                </div>
              </div>
            </div>
            
            <div className="flex items-center gap-4">
              {loanId && (
                <span className="text-sm text-gray-500">
                  Loan ID: <span className="font-medium text-gray-700">{loanId}</span>
                </span>
              )}
              <div className="flex items-center gap-2 text-sm">
                <Shield className="w-4 h-4 text-green-500" />
                <span className="text-green-600 font-medium">Secure</span>
              </div>
            </div>
          </div>

          {/* Progress Bar */}
          <div className="mt-4">
            <div className="flex justify-between text-sm mb-2">
              <span className="text-gray-600">Application Progress</span>
              <span className={`font-medium ${
                stageInfo.color === 'green' ? 'text-green-600' :
                stageInfo.color === 'red' ? 'text-red-600' :
                stageInfo.color === 'yellow' ? 'text-yellow-600' :
                stageInfo.color === 'purple' ? 'text-purple-600' :
                'text-blue-600'
              }`}>
                {stageInfo.label}
              </span>
            </div>
            <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
              <motion.div 
                initial={{ width: 0 }}
                animate={{ width: `${stageInfo.progress}%` }}
                className={`h-full rounded-full ${
                  stageInfo.color === 'green' ? 'bg-green-500' :
                  stageInfo.color === 'red' ? 'bg-red-500' :
                  stageInfo.color === 'yellow' ? 'bg-yellow-500' :
                  stageInfo.color === 'purple' ? 'bg-purple-500' :
                  'bg-blue-500'
                }`}
              />
            </div>
          </div>
        </div>
      </header>

      {/* Chat Messages */}
      <main className="flex-1 overflow-y-auto">
        <div className="max-w-4xl mx-auto px-4 py-6 space-y-4">
          <AnimatePresence>
            {messages.map((message) => (
              <motion.div
                key={message.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div className={`flex gap-3 max-w-[80%] ${message.sender === 'user' ? 'flex-row-reverse' : ''}`}>
                  {/* Avatar */}
                  <div className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${
                    message.sender === 'user' 
                      ? 'bg-[#004c8c]' 
                      : message.isError 
                        ? 'bg-red-100' 
                        : 'bg-gray-100'
                  }`}>
                    {message.sender === 'user' ? (
                      <User className="w-5 h-5 text-white" />
                    ) : (
                      <Bot className={`w-5 h-5 ${message.isError ? 'text-red-500' : 'text-[#004c8c]'}`} />
                    )}
                  </div>

                  {/* Message Content */}
                  <div className={`rounded-2xl px-4 py-3 ${
                    message.sender === 'user'
                      ? 'bg-[#004c8c] text-white'
                      : message.isError
                        ? 'bg-red-50 text-red-700 border border-red-200'
                        : 'bg-white text-gray-800 shadow-sm border'
                  }`}>
                    <p className="whitespace-pre-wrap">{message.text}</p>
                    
                    {/* Options */}
                    {message.options && message.options.length > 0 && (
                      <div className="mt-3 flex flex-wrap gap-2">
                        {message.options.map((option, index) => (
                          <button
                            key={index}
                            onClick={() => handleOptionClick(option)}
                            className="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-800 rounded-lg text-sm font-medium transition-colors border"
                          >
                            {option}
                          </button>
                        ))}
                      </div>
                    )}

                    {/* Download Button for Approved */}
                    {message.stage === 'approved' && (
                      <button
                        onClick={downloadSanctionLetter}
                        className="mt-3 flex items-center gap-2 bg-green-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-green-700 transition-colors"
                      >
                        <Download className="w-4 h-4" />
                        Download Sanction Letter
                      </button>
                    )}

                    <p className={`text-xs mt-2 ${message.sender === 'user' ? 'text-white/60' : 'text-gray-400'}`}>
                      {new Date(message.timestamp).toLocaleTimeString('en-IN', { 
                        hour: '2-digit', 
                        minute: '2-digit' 
                      })}
                    </p>
                  </div>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>

          {/* Typing Indicator */}
          {isLoading && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex gap-3"
            >
              <div className="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center">
                <Bot className="w-5 h-5 text-[#004c8c]" />
              </div>
              <div className="bg-white rounded-2xl px-4 py-3 shadow-sm border">
                <div className="flex gap-1">
                  <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                  <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                  <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
              </div>
            </motion.div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </main>

      {/* File Upload Modal */}
      {showFileUpload && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            className="bg-white rounded-2xl p-6 max-w-md w-full"
          >
            <h3 className="text-lg font-semibold text-gray-800 mb-4">Upload Salary Slip</h3>
            <p className="text-gray-600 mb-4">Please upload your latest salary slip (PDF format)</p>
            
            <div 
              onClick={() => fileInputRef.current?.click()}
              className="border-2 border-dashed border-gray-300 rounded-xl p-8 text-center cursor-pointer hover:border-[#004c8c] transition-colors"
            >
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf"
                onChange={(e) => e.target.files[0] && handleFileUpload(e.target.files[0])}
                className="hidden"
              />
              <Upload className="w-12 h-12 text-gray-400 mx-auto mb-3" />
              <p className="text-gray-600">Click to upload or drag and drop</p>
              <p className="text-sm text-gray-500 mt-1">PDF (max 5MB)</p>
            </div>

            <button
              onClick={() => setShowFileUpload(false)}
              className="w-full mt-4 py-2 text-gray-600 hover:text-gray-800"
            >
              Cancel
            </button>
          </motion.div>
        </div>
      )}

      {/* Input Area */}
      <footer className="bg-white border-t sticky bottom-0">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <form onSubmit={handleSubmit} className="flex gap-3">
            <input
              ref={inputRef}
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder={isCompleted ? "Conversation completed" : "Type your message..."}
              disabled={isLoading || isCompleted}
              autoFocus
              className="flex-1 px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-[#004c8c] focus:border-transparent transition-all disabled:bg-gray-100"
            />
            <button
              type="submit"
              disabled={isLoading || !inputValue.trim() || isCompleted}
              className="px-6 py-3 bg-[#004c8c] text-white rounded-xl font-medium hover:bg-[#003d73] transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              <Send className="w-5 h-5" />
            </button>
          </form>

          <div className="flex items-center justify-center gap-4 mt-3 text-xs text-gray-500">
            <span className="flex items-center gap-1">
              <Shield className="w-3 h-3" />
              256-bit encryption
            </span>
            <span>•</span>
            <span className="flex items-center gap-1">
              <Sparkles className="w-3 h-3" />
              AI-Powered
            </span>
          </div>
        </div>
      </footer>

      {/* Loan Approval Celebration */}
      <AnimatePresence>
        {showCelebration && (
          <LoanApprovalCelebration
            loanDetails={loanDetails}
            customerName={userInfo?.full_name || loanDetails?.customerName || 'Customer'}
            sessionId={sessionId}
            onDownloadLetter={downloadSanctionLetter}
            onBackToDashboard={onBack}
          />
        )}
      </AnimatePresence>
    </div>
  );
};

export default BankChatInterface;
