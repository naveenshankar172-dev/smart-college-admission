const STUDENT_ID_KEY = 'admitflow.studentId'
const ROLE_KEY = 'admitflow.role'

export function setStudentSession(studentId: string): void {
  window.localStorage.setItem(STUDENT_ID_KEY, studentId)
  window.localStorage.setItem(ROLE_KEY, 'student')
}

export function setRoleSession(role: 'student' | 'admin'): void {
  window.localStorage.setItem(ROLE_KEY, role)
}

export function getCurrentStudentId(): number {
  const value = window.localStorage.getItem(STUDENT_ID_KEY)
  const id = Number(value)
  if (!value || !Number.isInteger(id) || id < 1) throw new Error('No student session is available.')
  return id
}

export function getCurrentRole(): 'student' | 'admin' | null {
  const role = window.localStorage.getItem(ROLE_KEY)
  return role === 'student' || role === 'admin' ? role : null
}

export function clearSession(): void {
  window.localStorage.removeItem(STUDENT_ID_KEY)
  window.localStorage.removeItem(ROLE_KEY)
  window.localStorage.removeItem('admitflow.applicationId')
}