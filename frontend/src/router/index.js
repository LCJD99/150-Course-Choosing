import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes = [
  {
    path: '/',
    name: 'login',
    component: () => import('../views/LoginView.vue')
  },
  {
    path: '/selection',
    name: 'selection',
    component: () => import('../views/SelectionView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/admin',
    name: 'dashboard',
    component: () => import('../views/DashboardView.vue')
  },
  {
    path: '/admin/import',
    name: 'import',
    component: () => import('../views/ImportView.vue')
  },
  {
    path: '/admin/courses',
    name: 'courses',
    component: () => import('../views/CoursesView.vue')
  },
  {
    path: '/admin/students',
    name: 'students',
    component: () => import('../views/StudentsView.vue')
  },
  {
    path: '/admin/courses/:courseId/students',
    name: 'course-students',
    component: () => import('../views/CourseStudentsView.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const { isLoggedIn } = useAuthStore()  
  if (to.meta.requiresAuth && !isLoggedIn.value) {
    next('/')
  } else if (to.name === 'login' && isLoggedIn.value) {
    next('/selection')
  } else {
    next()
  }
})

export default router
