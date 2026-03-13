// API service for backend communication
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || `${window.location.protocol}//${window.location.hostname}:8000`

class ApiService {
  async request(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers
    }
    
    const response = await fetch(url, {
      ...options,
      headers
    })
    
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Request failed')
    }
    
    return response.json()
  }
  
  async get(endpoint, token = null) {
    const headers = token ? { 'Authorization': `Bearer ${token}` } : {}
    return this.request(endpoint, { method: 'GET', headers })
  }
  
  async post(endpoint, data, token = null) {
    const headers = token ? { 'Authorization': `Bearer ${token}` } : {}
    return this.request(endpoint, { 
      method: 'POST', 
      headers,
      body: JSON.stringify(data)
    })
  }
  
  async put(endpoint, data, token = null) {
    const headers = token ? { 'Authorization': `Bearer ${token}` } : {}
    return this.request(endpoint, { 
      method: 'PUT', 
      headers,
      body: JSON.stringify(data)
    })
  }

  async delete(endpoint, token = null) {
    const headers = token ? { 'Authorization': `Bearer ${token}` } : {}
    return this.request(endpoint, { method: 'DELETE', headers })
  }
  
  // Student endpoints
  async login(name, idCard) {
    return this.post('/api/student/login', { name, id_card: idCard })
  }
  
  async getCourses(day, token) {
    return this.get(`/api/student/courses?day=${day}`, token)
  }
  
  async getSelections(token) {
    return this.get('/api/student/selections', token)
  }
  
  async getProgress(token) {
    return this.get('/api/student/progress', token)
  }
  
  async selectCourse(day, courseId, token) {
    return this.put(`/api/student/selections/${day}`, { course_id: courseId }, token)
  }

  async logout(token) {
    return this.post('/api/student/logout', {}, token)
  }
  
  // Admin endpoints
  async importCourses(file) {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await fetch(`${API_BASE_URL}/api/admin/import/courses`, {
      method: 'POST',
      body: formData
    })
    
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Import failed')
    }
    
    return response.json()
  }
  
  async importCourseGrades(file) {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await fetch(`${API_BASE_URL}/api/admin/import/course-grades`, {
      method: 'POST',
      body: formData
    })
    
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Import failed')
    }
    
    return response.json()
  }
  
  async importStudents(file) {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await fetch(`${API_BASE_URL}/api/admin/import/students`, {
      method: 'POST',
      body: formData
    })
    
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Import failed')
    }
    
    return response.json()
  }
  
  async setSelectionOpen(open) {
    return this.put('/api/admin/settings/selection-open', { open })
  }
  
  async getSelectionOpen() {
    return this.get('/api/admin/settings/selection-open')
  }

  async getAdminCourses() {
    return this.get('/api/admin/courses')
  }

  async getAdminStats() {
    return this.get('/api/admin/stats')
  }

  async getAdminStudents(filters = {}) {
    const params = new URLSearchParams()
    if (filters.grade) params.append('grade', String(filters.grade))
    if (filters.class_name) params.append('class_name', filters.class_name)
    const query = params.toString()
    return this.get(`/api/admin/students${query ? `?${query}` : ''}`)
  }

  async getSelectedStudents(filters = {}) {
    const params = new URLSearchParams()
    if (filters.grade) params.append('grade', String(filters.grade))
    if (filters.class_name) params.append('class_name', filters.class_name)
    const query = params.toString()
    return this.get(`/api/admin/selected-students${query ? `?${query}` : ''}`)
  }

  async clearStudentSelections(studentId) {
    return this.delete(`/api/admin/selected-students/${studentId}/selections`)
  }

  async deleteAdminCourse(courseId) {
    return this.delete(`/api/admin/courses/${courseId}`)
  }
}

export const apiService = new ApiService()
