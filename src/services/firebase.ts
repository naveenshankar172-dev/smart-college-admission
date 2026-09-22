import { getApp, getApps, initializeApp } from 'firebase/app'
import { getAuth, GoogleAuthProvider, signInWithPopup, signOut, type User } from 'firebase/auth'

const config = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID,
}

export const firebaseConfigured = Boolean(config.apiKey && config.authDomain && config.projectId && config.appId)
export const firebaseApp = firebaseConfigured ? (getApps().length ? getApp() : initializeApp(config)) : null
export const firebaseAuth = firebaseApp ? getAuth(firebaseApp) : null

export async function signInWithGoogle(): Promise<User> {
  if (!firebaseAuth) throw new Error('Firebase is not configured. Add the VITE_FIREBASE_* values to .env.')
  const provider = new GoogleAuthProvider()
  const result = await signInWithPopup(firebaseAuth, provider)
  return result.user
}

export async function signOutFirebase(): Promise<void> {
  if (firebaseAuth) await signOut(firebaseAuth)
}