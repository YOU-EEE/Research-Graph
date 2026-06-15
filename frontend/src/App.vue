<script setup>
import { useRoute, useRouter } from 'vue-router'
import { computed } from 'vue'
import {
  Document, Notebook, UploadFilled, FolderOpened,
  List, DataBoard, Connection, SwitchButton, HomeFilled,
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()

const isLoginPage = computed(() => route.path === '/login')

function handleLogout() {
  localStorage.removeItem('user')
  localStorage.removeItem('x_user_id')
  router.push('/login')
}
</script>

<template>
  <!-- 登录页不显示侧边栏 -->
  <div v-if="isLoginPage" class="full-page">
    <router-view />
  </div>

  <el-container v-else class="app-shell">
    <el-aside class="sidebar" width="232px">
      <div class="brand">
        <div class="brand-mark">RG</div>
        <div>
          <div class="brand-title">ResearchGraph</div>
          <div class="brand-subtitle">科研协作系统</div>
        </div>
      </div>

      <el-menu router :default-active="route.path" class="nav-menu">
        <el-menu-item index="/dashboard">
          <el-icon><HomeFilled /></el-icon>
          <span>Dashboard</span>
        </el-menu-item>
        <el-menu-item index="/papers">
          <el-icon><Document /></el-icon>
          <span>论文管理</span>
        </el-menu-item>
        <el-menu-item index="/import/bibtex">
          <el-icon><UploadFilled /></el-icon>
          <span>BibTeX 导入</span>
        </el-menu-item>
        <el-menu-item index="/projects">
          <el-icon><FolderOpened /></el-icon>
          <span>科研项目</span>
        </el-menu-item>
        <el-menu-item index="/tasks">
          <el-icon><List /></el-icon>
          <span>阅读任务</span>
        </el-menu-item>
        <el-menu-item index="/graph">
          <el-icon><Connection /></el-icon>
          <span>知识图谱</span>
        </el-menu-item>
        <el-menu-item index="/papers">
          <el-icon><Notebook /></el-icon>
          <span>AI 分析</span>
        </el-menu-item>
      </el-menu>

      <div class="sidebar-footer">
        <el-button text @click="handleLogout" style="width: 100%; color: #909399">
          <el-icon><SwitchButton /></el-icon>
          退出登录
        </el-button>
      </div>
    </el-aside>

    <el-container>
      <el-header class="topbar">
        <div>
          <div class="topbar-title">{{ route.meta.title || 'ResearchGraph' }}</div>
        </div>
        <el-tag effect="plain">Module D: 协作与知识图谱</el-tag>
      </el-header>

      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<style>
/* 全局基础样式 */
body {
  margin: 0;
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', Arial, sans-serif;
}

/* 侧边栏 */
.app-shell {
  min-height: 100vh;
}
.sidebar {
  background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
  color: #fff;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}
.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 20px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}
.brand-mark {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 8px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: #fff;
  font-size: 18px;
  font-weight: 700;
  flex-shrink: 0;
}
.brand-title {
  font-size: 16px;
  font-weight: 700;
  color: #fff;
  line-height: 1.3;
}
.brand-subtitle {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.45);
}
.nav-menu {
  border-right: none;
  background: transparent;
  flex: 1;
}
.nav-menu .el-menu-item {
  color: rgba(255, 255, 255, 0.65);
  border-radius: 6px;
  margin: 2px 8px;
}
.nav-menu .el-menu-item:hover {
  background: rgba(255, 255, 255, 0.08);
  color: #fff;
}
.nav-menu .el-menu-item.is-active {
  background: rgba(102, 126, 234, 0.3);
  color: #fff;
}
.sidebar-footer {
  padding: 12px 8px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

/* 顶栏 */
.topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 56px;
  border-bottom: 1px solid #ebeef5;
  background: #fff;
  padding: 0 24px !important;
}
.topbar-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

/* 主内容区 */
.main-content {
  background: #f5f7fa;
  min-height: calc(100vh - 56px);
  padding: 20px 24px;
}

/* 全屏页（登录） */
.full-page {
  width: 100%;
  min-height: 100vh;
}
</style>

<style scoped>
/* Element Plus menu item icon 样式覆盖 */
.nav-menu .el-menu-item .el-icon {
  color: inherit;
}
</style>
