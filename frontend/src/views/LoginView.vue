<template>
  <div class="login-container">
    <div class="login-card">
      <h1 class="title">兴趣班选课系统</h1>
      <p class="subtitle">150团中学</p>
      
      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label for="name">姓名</label>
          <input
            id="name"
            v-model="name"
            type="text"
            placeholder="请输入姓名"
            required
            :disabled="loading"
          />
        </div>
        
        <div class="form-group">
          <label for="idCard">身份证号</label>
          <input
            id="idCard"
            v-model="idCard"
            type="text"
            placeholder="请输入身份证号"
            required
            :disabled="loading"
            maxlength="18"
          />
        </div>
        
        <button
          type="submit"
          class="login-btn"
          :disabled="loading"
        >
          {{ loading ? '登录中...' : '登录' }}
        </button>
        
        <div v-if="error" class="error-message">
          {{ error }}
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { apiService } from '../services/api'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const { setAuth, updateCourseSelectionOpen } = useAuthStore()

const name = ref('')
const idCard = ref('')
const loading = ref(false)
const error = ref('')

const handleLogin = async () => {
  if (loading.value) return
  
  loading.value = true
  error.value = ''
  
  try {
    const authData = await apiService.login(name.value, idCard.value)
    setAuth(authData)
    
    if (!authData.course_selection_open) {
      updateCourseSelectionOpen(false)
    }
    
    router.push('/selection')
  } catch (err) {
    error.value = '登录失败，请检查姓名和身份证号'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-card {
  background: white;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  padding: 40px;
  width: 100%;
  max-width: 400px;
}

.title {
  font-size: 28px;
  font-weight: 600;
  color: #333;
  text-align: center;
  margin: 0 0 8px 0;
}

.subtitle {
  font-size: 16px;
  color: #666;
  text-align: center;
  margin: 0 0 32px 0;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

label {
  font-size: 14px;
  color: #555;
  font-weight: 500;
}

input {
  padding: 14px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 16px;
  transition: border-color 0.3s;
}

input:focus {
  outline: none;
  border-color: #667eea;
}

input:disabled {
  background: #f5f5f5;
  cursor: not-allowed;
}

.login-btn {
  padding: 14px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  margin-top: 8px;
}

.login-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
}

.login-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error-message {
  padding: 12px;
  background: #fee;
  color: #c33;
  border-radius: 8px;
  font-size: 14px;
  text-align: center;
}

@media (max-width: 480px) {
  .login-card {
    padding: 30px 24px;
  }
  
  .title {
    font-size: 24px;
  }
}
</style>
