import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api, ApiError } from '../../services/api'
import { getCurrentStudentId } from '../../services/session'
import { Button, Card, ErrorState, Field, LoadingState, SectionHeading, SelectField, Toast } from '../../components/common'
import type { Student } from '../../types'

const courses = ['Computer Science and Engineering', 'Information Technology', 'Artificial Intelligence and Data Science', 'Artificial Intelligence and Machine Learning', 'Electronics and Communication Engineering', 'Electrical and Electronics Engineering', 'Mechanical Engineering', 'Civil Engineering', 'Other']

export function RealAdmissionPage() {
  const navigate = useNavigate()
  const [student, setStudent] = useState<Student | null>(null)
  const [course, setCourse] = useState('')
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')
  const [saving, setSaving] = useState(false)
  useEffect(() => { api.getStudent(getCurrentStudentId()).then(value => { setStudent(value); setCourse(value.course) }).catch(reason => setError(reason instanceof ApiError ? reason.message : 'Unable to load admission profile.')) }, [])
  const submit = async () => { if (!student || !course.trim()) return; setSaving(true); setError(''); try { await api.createApplication({ studentId: Number(student.id), course, status: 'submitted', submittedAt: new Date().toISOString() }); setMessage('Admission application submitted.'); setTimeout(() => navigate('/student/status'), 500) } catch (reason: unknown) { setError(reason instanceof ApiError ? reason.message : 'Application could not be submitted.') } finally { setSaving(false) } }
  if (!student) return error ? <ErrorState message={error} onRetry={() => window.location.reload()} /> : <LoadingState />
  return <div><SectionHeading eyebrow="Admission application" title="Submit your application" description="Applicant details are loaded from your authenticated student record." />{error && <div className="notice" role="alert">{error}</div>}{message && <Toast message={message} onClose={() => setMessage('')} />}<Card className="form-card"><div className="form-grid"><Field label="Full name" value={student.name} onChange={() => {}} /><Field label="Email" value={student.email} onChange={() => {}} /><Field label="Phone" value={student.phone} onChange={() => {}} /><SelectField label="Department / course" value={course || courses[0]} onChange={setCourse} options={courses} /><Field label="Academic year" value={student.academicYear ?? ''} onChange={() => {}} /></div><div className="form-actions"><Button onClick={submit} disabled={saving}>{saving ? 'Submitting...' : 'Submit application'}</Button></div></Card></div>
}