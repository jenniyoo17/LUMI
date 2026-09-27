import type { AuthResult, User } from '../types'
import { seededUsers, TOKEN_KEY, USER_KEY, type StoredUser } from './mockAuthData'
import { wait } from './mockData'

// In-memory "users table" — resets on reload, same caveat as the rest of the mock layer.
let users: StoredUser[] = [...seededUsers]

function isValidEmail(email: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
}

function toPublicUser(u: StoredUser): User {
  const { password: _password, ...publicUser } = u
  return publicUser
}

function makeFakeToken(userId: string): string {
  // Not a real JWT — just enough shape to simulate persisting a session.
  return `mock.${userId}.${Date.now()}`
}

function persistSession(user: User, token: string) {
  localStorage.setItem(TOKEN_KEY, token)
  localStorage.setItem(USER_KEY, JSON.stringify(user))
}

export const mockAuth = {
  async login(email: string, password: string): Promise<AuthResult> {
    await wait(500)
    const normalizedEmail = email.trim().toLowerCase()
    if (!isValidEmail(normalizedEmail)) {
      throw new Error('Enter a valid email address.')
    }
    const found = users.find((u) => u.email.toLowerCase() === normalizedEmail)
    if (!found || found.password !== password) {
      throw new Error('That email and password don\'t match.')
    }
    const user = toPublicUser(found)
    const token = makeFakeToken(user.id)
    persistSession(user, token)
    return { user, token }
  },

  async signup(email: string, password: string, name?: string): Promise<AuthResult> {
    await wait(500)
    const normalizedEmail = email.trim().toLowerCase()
    if (!isValidEmail(normalizedEmail)) {
      throw new Error('Enter a valid email address.')
    }
    if (password.length < 8) {
      throw new Error('Password must be at least 8 characters.')
    }
    if (users.some((u) => u.email.toLowerCase() === normalizedEmail)) {
      throw new Error('An account with that email already exists.')
    }
    const newUser: StoredUser = {
      id: `user-${Date.now()}`,
      email: normalizedEmail,
      name: name?.trim() || undefined,
      password,
    }
    users = [...users, newUser]
    const user = toPublicUser(newUser)
    const token = makeFakeToken(user.id)
    persistSession(user, token)
    return { user, token }
  },

  async logout(): Promise<void> {
    await wait(150)
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
  },

  /** Restores a session from localStorage on app load, if one exists. */
  async restoreSession(): Promise<User | null> {
    await wait(200)
    const token = localStorage.getItem(TOKEN_KEY)
    const rawUser = localStorage.getItem(USER_KEY)
    if (!token || !rawUser) return null
    try {
      return JSON.parse(rawUser) as User
    } catch {
      return null
    }
  },
}
