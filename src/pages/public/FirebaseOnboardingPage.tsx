import { useEffect, useState } from 'react'
import { ArrowRight, CircleAlert } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { api, ApiError } from '../../services/api'
import { firebaseAuth, signOutFirebase } from '../../services/firebase'
import { setRoleSession, setStudentSession } from '../../services/session'
import { Button, Field, SelectField } from '../../components/common'

const courses = ['Computer Science and Engineering', 'Information Technology', 'Artificial Intelligence and Data Science', 'Artificial Intelligence and Machine Learning', 'Electronics and Communication Engineering', 'Electrical and Electronics Engineering', 'Mechanical Engineering', 'Civil Engineering', 'Other']
const years = ['1st Year', '2nd Year', '3rd Year', '4th Year', '5th Year']

export function FirebaseOnboardingPage() {
  const navigate = useNavigate()
  const user = firebaseAuth?.currentUser
  const [name, setName] = useState(user?.displayName ?? '')
  const [phone, setPhone] = useState('')
  const [course, setCourse] = useState(courses[0])
  const [otherCourse, setOtherCourse] = useState('')
  const [academicYear, setAcademicYear] = useState(years[0])
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  useEffect(() => { if (!firebaseAuth?.currentUser) navigate('/login', { replace: true }) }, [navigate])
  const submit = async () => { setSaving(true); setError(''); try { const student = await api.firebaseOnboard({ name, phone, course: course === 'Other' ? otherCourse : course, academicYear }); setRoleSession('student'); setStudentSession(student.id); navigate('/student/dashboard') } catch (reason: unknown) { setError(reason instanceof ApiError ? reason.message : 'Onboarding could not be saved.') } finally { setSaving(false) } }
  if (!user) return <div>Checking authentication...</div>
  return <div className="auth-page"><div className="auth-panel"><div className="auth-content"><p className="eyebrow">First-time setup</p><h1 className="heading">Complete your student profile</h1><p className="muted">Your Google account is connected. Add the academic information required for admissions.</p>{error && <div className="notice" role="alert"><CircleAlert size={18} />{error}</div>}<div className="auth-form"><Field label="Full name" value={name} onChange={setName} required /><Field label="Email" value={user.email ?? ''} onChange={() => {}} type="email" /><Field label="Phone number" value={phone} onChange={setPhone} type="tel" required /><SelectField label="Department / course" value={course} onChange={setCourse} options={courses} />{course === 'Other' && <Field label="Specify your course" value={otherCourse} onChange={setOtherCourse} required />}<SelectField label="Academic year" value={academicYear} onChange={setAcademicYear} options={years} /><Button className="full-width" onClick={submit} disabled={saving}>{saving ? 'Saving profile...' : 'Continue'} <ArrowRight size={17} /></Button><Button variant="ghost" onClick={() => signOutFirebase().then(() => navigate('/login'))}>Use a different Google account</Button></div></div></div></div>
}