import { useEffect, useState } from 'react'
import { Card, ErrorState, LoadingState, SectionHeading } from '../../components/common'
import { api, ApiError } from '../../services/api'
import type { DashboardStatistics } from '../../types'

export function RealAdminReports() {
  const [stats, setStats] = useState<DashboardStatistics | null>(null)
  const [error, setError] = useState('')
  useEffect(() => { api.getAdminStatistics().then(result => setStats(result.stats)).catch(reason => setError(reason instanceof ApiError ? reason.message : 'Unable to load reports.')) }, [])
  if (error) return <ErrorState message={error} onRetry={() => window.location.reload()} />
  if (!stats) return <LoadingState />
  return <div><SectionHeading eyebrow="Reports" title="Database reports" description="These summaries are calculated from current SQLite records." /><div className="report-grid"><Card><h3 className="heading">Students</h3><strong className="report-number">{stats.totalStudents ?? 0}</strong><p className="muted">Registered students</p></Card><Card><h3 className="heading">Admission applications</h3><strong className="report-number">{stats.totalApplications}</strong><p className="muted">Stored applications</p></Card><Card><h3 className="heading">Pending documents</h3><strong className="report-number">{stats.pendingVerification}</strong><p className="muted">Pending or processing</p></Card><Card><h3 className="heading">Manual review documents</h3><strong className="report-number">{stats.manualReview}</strong><p className="muted">Needs officer review</p></Card><Card><h3 className="heading">Scholarship applications</h3><strong className="report-number">{stats.scholarshipApplications}</strong><p className="muted">Stored applications</p></Card><Card><h3 className="heading">Rejected scholarships</h3><strong className="report-number">{stats.rejected}</strong><p className="muted">Current status count</p></Card></div></div>
}