import React from 'react'
import { motion } from 'framer-motion'
import { User, Bot, CheckCircle, XCircle } from 'lucide-react'

const ChatMessage = ({ message, index }) => {
  const isUser = message.sender === 'user'
  const isError = message.isError

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1 }}
      className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}
    >
      <div className={`flex items-start space-x-3 max-w-[80%] ${isUser ? 'flex-row-reverse space-x-reverse' : ''}`}>
        {/* Avatar */}
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: index * 0.1 + 0.2 }}
          className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 shadow-md ${
            isUser 
              ? 'bg-gradient-to-r from-primary-500 to-primary-600' 
              : isError 
                ? 'bg-red-500' 
                : 'bg-gradient-to-r from-accent-500 to-accent-600'
          }`}
        >
          {isUser ? (
            <User className="w-5 h-5 text-white" />
          ) : isError ? (
            <XCircle className="w-5 h-5 text-white" />
          ) : (
            <Bot className="w-5 h-5 text-white" />
          )}
        </motion.div>

        {/* Message Bubble */}
        <motion.div
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ delay: index * 0.1 + 0.3 }}
          className={`relative px-4 py-3 rounded-2xl shadow-sm ${
            isUser 
              ? 'bg-gradient-to-r from-primary-500 to-primary-600 text-white rounded-br-md' 
              : isError 
                ? 'bg-red-50 border border-red-200 text-red-800 rounded-bl-md'
                : 'bg-white border border-slate-200 text-slate-800 rounded-bl-md'
          }`}
        >
          {/* Message Text */}
          <div className={`whitespace-pre-wrap text-sm leading-relaxed ${isUser ? 'text-white' : ''}`}>
            {message.text}
          </div>

          {/* Options */}
          {message.options && message.options.length > 0 && (
            <div className="mt-3 space-y-2">
              {message.options.map((option, idx) => (
                <motion.button
                  key={idx}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.5 + idx * 0.1 }}
                  className="block w-full text-left px-3 py-2 bg-slate-50 hover:bg-slate-100 rounded-lg text-sm transition-colors border border-slate-200"
                  onClick={() => {
                    // Handle option selection
                    const event = new CustomEvent('optionSelected', { detail: option })
                    window.dispatchEvent(event)
                  }}
                >
                  {option}
                </motion.button>
              ))}
            </div>
          )}

          {/* Success Indicator for Approved Messages */}
          {message.text.toLowerCase().includes('approved') && !isUser && (
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.5 }}
              className="flex items-center space-x-2 mt-3 p-2 bg-green-50 rounded-lg border border-green-200"
            >
              <CheckCircle className="w-4 h-4 text-green-600" />
              <span className="text-green-800 text-xs font-medium">Loan Approved!</span>
            </motion.div>
          )}

          {/* Timestamp */}
          <div className={`text-xs mt-2 opacity-70 ${isUser ? 'text-primary-100' : 'text-slate-500'}`}>
            {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </div>

          {/* Message tail */}
          <div
            className={`absolute bottom-0 ${
              isUser 
                ? 'right-0 transform translate-x-1 translate-y-1' 
                : 'left-0 transform -translate-x-1 translate-y-1'
            }`}
          >
            <div
              className={`w-0 h-0 ${
                isUser
                  ? 'border-l-8 border-l-primary-600 border-t-8 border-t-transparent'
                  : isError
                    ? 'border-r-8 border-r-red-50 border-t-8 border-t-transparent'
                    : 'border-r-8 border-r-white border-t-8 border-t-transparent'
              }`}
            />
          </div>
        </motion.div>
      </div>
    </motion.div>
  )
}

export default ChatMessage