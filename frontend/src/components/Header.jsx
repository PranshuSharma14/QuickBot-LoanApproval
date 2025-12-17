import React, { useState, useEffect } from 'react'
import { motion, useScroll, useTransform } from 'framer-motion'
import { Banknote, Shield, Zap, Sparkles, TrendingUp, Award, Clock } from 'lucide-react'

const Header = () => {
  const [time, setTime] = useState(new Date())
  const { scrollY } = useScroll()
  const headerOpacity = useTransform(scrollY, [0, 100], [1, 0.95])
  const headerBlur = useTransform(scrollY, [0, 100], [10, 20])

  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000)
    return () => clearInterval(timer)
  }, [])

  const features = [
    { icon: Zap, text: 'Instant Approval', color: 'from-yellow-400 to-orange-500', delay: 0.2 },
    { icon: Shield, text: 'Bank-Grade Security', color: 'from-green-400 to-emerald-500', delay: 0.3 },
    { icon: TrendingUp, text: 'Best Rates', color: 'from-blue-400 to-cyan-500', delay: 0.4 },
  ]

  return (
    <motion.header 
      style={{ 
        opacity: headerOpacity,
        backdropFilter: `blur(${headerBlur}px)`,
      }}
      className="relative backdrop-blur-xl bg-white/5 shadow-2xl border-b border-white/10"
    >
      {/* Animated gradient border */}
      <div className="absolute inset-0 bg-gradient-to-r from-purple-500/20 via-cyan-500/20 to-purple-500/20 animate-gradient-x" />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 relative z-10">
        <div className="flex items-center justify-between">
          {/* Logo with enhanced animation */}
          <motion.div 
            className="flex items-center space-x-3"
            initial={{ x: -50, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ duration: 0.8, ease: "easeOut" }}
            whileHover={{ scale: 1.05 }}
          >
            <motion.div 
              className="relative w-12 h-12 bg-gradient-to-br from-purple-500 via-indigo-500 to-cyan-500 rounded-2xl flex items-center justify-center shadow-2xl"
              animate={{ 
                boxShadow: [
                  '0 0 20px rgba(168, 85, 247, 0.4)',
                  '0 0 40px rgba(168, 85, 247, 0.6)',
                  '0 0 20px rgba(168, 85, 247, 0.4)',
                ],
                rotate: [0, 5, -5, 0]
              }}
              transition={{ 
                boxShadow: { duration: 2, repeat: Infinity },
                rotate: { duration: 4, repeat: Infinity }
              }}
            >
              <Banknote className="w-7 h-7 text-white" strokeWidth={2.5} />
              <motion.div
                className="absolute inset-0 bg-gradient-to-br from-white/30 to-transparent rounded-2xl"
                animate={{ opacity: [0.3, 0.6, 0.3] }}
                transition={{ duration: 2, repeat: Infinity }}
              />
            </motion.div>
            
            <div>
              <motion.h1 
                className="text-3xl font-extrabold bg-gradient-to-r from-purple-400 via-pink-400 to-cyan-400 bg-clip-text text-transparent"
                animate={{ 
                  backgroundPosition: ['0% 50%', '100% 50%', '0% 50%']
                }}
                transition={{ duration: 5, repeat: Infinity }}
                style={{ backgroundSize: '200% 200%' }}
              >
                QuickLoan AI
              </motion.h1>
              <motion.div 
                className="flex items-center space-x-1 text-xs text-cyan-300/90"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.5 }}
              >
                <Sparkles className="w-3 h-3" />
                <span className="font-semibold">Powered by Advanced AI</span>
              </motion.div>
            </div>
          </motion.div>

          {/* Features with enhanced design */}
          <div className="hidden lg:flex items-center space-x-6">
            {features.map(({ icon: Icon, text, color, delay }, index) => (
              <motion.div
                key={index}
                className="group relative"
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay, duration: 0.6 }}
                whileHover={{ scale: 1.1, y: -2 }}
              >
                <div className="flex items-center space-x-2 px-4 py-2 rounded-xl bg-white/5 backdrop-blur-sm border border-white/10 shadow-lg group-hover:shadow-2xl transition-all duration-300">
                  <motion.div
                    className={`w-8 h-8 rounded-lg bg-gradient-to-br ${color} flex items-center justify-center shadow-lg`}
                    whileHover={{ rotate: 360 }}
                    transition={{ duration: 0.6 }}
                  >
                    <Icon className="w-4 h-4 text-white" strokeWidth={2.5} />
                  </motion.div>
                  <span className="text-sm font-bold text-white/90 whitespace-nowrap">{text}</span>
                </div>
                
                {/* Hover glow effect */}
                <motion.div
                  className={`absolute inset-0 bg-gradient-to-r ${color} rounded-xl opacity-0 group-hover:opacity-20 blur-xl transition-opacity duration-300`}
                />
              </motion.div>
            ))}
          </div>

          {/* Time and status indicator */}
          <motion.div 
            className="hidden md:flex items-center space-x-4"
            initial={{ x: 50, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ duration: 0.8, delay: 0.3 }}
          >
            <div className="flex items-center space-x-2 px-4 py-2 rounded-xl bg-gradient-to-r from-green-500/20 to-emerald-500/20 border border-green-400/30 backdrop-blur-sm">
              <motion.div
                className="w-2 h-2 rounded-full bg-green-400"
                animate={{ 
                  scale: [1, 1.2, 1],
                  opacity: [1, 0.7, 1]
                }}
                transition={{ duration: 2, repeat: Infinity }}
              />
              <span className="text-xs font-bold text-green-300">System Online</span>
            </div>
            
            <div className="flex items-center space-x-2 px-4 py-2 rounded-xl bg-white/5 backdrop-blur-sm border border-white/10">
              <Clock className="w-4 h-4 text-cyan-400" />
              <span className="text-xs font-mono font-bold text-white/90">
                {time.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}
              </span>
            </div>
          </motion.div>
        </div>

        {/* Stats bar */}
        <motion.div 
          className="mt-4 flex items-center justify-center space-x-8 text-xs"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6, duration: 0.6 }}
        >
          {[
            { label: 'Loans Approved', value: '50,000+', icon: Award },
            { label: 'Happy Customers', value: '45,000+', icon: Sparkles },
            { label: 'Avg. Approval Time', value: '< 5 min', icon: Zap },
          ].map((stat, idx) => (
            <motion.div
              key={idx}
              className="flex items-center space-x-2 text-white/70"
              whileHover={{ scale: 1.05, color: 'rgba(255, 255, 255, 0.9)' }}
            >
              <stat.icon className="w-3 h-3 text-purple-400" />
              <span className="font-bold">{stat.value}</span>
              <span className="text-white/50">{stat.label}</span>
            </motion.div>
          ))}
        </motion.div>
      </div>

      {/* Bottom glow effect */}
      <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-purple-500 to-transparent opacity-50" />
    </motion.header>
  )
}

export default Header