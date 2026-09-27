import { Navigate, Route, Routes } from 'react-router-dom'
import { AppLayout } from './components/AppLayout'
import { RequireAuth } from './components/RequireAuth'
import { useAuth } from './hooks/useAuth'
import { Login } from './pages/Login'
import { Signup } from './pages/Signup'
import { Onboarding } from './pages/Onboarding'
import { Chat } from './pages/Chat'
import { Memory } from './pages/Memory'
import { DataControl } from './pages/DataControl'
import { Settings } from './pages/Settings'

export function isOnboarded(userId: string) {
  return localStorage.getItem(`lumi-onboarded-${userId}`) === 'true'
}

function RootRedirect() {
  const { user, loading } = useAuth()
  if (loading) return <div className="auth-loading">Loading Lumi…</div>
  if (!user) return <Navigate to="/login" replace />
  return <Navigate to={isOnboarded(user.id) ? '/chat' : '/onboarding'} replace />
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/signup" element={<Signup />} />

      <Route
        path="/onboarding"
        element={
          <RequireAuth>
            <Onboarding />
          </RequireAuth>
        }
      />

      <Route
        element={
          <RequireAuth>
            <AppLayout />
          </RequireAuth>
        }
      >
        <Route path="/chat" element={<Chat />} />
        <Route path="/memory" element={<Memory />} />
        <Route path="/data" element={<DataControl />} />
        <Route path="/settings" element={<Settings />} />
      </Route>

      <Route path="*" element={<RootRedirect />} />
    </Routes>
  )
}
