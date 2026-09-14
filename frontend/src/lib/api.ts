const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export async function fetchApi(endpoint: string, options: RequestInit = {}) {
  const token = typeof window !== 'undefined' ? localStorage.getItem('janseva_token') : null;
  
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> || {}),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'An unexpected error occurred' }));
    throw new Error(errorData.detail || `HTTP Error ${response.status}`);
  }

  return response.json();
}

// Authentication API methods
export const authApi = {
  register: (data: any) => fetchApi('/auth/register', { method: 'POST', body: JSON.stringify(data) }),
  login: (data: any) => fetchApi('/auth/login', { method: 'POST', body: JSON.stringify(data) }),
  getMe: () => fetchApi('/auth/me'),
  updateProfile: (data: any) => fetchApi('/auth/profile', { method: 'PUT', body: JSON.stringify(data) }),
};

// Schemes API methods
export const schemeApi = {
  getAll: (search?: string, category_id?: string) => {
    const params = new URLSearchParams();
    if (search) params.append('search', search);
    if (category_id) params.append('category_id', category_id);
    return fetchApi(`/schemes?${params.toString()}`);
  },
  getCategories: () => fetchApi('/schemes/categories'),
  getById: (id: string) => fetchApi(`/schemes/${id}`),
  searchByAlias: (alias: string) => fetchApi(`/schemes/alias/search?alias=${encodeURIComponent(alias)}`),
};

// Eligibility & AI Recommendation API methods
export const eligibilityApi = {
  checkEligibility: (data: any) => fetchApi('/eligibility/check', { method: 'POST', body: JSON.stringify(data) }),
  reasonLifeEvent: (lifeEventPrompt: string) => fetchApi('/eligibility/life-event', { method: 'POST', body: JSON.stringify({ prompt: lifeEventPrompt }) }),
  getRecommendations: () => fetchApi('/eligibility/recommendations'),
};

// RAG & Voice AI Assistant API methods
export const aiApi = {
  askAssistant: (query: string, explanationLevel: 'legal' | 'simple' | 'eli10' = 'simple') => 
    fetchApi('/rag/query', { method: 'POST', body: JSON.stringify({ query, explanation_level: explanationLevel }) }),
  getChatHistory: () => fetchApi('/rag/history'),
  processVoiceAudio: (formData: FormData) => {
    const token = typeof window !== 'undefined' ? localStorage.getItem('janseva_token') : null;
    return fetch(`${API_BASE_URL}/voice/process`, {
      method: 'POST',
      headers: token ? { 'Authorization': `Bearer ${token}` } : {},
      body: formData
    }).then(res => res.json());
  }
};

// Application Assistant & Forms API methods
export const applicationApi = {
  createApplication: (schemeId: string) => fetchApi('/applications', { method: 'POST', body: JSON.stringify({ scheme_id: schemeId }) }),
  getUserApplications: () => fetchApi('/applications'),
  getApplicationDetails: (id: string) => fetchApi(`/applications/${id}`),
  uploadDocument: (applicationId: string, docType: string, file: File) => {
    const token = typeof window !== 'undefined' ? localStorage.getItem('janseva_token') : null;
    const formData = new FormData();
    formData.append('file', file);
    formData.append('document_type', docType);
    return fetch(`${API_BASE_URL}/applications/${applicationId}/upload-document`, {
      method: 'POST',
      headers: token ? { 'Authorization': `Bearer ${token}` } : {},
      body: formData
    }).then(res => res.json());
  },
  generateFormPdf: (applicationId: string, formData: any) => fetchApi(`/applications/${applicationId}/generate-pdf`, { method: 'POST', body: JSON.stringify(formData) }),
};

// Dashboard & Analytics API methods
export const dashboardApi = {
  getStats: () => fetchApi('/dashboard/stats'),
  getAdminAnalytics: () => fetchApi('/admin/analytics'),
  triggerMySchemeSync: () => fetchApi('/admin/update-schemes', { method: 'POST' }),
};

