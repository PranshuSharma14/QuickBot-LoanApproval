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
      <div className="mb-3 text-center">
        <h3 className="text-lg font-bold text-slate-800 mb-1 flex items-center justify-center gap-2">
          <FileText className="w-5 h-5 text-primary-500" />
          Upload Salary Slip
        </h3>
        <p className="text-xs text-slate-600">
          Upload your latest salary slip to continue
        </p>
      </div>

      <div
        {...getRootProps()}
        className={`
          relative border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition-all duration-300 shadow-sm
          ${isDragActive && !isDragReject 
            ? 'border-primary-400 bg-primary-50 shadow-md' 
            : isDragReject 
              ? 'border-red-400 bg-red-50'
              : 'border-slate-300 bg-white hover:border-primary-300 hover:bg-primary-25 hover:shadow-md'
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
            <AlertCircle className="w-10 h-10 text-red-500 mx-auto mb-3" />
          ) : (
            <Upload className={`w-10 h-10 mx-auto mb-3 ${
              isDragActive ? 'text-primary-500' : 'text-slate-400'
            }`} />
          )}
          
          <div className="space-y-1">
            <p className={`text-base font-medium ${
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