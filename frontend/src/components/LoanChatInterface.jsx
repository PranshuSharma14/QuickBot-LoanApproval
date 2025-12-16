import React, { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Send, MessageCircle, User, Bot, Download, Upload, FileText, CheckCircle, XCircle } from 'lucide-react'
import { toast } from 'react-hot-toast'
import axios from 'axios'
import ChatMessage from './ChatMessage'
import TypingIndicator from './TypingIndicator'
import FileUploader from './FileUploader'
import LoanProgress from './LoanProgress'

const API_BASE_URL = 'http://127.0.0.1:8000/api'

const LoanChatInterface = () => {
  const [messages, setMessages] = useState([])
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [sessionId, setSessionId] = useState(null)
  const [currentStage, setCurrentStage] = useState('greeting')
  const [showFileUpload, setShowFileUpload] = useState(false)
  const [loanDetails, setLoanDetails] = useState({})
  const [conversationStarted, setConversationStarted] = useState(false)
  const [isRejected, setIsRejected] = useState(false)
  
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)
 //reset function
  const resetConversation = () => {
    setMessages([])
    setInputValue('')
    setIsLoading(false)
    setSessionId(null)
    setCurrentStage('greeting')
    setShowFileUpload(false)
    setLoanDetails({})
    setConversationStarted(false)
    setIsRejected(false)
  }

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const startConversation = async () => {
    setConversationStarted(true)
    await sendMessage('Hello, I need a loan')
  }

  const handleOptionClick = (option) => {
    // Automatically send the selected option as a message
    sendMessage(option)
  }

  const sendMessage = async (message) => {
    if (!message.trim()) return

    // Add user message
    const userMessage = {
      id: Date.now(),
      text: message,
      sender: 'user',
      timestamp: new Date()
    }
    setMessages(prev => [...prev, userMessage])
    setInputValue('')
    setIsLoading(true)

    try {
      const response = await axios.post(`${API_BASE_URL}/chat`, {
        message: message,
        session_id: sessionId,
        phone: null // Will be collected during conversation
      })

      const { data } = response

      // Update session ID
      if (data.session_id && !sessionId) {
        setSessionId(data.session_id)
      }

      // Update current stage
      setCurrentStage(data.stage)

      // Check if loan is rejected - more comprehensive check
      console.log('Stage:', data.stage, 'Message:', data.message.substring(0, 50))
      if (data.stage === 'rejected' || 
          (data.final === true && (
            data.message.toLowerCase().includes('cannot approve') ||
            data.message.toLowerCase().includes('unfortunately') ||
            data.message.toLowerCase().includes('not approved')
          ))) {
        console.log('Setting isRejected to TRUE')
        setIsRejected(true)
      }

      // Extract loan details from response if loan is approved
      if (data.message.toLowerCase().includes('approved')) {
        extractLoanDetails(data.message)
      }

      // Add bot response
      const botMessage = {
        id: Date.now() + 1,
        text: data.message,
        sender: 'bot',
        timestamp: new Date(),
        stage: data.stage,
        options: data.options,
        final: data.final
      }

      // Simulate typing delay for realism
      setTimeout(() => {
        setMessages(prev => [...prev, botMessage])
        setIsLoading(false)

        // Auto-focus input field after bot responds
        setTimeout(() => {
          inputRef.current?.focus()
        }, 100)

        // Show file upload after message with a small delay
        if (data.file_upload) {
          setTimeout(() => {
            setShowFileUpload(true)
          }, 500)
        }

        // Show success toast for approvals
        //{incorrect }if (data.message.includes('approved') || data.message.includes('APPROVED')) {
         // toast.success('🎉 Congratulations! Your loan has been approved!')
        //}
        if (data.final === true && data.stage === 'completed' && data.message.startsWith('🎉')) {
           toast.success('🎉 Congratulations! Your loan has been approved!')
        }

      }, 1500)

    } catch (error) {
      setIsLoading(false)
      console.error('Error sending message:', error)

      const errorMessage = {
        id: Date.now() + 1,
        text: 'I apologize, but I\'m experiencing some technical difficulties. Please try again in a moment.',
        sender: 'bot',
        timestamp: new Date(),
        isError: true
      }

      setMessages(prev => [...prev, errorMessage])
      toast.error('Connection error. Please try again.')
    }
  }

  const extractLoanDetails = (message) => {
      const amountMatch = message.match(/Principal Amount\*\*: ₹([\d,]+)/i)
      const emiMatch = message.match(/Monthly EMI\*\*: ₹([\d,]+)/i)
      const tenureMatch = message.match(/Loan Tenure\*\*: (\d+)\s*months/i)
      const rateMatch = message.match(/Interest Rate\*\*: ([\d.]+)%/i)

      if (!amountMatch) return

      setLoanDetails({
        amount: `₹${amountMatch[1]}`,
        emi: emiMatch ? `₹${emiMatch[1]}` : '—',
        tenure: tenureMatch ? `${tenureMatch[1]} months` : '—',
        rate: rateMatch ? `${rateMatch[1]}%` : '—'
      })
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    if (inputValue.trim()) {
      sendMessage(inputValue)
    }
  }

  const handleFileUpload = async (file) => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('phone', '9876543210') // Demo phone number

    try {
      setIsLoading(true)
      const response = await axios.post(`${API_BASE_URL}/upload/salary-slip`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })

      const { data } = response

      if (data.uploaded) {
        toast.success('Salary slip uploaded successfully!')
        setShowFileUpload(false)

        // Continue conversation after upload
        await sendMessage('I have uploaded my salary slip')
      } else {
        toast.error('Failed to upload file. Please try again.')
      }
    } catch (error) {
      console.error('Upload error:', error)
      toast.error('Upload failed. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  const downloadSanctionLetter = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/download-sanction-letter/${sessionId}`)

      if (!response.ok) {
        throw new Error('Failed to download sanction letter')
      }

      // Create blob from response
      const blob = await response.blob()

      // Create download link
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'QuickLoan_Sanction_Letter.pdf'
      document.body.appendChild(a)
      a.click()

      // Cleanup
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)

      toast.success('Sanction letter downloaded successfully!')
    } catch (error) {
      console.error('Download error:', error)
      toast.error('Failed to download sanction letter. Please try again.')
    }
  }

  const getStageProgress = () => {
    const stages = ['greeting', 'sales', 'verification', 'underwriting', 'decision', 'completed']
    
    // If stage is 'rejected', return decision stage index (4)
    if (currentStage === 'rejected') {
      return 4
    }
    
    // Map salary_slip stage to underwriting (index 3)
    if (currentStage === 'salary_slip') {
      return 3
    }
    
    const stageIndex = stages.indexOf(currentStage)
    
    // If rejected flag is set, ensure we don't go past decision
    if (isRejected) {
      return 4
    }
    
    console.log('getStageProgress - currentStage:', currentStage, 'stageIndex:', stageIndex)
    return stageIndex >= 0 ? stageIndex : 0
  }
  
  //reset
  const conversationEnded =
   messages.length > 0 &&
   messages[messages.length - 1].final === true
  
  if (!conversationStarted) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-4xl mx-auto"
      >
        {/* Welcome Hero Section */}
        <div className="text-center mb-8">
          <motion.div
            initial={{ scale: 0.5, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="w-24 h-24 bg-gradient-to-r from-primary-500 to-accent-500 rounded-full flex items-center justify-center mx-auto mb-6 shadow-2xl"
          >
            <Bot className="w-12 h-12 text-white" />
          </motion.div>

          <motion.h1
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.4 }}
            className="text-4xl md:text-5xl font-bold font-display mb-4"
          >
            Welcome to <span className="gradient-text">QuickLoan</span>
          </motion.h1>

          <motion.p
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.6 }}
            className="text-xl text-slate-600 mb-8 max-w-2xl mx-auto"
          >
            Your AI-powered loan assistant is here to help you get instant personal loans
            with competitive rates and minimal documentation.
          </motion.p>

          {/* Features Grid */}
          <motion.div
            initial={{ y: 30, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.8 }}
            className="grid md:grid-cols-3 gap-6 mb-10"
          >
            <div className="glass-effect p-6 rounded-2xl">
              <CheckCircle className="w-8 h-8 text-accent-500 mx-auto mb-3" />
              <h3 className="font-semibold mb-2">Instant Approval</h3>
              <p className="text-sm text-slate-600">Get loan decisions in minutes, not days</p>
            </div>

            <div className="glass-effect p-6 rounded-2xl">
              <FileText className="w-8 h-8 text-primary-500 mx-auto mb-3" />
              <h3 className="font-semibold mb-2">Minimal Docs</h3>
              <p className="text-sm text-slate-600">Simple paperwork, maximum convenience</p>
            </div>

            <div className="glass-effect p-6 rounded-2xl">
              <User className="w-8 h-8 text-accent-500 mx-auto mb-3" />
              <h3 className="font-semibold mb-2">Human-like AI</h3>
              <p className="text-sm text-slate-600">Natural conversation, personalized service</p>
            </div>
          </motion.div>

          <motion.button
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 1 }}
            onClick={startConversation}
            className="btn-primary text-lg px-8 py-4 inline-flex items-center space-x-2"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <MessageCircle className="w-5 h-5" />
            <span>Start Your Loan Journey</span>
          </motion.button>
        </div>
      </motion.div>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="w-full max-w-6xl mx-auto h-[80vh] flex flex-col relative"
    >
      {/* Progress Indicator */}
      <LoanProgress currentStage={getStageProgress()} isRejected={isRejected} />

      {/* Chat Container */}
      <div className="flex-1 flex bg-white/60 backdrop-blur-sm rounded-3xl shadow-xl border border-white/20 overflow-hidden">
        {/* Chat Messages */}
        <div className="flex-1 flex flex-col">
          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto p-6 space-y-4 scrollbar-hide">
            <AnimatePresence>
              {messages.map((message, index) => (
                <ChatMessage
                  key={message.id}
                  message={message}
                  index={index}
                  onOptionClick={handleOptionClick}
                />
              ))}

              {isLoading && !showFileUpload && <TypingIndicator />}
              
              {/* File Upload Area - Inline */}
              {showFileUpload && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  className="my-4"
                >
                  <FileUploader onUpload={handleFileUpload} />
                </motion.div>
              )}
            </AnimatePresence>
            <div ref={messagesEndRef} />
          </div>

         {/* Input Area or Reset */}
         <div className="p-6 border-t border-slate-200/50">
            {conversationEnded ? (
              <div className="flex justify-center">
                <motion.button
                   onClick={resetConversation}
                   className="btn-secondary px-6 py-3 flex items-center space-x-2"
                   whileHover={{ scale: 1.05 }}
                       whileTap={{ scale: 0.95 }}
                >
                   <span>🔁 Start New Loan</span>
                </motion.button>
             </div>
            ) : (
              <form onSubmit={handleSubmit} className="flex space-x-4">
                <input
                   ref={inputRef}
                   type="text"
                   value={inputValue}
                   onChange={(e) => setInputValue(e.target.value)}
                   placeholder="Type your message..."
                   className="input-field"
                   disabled={isLoading || showFileUpload}
                />

               <motion.button
                  type="submit"
                  disabled={isLoading || !inputValue.trim() || showFileUpload}
                  className="btn-primary px-4 py-3 disabled:opacity-50 disabled:cursor-not-allowed"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
              >
                 <Send className="w-5 h-5" />
              </motion.button>
           </form>
          )}
        </div>
        </div>
        {/* Loan Details Sidebar */}
        <AnimatePresence>
          {Object.keys(loanDetails).length > 0 && (
            <motion.div
              initial={{ width: 0, opacity: 0 }}
              animate={{ width: 300, opacity: 1 }}
              exit={{ width: 0, opacity: 0 }}
              className="border-l border-slate-200/50 p-6 bg-gradient-to-b from-accent-50 to-primary-50"
            >
              <h3 className="font-semibold text-lg mb-4 text-slate-800">Loan Summary</h3>
              
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-slate-600">Amount:</span>
                  <span className="font-semibold">{loanDetails.amount}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-600">EMI:</span>
                  <span className="font-semibold">{loanDetails.emi}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-600">Tenure:</span>
                  <span className="font-semibold">{loanDetails.tenure}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-600">Rate:</span>
                  <span className="font-semibold">{loanDetails.rate}</span>
                </div>
              </div>

              <button
                onClick={downloadSanctionLetter}
                className="btn-primary w-full mt-6 inline-flex items-center justify-center space-x-2"
              >
                <Download className="w-4 h-4" />
                <span>Download Letter</span>
              </button>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  )
}

export default LoanChatInterface