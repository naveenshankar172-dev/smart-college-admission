import { useEffect, useState } from 'react'
import { Search } from 'lucide-react'
import { api, ApiError } from '../../services/api'
import { Badge, Card, EmptyState, ErrorState, LoadingState, SearchBar, SectionHeading, SelectField, TextArea, Toast, Button } from '../../components/common'
import type { ApiScholarshipApplication } from '../../types'

export function RealAdminScholarshipApplications() {
  const [items, setItems] = useState<ApiScholarshipApplication[]>([])
  const [search, setSearch] = useState('')
  const [filter, setFilter] = useState('All statuses')
  const [editing, setEditing] = useState<number | null>(null)
  const [remarks, setRemarks] = useState('')
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)
  const load = () => { setLoading(true); api.getScholarshipApplications().then(setItems).catch(reason => setError(reason instanceof ApiError ? reason.message : 'Unable to load scholarship applications.')).finally(() => setLoading(false)) }
  useEffect(load, [])
  const update = async (item: ApiScholarshipApplication, status: string, note = item.remarks) => { try { const updated = await api.updateScholarshipApplication(item.id, { applicationStatus: status, remarks: note }); setItems(current => current.map(value => value.id === updated.id ? updated : value)); setEditing(null); setMessage('Scholarship application updated.') } catch (reason: unknown) { setError(reason instanceof ApiError ? reason.message : 'Unable to update application.') } }
  if (loading) return <LoadingState />
  if (error) return <ErrorState message={error} onRetry={load} />
  const visible = items.filter(item => (filter === 'All statuses' || item.applicationStatus === filter) && `${item.id} ${item.studentId} ${item.scholarshipId}`.includes(search))
  return <div><SectionHeading eyebrow="Funding operations" title="Scholarship applications" description="Live applications from SQLite with persisted status and remarks." /><div className="toolbar"><SearchBar value={search} onChange={setSearch} placeholder="Search application, student, or scholarship" /><SelectField label="Status" value={filter} onChange={setFilter} options={['All statuses', 'Applied', 'Under Review', 'Approved', 'Rejected', 'Closed']} /></div>{!visible.length ? <EmptyState title="No scholarship applications" message="No records match the current filters." /> : <Card className="table-card"><div className="simple-list">{visible.map(item => <div className="scheme-row" key={item.id}><div><strong>Application #{item.id}</strong><small>Student #{item.studentId} · Scholarship #{item.scholarshipId}</small></div><Badge tone="neutral">{item.eligibilityStatus}</Badge><SelectField label="Application status" value={item.applicationStatus} onChange={value => update(item, value)} options={['Applied', 'Under Review', 'Approved', 'Rejected', 'Closed']} />{editing === item.id ? <div><TextArea label="Remarks" value={remarks} onChange={setRemarks} /><Button onClick={() => update(item, item.applicationStatus, remarks)}>Save remarks</Button></div> : <Button variant="ghost" onClick={() => { setEditing(item.id); setRemarks(item.remarks ?? '') }}>Edit remarks</Button>}<small>{item.remarks || 'No remarks'}</small></div>)}</div></Card>}{message && <Toast message={message} onClose={() => setMessage('')} />}</div>
}