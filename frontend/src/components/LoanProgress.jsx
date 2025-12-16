import React from 'react'
import { motion } from 'framer-motion'
import { Check, Circle, X } from 'lucide-react'

const LoanProgress = ({ currentStage, isRejected }) => {
  const stages = [
    { name: 'Welcome', description: 'Getting started' },
    { name: 'Requirements', description: 'Loan details' },
    { name: 'Verification', description: 'Identity check' },
    { name: 'Assessment', description: 'Credit evaluation' },
    { name: 'Decision', description: 'Loan approval' },
    { name: 'Complete', description: 'Sanction letter' }
  ]

  console.log('LoanProgress - currentStage:', currentStage, 'isRejected:', isRejected)

  return (
    <motion.div
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      className="mb-6 p-4 glass-effect rounded-2xl"
    >
      <div className="flex items-center justify-between">
        {stages.map((stage, index) => (
          <div key={index} className="flex items-center">
            {/* Stage Circle */}
            <div className="flex flex-col items-center">
              <motion.div
                initial={{ scale: 0.8 }}
                animate={{ scale: 1 }}
                transition={{ delay: index * 0.1 }}
                className={`w-10 h-10 rounded-full flex items-center justify-center transition-all duration-300 ${
                  isRejected && index === 4
                    ? 'bg-red-500 text-white shadow-lg ring-4 ring-red-200'
                    : isRejected && index > 4
                    ? 'bg-slate-200 text-slate-400'
                    : index <= currentStage && currentStage === 5 && index === 5
                    ? 'bg-accent-500 text-white shadow-lg'
                    : index < currentStage
                    ? 'bg-accent-500 text-white shadow-lg'
                    : index === currentStage
                      ? 'bg-primary-500 text-white shadow-lg ring-4 ring-primary-200'
                      : 'bg-slate-200 text-slate-400'
                }`}
              >
                {isRejected && index === 4 ? (
                  <X className="w-5 h-5" />
                ) : isRejected && index > 4 ? (
                  <Circle className="w-4 h-4" />
                ) : !isRejected && (index < currentStage || (index === currentStage && currentStage < 5) || (index <= currentStage && currentStage === 5)) ? (
                  <Check className="w-5 h-5" />
                ) : isRejected && index < 4 ? (
                  <Check className="w-5 h-5" />
                ) : (
                  <Circle className="w-4 h-4" />
                )}
              </motion.div>
              
              {/* Stage Label */}
              <div className="mt-2 text-center">
                <p className={`text-xs font-medium ${
                  isRejected && index === 4
                    ? 'text-red-600'
                    : index <= currentStage ? 'text-slate-700' : 'text-slate-400'
                }`}>
                  {stage.name}
                </p>
                <p className={`text-xs ${
                  isRejected && index === 4
                    ? 'text-red-500'
                    : index <= currentStage ? 'text-slate-500' : 'text-slate-400'
                }`}>
                  {stage.description}
                </p>
              </div>
            </div>

            {/* Connector Line */}
            {index < stages.length - 1 && (
              <div className="flex-1 h-0.5 mx-4 mt-[-20px]">
                <motion.div
                  initial={{ scaleX: 0 }}
                  animate={{ scaleX: (index < currentStage && !(isRejected && index >= 4)) ? 1 : 0 }}
                  transition={{ duration: 0.5, delay: index * 0.2 }}
                  className="h-full bg-accent-300 origin-left"
                />
                <div className={`h-full ${(index < currentStage && !(isRejected && index >= 4)) ? 'bg-transparent' : 'bg-slate-200'}`} />
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Progress Bar */}
      <div className="mt-4">
        <div className="flex justify-between text-xs text-slate-500 mb-2">
          <span>Progress</span>
          <span>{Math.round((currentStage / (stages.length - 1)) * 100)}% Complete</span>
        </div>
        <div className="w-full bg-slate-200 rounded-full h-2">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${(currentStage / (stages.length - 1)) * 100}%` }}
            transition={{ duration: 0.8, ease: "easeInOut" }}
            className={`h-2 rounded-full ${
              isRejected 
                ? 'bg-gradient-to-r from-red-500 to-red-400'
                : 'bg-gradient-to-r from-primary-500 to-accent-500'
            }`}
          />
        </div>
      </div>
    </motion.div>
  )
}

export default LoanProgress