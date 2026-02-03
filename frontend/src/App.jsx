import { useState, useEffect } from 'react'
import Dashboard from './components/Dashboard'
import ApplicationList from './components/ApplicationList'
import ApplicationForm from './components/ApplicationForm'
import KanbanBoard from './components/KanbanBoard'
import AuthForm from './components/AuthForm'
import ResetPassword from './components/ResetPassword'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api'

function App() {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(localStorage.getItem('token'))
  const [resetToken, setResetToken] = useState(null)
  const [applications, setApplications] = useState([])
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [editingApp, setEditingApp] = useState(null)
  const [darkMode, setDarkMode] = useState(() => {
    const saved = localStorage.getItem('darkMode')
    return saved ? JSON.parse(saved) : false
  })
  const [viewMode, setViewMode] = useState(() => {
    const saved = localStorage.getItem('viewMode')
    return saved || 'table'
  })

  // Check for password reset token in URL
  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    const resetTokenParam = params.get('token')
    const path = window.location.pathname

    if (path === '/reset-password' && resetTokenParam) {
      setResetToken(resetTokenParam)
    }
  }, [])

  // Apply dark mode class to document
  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
    localStorage.setItem('darkMode', JSON.stringify(darkMode))
  }, [darkMode])

  // Save view mode preference
  useEffect(() => {
    localStorage.setItem('viewMode', viewMode)
  }, [viewMode])

  // Check authentication on mount
  useEffect(() => {
    if (token) {
      verifyToken()
    } else {
      setLoading(false)
    }
  }, [])

  // Fetch applications and stats when user is authenticated
  useEffect(() => {
    if (user && token) {
      fetchApplications()
      fetchStats()
    }
  }, [user, token])

  const verifyToken = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/me`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      const data = await response.json()

      if (data.success) {
        setUser(data.user)
      } else {
        handleLogout()
      }
    } catch (error) {
      console.error('Error verifying token:', error)
      handleLogout()
    } finally {
      setLoading(false)
    }
  }

  const handleLogin = async (email, password) => {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    })

    const data = await response.json()

    if (!data.success) {
      throw new Error(data.error || 'Login failed')
    }

    setToken(data.access_token)
    setUser(data.user)
    localStorage.setItem('token', data.access_token)
  }

  const handleRegister = async (email, password, name) => {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password, name })
    })

    const data = await response.json()

    if (!data.success) {
      throw new Error(data.error || 'Registration failed')
    }

    setToken(data.access_token)
    setUser(data.user)
    localStorage.setItem('token', data.access_token)
  }

  const handleLogout = () => {
    setToken(null)
    setUser(null)
    setApplications([])
    setStats(null)
    localStorage.removeItem('token')
  }

  const toggleDarkMode = () => {
    setDarkMode(!darkMode)
  }

  const toggleViewMode = () => {
    setViewMode(viewMode === 'table' ? 'kanban' : 'table')
  }

  const fetchApplications = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/applications`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      const data = await response.json()
      if (data.success) {
        setApplications(data.applications)
      }
    } catch (error) {
      console.error('Error fetching applications:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchStats = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/stats`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      const data = await response.json()
      if (data.success) {
        setStats(data.stats)
      }
    } catch (error) {
      console.error('Error fetching stats:', error)
    }
  }

  const handleAddNew = () => {
    setEditingApp(null)
    setShowForm(true)
  }

  const handleEdit = (app) => {
    setEditingApp(app)
    setShowForm(true)
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this application?')) {
      return
    }

    try {
      const response = await fetch(`${API_BASE_URL}/applications/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      const data = await response.json()

      if (data.success) {
        fetchApplications()
        fetchStats()
      }
    } catch (error) {
      console.error('Error deleting application:', error)
    }
  }

  const handleFavoriteToggle = async (id) => {
    try {
      const response = await fetch(`${API_BASE_URL}/applications/${id}/favorite`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      const data = await response.json()

      if (data.success) {
        setApplications(prev =>
          prev.map(app => app.id === id ? { ...app, is_favorite: data.application.is_favorite } : app)
        )
      }
    } catch (error) {
      console.error('Error toggling favorite:', error)
    }
  }

  const handleFormSubmit = async (formData) => {
    try {
      const url = editingApp
        ? `${API_BASE_URL}/applications/${editingApp.id}`
        : `${API_BASE_URL}/applications`

      const method = editingApp ? 'PUT' : 'POST'

      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(formData)
      })

      const data = await response.json()

      if (data.success) {
        setShowForm(false)
        setEditingApp(null)
        fetchApplications()
        fetchStats()
      } else {
        console.error('Error saving application:', data.error)
      }
    } catch (error) {
      console.error('Error saving application:', error)
    }
  }

  const handleFormCancel = () => {
    setShowForm(false)
    setEditingApp(null)
  }

  const handleStatusUpdate = async (id, newStatus) => {
    try {
      const application = applications.find(app => app.id === id)
      if (!application) return

      const response = await fetch(`${API_BASE_URL}/applications/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ ...application, status: newStatus })
      })

      const data = await response.json()

      if (data.success) {
        fetchApplications()
        fetchStats()
      } else {
        console.error('Error updating application status:', data.error)
      }
    } catch (error) {
      console.error('Error updating application status:', error)
    }
  }

  // Handle back to login from reset password
  const handleBackToLogin = () => {
    setResetToken(null)
    // Clean up URL
    window.history.replaceState({}, document.title, '/')
  }

  // Show reset password form if token is present
  if (resetToken) {
    return <ResetPassword token={resetToken} onBackToLogin={handleBackToLogin} />
  }

  // Show auth form if not logged in
  if (!token || !user) {
    return <AuthForm onLogin={handleLogin} onRegister={handleRegister} />
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-green-50 to-emerald-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 transition-colors duration-300">
      {/* Header */}
      <header className="bg-gradient-to-r from-green-600 via-emerald-600 to-teal-600 dark:from-green-700 dark:via-emerald-700 dark:to-teal-700 shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-white dark:bg-gray-800 rounded-lg flex items-center justify-center shadow-md">
                <svg className="w-6 h-6 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
              </div>
              <div>
                <h1 className="text-3xl font-bold text-white">JobTracker</h1>
                <p className="text-sm text-green-100">Welcome, {user.name}</p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <button
                onClick={toggleViewMode}
                className="bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-green-50 dark:hover:bg-gray-700 p-3 rounded-lg transition-all duration-200 shadow-md hover:shadow-xl hover:scale-105"
                title={viewMode === 'table' ? 'Switch to board view' : 'Switch to table view'}
              >
                {viewMode === 'table' ? (
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7m0 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2h-2a2 2 0 00-2 2" />
                  </svg>
                ) : (
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M3 14h18m-9-4v8m-7 0h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                  </svg>
                )}
              </button>
              <button
                onClick={toggleDarkMode}
                className="bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-green-50 dark:hover:bg-gray-700 p-3 rounded-lg transition-all duration-200 shadow-md hover:shadow-xl hover:scale-105"
                title={darkMode ? 'Switch to light mode' : 'Switch to dark mode'}
              >
                {darkMode ? (
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
                  </svg>
                ) : (
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
                  </svg>
                )}
              </button>
              <button
                onClick={handleLogout}
                className="bg-white dark:bg-gray-800 text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-gray-700 p-3 rounded-lg transition-all duration-200 shadow-md hover:shadow-xl hover:scale-105"
                title="Logout"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                </svg>
              </button>
              <button
                onClick={handleAddNew}
                className="bg-white dark:bg-gray-800 text-green-600 dark:text-green-400 hover:bg-green-50 dark:hover:bg-gray-700 px-6 py-3 rounded-lg font-semibold transition-all duration-200 shadow-md hover:shadow-xl hover:scale-105 flex items-center space-x-2"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                <span>Add Application</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block w-8 h-8 border-4 border-green-600 dark:border-green-400 border-t-transparent rounded-full animate-spin"></div>
            <p className="mt-4 text-gray-600 dark:text-gray-400">Loading...</p>
          </div>
        ) : (
          <>
            {/* Dashboard Stats */}
            <Dashboard stats={stats} />

            {/* Applications List or Kanban Board */}
            {viewMode === 'table' ? (
              <ApplicationList
                applications={applications}
                onEdit={handleEdit}
                onDelete={handleDelete}
                onFavoriteToggle={handleFavoriteToggle}
              />
            ) : (
              <KanbanBoard
                applications={applications}
                onEdit={handleEdit}
                onDelete={handleDelete}
                onStatusUpdate={handleStatusUpdate}
                onFavoriteToggle={handleFavoriteToggle}
              />
            )}
          </>
        )}
      </main>

      {/* Application Form Modal */}
      {showForm && (
        <ApplicationForm
          application={editingApp}
          onSubmit={handleFormSubmit}
          onCancel={handleFormCancel}
        />
      )}
    </div>
  )
}

export default App
