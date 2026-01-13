import React, { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Send, MessageCircle, User, Bot, Download, Upload, FileText, CheckCircle, XCircle, Sparkles, Star, Zap } from 'lucide-react'
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
      // Try multiple patterns for loan amount
      const amountMatch = message.match(/(?:Principal Amount|Principal|Loan Amount|Amount)\s*(?:\*\*)?:?\s*₹\s*([\d,]+)/i)
      const emiMatch = message.match(/(?:Monthly EMI|EMI)\s*(?:\*\*)?:?\s*₹\s*([\d,]+)/i)
      const tenureMatch = message.match(/(?:Loan Tenure|Tenure)\s*(?:\*\*)?:?\s*(\d+)\s*months?/i)
      const rateMatch = message.match(/(?:Interest Rate|Rate)\s*(?:\*\*)?:?\s*([\d.]+)\s*%/i)

      if (!amountMatch) return

      setLoanDetails({
        amount: `₹${amountMatch[1]}`,
        emi: emiMatch ? `₹${emiMatch[1]}` : '—',
        tenure: tenureMatch ? `${tenureMatch[1]} months` : '—',
        rate: rateMatch ? `${rateMatch[1]}%` : '—'
      })
      
      console.log('Extracted loan details:', {
        amount: amountMatch ? amountMatch[1] : 'not found',
        emi: emiMatch ? emiMatch[1] : 'not found',
        tenure: tenureMatch ? tenureMatch[1] : 'not found',
        rate: rateMatch ? rateMatch[1] : 'not found'
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
      <div className="w-full max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
        {/* Left: Bank-style hero (blue) */}
        <motion.div
            initial={{ opacity: 0, x: -30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8 }}
            className="min-h-[70vh] p-10 rounded-3xl bg-[#0b4f82] text-white shadow-xl overflow-hidden relative"
          >
          {/* subtle decorative orbs */}
          <div className="absolute inset-0 mix-blend-overlay opacity-20 pointer-events-none">
            <div className="absolute -left-16 top-8 w-72 h-72 rounded-full blur-3xl" style={{ background: 'var(--brand-blue)' }} />
            <div className="absolute -right-16 bottom-8 w-72 h-72 rounded-full blur-3xl" style={{ background: 'var(--brand-blue-dark)' }} />
          </div>

          <div className="relative z-10 max-w-xl">
            <h2 className="text-4xl md:text-5xl font-extrabold mb-4">Easy and Simple way to apply for a Loan</h2>
            <p className="text-lg text-sky-100/90 mb-8">Paperless • Fast • Secure. Get personalised offers and instant decisions using our AI-powered assistant.</p>

            <ul className="space-y-3 mb-8">
              <li className="flex items-start gap-3">
                <span className="inline-block w-10 h-10 rounded-lg bg-white/10 flex items-center justify-center">💡</span>
                <div>
                  <div className="font-semibold">Instant Approvals</div>
                  <div className="text-sm text-sky-100/80">Most customers approved within minutes</div>
                </div>
              </li>
              <li className="flex items-start gap-3">
                <span className="inline-block w-10 h-10 rounded-lg bg-white/10 flex items-center justify-center">🔒</span>
                <div>
                  <div className="font-semibold">Bank-grade Security</div>
                  <div className="text-sm text-sky-100/80">Your data stays safe and private</div>
                </div>
              </li>
            </ul>

            <div className="mt-6">
              <button
                onClick={startConversation}
                className="px-8 py-4 bg-white text-[#0b4f82] rounded-lg font-bold shadow-lg hover:shadow-2xl transition"
              >
                Start Application
              </button>
            </div>
          </div>
        </motion.div>

        {/* Right: White card (bank login style) containing a compact chat card */}
        <motion.div
          initial={{ opacity: 0, x: 30 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.8 }}
          className="min-h-[70vh] flex items-center justify-center"
        >
          <div className="w-full max-w-md bg-white rounded-3xl shadow-2xl p-8 text-slate-900 border border-slate-200">
            <div className="text-center mb-4">
              <h3 className="text-2xl font-bold">QuickLoan</h3>
              <p className="text-sm text-slate-500">AI Loan Assistant — Secure & Fast</p>
            </div>

            <div className="mt-4">
              <p className="text-sm text-slate-600 mb-4">Start a secure chat with our assistant to apply for a loan. You can upload documents when prompted.</p>

              <button
                onClick={startConversation}
                className="w-full py-3 bg-[#0b4f82] text-white rounded-lg font-semibold shadow"
              >
                Start Chat
              </button>
            </div>

            <div className="mt-6 border-t pt-4 text-xs text-slate-500">
              <div className="flex items-center justify-between">
                <span>Need help?</span>
                <a className="text-blue-700 font-semibold" href="#">Contact Support</a>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="w-full max-w-5xl mx-auto h-[90vh] flex flex-col relative"
    >
      {/* Progress Indicator with stunning design */}
      <motion.div
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.2 }}
      >
        <LoanProgress currentStage={getStageProgress()} isRejected={isRejected} />
      </motion.div>

      {/* Chat Container with glass morphism */}
      <motion.div
        initial={{ scale: 0.95, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ delay: 0.3, duration: 0.5 }}
        className="flex-1 flex backdrop-blur-2xl bg-white/10 rounded-3xl shadow-2xl border border-white/20 overflow-hidden relative"
      >
        {/* Animated gradient border */}
        <div className="absolute inset-0 animate-gradient-x pointer-events-none" style={{ background: 'linear-gradient(90deg, rgba(11,79,130,0.08), rgba(200,16,46,0.06))' }} />
        
        {/* Chat Messages */}
        <div className="flex-1 flex flex-col relative z-10">
          {/* Messages Area with custom scrollbar */}
          <div className="flex-1 overflow-y-auto p-10 space-y-6 custom-scrollbar">
            <AnimatePresence mode="popLayout">
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
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.9 }}
                  className="my-4"
                >
                  <FileUploader onUpload={handleFileUpload} />
                </motion.div>
              )}
            </AnimatePresence>
            <div ref={messagesEndRef} />
          </div>

         {/* Input Area with glassmorphism */}
         <div className="p-8 border-t border-white/10 backdrop-blur-xl bg-white/5">
            {conversationEnded ? (
              <div className="flex justify-center">
                <motion.button
                   onClick={resetConversation}
                   className="relative group px-8 py-4 text-lg font-bold text-white rounded-2xl overflow-hidden shadow-xl"
                   whileHover={{ scale: 1.05 }}
                   whileTap={{ scale: 0.95 }}
                >
                  {/* Animated background */}
                  {/* Animated background */}
                  <motion.div
                    className="absolute inset-0"
                    style={{ background: 'linear-gradient(90deg, var(--brand-blue), var(--brand-red))', backgroundSize: '200% 200%' }}
                    animate={{
                      backgroundPosition: ['0% 50%', '100% 50%', '0% 50%']
                    }}
                    transition={{ duration: 3, repeat: Infinity }}
                  />
                  <span className="relative z-10 flex items-center space-x-2">
                    <span>🔁</span>
                    <span>Start New Application</span>
                  </span>
                </motion.button>
             </div>
            ) : (
              <form onSubmit={handleSubmit} className="flex space-x-4">
                <div className="flex-1 relative">
                  <input
                     ref={inputRef}
                     type="text"
                     value={inputValue}
                     onChange={(e) => setInputValue(e.target.value)}
                     placeholder="Type your message..."
                     className="w-full px-6 py-5 bg-[#f8fafc] border border-slate-200 rounded-2xl text-slate-900 text-lg placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-brand-blue focus:border-transparent transition-all duration-300 font-medium"
                     disabled={isLoading || showFileUpload}
                  />
                  {/* Input glow effect */}
                  <div className="absolute inset-0 rounded-2xl blur-xl opacity-0 group-focus-within:opacity-100 transition-opacity pointer-events-none" style={{ background: 'linear-gradient(90deg, rgba(11,79,130,0.08), rgba(200,16,46,0.06))' }} />
                </div>

              <motion.button
                type="submit"
                disabled={isLoading || !inputValue.trim() || showFileUpload}
                className="relative group px-8 py-5 rounded-2xl disabled:opacity-50 disabled:cursor-not-allowed shadow-lg overflow-hidden"
                style={{ background: 'linear-gradient(90deg, var(--brand-blue), var(--brand-red))', color: 'white' }}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
              >
                <motion.div
                  className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity"
                  style={{ background: 'linear-gradient(90deg, rgba(11,79,130,0.06), rgba(200,16,46,0.04))', backgroundSize: '200% 200%' }}
                  animate={{ backgroundPosition: ['0% 50%', '100% 50%', '0% 50%'] }}
                  transition={{ duration: 2, repeat: Infinity }}
                />
                 <Send className="w-6 h-6 text-white relative z-10" />
              </motion.button>
           </form>
          )}
        </div>
        </div>

        {/* Loan Details Sidebar with stunning design */}
        <AnimatePresence>
          {Object.keys(loanDetails).length > 0 && (
            <motion.div
              initial={{ width: 0, opacity: 0, x: 20 }}
              animate={{ width: 350, opacity: 1, x: 0 }}
              exit={{ width: 0, opacity: 0, x: 20 }}
              transition={{ type: "spring", stiffness: 100 }}
              className="relative border-l border-white/10 backdrop-blur-xl overflow-hidden"
              style={{ background: 'linear-gradient(180deg, rgba(11,79,130,0.04), rgba(200,16,46,0.02))' }}
            >
              {/* Animated background */}
              <div className="absolute inset-0" style={{ background: 'linear-gradient(135deg, rgba(11,79,130,0.04), transparent, rgba(200,16,46,0.03))' }} />
              
              <div className="p-6 relative z-10 flex flex-col h-full">
                <motion.h3
                  initial={{ y: -10, opacity: 0 }}
                  animate={{ y: 0, opacity: 1 }}
                  className="text-xl font-bold gradient-text mb-4"
                >
                  Loan Summary
                </motion.h3>
                
                <div className="space-y-3 mb-6 flex-1">
                  {[
                    { label: 'Principal', value: loanDetails.amount, icon: '💰', color: 'from-brand-blue to-brand-red' },
                    { label: 'Monthly EMI', value: loanDetails.emi, icon: '📅', color: 'from-brand-blue to-brand-red' },
                    { label: 'Tenure', value: loanDetails.tenure, icon: '⏱️', color: 'from-brand-blue to-brand-red' },
                    { label: 'Interest Rate', value: loanDetails.rate, icon: '📈', color: 'from-brand-blue to-brand-red' }
                  ].map((item, idx) => (
                    <motion.div
                      key={idx}
                      initial={{ x: 20, opacity: 0 }}
                      animate={{ x: 0, opacity: 1 }}
                      transition={{ delay: idx * 0.1 }}
                      className="relative group"
                    >
                      <div className="flex items-center justify-between p-3 rounded-xl bg-white/10 backdrop-blur-sm border border-white/20 hover:bg-white/20 transition-all duration-300">
                        <div className="flex items-center space-x-2">
                          <motion.div
                            className={`w-8 h-8 rounded-lg bg-gradient-to-br ${item.color} flex items-center justify-center shadow-lg`}
                            whileHover={{ rotate: 360, scale: 1.1 }}
                            transition={{ duration: 0.5 }}
                          >
                            <span className="text-base">{item.icon}</span>
                          </motion.div>
                          <span className="text-xs font-medium text-white/70">{item.label}</span>
                        </div>
                        <span className="text-base font-bold text-white">{item.value}</span>
                      </div>
                    </motion.div>
                  ))}
                </div>

                <motion.button
                  onClick={downloadSanctionLetter}
                  className="relative w-full group py-3 text-white font-bold rounded-xl overflow-hidden shadow-2xl mt-auto"
                  whileHover={{ scale: 1.02, y: -2 }}
                  whileTap={{ scale: 0.98 }}
                  initial={{ y: 20, opacity: 0 }}
                  animate={{ y: 0, opacity: 1 }}
                  transition={{ delay: 0.4 }}
                >
                  {/* Animated gradient background */}
                  <motion.div
                    className="absolute inset-0"
                    style={{ background: 'linear-gradient(90deg, var(--brand-blue), var(--brand-red))', backgroundSize: '200% 200%' }}
                    animate={{
                      backgroundPosition: ['0% 50%', '100% 50%', '0% 50%']
                    }}
                    transition={{ duration: 3, repeat: Infinity }}
                  />
                  
                  <div className="relative z-10 flex items-center justify-center space-x-3">
                    <Download className="w-5 h-5" />
                    <span>Download Sanction Letter</span>
                  </div>

                  {/* Shine effect */}
                  <motion.div
                    className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent"
                    animate={{ x: ['-200%', '200%'] }}
                    transition={{ duration: 2, repeat: Infinity, repeatDelay: 1 }}
                  />
                </motion.button>

                {/* Celebration confetti effect */}
                <div className="absolute inset-0 pointer-events-none">
                  {[...Array(15)].map((_, i) => (
                    <motion.div
                      key={i}
                      className="absolute w-2 h-2 rounded-full"
                      style={{
                        left: `${Math.random() * 100}%`,
                        top: `${Math.random() * 100}%`,
                        background: ['#0b4f82', '#c8102e', '#93c5fd', '#fbbf24'][Math.floor(Math.random() * 4)]
                      }}
                      animate={{
                        y: [0, -100],
                        opacity: [1, 0],
                        scale: [1, 0],
                      }}
                      transition={{
                        duration: 2,
                        repeat: Infinity,
                        delay: Math.random() * 2,
                      }}
                    />
                  ))}
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </motion.div>
  )
}

export default LoanChatInterface