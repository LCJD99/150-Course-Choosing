<template>
  <div class="courses-container">
    <div class="header">
      <button @click="$router.back()" class="back-btn">← 返回</button>
      <h1 class="title">课程管理</h1>
    </div>
    
    <div class="filters">
      <div class="filter-group">
        <label class="filter-label">筛选条件</label>
        <select v-model="filterDay" class="filter-select">
          <option value="">全部星期</option>
          <option v-for="day in [1, 3, 4, 5]" :key="day" :value="day">
            {{ getDayName(day) }}
          </option>
        </select>
      </div>
      
      <div class="filter-group">
        <label class="filter-label">年级</label>
        <select v-model="filterGrade" class="filter-select">
          <option value="">全部年级</option>
          <option v-for="grade in [1, 2, 3, 4, 5, 6]" :key="grade" :value="grade">
            {{ grade }} 年级
          </option>
        </select>
      </div>
      
      <div class="filter-group">
        <label class="filter-label">搜索</label>
        <input
          v-model="searchText"
          type="text"
          placeholder="课程名或教师"
          class="filter-input"
        />
      </div>
    </div>
    
    <div class="courses-list">
      <div
        v-for="course in filteredCourses"
        :key="course.id"
        class="course-card"
      >
        <div class="course-header">
          <div class="course-badge" :class="'day-' + course.day">
            {{ getDayName(course.day) }}
          </div>
          <div class="course-id">{{ course.course_id }}</div>
        </div>
        
        <h3 class="course-name">{{ course.course_name }}</h3>
        <div class="course-details">
          <div class="detail-item">
            <span class="detail-label">教师</span>
            <span class="detail-value">{{ course.teacher }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">开设年级</span>
            <span class="detail-value">{{ formatGrades(course.grades) }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">容量</span>
            <span class="detail-value">{{ course.capacity }} 人</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">已选</span>
            <span class="detail-value">{{ course.enrolled_count }} 人</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">剩余</span>
            <span class="detail-value" :class="{ 'full': course.remaining === 0 }">
              {{ course.remaining }} 人
            </span>
          </div>
        </div>
        
        <div class="course-progress">
          <div class="progress-bar">
            <div
              class="progress-fill"
              :class="{ 'warning': course.remaining <= 5, 'full': course.remaining === 0 }"
              :style="{ width: course.fill_percentage + '%' }"
            ></div>
          </div>
          <div class="progress-text">
            {{ course.fill_percentage }}%
          </div>
        </div>
        
        <div class="course-actions">
          <button @click="toggleCourseStatus(course)" class="action-btn toggle">
            {{ course.is_active ? '禁用' : '启用' }}
          </button>
          <button @click="deleteCourse(course)" class="action-btn delete">
            删除
          </button>
        </div>
      </div>
      
      <div v-if="filteredCourses.length === 0" class="empty-message">
        <div class="empty-icon">📭</div>
        <div class="empty-text">暂无符合条件的课程</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { apiService } from '../services/api'

const router = useRouter()

const courses = ref([])
const filterDay = ref('')
const filterGrade = ref('')
const searchText = ref('')

const filteredCourses = computed(() => {
  return courses.value.filter(course => {
    const matchDay = !filterDay.value || course.day === parseInt(filterDay.value)
    const matchGrade = !filterGrade.value || (course.grades || []).includes(parseInt(filterGrade.value))
    const matchSearch = !searchText.value || 
      course.course_name.includes(searchText.value) || 
      course.teacher.includes(searchText.value)
    return matchDay && matchGrade && matchSearch
  })
})

const getDayName = (day) => {
  const dayNames = { 1: '周一', 3: '周三', 4: '周四', 5: '周五' }
  return dayNames[day]
}

const formatGrades = (grades) => {
  if (!grades || grades.length === 0) return '未配置'
  return grades.slice().sort((a, b) => a - b).map(g => `${g}年级`).join('、')
}

const toggleCourseStatus = (course) => {
  course.is_active = !course.is_active
  alert(`课程"${course.course_name}"已${course.is_active ? '启用' : '禁用'}`)
}

const deleteCourse = (course) => {
  if (!confirm(`确认删除课程"${course.course_name}"？`)) return

  apiService.deleteAdminCourse(course.id)
    .then(() => {
      courses.value = courses.value.filter(c => c.id !== course.id)
      alert('课程已删除')
    })
    .catch((err) => {
      alert(err.message || '删除失败')
    })
}

onMounted(async () => {
  try {
    courses.value = await apiService.getAdminCourses()
  } catch (err) {
    alert(err.message || '加载课程失败')
  }
})
</script>

<style scoped>
.courses-container {
  min-height: 100vh;
  background: #f5f7fa;
  padding: 20px;
}

.header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.back-btn {
  background: none;
  border: none;
  font-size: 18px;
  color: #667eea;
  cursor: pointer;
  padding: 8px;
  transition: color 0.2s;
}

.back-btn:hover {
  color: #764ba2;
}

.title {
  font-size: 24px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.filters {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.filter-label {
  font-size: 14px;
  font-weight: 500;
  color: #555;
}

.filter-select,
.filter-input {
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  background: white;
}

.filter-select:focus,
.filter-input:focus {
  outline: none;
  border-color: #667eea;
}

.courses-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.course-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: box-shadow 0.2s;
}

.course-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.course-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.course-badge {
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  color: white;
}

.course-badge.day-1 {
  background: #ff6b6b;
}

.course-badge.day-3 {
  background: #4ecdc4;
}

.course-badge.day-4 {
  background: #45b7d1;
}

.course-badge.day-5 {
  background: #96ceb4;
}

.course-id {
  font-size: 14px;
  color: #888;
}

.course-name {
  font-size: 20px;
  font-weight: 600;
  color: #333;
  margin: 0 0 16px 0;
}

.course-details {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-bottom: 16px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.detail-label {
  font-size: 12px;
  color: #888;
}

.detail-value {
  font-size: 16px;
  font-weight: 500;
  color: #333;
}

.detail-value.full {
  color: #f44;
}

.course-progress {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.progress-bar {
  flex: 1;
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

.progress-fill.warning {
  background: linear-gradient(90deg, #ffa726 0%, #ff7043 100%);
}

.progress-fill.full {
  background: #f44;
}

.progress-text {
  font-size: 14px;
  font-weight: 600;
  color: #555;
  min-width: 50px;
  text-align: right;
}

.course-actions {
  display: flex;
  gap: 12px;
}

.action-btn {
  flex: 1;
  padding: 12px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn.toggle {
  background: #e0e0e0;
  color: #333;
}

.action-btn.toggle:hover {
  background: #d0d0d0;
}

.action-btn.delete {
  background: #fee;
  color: #c33;
}

.action-btn.delete:hover {
  background: #fcc;
  background-color: #f55;
}

.empty-message {
  text-align: center;
  padding: 80px 20px;
  color: #999;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.empty-text {
  font-size: 18px;
}

@media (max-width: 768px) {
  .filters {
    grid-template-columns: 1fr;
  }
  
  .course-details {
    grid-template-columns: 1fr;
  }
  
  .course-actions {
    flex-direction: column;
  }
}
</style>
