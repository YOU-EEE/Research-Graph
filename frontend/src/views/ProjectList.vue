<script setup>
import { ref, onMounted, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { listProjects, createProject, deleteProject } from '../api/projects'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Delete } from '@element-plus/icons-vue'

const router = useRouter()
const projects = ref([])
const loading = ref(false)
const showCreate = ref(false)
const form = reactive({ project_name: '', description: '' })

async function loadProjects() {
  loading.value = true
  try {
    const { data } = await listProjects()
    projects.value = data
  } catch (e) {
    ElMessage.error('加载项目列表失败')
  } finally {
    loading.value = false
  }
}

async function handleCreate() {
  try {
    await createProject(form)
    ElMessage.success('项目创建成功')
    showCreate.value = false
    form.project_name = ''
    form.description = ''
    loadProjects()
  } catch (e) {
    ElMessage.error(e.userMessage || '创建失败')
  }
}

async function handleDelete(id) {
  try {
    await ElMessageBox.confirm('确定要删除该项目吗？', '确认')
    await deleteProject(id)
    ElMessage.success('项目已删除')
    loadProjects()
  } catch { /* cancelled */ }
}

onMounted(loadProjects)
</script>

<template>
  <div class="project-list-page">
    <div class="page-header">
      <h1>科研项目</h1>
      <el-button type="primary" :icon="Plus" @click="showCreate = true">创建项目</el-button>
    </div>

    <el-row :gutter="16">
      <el-col v-for="p in projects" :key="p.project_id" :span="8">
        <el-card shadow="hover" class="project-card" @click="router.push(`/projects/${p.project_id}`)">
          <template #header>
            <div class="card-header">
              <span class="project-name">{{ p.project_name }}</span>
              <el-button
                type="danger"
                size="small"
                :icon="Delete"
                circle
                @click.stop="handleDelete(p.project_id)"
              />
            </div>
          </template>
          <p class="project-desc">{{ p.description || '暂无描述' }}</p>
          <el-space>
            <el-tag size="small">成员: {{ p.member_count }}</el-tag>
            <el-tag type="warning" size="small">任务: {{ p.task_count }}</el-tag>
          </el-space>
        </el-card>
      </el-col>
      <el-col v-if="!projects.length && !loading" :span="24">
        <el-empty description="暂无项目，请创建第一个项目" />
      </el-col>
    </el-row>

    <!-- 创建项目对话框 -->
    <el-dialog v-model="showCreate" title="创建项目" width="400px">
      <el-form :model="form" label-position="top">
        <el-form-item label="项目名称" required>
          <el-input v-model="form.project_name" placeholder="例如：Flow Matching 研究" />
        </el-form-item>
        <el-form-item label="项目描述">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="描述项目的目标和范围" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreate = false">取消</el-button>
        <el-button type="primary" @click="handleCreate">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.project-list-page h1 {
  font-size: 24px;
  color: #303133;
}
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.project-card {
  margin-bottom: 16px;
  cursor: pointer;
  transition: transform 0.2s;
}
.project-card:hover {
  transform: translateY(-2px);
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.project-name {
  font-weight: 600;
  font-size: 16px;
  color: #303133;
}
.project-desc {
  color: #909399;
  font-size: 13px;
  min-height: 40px;
  margin-bottom: 12px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
