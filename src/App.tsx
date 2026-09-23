import { useEffect } from 'react'
import { Navigate, Route, Routes, useLocation, useNavigate } from 'react-router-dom'
import { PublicLayout } from './layouts/PublicLayout'
import { PortalLayout } from './layouts/PortalLayout'
import { LandingPage, LoginPage } from './pages/public/Pages'
import { RealRegisterPage } from './pages/public/RealRegisterPage'
import { RealProfilePage } from './pages/student/RealProfilePage'
import { StudentDashboardPage } from './pages/student/StudentDashboardPage'
import { RealNotificationsPage } from './pages/student/RealNotificationsPage'
import { RealAdmissionPage } from './pages/student/RealAdmissionPage'
import { RealStatusPage } from './pages/student/RealStatusPage'
import { RealAdminDashboard } from './pages/admin/RealAdminDashboard'
import { RealAdminReports } from './pages/admin/RealAdminReports'
import { RealAdminSettings } from './pages/admin/RealAdminSettings'
import { RealAdminScholarshipApplications } from './pages/admin/RealAdminScholarshipApplications'
import { ConnectedAdminApplications } from './pages/integrated/Pages'
import { ConnectedAdminScholarshipsPage, ConnectedScholarshipApplyPage, ConnectedScholarshipDetailPage, ConnectedScholarshipsPage } from './pages/integrated/ScholarshipPages'
import { RealAdminApplicationDetail, RealDocumentsPage, RealVerificationPage } from './pages/integrated/DocumentPages'
import { clearSession, hasAdminSession, hasStudentSession } from './services/session'

export default function App() {
	const location = useLocation()
	const navigate = useNavigate()

	useEffect(() => {
		const path = location.pathname
		if (path.startsWith('/student') && !hasStudentSession()) {
			clearSession()
			navigate('/login', { replace: true })
			return
		}
		if (path.startsWith('/admin') && !hasAdminSession()) {
			clearSession()
			navigate('/login', { replace: true })
		}
	}, [location.pathname, navigate])

	return <Routes><Route element={<PublicLayout />}><Route path="/" element={<LandingPage />} /><Route path="/login" element={<LoginPage />} /><Route path="/login/development" element={<Navigate to="/login" replace />} /><Route path="/onboarding" element={<Navigate to="/register" replace />} /><Route path="/register" element={<RealRegisterPage />} /></Route><Route element={<PortalLayout />}><Route path="/student/dashboard" element={<StudentDashboardPage />} /><Route path="/student/admission" element={<RealAdmissionPage />} /><Route path="/student/documents" element={<RealDocumentsPage />} /><Route path="/student/status" element={<RealStatusPage />} /><Route path="/student/scholarships" element={<ConnectedScholarshipsPage />} /><Route path="/student/scholarships/:id" element={<ConnectedScholarshipDetailPage />} /><Route path="/student/scholarships/:id/apply" element={<ConnectedScholarshipApplyPage />} /><Route path="/student/notifications" element={<RealNotificationsPage />} /><Route path="/student/profile" element={<RealProfilePage />} /></Route><Route element={<PortalLayout admin />}><Route path="/admin/dashboard" element={<RealAdminDashboard />} /><Route path="/admin/applications" element={<ConnectedAdminApplications />} /><Route path="/admin/applications/:id" element={<RealAdminApplicationDetail />} /><Route path="/admin/verification" element={<RealVerificationPage />} /><Route path="/admin/scholarships" element={<ConnectedAdminScholarshipsPage />} /><Route path="/admin/scholarship-applications" element={<RealAdminScholarshipApplications />} /><Route path="/admin/reports" element={<RealAdminReports />} /><Route path="/admin/settings" element={<RealAdminSettings />} /></Route><Route path="*" element={<Navigate to="/" replace />} /></Routes>
}
