import React from 'react'
import { motion } from 'framer-motion'
import { Check, Circle, X, Sparkles } from 'lucide-react'

const LoanProgress = ({ currentStage, isRejected }) => {
  const stages = [
    { name: 'Welcome', description: 'Getting started', icon: '👋' },
    { name: 'Requirements', description: 'Loan details', icon: '📋' },
    { name: 'Verification', description: 'Identity check', icon: '🔍' },
    { name: 'Assessment', description: 'Credit evaluation', icon: '📊' },
    { name: 'Decision', description: 'Loan approval', icon: '✅' },
    { name: 'Complete', description: 'Sanction letter', icon: '🎉' }
  ]

  console.log('LoanProgress - currentStage:', currentStage, 'isRejected:', isRejected)

  return (
    <motion.div
      initial={{ opacity: 0, y: -30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="mb-4 p-4 backdrop-blur-2xl bg-white/10 rounded-2xl border border-white/20 shadow-2xl relative overflow-hidden"
    >
      {/* Animated background gradient */}
      <div className="absolute inset-0 animate-gradient-x" style={{ background: 'linear-gradient(90deg, rgba(11,79,130,0.08), rgba(200,16,46,0.06))' }} />
      
      <div className="relative z-10">
        {/* Header */}
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-3">
              <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
            >
              <Sparkles className="w-6 h-6 text-brand-blue" />
            </motion.div>
            <h3 className="text-lg font-bold text-slate-900">Application Progress</h3>
          </div>
          <div className="text-sm font-bold gradient-text">
            {Math.round((currentStage / (stages.length - 1)) * 100)}% Complete
          </div>
        </div>

        {/* Progress Steps */}
        <div className="flex items-center justify-between mb-6">
          {stages.map((stage, index) => (
            <div key={index} className="flex items-center flex-1">
              {/* Stage Circle */}
              <div className="flex flex-col items-center flex-1">
                <motion.div
                  initial={{ scale: 0.5, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  transition={{ delay: index * 0.15, type: "spring", stiffness: 200 }}
                  className="relative"
                >
                  <motion.div
                    className={`w-10 h-10 rounded-xl flex items-center justify-center transition-all duration-500 shadow-xl relative overflow-hidden ${isRejected && index === 4 ? 'bg-gradient-to-br from-red-500 to-rose-600' : isRejected && index > 4 ? 'bg-white/5 backdrop-blur-sm border-2 border-white/10' : index <= currentStage && currentStage === 5 && index === 5 ? 'bg-gradient-to-br from-green-500 to-emerald-600' : index < currentStage ? 'bg-gradient-to-br from-brand-blue to-brand-red' : index === currentStage ? 'bg-gradient-to-br from-brand-blue to-brand-red' : 'bg-white/5 backdrop-blur-sm border-2 border-white/10'}`}
                    animate={index === currentStage ? {
                      boxShadow: [
                        '0 0 20px rgba(11,79,130,0.45)',
                        '0 0 40px rgba(200,16,46,0.35)',
                        '0 0 20px rgba(11,79,130,0.3)'
                      ],
                      scale: [1, 1.05, 1]
                    } : {}}
                    transition={{ duration: 2, repeat: Infinity }}
                  >
                    {/* Shimmer effect for active stage */}
                    {index === currentStage && (
                      <motion.div
                        className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent"
                        animate={{ x: ['-200%', '200%'] }}
                        transition={{ duration: 2, repeat: Infinity, repeatDelay: 0.5 }}
                      />
                    )}
                    
                    <div className="relative z-10">
                      {isRejected && index === 4 ? (
                        <X className="w-5 h-5 text-white" strokeWidth={3} />
                      ) : isRejected && index > 4 ? (
                        <Circle className="w-3 h-3 text-white/30" />
                      ) : !isRejected && (index < currentStage || (index === currentStage && currentStage < 5) || (index <= currentStage && currentStage === 5)) ? (
                        <Check className="w-5 h-5 text-white" strokeWidth={3} />
                      ) : isRejected && index < 4 ? (
                        <Check className="w-5 h-5 text-white" strokeWidth={3} />
                      ) : (
                        <span className="text-lg">{stage.icon}</span>
                      )}
                    </div>
                  </motion.div>

                  {/* Pulsing ring for current stage */}
                  {index === currentStage && !isRejected && (
                    <motion.div
                      className="absolute inset-0 rounded-xl border-2 border-brand-blue"
                      animate={{
                        scale: [1, 1.3, 1],
                        opacity: [0.8, 0, 0.8]
                      }}
                      transition={{ duration: 2, repeat: Infinity }}
                    />
                  )}
                </motion.div>
                
                {/* Stage Label */}
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.15 + 0.2 }}
                  className="mt-2 text-center"
                >
                  <p className={`text-xs font-bold mb-0.5 transition-colors duration-300 ${isRejected && index === 4 ? 'text-red-400' : index <= currentStage ? 'text-white' : 'text-white/40'}`}>
                    {stage.name}
                  </p>
                  <p className={`text-[10px] transition-colors duration-300 ${isRejected && index === 4 ? 'text-red-300/70' : index <= currentStage ? 'text-white/70' : 'text-white/30'}`}>
                    {stage.description}
                  </p>
                </motion.div>
              </div>

              {/* Connector Line */}
              {index < stages.length - 1 && (
                <div className="flex-1 h-1 mx-2 mt-[-40px] relative">
                  <div className="absolute inset-0 bg-white/10 rounded-full" />
                  <motion.div
                    initial={{ scaleX: 0 }}
                    animate={{ scaleX: (index < currentStage && !(isRejected && index >= 4)) ? 1 : 0 }}
                    transition={{ duration: 0.8, delay: index * 0.2, ease: "easeInOut" }}
                    className={`absolute inset-0 rounded-full origin-left ${isRejected && index >= 4 ? 'bg-gradient-to-r from-red-500 to-rose-600' : 'bg-gradient-to-r from-brand-blue to-brand-red'}`}
                    style={{ transformOrigin: 'left' }}
                  />
                  
                  {/* Animated particles on active connector */}
                  {index === currentStage - 1 && !isRejected && (
                    <motion.div
                      className="absolute top-1/2 w-2 h-2 bg-white rounded-full"
                      animate={{ x: ['0%', '100%'] }}
                      transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
                      style={{ y: '-50%' }}
                    />
                  )}
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Animated Progress Bar */}
        <div className="space-y-1.5">
            <div className="flex justify-between text-[10px] font-semibold">
            <span className="text-slate-700">Overall Progress</span>
            <motion.span
              key={currentStage}
              initial={{ scale: 1.5, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              className="gradient-text"
            >
              {Math.round((currentStage / (stages.length - 1)) * 100)}%
            </motion.span>
          </div>
          
          <div className="relative h-2 bg-white/10 rounded-full overflow-hidden backdrop-blur-sm">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${(currentStage / (stages.length - 1)) * 100}%` }}
              transition={{ duration: 1, ease: "easeOut" }}
              className={`h-full rounded-full relative overflow-hidden ${isRejected ? 'bg-gradient-to-r from-red-500 to-rose-600' : 'bg-gradient-to-r from-brand-blue to-brand-red'}`}
            >
              {/* Shimmer effect on progress bar */}
              <motion.div
                className="absolute inset-0"
                style={{ background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent)' }}
                animate={{ x: ['-200%', '200%'] }}
                transition={{ duration: 2, repeat: Infinity, repeatDelay: 0.5 }}
              />
            </motion.div>
          </div>
        </div>
      </div>
    </motion.div>
  )
}

export default LoanProgress