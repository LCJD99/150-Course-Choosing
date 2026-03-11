<template>
  <div class="dashboard-container">
    <div class="header">
      <h1 class="title">管理后台</h1>
      <div class="switch-container">
        <span class="switch-label">选课开关</span>
        <label class="switch">
          <input type="checkbox" v-model="isOpen" @change="handleToggle" :disabled="loading" />
          <span class="slider" :class="{ on: isOpen }"></span>
        </label>
      </div>
    </div>
    
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon">📚</div>
        <div class="stat-content">
          <div class="stat-label">总课程数</div>
          <div class="stat-value">{{ stats.total_courses }}</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon">👥</div>
        <div class="stat-content">
          <div class="stat-label">总学生数</div>
          <div class="stat-value">{{ stats.total_students }}</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon">✅</div>
        <div class="stat-content">
          <div class="stat-label">已完成选课</div>
          <div class="stat-value">{{ stats.completed_selections }}</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon">🎯</div>
        <div class="stat-content">
          <div class="stat-label">完成度</div>
          <div class="stat-value">{{ stats.completion_rate }}%</div>
        </div>
      </div>
    </div>
    
    <div class="section">
      <h2 class="section-title">按天选课统计</h2>
      <div class="day-stats">
        <div v-for="day in dayStats" :key="day.day" class="day-stat">
          <div class="day-label">{{ getDayName(day.day) }}</div>
          <div class="day-bar">
            <div class="day-bar-fill" :style="{ width: day.percentage + '%' }"></div>
          </div>
          <div class="day-count">{{ day.count }} 人</div>
        </div>
      </div>
    </div>
    
    <div class="section">
      <h2 class="section-title">热门课程</h2>
      <div class="course-list">
        <div v-for="course in topCourses" :key="course.id" class="course-item">
          <div class="course-info">
            <div class="course-name">{{ course.course_name }}</div>
            <div class="course-meta">
              <span class="teacher">{{ course.teacher }}</span>
              <span class="day">{{ getDayName(course.day) }}</span>
            </div>
          </div>
          <div class="course-progress">
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: course.fill_rate + '%' }"></div>
            </div>
            <div class="progress-text">{{ course.enrolled }}/{{ course.capacity }}</div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="section">
      <h2 class="section-title">快速操作</h2>
      <div class="quick-actions">
        <button @click="$router.push('/admin/import')" class="action-btn">
          <span class="btn-icon">📤</span>
          <span class="btn-text">导入数据</span>
        </button>
        <button @click="$router.push('/admin/courses')" class="action-btn">
          <span class="btn-icon">📋</span>
          <span class="btn-text">课程管理</span>
        </button>
        <button @click="$router.push('/')" class="action-btn secondary">
          <span class="btn-icon">🔙</span>
          <span class="btn-text">返回选课</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { apiService } from '../services/api'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const { updateCourseSelectionOpen } = useAuthStore()

const isOpen = ref(false)
const loading = ref(false)
const stats = ref({
  total_courses: 0,
  total_students: 0,
  completed_selections: 0,
  completion_rate: 0
})

const dayStats = ref([])
const topCourses = ref([])

const getDayName = (day) => {
  const dayNames = { 1: '周一', 3: '周三', 4: '周四', 5: '周五' }
  return dayNames[day]
}

const loadStats = async () => {
  try {
    const selectionOpen = await apiService.getSelectionOpen()
    isOpen.value = selectionOpen.open
    updateCourseSelectionOpen(selectionOpen.open)
  } catch (err) {
    console.error('Failed to load settings:', err)
  }
}

const handleToggle = async () => {
  loading.value = true
  try {
    await apiService.setSelectionOpen(isOpen.value)
    updateCourseSelectionOpen(isOpen.value)
    alert(`选课已${isOpen.value ? '开启' : '关闭'}`)
  } catch (err) {
    console.error('Failed to toggle selection:', err)
    isOpen.value = !isOpen.value
    alert('操作失败，请重试')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadStats()
  
  stats.value = {
    total_courses: 4,
    total_students: 2,
    completed_selections: 1,
    completion_rate: 12.5
  }
  
  dayStats.value = [
    { day: 1, count: 1, percentage: 25 },
    { day: 3, count: 0, percentage: 0 },
    { day: 4, count: 0, percentage: 0 },
    { day: 5, count: 0, percentage: 0 }
  ]
  
  topCourses.value = [
    { id: 1, course_name: '非遗剪纸与重彩画', teacher: '李艳华', day: 1, enrolled: 1, capacity: 15, fill_rate: 7 }
  ]
})
</script>

<style scoped>
.dashboard-container {
  min-height: 100vh;
  background: #f5f7fa;
  padding: 20px;
}

.header {
  background: white;
  padding: 24px;
  border-radius: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  margin-bottom: 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title {
  font-size: 28px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.switch-container {
  display: flex;
  align-items: center;
  gap: 16px;
}

.switch-label {
  font-size: 16px;
  color: #555;
  font-weight: 500;
}

.switch {
  position: relative;
  display: inline-block;
  width: 56px;
  height: 32px;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: #ccc;
  transition: 0.4s;
  border-radius: 32px;
}

.slider:before {
  position: absolute;
  content: '';
  height: 26px;
  width: 26px;
  left: 3px;
  bottom: 3px;
  background: white;
  transition: 0.4s;
  border-radius: 50%;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

input:checked + .slider {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

input:checked + .slider:before {
  transform: translateX(24px);
}

.slider.on {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

input:disabled + .slider {
  opacity: 0.5;
  cursor: not-allowed;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 20px;
  margin-bottom: 32px;
}

.stat-card {
  background: white;
  padding: 24px;
  border-radius: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  display: flex;
  align-items: center;
  gap: 16px;
  transition: transform 0.2s, box-shadow 0.2s;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  font-size: 48px;
}

.stat-content {
  flex: 1;
}

.stat-label {
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #333;
}

.section {
  background: white;
  padding: 24px;
  border-radius: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  margin-bottom: 24px;
}

.section-title {
  font-size: 20px;
  font-weight: 600;
  color: #333;
  margin: 0 0 20px 0;
}

.day-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.day-stat {
  text-align: center;
}

.day-label {
  font-size: 16px;
  font-weight: 600;
  color: #555;
  margin-bottom: 12px;
}

.day-bar {
  height: 24px;
  background: #f0f0f0;
  border-radius: 12px;
  overflow: hidden;
  margin-bottom: 8px;
}

.day-bar-fill {
  height: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  transition: width 0.5s ease;
}

.day-count {
  font-size: 14px;
  color: #888;
}

.course-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.course-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: #f9fafb;
  border-radius: 12px;
  transition: background 0.2s;
}

.course-item:hover {
  background: #f0f4f8;
}

.course-info {
  flex: 1;
}

.course-name {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-bottom: 4px;
}

.course-meta {
  font-size: 14px;
  color: #666;
}

.course-meta span {
  margin-right: 16px;
}

.course-progress {
  display: flex;
  align-items: center;
  gap: 12px;
}

.progress-bar {
  width: 120px;
  height: 8px;
  background: #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  transition: width 0.5s ease;
}

.progress-text {
  font-size: 14px;
  color: #666;
  white-space: nowrap;
}

.quick-actions {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.action-btn {
  padding: 20px;
  background: white;
  border: 2px solid #667eea;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  color: #667eea;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.action-btn:hover {
  background: #667eea;
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.action-btn.secondary {
  border-color: #ccc;
  color: #666;
}

.action-btn.secondary:hover {
  background: #ccc;
  color: #333;
}

.btn-icon {
  font-size: 32px;
}

.btn-text {
  font-size: 16px;
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .day-stats {
    grid-template-columns: 1fr;
  }
  
  .course-item {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .course-progress {
    width: 100%;
    margin-top: 12px;
  }
  
  .quick-actions {
    grid-template-columns: 1fr;
  }
}
</style>
