import { useState } from 'react'
import { ArrowRight, CircleAlert } from 'lucide-react'
import { Link, useNavigate } from 'react-router-dom'
import { Button } from '../../components/common'
import { api, ApiError } from '../../services/api'
import { firebaseConfigured, signInWithGoogle } from '../../services/firebase'
import { setRoleSession, setStudentSession } from '../../services/session'

const developmentAuthEnabled = import.meta.env.VITE_AUTH_MODE === 'development'

export function FirebaseLoginPage() {
  const navigate = useNavigate()
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const googleLogin = async () => { setBusy(true); setError(''); try { await signInWithGoogle(); const session = await api.firebaseSession(); if (session.role === 'admin') { setRoleSession('admin'); navigate('/admin/dashboard') } else if (session.registered && session.student_id) { setRoleSession('student'); setStudentSession(String(session.student_id)); navigate('/student/dashboard') } else navigate('/onboarding') } catch (reason: unknown) { setError(reason instanceof ApiError ? reason.status === 404 ? 'The authentication session endpoint was not found. Restart FastAPI from the current source.' : reason.message : reason instanceof Error ? reason.message : 'Google sign-in failed.') } finally { setBusy(false) } }
  return <div className="auth-page"><div className="auth-panel"><div className="auth-content"><p className="eyebrow">Smart College Admission</p><h1 className="heading">Welcome to Smart College Admission</h1><p className="muted">Sign in with your Google account to continue.</p>{error && <div className="notice" role="alert"><CircleAlert size={18} />{error}</div>}<Button className="full-width" onClick={googleLogin} disabled={busy || !firebaseConfigured}>{busy ? 'Signing in with Google...' : 'Continue with Google'} <ArrowRight size={17} /></Button>{!firebaseConfigured && <p className="field-error">Firebase configuration is missing. Add the VITE_FIREBASE_* values to .env.</p>}{developmentAuthEnabled && <p className="auth-switch"><Link to="/login/development">Development email sign-in</Link></p>}</div></div></div>
}