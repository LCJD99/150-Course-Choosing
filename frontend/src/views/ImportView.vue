<template>
  <div class="import-container">
    <div class="header">
      <button @click="$router.back()" class="back-btn">← 返回</button>
      <h1 class="title">数据导入</h1>
    </div>
    
    <div class="tabs">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        @click="activeTab = tab.id"
        class="tab"
        :class="{ active: activeTab === tab.id }"
      >
        {{ tab.name }}
      </button>
    </div>
    
    <div v-if="activeTab === 'courses'" class="import-section">
      <div class="upload-card">
        <h2 class="card-title">导入课程</h2>
        <div class="template-download">
          <a href="#" class="download-link">📥 下载模板</a>
          <span class="template-hint">CSV格式：course_id, course_name, teacher, capacity, day</span>
        </div>
        
        <div class="upload-area" :class="{ dragover: isDragover }" @dragover.prevent @dragleave.prevent="isDragover = false" @drop.prevent="handleDrop">
          <input
            ref="fileInput"
            type="file"
            accept=".csv"
            @change="handleFileChange"
            class="file-input"
          />
          <div class="upload-content">
            <div class="upload-icon">📤</div>
            <div class="upload-text">
              <div class="upload-main">点击或拖拽文件到此处</div>
              <div class="upload-sub">支持 .csv 格式</div>
            </div>
          </div>
        </div>
        
        <button
          @click="importCourses"
          class="import-btn"
          :disabled="!selectedFile || loading"
        >
          {{ loading ? '导入中...' : '开始导入' }}
        </button>
        
        <div v-if="result" class="result-section">
          <h3 class="result-title">导入结果</h3>
          <div class="result-stats">
            <div class="result-item success">
              <span class="result-label">成功</span>
              <span class="result-value">{{ result.success_rows }}</span>
            </div>
            <div class="result-item error">
              <span class="result-label">失败</span>
              <span class="result-value">{{ result.failed_rows }}</span>
            </div>
            <div class="result-item total">
              <span class="result-label">总计</span>
              <span class="result-value">{{ result.total_rows }}</span>
            </div>
          </div>
          
          <div v-if="result.errors && result.errors.length > 0" class="errors-list">
            <h4 class="errors-title">错误详情</h4>
            <div v-for="(error, index) in result.errors" :key="index" class="error-item">
              {{ error }}
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div v-else-if="activeTab === 'grades'" class="import-section">
      <div class="upload-card">
        <h2 class="card-title">导入课程开设年级</h2>
        <div class="template-download">
          <a href="#" class="download-link">📥 下载模板</a>
          <span class="template-hint">CSV格式：course_id, grade</span>
        </div>
        
        <div class="upload-area" :class="{ dragover: isDragover }" @dragover.prevent @dragleave.prevent="isDragover = false" @drop.prevent="handleDrop">
          <input
            ref="fileInput"
            type="file"
            accept=".csv"
            @change="handleFileChange"
            class="file-input"
          />
          <div class="upload-content">
            <div class="upload-icon">📤</div>
            <div class="upload-text">
              <div class="upload-main">点击或拖拽文件到此处</div>
              <div class="upload-sub">支持 .csv 格式</div>
            </div>
          </div>
        </div>
        
        <button
          @click="importGrades"
          class="import-btn"
          :disabled="!selectedFile || loading"
        >
          {{ loading ? '导入中...' : '开始导入' }}
        </button>
        
        <div v-if="result" class="result-section">
          <h3 class="result-title">导入结果</h3>
          <div class="result-stats">
            <div class="result-item success">
              <span class="result-label">成功</span>
              <span class="result-value">{{ result.success_rows }}</span>
            </div>
            <div class="result-item error">
              <span class="result-label">失败</span>
              <span class="result-value">{{ result.failed_rows }}</span>
            </div>
            <div class="result-item total">
              <span class="result-label">总计</span>
              <span class="result-value">{{ result.total_rows }}</span>
            </div>
          </div>
          
          <div v-if="result.errors && result.errors.length > 0" class="errors-list">
            <h4 class="errors-title">错误详情</h4>
            <div v-for="(error, index) in result.errors" :key="index" class="error-item">
              {{ error }}
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div v-else-if="activeTab === 'students'" class="import-section">
      <div class="upload-card">
        <h2 class="card-title">导入学生</h2>
        <div class="template-download">
          <a href="#" class="download-link">📥 下载模板</a>
          <span class="template-hint">CSV格式：name, class_name, grade, id_card</span>
        </div>
        
        <div class="upload-area" :class="{ dragover: isDragover }" @dragover.prevent @dragleave.prevent="isDragover = false" @drop.prevent="handleDrop">
          <input
            ref="fileInput"
            type="file"
            accept=".csv"
            @change="handleFileChange"
            class="file-input"
          />
          <div class="upload-content">
            <div class="upload-icon">📤</div>
            <div class="upload-text">
              <div class="upload-main">点击或拖拽文件到此处</div>
              <div class="upload-sub">支持 .csv 格式</div>
            </div>
          </div>
        </div>
        
        <button
          @click="importStudents"
          class="import-btn"
          :disabled="!selectedFile || loading"
        >
          {{ loading ? '导入中...' : '开始导入' }}
        </button>
        
        <div v-if="result" class="result-section">
          <h3 class="result-title">导入结果</h3>
          <div class="result-stats">
            <div class="result-item success">
              <span class="result-label">成功</span>
              <span class="result-value">{{ result.success_rows }}</span>
            </div>
            <div class="result-item error">
              <span class="result-label">失败</span>
              <span class="result-value">{{ result.failed_rows }}</span>
            </div>
            <div class="result-item total">
              <span class="result-label">总计</span>
              <span class="result-value">{{ result.total_rows }}</span>
            </div>
          </div>
          
          <div v-if="result.errors && result.errors.length > 0" class="errors-list">
            <h4 class="errors-title">错误详情</h4>
            <div v-for="(error, index) in result.errors" :key="index" class="error-item">
              {{ error }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { apiService } from '../services/api'

const router = useRouter()

const activeTab = ref('courses')
const selectedFile = ref(null)
const loading = ref(false)
const isDragover = ref(false)
const result = ref(null)
const fileInput = ref(null)

const tabs = [
  { id: 'courses', name: '课程' },
  { id: 'grades', name: '开设年级' },
  { id: 'students', name: '学生' }
]

const handleDrop = (e) => {
  isDragover.value = false
  const files = e.dataTransfer.files
  if (files.length > 0) {
    selectedFile.value = files[0]
  }
}

const handleFileChange = (e) => {
  const files = e.target.files
  if (files.length > 0) {
    selectedFile.value = files[0]
  }
}

const importCourses = async () => {
  if (!selectedFile.value) return
  
  loading.value = true
  result.value = null
  
  try {
    const data = await apiService.importCourses(selectedFile.value)
    result.value = data
  } catch (err) {
    console.error('Import failed:', err)
    alert('导入失败：' + err.message)
  } finally {
    loading.value = false
    selectedFile.value = null
  }
}

const importGrades = async () => {
  if (!selectedFile.value) return
  
  loading.value = true
  result.value = null
  
  try {
    const data = await apiService.importCourseGrades(selectedFile.value)
    result.value = data
  } catch (err) {
    console.error('Import failed:', err)
    alert('导入失败：' + err.message)
  } finally {
    loading.value = false
    selectedFile.value = null
  }
}

const importStudents = async () => {
  if (!selectedFile.value) return
  
  loading.value = true
  result.value = null
  
  try {
    const data = await apiService.importStudents(selectedFile.value)
    result.value = data
  } catch (err) {
    console.error('Import failed:', err)
    alert('导入失败：' + err.message)
  } finally {
    loading.value = false
    selectedFile.value = null
  }
}
</script>

<style scoped>
.import-container {
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

.tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 24px;
}

.tab {
  padding: 12px 24px;
  background: white;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
  color: #666;
  cursor: pointer;
  transition: all 0.2s;
}

.tab:hover {
  border-color: #667eea;
  color: #667eea;
}

.tab.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-color: transparent;
}

.import-section {
  max-width: 800px;
  margin: 0 auto;
}

.upload-card {
  background: white;
  border-radius: 16px;
  padding: 32px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.card-title {
  font-size: 24px;
  font-weight: 600;
  color: #333;
  margin: 0 0 24px 0;
}

.template-download {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
  padding: 16px;
  background: #f9fafb;
  border-radius: 8px;
}

.download-link {
  color: #667eea;
  text-decoration: none;
  font-weight: 600;
  transition: color 0.2s;
}

.download-link:hover {
  color: #764ba2;
  text-decoration: underline;
}

.template-hint {
  font-size: 14px;
  color: #666;
}

.upload-area {
  border: 2px dashed #ccc;
  border-radius: 12px;
  padding: 48px 24px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  margin-bottom: 24px;
}

.upload-area:hover,
.upload-area.dragover {
  border-color: #667eea;
  background: #f0f4f8;
}

.file-input {
  display: none;
}

.upload-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.upload-icon {
  font-size: 64px;
}

.upload-text {
  text-align: center;
}

.upload-main {
  font-size: 18px;
  color: #333;
  font-weight: 500;
}

.upload-sub {
  font-size: 14px;
  color: #888;
}

.import-btn {
  width: 100%;
  padding: 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.import-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.import-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.result-section {
  margin-top: 32px;
  padding-top: 32px;
  border-top: 1px solid #e0e0e0;
}

.result-title {
  font-size: 20px;
  font-weight: 600;
  color: #333;
  margin: 0 0 16px 0;
}

.result-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.result-item {
  padding: 16px;
  border-radius: 8px;
  text-align: center;
}

.result-item.success {
  background: #d4edda;
  color: #155724;
}

.result-item.error {
  background: #f8d7da;
  color: #721c24;
}

.result-item.total {
  background: #e2e3e5;
  color: #383d41;
}

.result-label {
  display: block;
  font-size: 14px;
  margin-bottom: 4px;
}

.result-value {
  font-size: 24px;
  font-weight: 700;
}

.errors-list {
  background: #fff3cd;
  border: 1px solid #ffc107;
  border-radius: 8px;
  padding: 16px;
}

.errors-title {
  font-size: 16px;
  font-weight: 600;
  color: #856404;
  margin: 0 0 12px 0;
}

.error-item {
  font-size: 14px;
  color: #856404;
  padding: 8px 0;
  border-bottom: 1px solid rgba(133, 100, 4, 0.1);
}

.error-item:last-child {
  border-bottom: none;
}

@media (max-width: 768px) {
  .result-stats {
    grid-template-columns: 1fr;
  }
  
  .upload-area {
    padding: 32px 16px;
  }
  
  .upload-icon {
    font-size: 48px;
  }
}
</style>
