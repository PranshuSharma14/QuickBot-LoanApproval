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
    { icon: TrendingUp, text: 'Best Rates', color: 'from-brand-blue to-brand-red', delay: 0.4 },
  ]

  return (
    <motion.header
      style={{ opacity: headerOpacity, backdropFilter: `blur(${headerBlur}px)` }}
      className="w-full bg-[#0b4f82] text-white shadow-md"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3 flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <div className="w-12 h-12 rounded-lg bg-white flex items-center justify-center">
            <Banknote className="w-6 h-6 text-[#0b4f82]" />
          </div>
          <div>
            <div className="font-bold text-lg">QuickLoan</div>
            <div className="text-sm text-blue-200">AI Loan Assistant</div>
          </div>
        </div>

        <nav className="hidden md:flex items-center space-x-6 text-sm">
          <a className="hover:underline" href="#">Apply Now</a>
          <a className="hover:underline" href="#">Loan Products</a>
          <a className="hover:underline" href="#">Help</a>
          <a className="bg-white text-[#0b4f82] px-3 py-2 rounded-md font-semibold shadow-sm" href="#">Contact</a>
        </nav>
      </div>
    </motion.header>
  )
}

export default Header