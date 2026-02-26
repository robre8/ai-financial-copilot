import ChatInterface from './components/ChatInterface'
import AuthScreen from './components/AuthScreen'
import { AuthProvider, useAuth } from './auth/AuthContext'

function AuthGate() {
  const { user, loading } = useAuth()

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-emerald-100 dark:from-green-950 dark:to-emerald-900 flex items-center justify-center">
        <div className="text-slate-700 dark:text-slate-200">Loading...</div>
      </div>
    )
  }

  if (!user) {
    return <AuthScreen />
  }

  return <ChatInterface />
}

function App() {
  return (
    <AuthProvider>
      <AuthGate />
    </AuthProvider>
  )
}

export default App

