import React from 'react'
import { Toaster } from 'react-hot-toast'
import LoanChatInterface from './components/LoanChatInterface'
import Header from './components/Header'
import Footer from './components/Footer'

function App() {
  return (
    <div className="min-h-screen flex flex-col">
      <Toaster 
        position="top-center"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#363636',
            color: '#fff',
          },
        }}
      />
      
      <Header />
      
      <main className="flex-1 flex items-center justify-center p-4">
        <LoanChatInterface />
      </main>
      
      <Footer />
    </div>
  )
}

export default App