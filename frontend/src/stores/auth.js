import { ref, computed } from 'vue'
import { apiService } from '../services/api'

export const useAuthStore = () => {
  const token = ref(localStorage.getItem('token') || null)
  const student = ref(JSON.parse(localStorage.getItem('student') || 'null'))
  const courseSelectionOpen = ref(localStorage.getItem('courseSelectionOpen') === 'true')
  
  const isLoggedIn = computed(() => !!token.value && !!student.value)
  
  const setAuth = (authData) => {
    token.value = authData.access_token
    student.value = authData.student
    courseSelectionOpen.value = authData.course_selection_open
    
    localStorage.setItem('token', authData.access_token)
    localStorage.setItem('student', JSON.stringify(authData.student))
    localStorage.setItem('courseSelectionOpen', authData.course_selection_open)
  }
  
  const clearAuth = () => {
    token.value = null
    student.value = null
    courseSelectionOpen.value = false
    
    localStorage.removeItem('token')
    localStorage.removeItem('student')
    localStorage.removeItem('courseSelectionOpen')
  }
  
  const updateCourseSelectionOpen = (isOpen) => {
    courseSelectionOpen.value = isOpen
    localStorage.setItem('courseSelectionOpen', isOpen)
  }
  
  return {
    token,
    student,
    courseSelectionOpen,
    isLoggedIn,
    setAuth,
    clearAuth,
    updateCourseSelectionOpen
  }
}
