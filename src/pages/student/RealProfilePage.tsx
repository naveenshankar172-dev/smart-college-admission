import { useEffect, useState } from 'react'
import { UserRound } from 'lucide-react'
import { api, ApiError } from '../../services/api'
import { getCurrentStudentId } from '../../services/session'
import { Button, Card, Field, SectionHeading, SelectField, Toast } from '../../components/common'
import type { Student } from '../../types'

const years = ['1st Year', '2nd Year', '3rd Year', '4th Year']

export function RealProfilePage() {
  const [student, setStudent] = useState<Student | null>(null)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')
  const [saving, setSaving] = useState(false)
  useEffect(() => { try { api.getStudent(getCurrentStudentId()).then(setStudent).catch(reason => setError(reason instanceof ApiError ? reason.message : 'Unable to load profile.')) } catch (reason: unknown) { setError(reason instanceof Error ? reason.message : 'No authenticated student session.') } }, [])
  const update = (key: 'name' | 'phone' | 'city' | 'course' | 'academicYear') => (value: string) => setStudent(current => current ? { ...current, [key]: value } : current)
  const save = async () => { if (!student || !/^\+?[0-9 ()-]{7,20}$/.test(student.phone)) { setError('Enter a valid phone number.'); return } setSaving(true); setError(''); try { setStudent(await api.updateStudent(getCurrentStudentId(), student)); setMessage('Profile changes saved.') } catch (reason: unknown) { setError(reason instanceof ApiError ? reason.message : 'Profile could not be saved.') } finally { setSaving(false) } }
  if (!student) return <div>{error ? <div className="notice" role="alert">{error}</div> : 'Loading profile...'}</div>
  return <div><SectionHeading eyebrow="Account" title="Your profile" description="These details are loaded from your authenticated SQLite student record." action={<Button onClick={save} disabled={saving}>{saving ? 'Saving...' : 'Save changes'}</Button>} />{error && <div className="notice" role="alert">{error}</div>}{message && <Toast message={message} onClose={() => setMessage('')} />}<div className="profile-grid"><Card><div className="profile-header"><span className="large-avatar">{student.name.split(' ').map(item => item[0]).join('').slice(0, 2).toUpperCase()}</span><div><h2 className="heading">{student.name}</h2><p className="muted">{student.email}</p></div></div><h3 className="form-section-title">Personal details</h3><div className="form-grid"><Field label="Full name" value={student.name} onChange={update('name')} /><Field label="Email" value={student.email} onChange={() => {}} type="email" /><Field label="Phone" value={student.phone} onChange={update('phone')} /><Field label="Department / course" value={student.course} onChange={update('course')} /><SelectField label="Academic year" value={student.academicYear || years[0]} onChange={update('academicYear')} options={years} /></div></Card><Card><h2 className="heading">Account settings</h2><label className="toggle-row"><span><strong>Email updates</strong><small>Receive verification and deadline reminders</small></span><input type="checkbox" checked={student.emailUpdates ?? true} onChange={event => setStudent({ ...student, emailUpdates: event.target.checked })} /></label><label className="toggle-row"><span><strong>Scholarship suggestions</strong><small>Show potentially relevant funding matches</small></span><input type="checkbox" checked={student.scholarshipSuggestions ?? true} onChange={event => setStudent({ ...student, scholarshipSuggestions: event.target.checked })} /></label><div className="security-note"><UserRound size={18} /><span><strong>Authenticated student</strong><small>Changes are stored against student #{student.id}.</small></span></div></Card></div></div>
}