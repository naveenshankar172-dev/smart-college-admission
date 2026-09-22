import { useEffect, useState } from 'react'
import { Check, Clock3 } from 'lucide-react'
import { api, ApiError } from '../../services/api'
import { getCurrentStudentId } from '../../services/session'
import { Card, EmptyState, ErrorState, LoadingState, SectionHeading, StatusBadge } from '../../components/common'
import type { Application } from '../../types'

export function RealStatusPage() {
  const [applications, setApplications] = useState<Application[]>([])
  const [error, setError] = useState('')
  useEffect(() => { api.getStudentApplications(getCurrentStudentId()).then(setApplications).catch(reason => setError(reason instanceof ApiError ? reason.message : 'Unable to load application status.')) }, [])
  if (error) return <ErrorState message={error} onRetry={() => window.location.reload()} />
  if (!applications.length) return <LoadingState />
  const application = applications[0]
  return <div><SectionHeading eyebrow="Admission status" title="Your application timeline" description="This status is loaded from the authenticated student application record." /><Card className="timeline-card"><div className="timeline-status"><div><span className="mini-label">APPLICATION ID</span><h3 className="heading">{application.id}</h3></div><StatusBadge status={application.status} /></div><div className="timeline">{application.timeline.map(item => <div className={`timeline-item ${item.status}`} key={item.label}><span className="timeline-dot">{item.status === 'complete' ? <Check size={15} /> : item.status === 'current' ? <Clock3 size={15} /> : ''}</span><div><h3>{item.label}</h3><p>{item.date ?? 'Waiting for backend status'}</p></div></div>)}</div></Card></div>
}