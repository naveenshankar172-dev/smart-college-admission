import { useEffect, useState } from 'react'
import { Bell } from 'lucide-react'
import { api, ApiError } from '../../services/api'
import { getCurrentStudentId } from '../../services/session'
import { Button, Card, EmptyState, ErrorState, LoadingState, SectionHeading } from '../../components/common'
import type { Notification } from '../../types'

export function RealNotificationsPage() {
  const [items, setItems] = useState<Notification[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const load = () => { setLoading(true); api.getNotifications(getCurrentStudentId()).then(setItems).catch(reason => setError(reason instanceof ApiError ? reason.message : 'Unable to load notifications.')).finally(() => setLoading(false)) }
  useEffect(load, [])
  const markRead = async (item: Notification) => { try { setItems(current => current.map(value => value.id === item.id ? { ...value, read: true } : value)); await api.markNotificationRead(item.id) } catch { load() } }
  const markAll = async () => { try { const updated = await api.markAllNotificationsRead(getCurrentStudentId()); setItems(updated) } catch { setError('Unable to mark notifications as read.') } }
  if (loading) return <LoadingState />
  if (error) return <ErrorState message={error} onRetry={load} />
  if (!items.length) return <EmptyState title="No notifications" message="Updates from your application will appear here." />
  return <div><SectionHeading eyebrow="Connected inbox" title="Notifications" description="Live notification records for the authenticated student." action={<Button variant="secondary" onClick={markAll}>Mark all as read</Button>} /><div className="notification-list">{items.map(item => <Card key={item.id} className={!item.read ? 'unread' : ''}><div className="notification-row"><span className="notification-icon"><Bell size={16} /></span><div><div className="card-top"><h3 className="heading">{item.title}</h3>{!item.read && <Button variant="ghost" onClick={() => markRead(item)}>Mark read</Button>}</div><p className="muted">{item.message}</p><small>{item.date}</small></div></div></Card>)}</div></div>
}