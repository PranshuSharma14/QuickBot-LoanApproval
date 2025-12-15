import React, { useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { motion } from 'framer-motion'
import { Upload, FileText, AlertCircle } from 'lucide-react'

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
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="w-full"
    >
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-slate-800 mb-2">Upload Salary Slip</h3>
        <p className="text-sm text-slate-600">
          Please upload your latest salary slip to continue with the loan approval process.
        </p>
      </div>

      <div
        {...getRootProps()}
        className={`
          relative border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all duration-300
          ${isDragActive && !isDragReject 
            ? 'border-primary-400 bg-primary-50' 
            : isDragReject 
              ? 'border-red-400 bg-red-50'
              : 'border-slate-300 bg-slate-50 hover:border-primary-300 hover:bg-primary-25'
          }
        `}
      >
        <input {...getInputProps()} />
        
        <motion.div
          animate={{ 
            y: isDragActive ? -5 : 0,
            scale: isDragActive ? 1.05 : 1
          }}
          transition={{ type: "spring", stiffness: 300 }}
        >
          {isDragReject ? (
            <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          ) : (
            <Upload className={`w-12 h-12 mx-auto mb-4 ${
              isDragActive ? 'text-primary-500' : 'text-slate-400'
            }`} />
          )}
          
          <div className="space-y-2">
            <p className={`text-lg font-medium ${
              isDragReject 
                ? 'text-red-600' 
                : isDragActive 
                  ? 'text-primary-600' 
                  : 'text-slate-700'
            }`}>
              {isDragReject 
                ? 'Invalid file type' 
                : isDragActive 
                  ? 'Drop your file here' 
                  : 'Drop your salary slip here'
              }
            </p>
            
            <p className="text-sm text-slate-500">
              or <span className="text-primary-500 font-medium">browse files</span>
            </p>
            
            <div className="flex items-center justify-center space-x-4 mt-4 text-xs text-slate-400">
              <div className="flex items-center space-x-1">
                <FileText className="w-3 h-3" />
                <span>PDF</span>
              </div>
              <div className="flex items-center space-x-1">
                <FileText className="w-3 h-3" />
                <span>JPG</span>
              </div>
              <div className="flex items-center space-x-1">
                <FileText className="w-3 h-3" />
                <span>PNG</span>
              </div>
              <span>•</span>
              <span>Max 5MB</span>
            </div>
          </div>
        </motion.div>
      </div>

      <div className="mt-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
        <p className="text-sm text-blue-800">
          <strong>Note:</strong> Your document is processed securely and deleted after verification. 
          We only extract salary information for loan eligibility assessment.
        </p>
      </div>
    </motion.div>
  )
}

export default FileUploader