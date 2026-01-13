import React from 'react'
import { motion } from 'framer-motion'
import { User, Bot, CheckCircle, XCircle, Sparkles } from 'lucide-react'

const ChatMessage = ({ message, index, onOptionClick }) => {
  const isUser = message.sender === 'user'
  const isError = message.isError

  // Function to highlight important parts of the message
  const formatMessage = (text) => {
    if (isUser) return text

    // Highlight loan approval
    if (text.includes('LOAN APPROVED') || text.includes('CONGRATULATIONS')) {
      return text.split('\n').map((line, i) => {
        if (line.includes('LOAN APPROVED') || line.includes('CONGRATULATIONS')) {
          return (
            <div key={i} className="text-2xl font-black text-green-300 mb-3 animate-pulse bg-green-500/20 px-4 py-3 rounded-xl border-2 border-green-400">
              {line}
            </div>
          )
        }
        return <div key={i}>{line}</div>
      })
    }

    // Highlight loan rejection
    if (text.includes('cannot approve') || text.includes('Unfortunately')) {
      return text.split('\n').map((line, i) => {
        if (line.includes('cannot approve') || line.includes('Unfortunately')) {
          return (
            <div key={i} className="text-xl font-bold text-red-300 mb-3 bg-red-500/20 px-4 py-3 rounded-xl border-2 border-red-400">
              {line}
            </div>
          )
        }
        return <div key={i}>{line}</div>
      })
    }

    // Highlight salary slip request
    if (text.includes('salary slip') || text.includes('verify your current salary')) {
      return text.split('\n').map((line, i) => {
          if (line.includes('salary slip') || line.includes('verify your current salary')) {
          return (
            <div key={i} className="text-lg font-bold mb-2 px-3 py-2 rounded-lg" style={{ background: 'rgba(11,79,130,0.06)', borderLeft: '4px solid rgba(11,79,130,0.18)', color: 'var(--brand-blue)' }}>
              {line}
            </div>
          )
        }
        return <div key={i}>{line}</div>
      })
    }

    return text
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1 }}
      className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}
    >
      <div className={`flex items-start space-x-3 max-w-[65%] ${isUser ? 'flex-row-reverse space-x-reverse' : ''}`}>
        {/* Avatar with glow effect */}
        <motion.div
          initial={{ scale: 0, rotate: -180 }}
          animate={{ scale: 1, rotate: 0 }}
          transition={{ delay: index * 0.1 + 0.2, type: "spring", stiffness: 200 }}
          className="relative"
        >
          <motion.div
            className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 shadow-2xl ${
              isUser 
                ? '' 
                : isError 
                  ? '' 
                  : ''
            }`}
            style={{ background: isError ? 'linear-gradient(90deg, #c8102e, #ff6b6b)' : 'linear-gradient(90deg, var(--brand-blue), var(--brand-red))' }}
            animate={{
              boxShadow: isUser
                ? ['0 0 20px rgba(11,79,130,0.25)', '0 0 30px rgba(200,16,46,0.22)', '0 0 20px rgba(11,79,130,0.25)']
                : ['0 0 20px rgba(11,79,130,0.2)', '0 0 30px rgba(11,79,130,0.3)', '0 0 20px rgba(11,79,130,0.2)']
            }}
            transition={{ duration: 2, repeat: Infinity }}
          >
            {isUser ? (
              <User className="w-5 h-5 text-white" strokeWidth={2.5} />
            ) : isError ? (
              <XCircle className="w-5 h-5 text-white" strokeWidth={2.5} />
            ) : (
              <Bot className="w-5 h-5 text-white" strokeWidth={2.5} />
            )}
          </motion.div>
        </motion.div>

        {/* Message Bubble with glassmorphism */}
          <motion.div
          initial={{ scale: 0.8, opacity: 0, x: isUser ? 20 : -20 }}
          animate={{ scale: 1, opacity: 1, x: 0 }}
          transition={{ delay: index * 0.1 + 0.3, type: "spring", stiffness: 100 }}
          className={`relative px-5 py-4 rounded-2xl shadow-2xl backdrop-blur-xl ${
            isUser 
              ? '' 
              : isError 
                ? 'bg-red-500/20 border border-red-400/50 text-red-100 rounded-bl-md backdrop-blur-xl'
                : 'bg-white/95 border border-white/20 text-slate-900 rounded-bl-md'
          }`}
          style={isUser ? { background: 'linear-gradient(90deg, var(--brand-blue), var(--brand-red))', color: 'white', borderColor: 'rgba(255,255,255,0.12)' } : {}}
        >
          {/* Message Text */}
          <div className={`whitespace-pre-wrap text-base leading-relaxed ${isUser ? 'text-white' : ''}`}>
            {formatMessage(message.text)}
          </div>

          {/* Options */}
          {message.options && message.options.length > 0 && (
            <div className="mt-4 space-y-3">
              {message.options.map((option, idx) => (
                <motion.button
                  key={idx}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.5 + idx * 0.1 }}
                  whileHover={{ scale: 1.02, x: 5 }}
                  whileTap={{ scale: 0.98 }}
                  className="relative group block w-full text-left px-5 py-4 rounded-xl text-base font-semibold transition-all duration-300 border-2 border-white/30 hover:border-white/60 hover:shadow-xl backdrop-blur-xl cursor-pointer overflow-hidden"
                  onClick={() => {
                    if (onOptionClick) {
                      onOptionClick(option)
                    }
                  }}
                >
                  {/* Hover glow effect */}
                  <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300" style={{ background: 'linear-gradient(90deg, rgba(11,79,130,0), rgba(11,79,130,0.12), rgba(200,16,46,0))' }} />
                  
                  <span className="relative z-10 flex items-center justify-between">
                    <span>{option}</span>
                    <motion.span
                      className="opacity-0 group-hover:opacity-100"
                      animate={{ x: [0, 5, 0] }}
                      transition={{ duration: 1, repeat: Infinity }}
                    >
                      →
                    </motion.span>
                  </span>
                </motion.button>
              ))}
            </div>
          )}

          {/* Success Indicator for Approved Messages */}
          {message.final === true &&message.stage === 'completed' &&message.text.startsWith('🎉') && !isUser && (
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