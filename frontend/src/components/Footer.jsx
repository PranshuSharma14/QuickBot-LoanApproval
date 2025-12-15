import React from 'react'
import { motion } from 'framer-motion'

const Footer = () => {
  return (
    <motion.footer 
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ delay: 1 }}
      className="glass-effect border-t border-white/20 py-6 mt-8"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col md:flex-row items-center justify-between space-y-4 md:space-y-0">
          <div className="text-center md:text-left">
            <p className="text-sm text-slate-600">
              © 2025 QuickLoan Financial Services Pvt. Ltd. All rights reserved.
            </p>
            <p className="text-xs text-slate-500 mt-1">
              NBFC License: 14.03.167 | Regulated by RBI
            </p>
          </div>
          
          <div className="flex items-center space-x-6 text-xs text-slate-500">
            <span>Privacy Policy</span>
            <span>Terms & Conditions</span>
            <span>Contact Us</span>
          </div>
        </div>
        
        <div className="mt-4 pt-4 border-t border-slate-200/50">
          <p className="text-xs text-slate-400 text-center">
            🤖 This is a demonstration of Agentic AI technology for educational purposes only. No real loans are processed.
          </p>
        </div>
      </div>
    </motion.footer>
  )
}

export default Footer