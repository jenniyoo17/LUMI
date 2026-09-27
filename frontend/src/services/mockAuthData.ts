import type { User } from '../types'

// A pretend "users table". In a real backend this would live in a database
// with hashed+salted passwords — see README "Connecting real authentication".
// Storing plaintext passwords here is only acceptable because this never
// leaves the browser and is thrown away on reload.
export interface StoredUser extends User {
  password: string
}

export const seededUsers: StoredUser[] = [
  {
    id: 'user-demo',
    email: 'demo@lumi.app',
    name: 'Demo User',
    password: 'lumi1234',
  },
]

export const TOKEN_KEY = 'lumi-auth-token'
export const USER_KEY = 'lumi-auth-user'
