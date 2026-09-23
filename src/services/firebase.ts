import { clearSession } from './session'

export const firebaseConfigured = false
export const firebaseApp = null
export const firebaseAuth: { currentUser: { displayName?: string | null; email?: string | null } | null } | null = null

export function useFirebaseAuth(): { user: null; loading: boolean } {
  return { user: null, loading: false }
}

export async function signInWithGoogle(): Promise<never> {
  throw new Error('Google sign-in has been disabled for this localhost demo build.')
}

export async function signOutFirebase(): Promise<void> {
  clearSession()
}