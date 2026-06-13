<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { login, register } from '../api/auth'
import { ElMessage } from 'element-plus'

const router = useRouter()

const form = reactive({ username: '', password: '' })
const isRegister = ref(false)
const loading = ref(false)

async function handleSubmit() {
  loading.value = true
  try {
    const fn = isRegister.value ? register : login
    const { data } = await fn(form.username, form.password)
    localStorage.setItem('user', JSON.stringify(data))
    localStorage.setItem('x_user_id', data.user_id)
    ElMessage.success(isRegister.value ? '注册成功' : '登录成功')
    router.push('/dashboard')
  } catch (e) {
    ElMessage.error(e.userMessage || '操作失败')
  } finally {
    loading.value = false
  }
}

// 检查是否已登录
const saved = localStorage.getItem('user')
if (saved) {
  router.replace('/dashboard')
}
</script>

<template>
  <div class="login-page">
    <div class="login-card">
      <div class="brand">
        <div class="brand-mark">RG</div>
        <div class="brand-title">ResearchGraph</div>
        <div class="brand-subtitle">科研协作与知识图谱系统</div>
      </div>
      <el-form @submit.prevent="handleSubmit" label-position="top">
        <el-form-item label="用户名">
          <el-input v-model="form.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="form.password" type="password" placeholder="请输入密码" show-password />
        </el-form-item>
        <el-button type="primary" native-type="submit" :loading="loading" block>
          {{ isRegister ? '注册' : '登录' }}
        </el-button>
        <el-button text type="primary" @click="isRegister = !isRegister" block style="margin-top: 8px">
          {{ isRegister ? '已有账号？去登录' : '没有账号？去注册' }}
        </el-button>
      </el-form>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
.login-card {
  width: 400px;
  padding: 40px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
}
.brand {
  text-align: center;
  margin-bottom: 32px;
}
.brand-mark {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 56px;
  height: 56px;
  border-radius: 12px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: #fff;
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 12px;
}
.brand-title {
  font-size: 22px;
  font-weight: 700;
  color: #303133;
}
.brand-subtitle {
  font-size: 13px;
  color: #909399;
  margin-top: 4px;
}
</style>
