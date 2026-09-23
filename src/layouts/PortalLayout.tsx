import { type ReactNode, useEffect, useState } from 'react'
import { Bell, ChevronDown, House, LayoutDashboard, LogOut, Settings, ShieldCheck, UserRound, X } from 'lucide-react'
import { Link, NavLink, Outlet, useLocation, useNavigate } from 'react-router-dom'
import { MobileMenuButton } from '../components/common'
import { api } from '../services/api'
import { clearSession, getCurrentRole, getCurrentStudentId, hasStudentSession } from '../services/session'

const studentLinks = [{ to: '/student/dashboard', label: 'Overview', icon: LayoutDashboard }, { to: '/student/admission', label: 'Admission application', icon: ShieldCheck }, { to: '/student/documents', label: 'My documents', icon: ShieldCheck }, { to: '/student/status', label: 'Application status', icon: House }, { to: '/student/scholarships', label: 'Scholarships', icon: ShieldCheck }, { to: '/student/notifications', label: 'Notifications', icon: Bell }, { to: '/student/profile', label: 'Profile', icon: UserRound }]
const adminLinks = [{ to: '/admin/dashboard', label: 'Overview', icon: LayoutDashboard }, { to: '/admin/applications', label: 'Applications', icon: ShieldCheck }, { to: '/admin/verification', label: 'Document verification', icon: ShieldCheck }, { to: '/admin/scholarships', label: 'Scholarship schemes', icon: ShieldCheck }, { to: '/admin/scholarship-applications', label: 'Scholarship applications', icon: ShieldCheck }, { to: '/admin/reports', label: 'Reports', icon: House }, { to: '/admin/settings', label: 'Settings', icon: Settings }]
export function PortalLayout({ admin = false }: { admin?: boolean }) {
  const [open, setOpen] = useState(false)
  const [profileOpen, setProfileOpen] = useState(false)
  const [studentName, setStudentName] = useState('')
  const location = useLocation()
  const navigate = useNavigate()
  const links = admin ? adminLinks : studentLinks

  useEffect(() => {
    try {
      if (admin) {
        if (getCurrentRole() !== 'admin') {
          clearSession()
          navigate('/login', { replace: true })
        }
        return
      }

      if (!hasStudentSession()) {
        clearSession()
        navigate('/login', { replace: true })
        return
      }

      api.getStudent(getCurrentStudentId())
        .then(student => setStudentName(student.name))
        .catch(() => {
          clearSession()
          navigate('/login', { replace: true })
        })
    } catch {
      clearSession()
      navigate('/login', { replace: true })
    }
  }, [admin, navigate])

  const logout = () => {
    clearSession()
    navigate('/login', { replace: true })
  }
 return <div className="portal"><a className="skip-link" href="#main-content">Skip to content</a>{open && <button className="nav-scrim" aria-label="Close navigation" onClick={() => setOpen(false)} />}<aside className={`sidebar ${open ? 'sidebar-open' : ''}`}><div className="brand"><span className="brand-mark">A</span><span><strong>AdmitFlow</strong><small>{admin ? 'Operations console' : 'Student portal'}</small></span><button className="icon-btn sidebar-close" aria-label="Close navigation" onClick={() => setOpen(false)}><X size={18} /></button></div><nav aria-label="Primary navigation">{links.map(({ to, label, icon: Icon }) => <NavLink key={to} to={to} onClick={() => setOpen(false)} className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}><Icon size={18} aria-hidden="true" /><span>{label}</span></NavLink>)}</nav><div className="sidebar-foot"><button type="button" className="nav-link" onClick={logout}><LogOut size={18} /> Sign out</button></div></aside><div className="portal-main"><header className="topbar"><MobileMenuButton onClick={() => setOpen(true)} /><div className="crumb"><span>{admin ? 'Operations' : 'Student workspace'}</span><strong>{location.pathname.split('/').filter(Boolean).at(-1)?.replaceAll('-', ' ')}</strong></div><div className="top-actions"><button className="icon-btn" aria-label="View notifications" onClick={() => navigate('/student/notifications')}><Bell size={19} /><i /></button><div className="profile-menu"><button className="profile-chip" onClick={() => setProfileOpen(value => !value)}><span className="avatar">{admin ? 'AD' : studentName ? studentName.split(' ').map(item => item[0]).join('').slice(0, 2).toUpperCase() : ''}</span><span className="profile-name">{admin ? 'Admissions team' : studentName}</span><ChevronDown size={15} /></button>{profileOpen && <div className="profile-dropdown"><Link to={admin ? '/admin/settings' : '/student/profile'} onClick={() => setProfileOpen(false)}>Profile</Link><Link to={admin ? '/admin/applications' : '/student/status'} onClick={() => setProfileOpen(false)}>My Applications</Link><Link to={admin ? '/admin/verification' : '/student/documents'} onClick={() => setProfileOpen(false)}>My Documents</Link><Link to={admin ? '/admin/settings' : '/student/notifications'} onClick={() => setProfileOpen(false)}>Notifications</Link><Link to={admin ? '/admin/settings' : '/student/profile'} onClick={() => setProfileOpen(false)}>Settings</Link><button type="button" onClick={logout}>Logout</button></div>}</div></div></header><main id="main-content" className="page-content"><Outlet /></main></div></div> }
