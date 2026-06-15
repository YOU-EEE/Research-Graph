<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getDashboard } from '../api/projects'
import {
  Document, Notebook, FolderOpened, Clock, Plus, List
} from '@element-plus/icons-vue'

const router = useRouter()
const stats = ref({
  paper_count: 0,
  note_count: 0,
  project_count: 0,
  pending_task_count: 0,
  recent_papers: [],
  recent_activities: [],
  top_tags: [],
})

onMounted(async () => {
  try {
    const { data } = await getDashboard()
    stats.value = data
  } catch (e) {
    console.error('Failed to load dashboard', e)
  }
})
</script>

<template>
  <div class="dashboard">
    <h1>Dashboard</h1>

    <!-- 统计卡片 -->
    <el-row :gutter="16" class="stats-row">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-value">{{ stats.paper_count }}</div>
          <div class="stat-label"><el-icon><Document /></el-icon> 论文总数</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-value">{{ stats.note_count }}</div>
          <div class="stat-label"><el-icon><Notebook /></el-icon> 笔记总数</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-value">{{ stats.project_count }}</div>
          <div class="stat-label"><el-icon><FolderOpened /></el-icon> 项目总数</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-value" style="color: #e6a23c">{{ stats.pending_task_count }}</div>
          <div class="stat-label"><el-icon><Clock /></el-icon> 待完成任务</div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" class="content-row">
      <!-- 最近新增论文 -->
      <el-col :span="12">
        <el-card header="最近新增论文">
          <el-table :data="stats.recent_papers" size="small" max-height="300">
            <el-table-column prop="title" label="标题" show-overflow-tooltip />
            <el-table-column prop="year" label="年份" width="70" />
          </el-table>
        </el-card>
      </el-col>

      <!-- 最近活动日志 -->
      <el-col :span="12">
        <el-card header="最近活动日志">
          <el-table :data="stats.recent_activities" size="small" max-height="300">
            <el-table-column prop="action_type" label="操作" width="130" />
            <el-table-column prop="description" label="描述" show-overflow-tooltip />
            <el-table-column prop="username" label="用户" width="80" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" class="content-row">
      <!-- 高频标签 -->
      <el-col :span="12">
        <el-card header="高频标签">
          <div class="tag-cloud">
            <el-tag
              v-for="tag in stats.top_tags"
              :key="tag.tag_name"
              :type="['', 'success', 'warning', 'danger', 'info'][Math.floor(Math.random() * 5)]"
              effect="plain"
              size="large"
              style="margin: 4px"
            >
              {{ tag.tag_name }} ({{ tag.count }})
            </el-tag>
            <el-empty v-if="!stats.top_tags.length" description="暂无标签" />
          </div>
        </el-card>
      </el-col>

      <!-- 快捷入口 -->
      <el-col :span="12">
        <el-card header="快捷入口">
          <el-space wrap>
            <el-button type="primary" :icon="Plus" @click="router.push('/projects')">
              创建项目
            </el-button>
            <el-button type="success" :icon="List" @click="router.push('/tasks')">
              查看任务
            </el-button>
            <el-button type="warning" @click="router.push('/graph')">
              知识图谱
            </el-button>
            <el-button @click="router.push('/papers')">
              文献管理
            </el-button>
            <el-button @click="router.push('/ai')">
              AI 分析
            </el-button>
          </el-space>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped>
.dashboard h1 {
  font-size: 24px;
  margin-bottom: 24px;
  color: #303133;
}
.stats-row {
  margin-bottom: 16px;
}
.stat-card {
  text-align: center;
}
.stat-value {
  font-size: 36px;
  font-weight: 700;
  color: #409eff;
}
.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}
.content-row {
  margin-bottom: 16px;
}
.tag-cloud {
  min-height: 80px;
}
</style>
