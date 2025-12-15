import React from 'react'
import { motion } from 'framer-motion'
import { Banknote, Shield, Zap } from 'lucide-react'

const Header = () => {
  return (
    <motion.header 
      initial={{ y: -50, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.6 }}
      className="glass-effect shadow-lg border-b border-white/20"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <motion.div 
            className="flex items-center space-x-2"
            whileHover={{ scale: 1.05 }}
            transition={{ type: "spring", stiffness: 300 }}
          >
            <div className="w-10 h-10 bg-gradient-to-r from-primary-500 to-accent-500 rounded-xl flex items-center justify-center shadow-lg">
              <Banknote className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold font-display gradient-text">QuickLoan</h1>
              <p className="text-xs text-slate-600">AI Loan Assistant</p>
            </div>
          </motion.div>

          {/* Features */}
          <div className="hidden md:flex items-center space-x-6">
            <motion.div 
              className="flex items-center space-x-2 text-slate-600"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.2 }}
            >
              <Zap className="w-4 h-4 text-accent-500" />
              <span className="text-sm font-medium">Instant Approval</span>
            </motion.div>
            
            <motion.div 
              className="flex items-center space-x-2 text-slate-600"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.3 }}
            >
              <Shield className="w-4 h-4 text-primary-500" />
              <span className="text-sm font-medium">Secure & Safe</span>
            </motion.div>
          </div>
        </div>
      </div>
    </motion.header>
  )
}

export default Header