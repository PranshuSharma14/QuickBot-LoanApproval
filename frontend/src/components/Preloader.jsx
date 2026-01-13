import React, { useEffect } from 'react'
import { motion } from 'framer-motion'

const Preloader = ({ onFinish }) => {
  useEffect(() => {
    const t = setTimeout(() => onFinish && onFinish(), 700)
    return () => clearTimeout(t)
  }, [onFinish])

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-gradient-to-br from-blue-900 via-blue-800 to-sky-800 text-white">
      <motion.div
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.6 }}
        className="flex items-center space-x-4"
      >
        <div className="w-16 h-16 rounded-xl bg-white/10 flex items-center justify-center shadow-lg">
          <svg width="36" height="36" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M3 12h18" stroke="#fff" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
            <path d="M3 6h18" stroke="#fff" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" opacity="0.6" />
            <path d="M3 18h18" stroke="#fff" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" opacity="0.4" />
          </svg>
        </div>
        <div>
          <div className="text-2xl font-bold">QuickLoan</div>
          <div className="text-sm text-white/80">Preparing your secure session...</div>
        </div>
      </motion.div>
    </div>
  )
}

export default Preloader
