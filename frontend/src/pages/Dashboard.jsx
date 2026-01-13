import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import { 
  LayoutDashboard, FileText, History, User, LogOut, 
  Plus, TrendingUp, AlertCircle, CheckCircle, Clock,
  IndianRupee, Calendar, Download, ChevronRight, RefreshCw,
  CreditCard, PieChart, ArrowUpRight, ArrowDownRight, Trash2, Play
} from 'lucide-react';
import toast from 'react-hot-toast';

const API_BASE = 'http://127.0.0.1:8000';

const Dashboard = ({ onStartNewLoan, onLogout }) => {
  const { user, getAuthHeader, logout } = useAuth();
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(false);
  const [initialLoad, setInitialLoad] = useState(true);
  const [dashboardData, setDashboardData] = useState({
    user: user || {},
    summary: {
      total_loans: 0,
      approved_loans: 0,
      ongoing_loans: 0,
      rejected_loans: 0,
      pending_loans: 0,
      total_borrowed: 0,
      total_outstanding: 0
    }
  });
  const [loans, setLoans] = useState([]);
  const [loanHistory, setLoanHistory] = useState([]);
  const [profile, setProfile] = useState(user || null);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    if (!initialLoad) setLoading(true);
    try {
      const headers = getAuthHeader();
      
      // Fetch in parallel but don't block UI
      const [summaryRes, loansRes, historyRes, profileRes] = await Promise.all([
        axios.get(`${API_BASE}/api/dashboard/summary`, { headers }).catch(e => ({ data: null })),
        axios.get(`${API_BASE}/api/dashboard/loans`, { headers }).catch(e => ({ data: { loans: [] } })),
        axios.get(`${API_BASE}/api/dashboard/loan-history`, { headers }).catch(e => ({ data: { loan_history: [] } })),
        axios.get(`${API_BASE}/api/dashboard/profile`, { headers }).catch(e => ({ data: { profile: null } }))
      ]);

      if (summaryRes.data) setDashboardData(summaryRes.data);
      setLoans(loansRes.data.loans || []);
      setLoanHistory(historyRes.data.loan_history || []);
      setProfile(profileRes.data.profile || user || null);
    } catch (error) {
      console.error('Dashboard fetch error:', error);
      if (error.response?.status === 401) {
        toast.error('Session expired. Please login again.');
        handleLogout();
      }
    } finally {
      setLoading(false);
      setInitialLoad(false);
    }
  };

  const handleLogout = async () => {
    await logout();
    onLogout?.();
  };

  const handleStartNewLoan = async () => {
    try {
      const headers = getAuthHeader();
      const response = await axios.post(`${API_BASE}/api/dashboard/start-new-loan`, {}, { headers });
      if (response.data.success) {
        toast.success('New loan application started!');
        onStartNewLoan?.(response.data.loan_id);
      }
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to start new loan');
    }
  };

  const handleContinueLoan = (loanId) => {
    toast.success(`Continuing loan application: ${loanId}`);
    onStartNewLoan?.(loanId);
  };

  const handleDeleteLoan = async (loanId) => {
    if (!window.confirm(`Are you sure you want to delete loan ${loanId}? This action cannot be undone.`)) {
      return;
    }
    try {
      const headers = getAuthHeader();
      await axios.delete(`${API_BASE}/api/dashboard/loans/${loanId}`, { headers });
      toast.success('Loan application deleted!');
      fetchDashboardData(); // Refresh the list
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to delete loan');
    }
  };

  const handleDownloadSanctionLetter = async (loanId) => {
    try {
      const headers = getAuthHeader();
      const response = await axios.get(`${API_BASE}/api/dashboard/loans/${loanId}/sanction-letter`, { headers });
      if (response.data.success && response.data.sanction_letter_path) {
        // Download the file
        const fileUrl = `${API_BASE}/${response.data.sanction_letter_path}`;
        const link = document.createElement('a');
        link.href = fileUrl;
        link.download = `QuickLoan_Sanction_Letter_${loanId}.pdf`;
        link.target = '_blank';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        toast.success('Sanction letter downloaded!');
      }
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Sanction letter not available');
    }
  };

  const handleViewLoanDetails = (loan) => {
    // Show loan details in a toast or modal
    const details = `
Loan ID: ${loan.loan_id}
Amount: ${formatCurrency(loan.approved_amount || loan.loan_amount)}
Interest Rate: ${loan.interest_rate || '-'}% p.a.
Tenure: ${loan.tenure_months || '-'} months
EMI: ${loan.emi_amount ? formatCurrency(loan.emi_amount) : '-'}
Status: ${loan.status.replace('_', ' ').toUpperCase()}
EMIs Paid: ${loan.emis_paid || 0}/${loan.total_emis || '-'}
Outstanding: ${loan.outstanding_balance ? formatCurrency(loan.outstanding_balance) : '-'}
    `.trim();
    
    toast.success(details, { duration: 8000, style: { whiteSpace: 'pre-line', textAlign: 'left' } });
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(amount || 0);
  };

  const formatDate = (dateString) => {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleDateString('en-IN', {
      day: '2-digit',
      month: 'short',
      year: 'numeric'
    });
  };

  const getStatusColor = (status) => {
    const colors = {
      approved: 'bg-green-100 text-green-700',
      ongoing: 'bg-blue-100 text-blue-700',
      disbursed: 'bg-blue-100 text-blue-700',
      pending: 'bg-yellow-100 text-yellow-700',
      under_review: 'bg-yellow-100 text-yellow-700',
      rejected: 'bg-red-100 text-red-700',
      closed: 'bg-gray-100 text-gray-700',
      draft: 'bg-gray-100 text-gray-700'
    };
    return colors[status] || 'bg-gray-100 text-gray-700';
  };

  const getStatusIcon = (status) => {
    const icons = {
      approved: CheckCircle,
      ongoing: TrendingUp,
      disbursed: TrendingUp,
      pending: Clock,
      under_review: Clock,
      rejected: AlertCircle,
      closed: CheckCircle
    };
    const Icon = icons[status] || Clock;
    return <Icon className="w-4 h-4" />;
  };

  const menuItems = [
    { id: 'overview', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'loans', label: 'All Loans', icon: FileText },
    { id: 'history', label: 'Loan History', icon: History },
    { id: 'profile', label: 'My Profile', icon: User }
  ];

  const summary = dashboardData?.summary || {};

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Loading overlay - shows only during refresh, not initial load */}
      {loading && !initialLoad && (
        <div className="fixed inset-0 bg-white/50 z-50 flex items-center justify-center">
          <RefreshCw className="w-8 h-8 text-[#004c8c] animate-spin" />
        </div>
      )}
      
      {/* Sidebar - Fixed position */}
      <aside className="w-64 bg-white shadow-lg flex flex-col fixed h-screen overflow-y-auto z-40">
        {/* Logo */}
        <div className="p-6 border-b">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-[#004c8c] rounded-lg flex items-center justify-center">
              <span className="text-white font-bold">QL</span>
            </div>
            <div>
              <h1 className="font-bold text-gray-800">QuickLoan</h1>
              <p className="text-xs text-gray-500">Banking Portal</p>
            </div>
          </div>
        </div>

        {/* User Info */}
        <div className="p-4 border-b bg-gray-50">
          <p className="text-sm text-gray-500">Welcome back,</p>
          <p className="font-semibold text-gray-800 truncate">{user?.full_name || 'User'}</p>
          <p className="text-xs text-gray-500">{user?.user_id}</p>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4">
          <ul className="space-y-1">
            {menuItems.map(item => (
              <li key={item.id}>
                <button
                  onClick={() => setActiveTab(item.id)}
                  className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
                    activeTab === item.id
                      ? 'bg-[#004c8c] text-white'
                      : 'text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  <item.icon className="w-5 h-5" />
                  {item.label}
                </button>
              </li>
            ))}
          </ul>
        </nav>

        {/* Apply New Loan Button */}
        <div className="p-4 border-t">
          <button
            onClick={handleStartNewLoan}
            className="w-full flex items-center justify-center gap-2 bg-[#c8102e] text-white py-3 rounded-lg font-semibold hover:bg-[#a50d26] transition-colors"
          >
            <Plus className="w-5 h-5" />
            Apply for New Loan
          </button>
        </div>

        {/* Logout */}
        <div className="p-4 border-t">
          <button
            onClick={handleLogout}
            className="w-full flex items-center justify-center gap-2 text-gray-600 hover:text-red-600 py-2 transition-colors"
          >
            <LogOut className="w-5 h-5" />
            Logout
          </button>
        </div>
      </aside>

      {/* Main Content - Add left margin for fixed sidebar */}
      <main className="flex-1 p-8 overflow-auto ml-64">
        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
          >
            <div className="flex justify-between items-center">
              <div>
                <h1 className="text-2xl font-bold text-gray-800">Dashboard Overview</h1>
                <p className="text-gray-500">Welcome back! Here's your loan summary.</p>
              </div>
              <button
                onClick={fetchDashboardData}
                className="flex items-center gap-2 text-[#004c8c] hover:underline"
              >
                <RefreshCw className="w-4 h-4" />
                Refresh
              </button>
            </div>

            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="bg-white rounded-xl p-6 shadow-sm border">
                <div className="flex justify-between items-start mb-4">
                  <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                    <FileText className="w-6 h-6 text-blue-600" />
                  </div>
                  <span className="text-sm text-gray-500">Total</span>
                </div>
                <p className="text-3xl font-bold text-gray-800">{summary.total_loans || 0}</p>
                <p className="text-sm text-gray-500">Loan Applications</p>
              </div>

              <div className="bg-white rounded-xl p-6 shadow-sm border">
                <div className="flex justify-between items-start mb-4">
                  <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                    <CheckCircle className="w-6 h-6 text-green-600" />
                  </div>
                  <span className="text-sm text-green-600 flex items-center gap-1">
                    <ArrowUpRight className="w-4 h-4" />
                    Active
                  </span>
                </div>
                <p className="text-3xl font-bold text-gray-800">{summary.ongoing_loans || 0}</p>
                <p className="text-sm text-gray-500">Ongoing Loans</p>
              </div>

              <div className="bg-white rounded-xl p-6 shadow-sm border">
                <div className="flex justify-between items-start mb-4">
                  <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                    <IndianRupee className="w-6 h-6 text-purple-600" />
                  </div>
                </div>
                <p className="text-3xl font-bold text-gray-800">{formatCurrency(summary.total_borrowed)}</p>
                <p className="text-sm text-gray-500">Total Borrowed</p>
              </div>

              <div className="bg-white rounded-xl p-6 shadow-sm border">
                <div className="flex justify-between items-start mb-4">
                  <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center">
                    <TrendingUp className="w-6 h-6 text-red-600" />
                  </div>
                </div>
                <p className="text-3xl font-bold text-gray-800">{formatCurrency(summary.total_outstanding)}</p>
                <p className="text-sm text-gray-500">Outstanding Balance</p>
              </div>
            </div>

            {/* Upcoming EMIs */}
            {dashboardData?.upcoming_emis?.length > 0 && (
              <div className="bg-white rounded-xl p-6 shadow-sm border">
                <h2 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
                  <Calendar className="w-5 h-5 text-[#004c8c]" />
                  Upcoming EMIs
                </h2>
                <div className="space-y-3">
                  {dashboardData.upcoming_emis.map((emi, index) => (
                    <div key={index} className="flex justify-between items-center p-4 bg-gray-50 rounded-lg">
                      <div>
                        <p className="font-medium text-gray-800">{emi.loan_id}</p>
                        <p className="text-sm text-gray-500">Due: {formatDate(emi.due_date)}</p>
                      </div>
                      <p className="text-lg font-bold text-[#c8102e]">{formatCurrency(emi.amount)}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Quick Stats */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-white rounded-xl p-6 shadow-sm border">
                <h2 className="text-lg font-semibold text-gray-800 mb-4">Loan Status Distribution</h2>
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">Approved</span>
                    <span className="font-semibold text-green-600">{summary.approved_loans || 0}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">Pending</span>
                    <span className="font-semibold text-yellow-600">{summary.pending_loans || 0}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">Rejected</span>
                    <span className="font-semibold text-red-600">{summary.rejected_loans || 0}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">Closed</span>
                    <span className="font-semibold text-gray-600">{summary.closed_loans || 0}</span>
                  </div>
                </div>
              </div>

              <div className="bg-gradient-to-br from-[#004c8c] to-[#0066b3] rounded-xl p-6 text-white">
                <h2 className="text-lg font-semibold mb-4">Need Another Loan?</h2>
                <p className="text-white/80 mb-6">
                  Apply for a new personal loan with our AI-powered instant approval system.
                </p>
                <button
                  onClick={handleStartNewLoan}
                  className="flex items-center gap-2 bg-white text-[#004c8c] px-6 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors"
                >
                  <Plus className="w-5 h-5" />
                  Apply Now
                </button>
              </div>
            </div>
          </motion.div>
        )}

        {/* All Loans Tab */}
        {activeTab === 'loans' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
          >
            <div>
              <h1 className="text-2xl font-bold text-gray-800">All Loans</h1>
              <p className="text-gray-500">View all your loan applications</p>
            </div>

            <div className="bg-white rounded-xl shadow-sm border overflow-hidden">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="text-left px-6 py-4 text-sm font-semibold text-gray-600">Loan ID</th>
                    <th className="text-left px-6 py-4 text-sm font-semibold text-gray-600">Amount</th>
                    <th className="text-left px-6 py-4 text-sm font-semibold text-gray-600">Tenure</th>
                    <th className="text-left px-6 py-4 text-sm font-semibold text-gray-600">Status</th>
                    <th className="text-left px-6 py-4 text-sm font-semibold text-gray-600">Applied On</th>
                    <th className="text-left px-6 py-4 text-sm font-semibold text-gray-600">EMI Progress</th>
                    <th className="text-left px-6 py-4 text-sm font-semibold text-gray-600">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {loans.length > 0 ? (
                    loans.map(loan => (
                      <tr key={loan.loan_id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 font-medium text-gray-800">{loan.loan_id}</td>
                        <td className="px-6 py-4 text-gray-600">{loan.loan_amount > 0 ? formatCurrency(loan.loan_amount) : formatCurrency(loan.approved_amount) || '₹0'}</td>
                        <td className="px-6 py-4 text-gray-600">{loan.tenure_months ? `${loan.tenure_months} months` : '-'}</td>
                        <td className="px-6 py-4">
                          <span className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm ${getStatusColor(loan.status)}`}>
                            {getStatusIcon(loan.status)}
                            {loan.status.replace('_', ' ')}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-gray-600">{formatDate(loan.applied_at)}</td>
                        <td className="px-6 py-4">
                          {loan.total_emis ? (
                            <div className="flex items-center gap-2">
                              <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                                <div 
                                  className="h-full bg-[#004c8c] rounded-full"
                                  style={{ width: `${(loan.emis_paid / loan.total_emis) * 100}%` }}
                                />
                              </div>
                              <span className="text-sm text-gray-600">{loan.emis_paid}/{loan.total_emis}</span>
                            </div>
                          ) : (
                            <span className="text-gray-400">-</span>
                          )}
                        </td>
                        <td className="px-6 py-4">
                          <div className="flex items-center gap-2 flex-wrap">
                            {/* Continue button - show ONLY for draft loans */}
                            {loan.status === 'draft' && (
                              <button
                                onClick={() => handleContinueLoan(loan.loan_id)}
                                className="flex items-center gap-1 px-3 py-1.5 text-sm bg-[#004c8c] text-white rounded-lg hover:bg-[#003d73] transition-colors"
                                title="Continue Application"
                              >
                                <Play className="w-3.5 h-3.5" />
                                Continue
                              </button>
                            )}
                            {/* Download Sanction Letter - show for approved/ongoing/disbursed loans */}
                            {['approved', 'disbursed', 'ongoing'].includes(loan.status) && loan.has_sanction_letter && (
                              <button
                                onClick={() => handleDownloadSanctionLetter(loan.loan_id)}
                                className="flex items-center gap-1 px-3 py-1.5 text-sm bg-green-100 text-green-700 rounded-lg hover:bg-green-200 transition-colors"
                                title="Download Sanction Letter"
                              >
                                <Download className="w-3.5 h-3.5" />
                                Letter
                              </button>
                            )}
                            {/* View Details button for approved/ongoing/closed loans */}
                            {['approved', 'disbursed', 'ongoing', 'closed'].includes(loan.status) && (
                              <button
                                onClick={() => handleViewLoanDetails(loan)}
                                className="flex items-center gap-1 px-3 py-1.5 text-sm bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-colors"
                              >
                                <ChevronRight className="w-3.5 h-3.5" />
                                Details
                              </button>
                            )}
                            {/* View Rejection Reason */}
                            {loan.status === 'rejected' && (
                              <button
                                onClick={() => toast.error(loan.rejection_reason || 'Application was rejected')}
                                className="flex items-center gap-1 px-3 py-1.5 text-sm bg-red-100 text-red-600 rounded-lg hover:bg-red-200 transition-colors"
                              >
                                <AlertCircle className="w-3.5 h-3.5" />
                                Reason
                              </button>
                            )}
                            {/* Delete button - show only for draft/rejected loans */}
                            {['draft', 'rejected'].includes(loan.status) && (
                              <button
                                onClick={() => handleDeleteLoan(loan.loan_id)}
                                className="flex items-center gap-1 px-3 py-1.5 text-sm bg-gray-100 text-gray-600 rounded-lg hover:bg-gray-200 transition-colors"
                                title="Delete Application"
                              >
                                <Trash2 className="w-3.5 h-3.5" />
                              </button>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={7} className="px-6 py-12 text-center text-gray-500">
                        No loan applications yet. Start your first application!
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </motion.div>
        )}

        {/* Loan History Tab */}
        {activeTab === 'history' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
          >
            <div>
              <h1 className="text-2xl font-bold text-gray-800">Loan History</h1>
              <p className="text-gray-500">Complete history of all your loan applications</p>
            </div>

            {loanHistory.length > 0 ? (
              <div className="space-y-4">
                {loanHistory.map(loan => (
                  <div key={loan.loan_id} className="bg-white rounded-xl p-6 shadow-sm border">
                    <div className="flex justify-between items-start mb-4">
                      <div>
                        <h3 className="font-semibold text-gray-800">{loan.loan_id}</h3>
                        <p className="text-sm text-gray-500">Applied: {formatDate(loan.applied_at)}</p>
                        {loan.approved_at && (
                          <p className="text-sm text-green-600">Approved: {formatDate(loan.approved_at)}</p>
                        )}
                      </div>
                      <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(loan.status)}`}>
                        {getStatusIcon(loan.status)}
                        <span className="ml-1">{loan.status.replace('_', ' ').toUpperCase()}</span>
                      </span>
                    </div>
                    
                    {/* Loan Details Grid */}
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                      <div>
                        <p className="text-sm text-gray-500">Loan Amount</p>
                        <p className="font-semibold text-gray-800">{formatCurrency(loan.approved_amount || loan.loan_amount)}</p>
                      </div>
                      {loan.interest_rate && (
                        <div>
                          <p className="text-sm text-gray-500">Interest Rate</p>
                          <p className="font-semibold text-gray-800">{loan.interest_rate}% p.a.</p>
                        </div>
                      )}
                      {loan.tenure_months && (
                        <div>
                          <p className="text-sm text-gray-500">Tenure</p>
                          <p className="font-semibold text-gray-800">{loan.tenure_months} months</p>
                        </div>
                      )}
                      {loan.emi_amount && (
                        <div>
                          <p className="text-sm text-gray-500">EMI</p>
                          <p className="font-semibold text-gray-800">{formatCurrency(loan.emi_amount)}</p>
                        </div>
                      )}
                    </div>

                    {/* EMI Progress for ongoing loans */}
                    {['ongoing', 'disbursed', 'approved'].includes(loan.status) && loan.total_emis && (
                      <div className="mb-4">
                        <div className="flex justify-between text-sm mb-2">
                          <span className="text-gray-600">EMI Progress</span>
                          <span className="font-medium text-gray-800">
                            {loan.emis_paid || 0} / {loan.total_emis} EMIs paid
                          </span>
                        </div>
                        <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                          <div 
                            className="h-full bg-gradient-to-r from-[#004c8c] to-[#0077cc] rounded-full transition-all"
                            style={{ width: `${((loan.emis_paid || 0) / loan.total_emis) * 100}%` }}
                          />
                        </div>
                      </div>
                    )}
                    
                    {/* Actions and Additional Info */}
                    <div className="flex flex-wrap justify-between items-center gap-4 pt-4 border-t">
                      {loan.status === 'rejected' && loan.rejection_reason && (
                        <div className="flex-1">
                          <p className="text-sm text-gray-500">Rejection Reason</p>
                          <p className="text-sm text-red-600">{loan.rejection_reason}</p>
                        </div>
                      )}
                      
                      {loan.outstanding_balance > 0 && (
                        <div>
                          <p className="text-sm text-gray-500">Outstanding</p>
                          <p className="font-semibold text-[#c8102e]">{formatCurrency(loan.outstanding_balance)}</p>
                        </div>
                      )}
                      
                      {loan.has_sanction_letter && (
                        <button 
                          onClick={() => handleDownloadSanctionLetter(loan.loan_id)}
                          className="flex items-center gap-2 px-4 py-2 bg-green-100 text-green-700 rounded-lg hover:bg-green-200 transition-colors"
                        >
                          <Download className="w-4 h-4" />
                          Download Sanction Letter
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="bg-white rounded-xl p-12 text-center shadow-sm border">
                <History className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-800 mb-2">No Loan History</h3>
                <p className="text-gray-500">Your loan applications will appear here once processed.</p>
              </div>
            )}
          </motion.div>
        )}

        {/* Profile Tab */}
        {activeTab === 'profile' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
          >
            <div>
              <h1 className="text-2xl font-bold text-gray-800">My Profile</h1>
              <p className="text-gray-500">Your account information and KYC status</p>
            </div>

            <div className="bg-white rounded-xl shadow-sm border overflow-hidden">
              {/* Profile Header */}
              <div className="bg-gradient-to-r from-[#004c8c] to-[#0066b3] p-6 text-white">
                <div className="flex items-center gap-4">
                  <div className="w-20 h-20 bg-white/20 rounded-full flex items-center justify-center text-3xl font-bold">
                    {profile?.full_name?.charAt(0) || 'U'}
                  </div>
                  <div className="flex-1">
                    <h2 className="text-2xl font-bold">{profile?.full_name}</h2>
                    <p className="text-white/80">{profile?.user_id}</p>
                    {/* Dynamic KYC Status Badges */}
                    {(() => {
                      const kycChecks = [
                        { verified: profile?.phone_verified },
                        { verified: profile?.aadhaar_verified || profile?.aadhaar_masked },
                        { verified: profile?.pan_verified || profile?.pan_masked },
                        { verified: !!profile?.monthly_income },
                      ];
                      const completedCount = kycChecks.filter(c => c.verified).length;
                      const isFullyVerified = completedCount === kycChecks.length;
                      const kycPercentage = Math.round((completedCount / kycChecks.length) * 100);
                      
                      return (
                        <div className="flex items-center gap-2 mt-2 flex-wrap">
                          <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                            isFullyVerified 
                              ? 'bg-green-500/30 text-green-100' 
                              : 'bg-yellow-500/30 text-yellow-100'
                          }`}>
                            {isFullyVerified ? '✓ KYC VERIFIED' : `KYC: ${kycPercentage}% Complete`}
                          </span>
                          {profile?.phone_verified && (
                            <span className="px-2 py-1 rounded text-xs font-medium bg-green-500/20 text-green-100">
                              ✓ Mobile
                            </span>
                          )}
                          {(profile?.aadhaar_verified || profile?.aadhaar_masked) && (
                            <span className="px-2 py-1 rounded text-xs font-medium bg-green-500/20 text-green-100">
                              ✓ Aadhaar
                            </span>
                          )}
                          {(profile?.pan_verified || profile?.pan_masked) && (
                            <span className="px-2 py-1 rounded text-xs font-medium bg-green-500/20 text-green-100">
                              ✓ PAN
                            </span>
                          )}
                        </div>
                      );
                    })()}
                  </div>
                </div>
              </div>

              {/* KYC Status Card - Real Bank Style */}
              {(() => {
                // Calculate KYC completion like real banks
                const kycChecks = [
                  { key: 'phone', label: 'Mobile Verification', verified: profile?.phone_verified },
                  { key: 'aadhaar', label: 'Aadhaar e-KYC', verified: profile?.aadhaar_verified || profile?.aadhaar_masked },
                  { key: 'pan', label: 'PAN Verification', verified: profile?.pan_verified || profile?.pan_masked },
                  { key: 'income', label: 'Income Proof', verified: !!profile?.monthly_income },
                ];
                const completedCount = kycChecks.filter(c => c.verified).length;
                const isFullyVerified = completedCount === kycChecks.length;
                const kycPercentage = Math.round((completedCount / kycChecks.length) * 100);

                return !isFullyVerified ? (
                  <div className="p-4 bg-gradient-to-r from-yellow-50 to-orange-50 border-b border-yellow-200">
                    <div className="flex items-start gap-3">
                      <div className="w-10 h-10 bg-yellow-100 rounded-full flex items-center justify-center">
                        <AlertCircle className="w-5 h-5 text-yellow-600" />
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center justify-between">
                          <h4 className="font-semibold text-yellow-800">KYC Verification</h4>
                          <span className="text-sm font-medium text-yellow-700">{kycPercentage}% Complete</span>
                        </div>
                        <div className="w-full bg-yellow-200 rounded-full h-2 mt-2 mb-3">
                          <div 
                            className="bg-yellow-500 h-2 rounded-full transition-all duration-500" 
                            style={{ width: `${kycPercentage}%` }}
                          />
                        </div>
                        <div className="grid grid-cols-2 gap-2">
                          {kycChecks.map((check) => (
                            <div key={check.key} className="flex items-center gap-2 text-sm">
                              {check.verified ? (
                                <CheckCircle className="w-4 h-4 text-green-500" />
                              ) : (
                                <Clock className="w-4 h-4 text-gray-400" />
                              )}
                              <span className={check.verified ? 'text-green-700 font-medium' : 'text-gray-600'}>
                                {check.label}
                              </span>
                            </div>
                          ))}
                        </div>
                        {completedCount < kycChecks.length && (
                          <p className="text-xs text-yellow-700 mt-3">
                            💡 Complete your KYC during loan application for instant approval
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="p-4 bg-gradient-to-r from-green-50 to-emerald-50 border-b border-green-200">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                        <CheckCircle className="w-5 h-5 text-green-600" />
                      </div>
                      <div>
                        <h4 className="font-semibold text-green-800">KYC Fully Verified</h4>
                        <p className="text-sm text-green-700">Your identity has been verified. Enjoy higher loan limits!</p>
                      </div>
                    </div>
                  </div>
                );
              })()}

              {/* Profile Details - Enhanced Layout */}
              <div className="p-6 space-y-6">
                {/* Personal Information Section */}
                <div>
                  <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">Personal Information</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="bg-gray-50 rounded-lg p-4">
                      <label className="text-xs text-gray-500 uppercase tracking-wide">Email Address</label>
                      <p className="font-medium text-gray-800 mt-1">{profile?.email || 'Not provided'}</p>
                    </div>
                    <div className="bg-gray-50 rounded-lg p-4">
                      <label className="text-xs text-gray-500 uppercase tracking-wide">Phone Number</label>
                      <div className="flex items-center gap-2 mt-1">
                        <p className="font-medium text-gray-800">{profile?.phone_masked || profile?.phone}</p>
                        {profile?.phone_verified ? (
                          <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-green-100 text-green-700 text-xs font-medium rounded-full">
                            <CheckCircle className="w-3 h-3" /> Verified
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-yellow-100 text-yellow-700 text-xs font-medium rounded-full">
                            <Clock className="w-3 h-3" /> Pending
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>

                {/* KYC Documents Section */}
                <div>
                  <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">KYC Documents</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="bg-gray-50 rounded-lg p-4">
                      <label className="text-xs text-gray-500 uppercase tracking-wide">Aadhaar Number</label>
                      <div className="flex items-center gap-2 mt-1">
                        <p className="font-medium text-gray-800 font-mono">{profile?.aadhaar_masked || 'Not provided'}</p>
                        {(profile?.aadhaar_verified || profile?.aadhaar_masked) ? (
                          <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-green-100 text-green-700 text-xs font-medium rounded-full">
                            <CheckCircle className="w-3 h-3" /> Verified
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-gray-200 text-gray-600 text-xs font-medium rounded-full">
                            Not Provided
                          </span>
                        )}
                      </div>
                    </div>
                    <div className="bg-gray-50 rounded-lg p-4">
                      <label className="text-xs text-gray-500 uppercase tracking-wide">PAN Number</label>
                      <div className="flex items-center gap-2 mt-1">
                        <p className="font-medium text-gray-800 font-mono">{profile?.pan_masked || 'Not provided'}</p>
                        {(profile?.pan_verified || profile?.pan_masked) ? (
                          <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-green-100 text-green-700 text-xs font-medium rounded-full">
                            <CheckCircle className="w-3 h-3" /> Verified
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-gray-200 text-gray-600 text-xs font-medium rounded-full">
                            Not Provided
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Financial Information Section */}
                <div>
                  <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">Financial Information</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="bg-gray-50 rounded-lg p-4">
                      <label className="text-xs text-gray-500 uppercase tracking-wide">Monthly Income</label>
                      <p className="font-semibold text-gray-800 text-lg mt-1">
                        {profile?.monthly_income ? formatCurrency(profile.monthly_income) : 'Not provided'}
                      </p>
                      {profile?.monthly_income && (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-green-100 text-green-700 text-xs font-medium rounded-full mt-1">
                          <CheckCircle className="w-3 h-3" /> Verified
                        </span>
                      )}
                    </div>
                    <div className="bg-gray-50 rounded-lg p-4">
                      <label className="text-xs text-gray-500 uppercase tracking-wide">Residential Address</label>
                      <p className="font-medium text-gray-800 mt-1">
                        {[profile?.residential_address, profile?.city, profile?.state, profile?.pincode].filter(Boolean).join(', ') || 'Not provided'}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Account Information Section */}
                <div className="border-t pt-6">
                  <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">Account Information</h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="text-center p-4 bg-gray-50 rounded-lg">
                      <p className="text-xs text-gray-500 uppercase tracking-wide">Account Created</p>
                      <p className="font-medium text-gray-800 mt-1">{formatDate(profile?.created_at)}</p>
                    </div>
                    <div className="text-center p-4 bg-gray-50 rounded-lg">
                      <p className="text-xs text-gray-500 uppercase tracking-wide">Last Login</p>
                      <p className="font-medium text-gray-800 mt-1">{formatDate(profile?.last_login)}</p>
                    </div>
                    <div className="text-center p-4 bg-gray-50 rounded-lg">
                      <p className="text-xs text-gray-500 uppercase tracking-wide">Account Status</p>
                      <span className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm font-medium mt-1 ${
                        profile?.status === 'active' 
                          ? 'bg-green-100 text-green-700' 
                          : 'bg-yellow-100 text-yellow-700'
                      }`}>
                        {profile?.status === 'active' && <CheckCircle className="w-4 h-4" />}
                        {profile?.status?.toUpperCase() || 'ACTIVE'}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </main>
    </div>
  );
};

export default Dashboard;
