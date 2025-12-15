import React from 'react'
import { motion } from 'framer-motion'
import { Bot } from 'lucide-react'

const TypingIndicator = () => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="flex justify-start"
    >
      <div className="flex items-start space-x-3 max-w-[80%]">
        {/* Avatar */}
        <div className="w-10 h-10 bg-gradient-to-r from-accent-500 to-accent-600 rounded-full flex items-center justify-center flex-shrink-0 shadow-md">
          <Bot className="w-5 h-5 text-white" />
        </div>

        {/* Typing Bubble */}
        <div className="bg-white border border-slate-200 px-4 py-3 rounded-2xl rounded-bl-md shadow-sm">
          <div className="flex items-center space-x-1">
            <motion.div
              animate={{ scale: [1, 1.2, 1] }}
              transition={{ duration: 0.8, repeat: Infinity, delay: 0 }}
              className="w-2 h-2 bg-slate-400 rounded-full"
            />
            <motion.div
              animate={{ scale: [1, 1.2, 1] }}
              transition={{ duration: 0.8, repeat: Infinity, delay: 0.2 }}
              className="w-2 h-2 bg-slate-400 rounded-full"
            />
            <motion.div
              animate={{ scale: [1, 1.2, 1] }}
              transition={{ duration: 0.8, repeat: Infinity, delay: 0.4 }}
              className="w-2 h-2 bg-slate-400 rounded-full"
            />
          </div>
        </div>
      </div>
    </motion.div>
  )
}

export default TypingIndicator