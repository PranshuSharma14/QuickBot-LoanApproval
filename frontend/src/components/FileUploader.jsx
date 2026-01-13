import React, { useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { motion } from 'framer-motion'
import { Upload, FileText, AlertCircle, Shield, CheckCircle } from 'lucide-react'

const FileUploader = ({ onUpload }) => {
  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles.length > 0) {
      onUpload(acceptedFiles[0])
    }
  }, [onUpload])

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png']
    },
    maxFiles: 1,
    maxSize: 5 * 1024 * 1024 // 5MB
  })

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9, y: 20 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      transition={{ type: "spring", stiffness: 200 }}
      className="w-full"
    >
      {/* Header with icon */}
      <div className="mb-6 text-center">
        <motion.div
          initial={{ scale: 0, rotate: -180 }}
          animate={{ scale: 1, rotate: 0 }}
          transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
          className="w-16 h-16 mx-auto mb-4 rounded-2xl flex items-center justify-center shadow-2xl"
          style={{ background: 'linear-gradient(90deg, var(--brand-blue), var(--brand-red))' }}
        >
          <FileText className="w-8 h-8 text-white" strokeWidth={2.5} />
        </motion.div>
        
        <motion.h3
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="text-2xl font-bold text-white mb-2"
        >
          Upload Salary Slip
        </motion.h3>
        
        <motion.p
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="text-sm text-white/70"
        >
          We need to verify your income to process your loan
        </motion.p>
      </div>

      {/* Drop zone */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        {...getRootProps()}
          className={`
          relative border-3 border-dashed rounded-3xl p-12 text-center cursor-pointer transition-all duration-300 backdrop-blur-xl overflow-hidden group
          ${isDragActive && !isDragReject 
            ? 'border-brand-blue bg-brand-blue/10 shadow-2xl scale-105' 
            : isDragReject 
              ? 'border-red-400 bg-red-50 shadow-2xl'
              : 'border-white/30 bg-white/5 hover:border-brand-blue hover:bg-white/10 hover:shadow-2xl hover:scale-102'
          }
        `}
      >
        {/* Animated background gradient */}
        <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500" style={{ background: 'linear-gradient(135deg, rgba(11,79,130,0.04), transparent, rgba(200,16,46,0.03))' }} />
        
        <input {...getInputProps()} />
        
        <motion.div
          animate={{ 
            y: isDragActive ? -10 : 0,
            scale: isDragActive ? 1.1 : 1
          }}
          transition={{ type: "spring", stiffness: 300 }}
          className="relative z-10"
        >
          {/* Icon with animation */}
          <motion.div
            animate={isDragActive ? {
              y: [0, -10, 0],
              rotate: [0, 5, -5, 0]
            } : {}}
            transition={{ duration: 0.6, repeat: isDragActive ? Infinity : 0 }}
          >
                {isDragReject ? (
              <AlertCircle className="w-16 h-16 text-red-400 mx-auto mb-6" strokeWidth={2} />
            ) : (
              <motion.div
                className={`w-20 h-20 mx-auto mb-6 rounded-2xl flex items-center justify-center shadow-2xl`}
                style={{ background: 'linear-gradient(90deg, var(--brand-blue), var(--brand-red))' }}
                whileHover={{ rotate: 360 }}
                transition={{ duration: 0.6 }}
              >
                <Upload className="w-10 h-10 text-white" strokeWidth={2.5} />
              </motion.div>
            )}
          </motion.div>
          
          {/* Text content */}
          <div className="space-y-3">
            <p className={`text-xl font-bold ${
              isDragReject 
                ? 'text-red-400' 
                : isDragActive 
                  ? 'text-brand-blue' 
                  : 'text-slate-900'
            }`}>
              {isDragReject 
                ? '❌ Invalid File Type' 
                : isDragActive 
                  ? '✨ Drop it here!' 
                  : 'Drag & Drop Your File'
              }
            </p>
            
              <p className="text-base text-slate-700">
              or{' '}
              <span className="text-transparent bg-clip-text gradient-text font-bold">
                click to browse
              </span>
            </p>
            
            {/* Supported formats */}
            <div className="flex items-center justify-center space-x-6 mt-6 pt-6 border-t border-white/10">
              {[
                { icon: '📄', label: 'PDF', color: 'from-brand-blue to-brand-red' },
                { icon: '🖼️', label: 'JPG', color: 'from-brand-blue to-brand-red' },
                { icon: '🎨', label: 'PNG', color: 'from-brand-blue to-brand-red' }
              ].map((format, idx) => (
                <motion.div
                  key={idx}
                  className={`flex items-center space-x-2 px-4 py-2 rounded-xl bg-gradient-to-r ${format.color} bg-opacity-10 border border-white/20`}
                  whileHover={{ scale: 1.1, y: -2 }}
                  transition={{ type: "spring", stiffness: 300 }}
                >
                  <span className="text-2xl">{format.icon}</span>
                  <span className="text-sm font-bold text-slate-900">{format.label}</span>
                </motion.div>
              ))}
            </div>
            
            <p className="text-sm text-white/50 mt-4">
              Maximum file size: <span className="font-bold text-white/70">5MB</span>
            </p>
          </div>
        </motion.div>

        {/* Decorative corner elements */}
        <div className="absolute top-4 left-4 w-8 h-8 rounded-tl-2xl" style={{ borderTopWidth: 2, borderLeftWidth: 2, borderTopColor: 'rgba(11,79,130,0.14)', borderLeftColor: 'rgba(11,79,130,0.14)' }} />
        <div className="absolute top-4 right-4 w-8 h-8 rounded-tr-2xl" style={{ borderTopWidth: 2, borderRightWidth: 2, borderTopColor: 'rgba(200,16,46,0.12)', borderRightColor: 'rgba(200,16,46,0.12)' }} />
        <div className="absolute bottom-4 left-4 w-8 h-8 rounded-bl-2xl" style={{ borderBottomWidth: 2, borderLeftWidth: 2, borderBottomColor: 'rgba(11,79,130,0.12)', borderLeftColor: 'rgba(11,79,130,0.12)' }} />
        <div className="absolute bottom-4 right-4 w-8 h-8 rounded-br-2xl" style={{ borderBottomWidth: 2, borderRightWidth: 2, borderBottomColor: 'rgba(200,16,46,0.12)', borderRightColor: 'rgba(200,16,46,0.12)' }} />
      </motion.div>

      {/* Security note */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
        className="mt-6 p-5 rounded-2xl backdrop-blur-xl border"
        style={{ background: 'linear-gradient(90deg, rgba(11,79,130,0.04), rgba(200,16,46,0.02))', borderColor: 'rgba(11,79,130,0.08)' }}
      >
        <div className="flex items-start space-x-4">
            <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
            className="flex-shrink-0"
          >
            <Shield className="w-6 h-6" style={{ color: 'var(--brand-blue)' }} />
          </motion.div>
          <div className="flex-1">
              <div className="flex items-center space-x-2 mb-2">
              <CheckCircle className="w-4 h-4" style={{ color: 'var(--brand-blue)' }} />
              <p className="font-bold" style={{ color: 'var(--brand-blue)' }}>Bank-Grade Security</p>
            </div>
            <p className="text-sm text-white/70 leading-relaxed">
              Your document is encrypted and processed securely. We only extract salary information for eligibility assessment and delete the file immediately after verification.
            </p>
          </div>
        </div>
      </motion.div>
    </motion.div>
  )
}

export default FileUploader