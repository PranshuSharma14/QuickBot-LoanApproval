import React, { useState, useEffect } from 'react';
import { Toaster } from 'react-hot-toast';
import { AuthProvider, useAuth } from './context/AuthContext';
import LoginPage from './pages/LoginPage';
import SignupPage from './pages/SignupPage';
import Dashboard from './pages/Dashboard';
import BankChatInterface from './components/BankChatInterface';

// Main App Content with Auth
const AppContent = () => {
  const { isAuthenticated, loading, user } = useAuth();
  const [currentPage, setCurrentPage] = useState('login'); // login, signup, dashboard, chat
  const [activeLoanId, setActiveLoanId] = useState(null);

  useEffect(() => {
    if (isAuthenticated) {
      setCurrentPage('dashboard');
    } else if (!loading) {
      setCurrentPage('login');
    }
  }, [isAuthenticated, loading]);

  const handleLoginSuccess = () => {
    setCurrentPage('dashboard');
  };

  const handleLogout = () => {
    setCurrentPage('login');
  };

  const handleStartNewLoan = (loanId) => {
    setActiveLoanId(loanId);
    setCurrentPage('chat');
  };

  const handleBackFromChat = () => {
    setCurrentPage('dashboard');
    setActiveLoanId(null);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-[#004c8c] to-[#0066b3]">
        <div className="text-center text-white">
          <div className="w-16 h-16 bg-white rounded-2xl flex items-center justify-center mx-auto mb-4 animate-pulse">
            <span className="text-[#004c8c] font-bold text-2xl">QL</span>
          </div>
          <p className="text-lg">Loading QuickLoan...</p>
        </div>
      </div>
    );
  }

  return (
    <>
      <Toaster 
        position="top-center"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#1e293b',
            color: '#fff',
            borderRadius: '12px',
            fontSize: '14px',
            fontWeight: '500',
            padding: '12px 16px',
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

      {currentPage === 'login' && (
        <LoginPage 
          onSwitchToSignup={() => setCurrentPage('signup')}
          onLoginSuccess={handleLoginSuccess}
        />
      )}

      {currentPage === 'signup' && (
        <SignupPage 
          onSwitchToLogin={() => setCurrentPage('login')}
        />
      )}

      {currentPage === 'dashboard' && (
        <Dashboard 
          onStartNewLoan={handleStartNewLoan}
          onLogout={handleLogout}
        />
      )}

      {currentPage === 'chat' && (
        <BankChatInterface 
          onBack={handleBackFromChat}
          userInfo={user}
          loanId={activeLoanId}
        />
      )}
    </>
  );
};

// Root App with Provider
function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;