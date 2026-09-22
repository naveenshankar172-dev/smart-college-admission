export type Role = 'student' | 'admin'
export type Status = 'verified' | 'pending' | 'manual-review' | 'rejected' | 'missing'
export type ApplicationStatus = 'draft' | 'submitted' | 'under-verification' | 'approved' | 'rejected' | 'manual-review'

export interface User { id: string; name: string; email: string; role: Role; avatar?: string }
export interface Student { id: string; userId: string; name: string; email: string; phone: string; course: string; academicScore: number; city: string; academicYear?: string; emailUpdates?: boolean; scholarshipSuggestions?: boolean }
export interface VerificationResult { status: Status; detectedInformation?: string; remarks?: string; checkedAt?: string }
export interface Document { id: string; name: string; required: boolean; studentId?: string; applicationId?: string; fileName?: string; originalFilename?: string; storedFilename?: string; filePath?: string; fileType?: string; fileSize?: number | string; uploadedAt?: string; ocrStatus?: string; extractedText?: string; matchedFields?: string[]; mismatchedFields?: string[]; verification: VerificationResult; uploadProgress?: number }
export interface Application { id: string; student: Student; course: string; submittedAt?: string; documentSummary: string; status: ApplicationStatus; documents: Document[]; timeline: { label: string; date?: string; status: 'complete' | 'current' | 'upcoming' }[] }
export interface Scholarship { id: string; name: string; provider: string; amount: string; deadline: string; eligibility: string[]; requiredDocuments: string[]; description: string; status: 'open' | 'closing-soon' | 'closed' }
export interface ScholarshipApplication { id: string; scholarshipId: string; studentName: string; scholarshipName: string; eligibilityStatus: string; documentStatus: string; applicationStatus: string }
export interface ApiScholarship { id: number; name: string; schemeName: string; description: string; provider: string; eligibilitySummary: string; eligibilityRules: Record<string, unknown>; requiredDocuments: string[]; applicationStartDate?: string; applicationEndDate?: string; amountOrBenefit: string; status: string; isActive: boolean; createdAt?: string; updatedAt?: string }
export interface ApiScholarshipApplication { id: number; studentId: number; scholarshipId: number; eligibilityStatus: string; verificationStatus: string; applicationStatus: string; remarks?: string; appliedAt?: string; updatedAt?: string }
export interface EligibilityResult { studentId: number; scholarshipId: number; eligibilityStatus: string; matchedRules: string[]; unmatchedRules: string[]; missingInformation: string[]; requiredDocuments: string[]; availableDocuments: string[]; missingDocuments: string[]; remarks: string }
export interface Notification { id: string; title: string; message: string; type: 'document' | 'admission' | 'scholarship' | 'system'; date: string; read: boolean }
export interface DashboardStatistics { totalStudents?: number; totalApplications: number; pendingVerification: number; verified: number; manualReview: number; rejected: number; scholarshipApplications: number; trend: { label: string; value: number }[]; verification: { label: string; value: number }[] }
export interface RPAStatus { status: 'running' | 'idle' | 'error'; lastRun: string; applicationsProcessed: number; documentsVerified: number }
