import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from 'react'
import type { User } from '../types'
import { authService } from '../services/authService'

interface AuthContextValue {
  user: User | null
  loading: boolean
  error: string | null
  login: (email: string, password: string) => Promise<boolean>
  signup: (email: string, password: string, name?: string) => Promise<boolean>
  logout: () => Promise<void>
  clearError: () => void
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    authService.restoreSession().then((restored) => {
      setUser(restored)
      setLoading(false)
    })
  }, [])

  const login = useCallback(async (email: string, password: string) => {
    setError(null)
    try {
      const { user: loggedInUser } = await authService.login(email, password)
      setUser(loggedInUser)
      return true
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong. Try again.')
      return false
    }
  }, [])

  const signup = useCallback(async (email: string, password: string, name?: string) => {
    setError(null)
    try {
      const { user: newUser } = await authService.signup(email, password, name)
      setUser(newUser)
      return true
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong. Try again.')
      return false
    }
  }, [])

  const logout = useCallback(async () => {
    await authService.logout()
    setUser(null)
  }, [])

  const clearError = useCallback(() => setError(null), [])

  return (
    <AuthContext.Provider value={{ user, loading, error, login, signup, logout, clearError }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within an AuthProvider')
  return ctx
}
