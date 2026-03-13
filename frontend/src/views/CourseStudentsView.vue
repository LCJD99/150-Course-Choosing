<template>
  <div class="course-students-container">
    <div class="header">
      <button @click="$router.back()" class="back-btn">← 返回</button>
      <h1 class="title">课程选课学生</h1>
    </div>

    <div class="course-card" v-if="courseInfo">
      <div class="course-name">{{ courseInfo.course_name }}</div>
      <div class="course-meta">{{ courseInfo.course_id }} · {{ getDayName(courseInfo.day) }} · {{ courseInfo.teacher }}</div>
      <div class="course-meta">已选人数：{{ total }}</div>
    </div>

    <div v-if="loading" class="loading">加载中...</div>
    <div v-else>
      <div v-if="students.length === 0" class="empty">暂无学生选该课程</div>
      <div v-else class="list">
        <div class="row header-row">
          <span>姓名</span><span>年级</span><span>班级</span><span>身份证后4位</span><span>选课时间</span>
        </div>
        <div class="row" v-for="student in students" :key="`${student.id}-${student.selected_at}`">
          <span>{{ student.name }}</span>
          <span>{{ student.grade }}年级</span>
          <span>{{ student.class_name }}</span>
          <span>{{ student.id_card_last4 }}</span>
          <span>{{ formatDate(student.selected_at) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { apiService } from '../services/api'

const route = useRoute()
const loading = ref(false)
const courseInfo = ref(null)
const students = ref([])
const total = ref(0)

const getDayName = (day) => ({ 1: '周一', 3: '周三', 4: '周四', 5: '周五' }[day] || '-')

const formatDate = (iso) => {
  if (!iso) return '-'
  return new Date(iso).toLocaleString()
}

const loadData = async () => {
  loading.value = true
  try {
    const data = await apiService.getCourseStudents(route.params.courseId)
    courseInfo.value = data.course
    students.value = data.students || []
    total.value = data.total || 0
  } catch (err) {
    alert(err.message || '加载失败')
  } finally {
    loading.value = false
  }
}

onMounted(loadData)
</script>

<style scoped>
.course-students-container { min-height: 100vh; background: #f5f7fa; padding: 20px; }
.header { display: flex; align-items: center; gap: 16px; margin-bottom: 16px; }
.back-btn { border: none; background: none; color: #667eea; cursor: pointer; font-size: 16px; }
.title { margin: 0; font-size: 24px; }
.course-card { background: white; border-radius: 10px; padding: 14px; margin-bottom: 14px; }
.course-name { font-size: 18px; font-weight: 600; margin-bottom: 6px; }
.course-meta { color: #64748b; font-size: 13px; }
.loading, .empty { text-align: center; padding: 28px; color: #888; }
.list { background: white; border-radius: 10px; overflow: hidden; }
.row { display: grid; grid-template-columns: 1fr 1fr 1fr 1fr 2fr; gap: 8px; padding: 10px 12px; border-bottom: 1px solid #eee; font-size: 14px; }
.header-row { background: #f8fafc; font-weight: 600; }
@media (max-width: 768px) { .row { grid-template-columns: 1fr 1fr; } }
</style>
