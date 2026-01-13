import React from 'react'
import { motion } from 'framer-motion'
import { Heart, Shield, Lock, Mail, Phone, MapPin, Facebook, Twitter, Linkedin, Instagram, ExternalLink } from 'lucide-react'

const Footer = () => {
  const socialLinks = [
    { icon: Facebook, href: '#', color: 'hover:text-blue-400', label: 'Facebook' },
    { icon: Twitter, href: '#', color: 'hover:text-sky-400', label: 'Twitter' },
    { icon: Linkedin, href: '#', color: 'hover:text-blue-500', label: 'LinkedIn' },
    { icon: Instagram, href: '#', color: 'hover:text-[#c8102e]', label: 'Instagram' },
  ]

  const quickLinks = [
    { name: 'About Us', href: '#' },
    { name: 'How It Works', href: '#' },
    { name: 'EMI Calculator', href: '#' },
    { name: 'FAQs', href: '#' },
  ]

  const legalLinks = [
    { name: 'Privacy Policy', href: '#' },
    { name: 'Terms & Conditions', href: '#' },
    { name: 'Grievance Redressal', href: '#' },
    { name: 'Fair Practice Code', href: '#' },
  ]

  return (
    <motion.footer 
      initial={{ opacity: 0, y: 50 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.8, duration: 0.6 }}
      className="relative backdrop-blur-xl bg-white/5 border-t border-white/10 mt-4"
    >
      {/* Animated top border */}
      <div className="absolute top-0 left-0 right-0 h-px" style={{ background: 'linear-gradient(90deg, transparent, var(--brand-blue), transparent)' }} />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        {/* Compact footer content */}
        <div className="flex flex-col md:flex-row items-center justify-between space-y-3 md:space-y-0">
          {/* Left: Branding */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.9 }}
            className="flex items-center space-x-4"
          >
            <h3 className="text-lg font-bold gradient-text">
              QuickLoan AI
            </h3>
            <div className="flex space-x-2">
              {socialLinks.map(({ icon: Icon, href, color, label }, idx) => (
                <motion.a
                  key={idx}
                  href={href}
                  aria-label={label}
                  whileHover={{ scale: 1.2 }}
                  whileTap={{ scale: 0.9 }}
                  className={`w-7 h-7 rounded-lg bg-white/10 backdrop-blur-sm border border-white/20 flex items-center justify-center text-white/70 ${color} transition-colors duration-300`}
                >
                  <Icon className="w-3 h-3" />
                </motion.a>
              ))}
            </div>
          </motion.div>

          {/* Center: Copyright */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1.0 }}
            className="text-center"
          >
            <p className="text-xs text-white/70">
              © {new Date().getFullYear()} QuickLoan Financial Services Pvt. Ltd.
            </p>
            <div className="flex items-center justify-center space-x-3 mt-1">
              <div className="flex items-center space-x-1 text-[10px] text-white/50">
                <Shield className="w-2.5 h-2.5 text-green-400" />
                <span>NBFC: 14.03.167</span>
              </div>
              <div className="flex items-center space-x-1 text-[10px] text-white/50">
                <Lock className="w-2.5 h-2.5 text-blue-400" />
                <span>RBI Regulated</span>
              </div>
            </div>
          </motion.div>

          {/* Right: Made with love */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 1.1 }}
            className="flex items-center space-x-2 text-xs text-white/70"
          >
            <span>Made with</span>
            <motion.div
              animate={{ 
                scale: [1, 1.2, 1],
                rotate: [0, 10, -10, 0]
              }}
              transition={{ 
                duration: 1.5,
                repeat: Infinity,
                repeatDelay: 0.5
              }}
            >
              <Heart className="w-3 h-3 text-red-500 fill-red-500" />
            </motion.div>
            <span>by AI Team</span>
          </motion.div>
        </div>

        {/* Disclaimer */}
        <motion.div 
          className="mt-3 p-2 rounded-xl border border-white/10"
          style={{ background: 'linear-gradient(90deg, rgba(11,79,130,0.04), rgba(200,16,46,0.03))' }}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.2 }}
        >
          <p className="text-[10px] text-white/60 text-center leading-relaxed">
            <span className="font-bold text-yellow-400">⚠️ Demo:</span> Educational purposes only. No real loans processed.
          </p>
        </motion.div>
      </div>

      {/* Animated particles effect */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        {[...Array(5)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-2 h-2 rounded-full"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              background: i % 2 === 0 ? 'rgba(11,79,130,0.18)' : 'rgba(200,16,46,0.14)'
            }}
            animate={{
              y: [-20, 20],
              opacity: [0, 1, 0],
            }}
            transition={{
              duration: 3 + Math.random() * 2,
              repeat: Infinity,
              delay: Math.random() * 2,
            }}
          />
        ))}
      </div>
    </motion.footer>
  )
}

export default Footer