import React from 'react'
import { motion } from 'framer-motion'
import { Bot } from 'lucide-react'

const TypingIndicator = () => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20, scale: 0.9 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: -20, scale: 0.9 }}
      className="flex justify-start"
    >
      <div className="flex items-start space-x-3 max-w-[80%]">
        {/* Avatar with pulsing glow */}
        <motion.div
          className="relative w-12 h-12"
          animate={{
            boxShadow: [
              '0 0 20px rgba(99, 102, 241, 0.4)',
              '0 0 40px rgba(99, 102, 241, 0.6)',
              '0 0 20px rgba(99, 102, 241, 0.4)'
            ]
          }}
          transition={{ duration: 2, repeat: Infinity }}
        >
          <div className="w-12 h-12 bg-gradient-to-br from-indigo-500 to-purple-500 rounded-2xl flex items-center justify-center shadow-2xl">
            <Bot className="w-6 h-6 text-white" strokeWidth={2.5} />
          </div>
        </motion.div>

        {/* Typing Bubble with glassmorphism */}
        <motion.div
          className="bg-white/10 backdrop-blur-xl border border-white/20 px-6 py-4 rounded-2xl rounded-bl-md shadow-2xl"
          animate={{
            boxShadow: [
              '0 4px 20px rgba(0, 0, 0, 0.1)',
              '0 8px 30px rgba(0, 0, 0, 0.15)',
              '0 4px 20px rgba(0, 0, 0, 0.1)'
            ]
          }}
          transition={{ duration: 1.5, repeat: Infinity }}
        >
          <div className="flex items-center space-x-2">
            {[0, 1, 2].map((index) => (
              <motion.div
                key={index}
                animate={{
                  scale: [1, 1.5, 1],
                  opacity: [0.4, 1, 0.4]
                }}
                transition={{
                  duration: 1,
                  repeat: Infinity,
                  delay: index * 0.2
                }}
                className="w-2.5 h-2.5 bg-gradient-to-r from-purple-400 to-cyan-400 rounded-full"
              />
            ))}
          </div>
        </motion.div>
      </div>
    </motion.div>
  )
}

export default TypingIndicator