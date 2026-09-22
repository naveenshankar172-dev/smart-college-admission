import { useState, type FormEvent } from 'react'
import { ArrowRight, CircleAlert } from 'lucide-react'
import { Link, useNavigate } from 'react-router-dom'
import { api, ApiError } from '../../services/api'
import { Button, Field, SelectField } from '../../components/common'

const courses = ['Computer Science and Engineering', 'Information Technology', 'Artificial Intelligence and Data Science', 'Artificial Intelligence and Machine Learning', 'Electronics and Communication Engineering', 'Electrical and Electronics Engineering', 'Mechanical Engineering', 'Civil Engineering', 'Other']
const years = ['1st Year', '2nd Year', '3rd Year', '4th Year']

export function RealRegisterPage() {
  const navigate = useNavigate()
  const [values, setValues] = useState({ name: '', email: '', phone: '', password: '', course: courses[0], otherCourse: '', academicYear: years[0] })
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)
  const update = (key: keyof typeof values) => (value: string) => setValues(current => ({ ...current, [key]: value }))
  const submit = async (event: FormEvent) => {
    event.preventDefault()
    setSaving(true)
    setError('')
    try {
      await api.createStudent({ name: values.name, email: values.email, phone: values.phone, password: values.password, course: values.course === 'Other' ? values.otherCourse : values.course, academicYear: values.academicYear, academicScore: 0, city: '' })
      navigate('/login')
    } catch (reason: unknown) {
      setError(reason instanceof ApiError ? reason.message : 'Registration could not be completed.')
    } finally {
      setSaving(false)
    }
  }
  return <div className="auth-page"><div className="auth-panel"><div className="auth-content"><p className="eyebrow">Student registration</p><h1 className="heading">Create your workspace</h1><p className="muted">Your admission profile will be stored in the connected SQLite database.</p>{error && <div className="notice" role="alert"><CircleAlert size={18} />{error}</div>}<form className="auth-form" onSubmit={submit}><Field label="Full name" value={values.name} onChange={update('name')} required /><Field label="Email address" value={values.email} onChange={update('email')} type="email" required /><Field label="Phone number" value={values.phone} onChange={update('phone')} type="tel" required /><Field label="Password" value={values.password} onChange={update('password')} type="password" required /><SelectField label="Department / course" value={values.course} onChange={update('course')} options={courses} />{values.course === 'Other' && <Field label="Specify your course" value={values.otherCourse} onChange={update('otherCourse')} required />}<SelectField label="Academic year" value={values.academicYear} onChange={update('academicYear')} options={years} /><label className="checkbox"><input type="checkbox" required /> I agree to the terms and privacy notice.</label><Button type="submit" className="full-width" disabled={saving}>{saving ? 'Creating account...' : 'Create account'} <ArrowRight size={17} /></Button></form><p className="auth-switch">Already have an account? <Link to="/login">Sign in</Link></p></div></div></div>
}