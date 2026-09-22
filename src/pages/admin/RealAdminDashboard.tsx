import { useEffect, useState } from 'react'
import { CircleAlert, FileCheck2, ShieldAlert, Users } from 'lucide-react'
import { api, ApiError } from '../../services/api'
import { Card, ErrorState, LoadingState, SectionHeading } from '../../components/common'
import type { DashboardStatistics } from '../../types'

export function RealAdminDashboard() {
  const [stats, setStats] = useState<DashboardStatistics | null>(null)
  const [error, setError] = useState('')
  useEffect(() => { api.getAdminStatistics().then(result => setStats(result.stats)).catch(reason => setError(reason instanceof ApiError ? reason.message : 'Unable to load admin statistics.')) }, [])
  if (error) return <ErrorState message={error} onRetry={() => window.location.reload()} />
  if (!stats) return <LoadingState />
  const items = [{ label: 'Admission applications', value: stats.totalApplications, icon: FileCheck2 }, { label: 'Pending documents', value: stats.pendingVerification, icon: CircleAlert }, { label: 'Manual review documents', value: stats.manualReview, icon: CircleAlert }, { label: 'Scholarship applications', value: stats.scholarshipApplications, icon: ShieldAlert }, { label: 'Approved scholarship applications', value: stats.verified, icon: FileCheck2 }, { label: 'Rejected scholarship applications', value: stats.rejected, icon: CircleAlert }]
  return <div><SectionHeading eyebrow="Operations overview" title="Live admissions metrics" description="Counts are calculated from the SQLite database." /><div className="kpi-grid"><Card className="kpi-card"><span className="kpi-icon"><Users size={18} /></span><span>Students</span><strong>{stats.totalStudents ?? 0}</strong></Card>{items.map(({ label, value, icon: Icon }) => <Card className="kpi-card" key={label}><span className="kpi-icon"><Icon size={18} /></span><span>{label}</span><strong>{value}</strong></Card>)}</div></div>
}