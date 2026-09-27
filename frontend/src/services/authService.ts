import type { AuthResult, User } from '../types'
import { mockAuth } from './mockAuth'

/**
 * authService is the single boundary between UI code and wherever
 * authentication actually happens. Swap the export at the bottom for a
 * real implementation when the backend is ready — see README.md
 * "Connecting real authentication". No component or hook should change.
 */
export interface AuthServiceInterface {
  login(email: string, password: string): Promise<AuthResult>
  signup(email: string, password: string, name?: string): Promise<AuthResult>
  logout(): Promise<void>
  restoreSession(): Promise<User | null>
}

export const authService: AuthServiceInterface = mockAuth
