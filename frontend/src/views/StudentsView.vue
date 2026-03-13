<template>
  <div class="students-container">
    <div class="header">
      <button @click="$router.push('/admin')" class="back-btn">← 返回</button>
      <h1 class="title">已选课学生管理</h1>
    </div>

    <div class="filters">
      <select v-model="filterGrade" class="input">
        <option value="">全部年级</option>
        <option v-for="grade in [1, 2, 3, 4, 5, 6]" :key="grade" :value="grade">{{ grade }} 年级</option>
      </select>
      <input v-model="filterClass" class="input" placeholder="班级，如 1班" />
      <button class="search-btn" @click="loadStudents">筛选</button>
    </div>

    <div v-if="loading" class="loading">加载中...</div>
    <div v-else>
      <div class="count">共 {{ students.length }} 名已选课学生</div>
      <div v-if="students.length === 0" class="empty">暂无符合条件的已选课学生</div>
      <div v-else class="list">
        <div v-for="student in students" :key="student.id" class="card">
          <div class="row">
            <div>
              <div class="name">{{ student.name }}</div>
              <div class="meta">{{ student.grade }}年级 · {{ student.class_name }} · 身份证后4位 {{ student.id_card_last4 }}</div>
            </div>
            <div class="days">已选 {{ student.selected_days }}/4 天</div>
          </div>
          <div class="meta selections">
            周一: {{ student.selections['1']?.course_name || '-' }} ｜
            周三: {{ student.selections['3']?.course_name || '-' }} ｜
            周四: {{ student.selections['4']?.course_name || '-' }} ｜
            周五: {{ student.selections['5']?.course_name || '-' }}
          </div>
          <div class="actions">
            <button class="clear-btn" @click="clearSelections(student)">清空该生选课</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { apiService } from '../services/api'

const students = ref([])
const loading = ref(false)
const filterGrade = ref('')
const filterClass = ref('')

const loadStudents = async () => {
  loading.value = true
  try {
    students.value = await apiService.getSelectedStudents({
      grade: filterGrade.value || undefined,
      class_name: filterClass.value.trim() || undefined
    })
  } catch (err) {
    alert(err.message || '加载学生失败')
  } finally {
    loading.value = false
  }
}

const clearSelections = async (student) => {
  if (!confirm(`确认清空 ${student.name} 的全部选课记录？`)) return
  try {
    await apiService.clearStudentSelections(student.id)
    await loadStudents()
    alert('已清空')
  } catch (err) {
    alert(err.message || '清空失败')
  }
}

onMounted(loadStudents)
</script>

<style scoped>
.students-container { min-height: 100vh; background: #f5f7fa; padding: 20px; }
.header { display: flex; align-items: center; gap: 16px; margin-bottom: 20px; }
.back-btn { border: none; background: none; color: #667eea; font-size: 16px; cursor: pointer; }
.title { margin: 0; font-size: 24px; }
.filters { display: grid; grid-template-columns: 1fr 1fr auto; gap: 12px; margin-bottom: 16px; }
.input { padding: 10px; border: 1px solid #ddd; border-radius: 8px; }
.search-btn { padding: 10px 16px; border: none; border-radius: 8px; background: #667eea; color: white; cursor: pointer; }
.count { color: #666; margin-bottom: 10px; }
.loading,.empty { text-align: center; color: #888; padding: 24px; }
.list { display: grid; gap: 12px; }
.card { background: white; border-radius: 10px; padding: 14px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
.row { display: flex; justify-content: space-between; gap: 12px; }
.name { font-size: 16px; font-weight: 600; margin-bottom: 6px; }
.meta { font-size: 13px; color: #666; }
.selections { margin-top: 8px; }
.days { color: #475569; font-size: 13px; font-weight: 600; }
.actions { margin-top: 10px; }
.clear-btn { border: 1px solid #ef4444; color: #ef4444; background: white; border-radius: 8px; padding: 6px 10px; cursor: pointer; }
@media (max-width: 640px) { .filters { grid-template-columns: 1fr; } .row { flex-direction: column; } }
</style>
