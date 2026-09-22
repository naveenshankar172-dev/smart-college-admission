import { useEffect, useState } from 'react'
import { Award, Bell, CalendarDays, Check, ClipboardCheck, FileCheck2, GraduationCap, UploadCloud } from 'lucide-react'
import { Link } from 'react-router-dom'
import { Badge, Card, EmptyState, ErrorState, StatusBadge } from '../../components/common'
import { api, ApiError } from '../../services/api'
import { getCurrentStudentId } from '../../services/session'
import type { ApiScholarshipApplication, Application, Document, EligibilityResult, Notification, Student, ApiScholarship } from '../../types'

interface DashboardData {
  student: Student
  application: Application | null
  documents: Document[]
  notifications: Notification[]
  scholarships: ApiScholarship[]
  eligibility: EligibilityResult[]
  scholarshipApplications: ApiScholarshipApplication[]
}

const formatDate = (value?: string) => value ? new Date(value).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }) : 'Not available'
const statusText = (value: string) => value.replaceAll('-', ' ')
const initials = (name: string) => name.split(' ').filter(Boolean).slice(0, 2).map(part => part[0]).join('').toUpperCase()

function DashboardLoadingState() {
  return <div className="dashboard-loading" role="status" aria-label="Loading student dashboard">
    <div className="dashboard-loading-head"><span /><span /></div>
    <div className="dashboard-loading-summary"><span /><span /><span /><span /></div>
    <div className="dashboard-loading-panel"><span /><span /><span /></div>
    <div className="dashboard-loading-columns"><span /><span /></div>
  </div>
}

function loadDashboard(studentId: number): Promise<DashboardData> {
  return Promise.all([
    api.getStudentDashboard(studentId),
    api.getStudentScholarshipEligibility(studentId),
    api.getStudentScholarshipApplications(studentId),
  ]).then(([dashboard, eligibility, scholarshipApplications]) => ({ ...dashboard, eligibility, scholarshipApplications }))
}

export function StudentDashboardPage() {
  const [data, setData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [attempt, setAttempt] = useState(0)

  useEffect(() => {
    let active = true
    setLoading(true)
    setError('')
    try {
      loadDashboard(getCurrentStudentId()).then(value => { if (active) setData(value) }).catch(reason => { if (active) setError(reason instanceof ApiError ? reason.message : 'Unable to load your student dashboard.') }).finally(() => { if (active) setLoading(false) })
    } catch (reason: unknown) {
      setError(reason instanceof Error ? reason.message : 'No authenticated student session is available.')
      setLoading(false)
    }
    return () => { active = false }
  }, [attempt])

  if (loading) return <DashboardLoadingState />
  if (error || !data) return <ErrorState message={error || 'Dashboard data is unavailable.'} onRetry={() => setAttempt(value => value + 1)} />

  const { student, application, documents, notifications, scholarships, eligibility, scholarshipApplications } = data
  const verifiedDocuments = documents.filter(document => document.verification.status === 'verified').length
  const unreadNotifications = notifications.filter(notification => !notification.read).length
  const activeScholarships = scholarships.filter(scholarship => scholarship.isActive)
  const recentDocuments = [...documents].sort((left, right) => new Date(right.uploadedAt ?? 0).getTime() - new Date(left.uploadedAt ?? 0).getTime()).slice(0, 5)
  const progressSteps = [
    { label: 'Registration', complete: true },
    { label: 'Application', complete: Boolean(application) },
    { label: 'Documents', complete: documents.length > 0 },
    { label: 'Verification', complete: documents.length > 0 && verifiedDocuments === documents.length },
    { label: 'Completed', complete: application?.status === 'approved' },
  ]
  const currentStep = progressSteps.findIndex(step => !step.complete)
  const applicationProgress = Math.round((progressSteps.filter(step => step.complete).length / progressSteps.length) * 100)
  const scholarshipState = (scholarshipId: number) => {
    const submitted = scholarshipApplications.find(item => item.scholarshipId === scholarshipId)
    if (submitted) return { label: statusText(submitted.applicationStatus), tone: submitted.applicationStatus.toLowerCase() === 'approved' ? 'green' as const : 'amber' as const }
    const screened = eligibility.find(item => item.scholarshipId === scholarshipId)
    if (screened) return { label: screened.eligibilityStatus, tone: screened.eligibilityStatus === 'Potentially Eligible' ? 'green' as const : 'amber' as const }
    return { label: 'Screening available', tone: 'neutral' as const }
  }

  return <div className="student-dashboard">
    <section className="dashboard-welcome">
      <div>
        <p className="eyebrow">Student workspace</p>
        <h1 className="heading">Welcome back, {student.name.split(' ')[0]}.</h1>
        <p className="muted">Keep your admission steps moving from one clear view.</p>
      </div>
      <div className="dashboard-identity"><span className="dashboard-avatar">{initials(student.name)}</span><div><strong>{student.name}</strong><span>{student.course || 'Course not set'}</span></div></div>
    </section>

    <section className="dashboard-summary" aria-label="Admission summary">
      <Card className="summary-card"><span className="summary-icon"><ClipboardCheck size={19} /></span><span className="summary-label">Application status</span><strong>{application ? statusText(application.status) : 'Not started'}</strong><small>{application ? application.id : 'Start your application'}</small></Card>
      <Card className="summary-card"><span className="summary-icon"><FileCheck2 size={19} /></span><span className="summary-label">Documents</span><strong>{verifiedDocuments}/{documents.length}</strong><small>{documents.length ? 'verified documents' : 'No uploads yet'}</small></Card>
      <Card className="summary-card"><span className="summary-icon"><Award size={19} /></span><span className="summary-label">Scholarships</span><strong>{activeScholarships.length}</strong><small>{scholarshipApplications.length ? `${scholarshipApplications.length} application${scholarshipApplications.length === 1 ? '' : 's'}` : 'opportunities available'}</small></Card>
      <Card className="summary-card"><span className="summary-icon"><Bell size={19} /></span><span className="summary-label">Notifications</span><strong>{unreadNotifications}</strong><small>{unreadNotifications ? 'unread updates' : 'all caught up'}</small></Card>
    </section>

    <Card className="progress-card">
      <div className="dashboard-card-heading"><div><p className="eyebrow">Admission journey</p><h2 className="heading">Your progress</h2></div><span className="progress-percent">{applicationProgress}% complete</span></div>
      <div className="journey-track" aria-label="Admission progress">{progressSteps.map((step, index) => <div className={`journey-step ${step.complete ? 'is-complete' : index === currentStep ? 'is-current' : ''}`} key={step.label}><span className="journey-dot">{step.complete ? <Check size={15} /> : index + 1}</span><strong>{step.label}</strong>{index < progressSteps.length - 1 && <span className="journey-line" />}</div>)}</div>
    </Card>

    <div className="dashboard-columns">
      <Card className="documents-panel"><div className="dashboard-card-heading"><div><p className="eyebrow">Document centre</p><h2 className="heading">Recent verification</h2></div><Link className="inline-link" to="/student/documents">View all <span aria-hidden="true">→</span></Link></div>{recentDocuments.length ? <div className="dashboard-table-wrap"><table className="dashboard-table"><caption className="sr-only">Recent document verification status</caption><thead><tr><th scope="col">Document</th><th scope="col">Status</th><th scope="col">Updated</th></tr></thead><tbody>{recentDocuments.map(document => <tr key={document.id}><td><div className="document-cell"><span className="document-cell-icon"><FileCheck2 size={16} /></span><div><strong>{document.name}</strong><small>{document.originalFilename ?? document.fileName ?? 'File record'}</small></div></div></td><td><StatusBadge status={document.verification.status} /></td><td>{formatDate(document.uploadedAt)}</td></tr>)}</tbody></table></div> : <EmptyState title="No documents yet" message="Upload your required documents to begin verification." />}</Card>
      <Card className="actions-panel"><div className="dashboard-card-heading"><div><p className="eyebrow">Next steps</p><h2 className="heading">Quick actions</h2></div><GraduationCap size={22} className="panel-mark" /></div><div className="quick-actions"><Link className="quick-action" to="/student/admission"><span><ClipboardCheck size={18} /></span><div><strong>Complete application</strong><small>Review and submit your details</small></div><span aria-hidden="true">→</span></Link><Link className="quick-action" to="/student/documents"><span><UploadCloud size={18} /></span><div><strong>Upload documents</strong><small>Add files for verification</small></div><span aria-hidden="true">→</span></Link><Link className="quick-action" to="/student/scholarships"><span><Award size={18} /></span><div><strong>View scholarships</strong><small>Explore screening opportunities</small></div><span aria-hidden="true">→</span></Link></div></Card>
    </div>

    <Card className="scholarship-summary"><div className="dashboard-card-heading"><div><p className="eyebrow">Funding opportunities</p><h2 className="heading">Scholarship summary</h2></div><Link className="inline-link" to="/student/scholarships">Explore all <span aria-hidden="true">→</span></Link></div>{activeScholarships.length ? <div className="scholarship-summary-grid">{activeScholarships.slice(0, 3).map(scholarship => { const state = scholarshipState(scholarship.id); return <Link className="scholarship-summary-item" to={`/student/scholarships/${scholarship.id}`} key={scholarship.id}><span className="scholarship-mark"><Award size={17} /></span><div><strong>{scholarship.schemeName}</strong><small>{scholarship.provider}</small></div><Badge tone={state.tone}>{state.label}</Badge></Link> })}</div> : <EmptyState title="No active scholarships" message="New opportunities will appear here when available." />}</Card>

    <div className="dashboard-footer-note"><CalendarDays size={17} /><span>Keep your profile and documents current to receive the most relevant admission updates.</span></div>
  </div>
}