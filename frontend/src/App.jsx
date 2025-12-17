import React from 'react'
import { Toaster } from 'react-hot-toast'
import { motion } from 'framer-motion'
import LoanChatInterface from './components/LoanChatInterface'
import Header from './components/Header'
import Footer from './components/Footer'
import AnimatedBackground from './components/AnimatedBackground'

function App() {
  return (
    <div className="min-h-screen flex flex-col relative overflow-hidden">
      {/* Animated Three.js Background */}
      <AnimatedBackground />
      
      {/* Toast Notifications with custom style */}
      <Toaster 
        position="top-center"
        toastOptions={{
          duration: 4000,
          style: {
            background: 'rgba(30, 30, 46, 0.95)',
            color: '#fff',
            backdropFilter: 'blur(10px)',
            border: '1px solid rgba(139, 92, 246, 0.3)',
            boxShadow: '0 10px 40px rgba(0, 0, 0, 0.3)',
            borderRadius: '16px',
            fontSize: '15px',
            fontWeight: '500',
          },
          success: {
            iconTheme: {
              primary: '#10b981',
              secondary: '#fff',
            },
          },
          error: {
            iconTheme: {
              primary: '#ef4444',
              secondary: '#fff',
            },
          },
        }}
      />
      
      {/* Animated Header */}
      <motion.div
        initial={{ y: -100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.8, ease: "easeOut" }}
      >
        <Header />
      </motion.div>
      
      {/* Main Content with smooth entrance */}
      <main className="flex-1 flex items-center justify-center p-4 md:p-8 relative z-10">
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.2, ease: "easeOut" }}
          className="w-full max-w-7xl"
        >
          <LoanChatInterface />
        </motion.div>
      </main>
      
      {/* Animated Footer */}
      <motion.div
        initial={{ y: 100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.8, delay: 0.4, ease: "easeOut" }}
      >
        <Footer />
      </motion.div>
    </div>
  )
}

export default App