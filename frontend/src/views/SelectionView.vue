<template>
  <div class="selection-container">
    <div class="header">
      <div class="progress-bar">
        <div class="progress-fill" :style="{ width: progressPercentage + '%' }"></div>
      </div>
      <div class="progress-text">
        已完成 {{ progress.completed_days }}/4 天
      </div>
    </div>
    
    <div v-if="!courseSelectionOpen" class="closed-notice">
      <div class="notice-icon">🔒</div>
      <div class="notice-text">系统尚未开通，仅支持预览</div>
    </div>
    
    <div class="day-tabs">
      <button
        v-for="day in [1, 3, 4, 5]"
        :key="day"
        @click="selectedDay = day"
        class="day-tab"
        :class="{ active: selectedDay === day }"
      >
        {{ getDayName(day) }}
      </button>
    </div>
    
    <div v-if="loading" class="loading">加载中...</div>
    
    <div v-else class="courses-list">
      <div
        v-for="course in courses"
        :key="course.id"
        class="course-card"
        :class="{ selected: course.is_selected, full: course.remaining === 0 }"
      >
        <div class="course-info">
          <h3 class="course-name">{{ course.course_name }}</h3>
          <div class="course-teacher">老师: {{ course.teacher }}</div>
          <div class="course-capacity">
            剩余名额: <span :class="{ 'full': course.remaining === 0 }">{{ course.remaining }}</span> / {{ course.capacity }}
          </div>
        </div>
        
        <button
          @click="handleCourseAction(course)"
          class="course-btn"
          :disabled="course.remaining === 0 || !courseSelectionOpen"
          :class="{
            'select': !course.is_selected,
            'selected': course.is_selected,
            'full': course.remaining === 0
          }"
        >
          {{ getButtonText(course) }}
        </button>
      </div>
      
      <div v-if="courses.length === 0" class="empty-message">
        该天暂无可选课程
      </div>
    </div>
    
    <div v-if="showConfirmDialog" class="dialog-overlay" @click="showConfirmDialog = false">
      <div class="dialog" @click.stop>
        <h3 class="dialog-title">{{ confirmDialogText }}</h3>
        <div class="dialog-buttons">
          <button @click="showConfirmDialog = false" class="dialog-btn cancel">取消</button>
          <button @click="confirmAction" class="dialog-btn confirm">确认</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { apiService } from '../services/api'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const { token, student, courseSelectionOpen } = useAuthStore()

const selectedDay = ref(1)
const courses = ref([])
const progress = ref({ completed_days: 0, is_complete_4_days: false })
const loading = ref(false)
const showConfirmDialog = ref(false)
const confirmDialogText = ref('')
const pendingAction = ref(null)
const pendingCourse = ref(null)

const progressPercentage = computed(() => {
  return (progress.value.completed_days / 4) * 100
})

const getDayName = (day) => {
  const dayNames = { 1: '周一', 3: '周三', 4: '周四', 5: '周五' }
  return dayNames[day]
}

const getButtonText = (course) => {
  if (course.remaining === 0) return '已满'
  if (course.is_selected) return '已选'
  return '选择'
}

const loadCourses = async () => {
  if (!token.value) return
  
  loading.value = true
  try {
    courses.value = await apiService.getCourses(selectedDay.value, token.value)
  } catch (err) {
    console.error('Failed to load courses:', err)
    alert('加载课程失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

const loadProgress = async () => {
  if (!token.value) return
  
  try {
    progress.value = await apiService.getProgress(token.value)
  } catch (err) {
    console.error('Failed to load progress:', err)
  }
}

const handleCourseAction = (course) => {
  if (course.remaining === 0 || !courseSelectionOpen.value) return
  
  if (course.is_selected) {
    confirmDialogText.value = '是否替换为该课程？'
    pendingAction.value = 'replace'
    pendingCourse.value = course
  } else {
    confirmDialogText.value = '确认选择该课程？'
    pendingAction.value = 'select'
    pendingCourse.value = course
  }
  showConfirmDialog.value = true
}

const confirmAction = async () => {
  showConfirmDialog.value = false
  
  try {
    await apiService.selectCourse(selectedDay.value, pendingCourse.value.id, token.value)
    await loadCourses()
    await loadProgress()
    alert('操作成功')
  } catch (err) {
    console.error('Failed to select course:', err)
    alert(err.message || '操作失败，请稍后重试')
  }
}

onMounted(() => {
  loadCourses()
  loadProgress()
})

const { watch } = require('vue')
watch(selectedDay, () => {
  loadCourses()
})
</script>

<style scoped>
.selection-container {
  min-height: 100vh;
  background: #f5f7fa;
  padding-bottom: 80px;
}

.header {
  background: white;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 100;
}

.progress-bar {
  height: 8px;
  background: #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 12px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  transition: width 0.5s ease;
}

.progress-text {
  font-size: 14px;
  color: #666;
  text-align: center;
}

.closed-notice {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px 20px;
  background: #fff3cd;
  border: 1px solid #ffc107;
  border-radius: 12px;
  margin: 20px;
}

.notice-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.notice-text {
  font-size: 16px;
  color: #856404;
  text-align: center;
}

.day-tabs {
  display: flex;
  gap: 8px;
  padding: 12px 16px;
  background: white;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

.day-tab {
  flex: 1;
  min-width: 70px;
  padding: 12px 16px;
  background: #f5f7fa;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #666;
  cursor: pointer;
  transition: all 0.3s;
  white-space: nowrap;
}

.day-tab.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-color: transparent;
}

.loading {
  text-align: center;
  padding: 40px;
  color: #999;
}

.courses-list {
  padding: 16px;
}

.course-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: transform 0.2s, box-shadow 0.2s;
}

.course-card:active {
  transform: scale(0.98);
}

.course-card.selected {
  border: 2px solid #667eea;
  background: #f0f4ff;
}

.course-card.full {
  opacity: 0.6;
}

.course-info {
  flex: 1;
}

.course-name {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin: 0 0 8px 0;
}

.course-teacher {
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
}

.course-capacity {
  font-size: 14px;
  color: #888;
}

.course-capacity .full {
  color: #f44;
  font-weight: 600;
}

.course-btn {
  padding: 10px 24px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  min-width: 80px;
}

.course-btn.select {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.course-btn.select:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.course-btn.selected {
  background: #4caf50;
  color: white;
}

.course-btn.full {
  background: #ccc;
  color: #999;
  cursor: not-allowed;
}

.course-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.empty-message {
  text-align: center;
  padding: 40px;
  color: #999;
  font-size: 16px;
}

.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.dialog {
  background: white;
  border-radius: 16px;
  padding: 32px;
  max-width: 320px;
  width: 100%;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.dialog-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin: 0 0 24px 0;
  text-align: center;
}

.dialog-buttons {
  display: flex;
  gap: 12px;
}

.dialog-btn {
  flex: 1;
  padding: 14px;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.dialog-btn.cancel {
  background: #f5f5f5;
  color: #666;
}

.dialog-btn.cancel:hover {
  background: #e0e0e0;
}

.dialog-btn.confirm {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.dialog-btn.confirm:hover {
  transform: scale(1.05);
}

@media (max-width: 480px) {
  .course-card {
    flex-direction: column;
    align-items: stretch;
  }
  
  .course-btn {
    width: 100%;
    margin-top: 16px;
  }
}
</style>
