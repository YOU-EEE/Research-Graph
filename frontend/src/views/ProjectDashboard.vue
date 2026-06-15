<script setup>
import { ref, onMounted, reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  getProject, listMembers, addMember, removeMember,
  updateMemberRole, listTasks, createTask, deleteTask,
} from '../api/projects'
import { getUsers } from '../api/auth'
import { getGraph } from '../api/graph'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, User, Delete, Setting } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const projectId = computed(() => Number(route.params.id))

const project = ref({})
const members = ref([])
const tasks = ref([])
const allUsers = ref([])
const showAddMember = ref(false)
const showCreateTask = ref(false)

const memberForm = reactive({ user_id: null, role: 'member' })
const taskForm = reactive({
  project_id: projectId.value,
  paper_id: null,
  title: '',
  task_description: '',
  deadline: null,
  assignee_ids: [],
})

async function loadProject() {
  try {
    const [projRes, memberRes, taskRes, userRes] = await Promise.all([
      getProject(projectId.value),
      listMembers(projectId.value),
      listTasks({ project_id: projectId.value }),
      getUsers(),
    ])
    project.value = projRes.data
    members.value = memberRes.data
    tasks.value = taskRes.data
    allUsers.value = userRes.data
  } catch (e) {
    ElMessage.error('加载项目失败')
  }
}

async function handleAddMember() {
  try {
    await addMember(projectId.value, memberForm)
    ElMessage.success('添加成员成功')
    showAddMember.value = false
    loadProject()
  } catch (e) {
    ElMessage.error(e.userMessage || '添加失败')
  }
}

async function handleRemoveMember(userId) {
  try {
    await ElMessageBox.confirm('确定要移除该成员吗？', '确认')
    await removeMember(projectId.value, userId)
    ElMessage.success('成员已移除')
    loadProject()
  } catch { /* cancelled */ }
}

async function handleRoleChange(userId, role) {
  try {
    await updateMemberRole(projectId.value, userId, { role })
    ElMessage.success('角色已更新')
  } catch (e) {
    ElMessage.error('更新失败')
  }
}

async function handleCreateTask() {
  taskForm.project_id = projectId.value
  try {
    await createTask(taskForm)
    ElMessage.success('任务创建成功')
    showCreateTask.value = false
    loadProject()
  } catch (e) {
    ElMessage.error(e.userMessage || '创建失败')
  }
}

async function handleDeleteTask(taskId) {
  try {
    await ElMessageBox.confirm('确定要删除该任务吗？', '确认')
    await deleteTask(taskId)
    ElMessage.success('任务已删除')
    loadProject()
  } catch { /* cancelled */ }
}

onMounted(loadProject)
</script>

<template>
  <div class="project-dashboard">
    <el-page-header @back="router.push('/projects')" :content="project.project_name" />

    <el-descriptions :column="2" border style="margin: 20px 0">
      <el-descriptions-item label="项目名称">{{ project.project_name }}</el-descriptions-item>
      <el-descriptions-item label="创建时间">{{ project.created_at }}</el-descriptions-item>
      <el-descriptions-item label="描述" :span="2">{{ project.description || '暂无描述' }}</el-descriptions-item>
      <el-descriptions-item label="成员数">{{ project.member_count }}</el-descriptions-item>
      <el-descriptions-item label="任务数">{{ project.task_count }}</el-descriptions-item>
    </el-descriptions>

    <el-row :gutter="16">
      <!-- 成员列表 -->
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>项目成员</span>
              <el-button type="primary" size="small" :icon="Plus" @click="showAddMember = true">
                添加成员
              </el-button>
            </div>
          </template>
          <el-table :data="members" size="small">
            <el-table-column prop="username" label="用户名" />
            <el-table-column prop="role" label="角色" width="120">
              <template #default="{ row }">
                <el-select
                  :model-value="row.role"
                  size="small"
                  @change="(val) => handleRoleChange(row.user_id, val)"
                >
                  <el-option label="Admin" value="admin" />
                  <el-option label="Member" value="member" />
                  <el-option label="Viewer" value="viewer" />
                </el-select>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="80">
              <template #default="{ row }">
                <el-button type="danger" size="small" :icon="Delete" circle @click="handleRemoveMember(row.user_id)" />
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <!-- 阅读任务列表 -->
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>阅读任务</span>
              <el-button type="primary" size="small" :icon="Plus" @click="showCreateTask = true">
                创建任务
              </el-button>
            </div>
          </template>
          <el-table :data="tasks" size="small">
            <el-table-column prop="title" label="任务名称" show-overflow-tooltip />
            <el-table-column prop="paper_title" label="对应论文" show-overflow-tooltip />
            <el-table-column label="负责人" width="100">
              <template #default="{ row }">
                <el-tag v-for="a in row.assignees" :key="a.user_id" size="small" style="margin: 1px">
                  {{ a.username }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="deadline" label="截止时间" width="110" />
            <el-table-column label="操作" width="80">
              <template #default="{ row }">
                <el-button type="danger" size="small" :icon="Delete" circle @click="handleDeleteTask(row.task_id)" />
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <!-- 知识图谱入口 -->
    <div style="margin-top: 16px">
      <el-button type="warning" size="large" @click="router.push(`/graph?project_id=${projectId}`)">
        查看项目知识图谱
      </el-button>
    </div>

    <!-- 添加成员对话框 -->
    <el-dialog v-model="showAddMember" title="添加成员" width="400px">
      <el-form :model="memberForm" label-position="top">
        <el-form-item label="选择用户">
          <el-select v-model="memberForm.user_id" placeholder="请选择" style="width: 100%">
            <el-option
              v-for="u in allUsers"
              :key="u.user_id"
              :label="u.username"
              :value="u.user_id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="memberForm.role" style="width: 100%">
            <el-option label="Admin" value="admin" />
            <el-option label="Member" value="member" />
            <el-option label="Viewer" value="viewer" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddMember = false">取消</el-button>
        <el-button type="primary" @click="handleAddMember">确定</el-button>
      </template>
    </el-dialog>

    <!-- 创建任务对话框 -->
    <el-dialog v-model="showCreateTask" title="创建阅读任务" width="500px">
      <el-form :model="taskForm" label-position="top">
        <el-form-item label="任务名称" required>
          <el-input v-model="taskForm.title" placeholder="例如：阅读 AnyFlow 论文" />
        </el-form-item>
        <el-form-item label="论文 ID" required>
          <el-input-number v-model="taskForm.paper_id" :min="1" placeholder="论文 ID" style="width: 100%" />
        </el-form-item>
        <el-form-item label="任务描述">
          <el-input v-model="taskForm.task_description" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="截止日期">
          <el-date-picker v-model="taskForm.deadline" type="date" style="width: 100%" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item label="分配给">
          <el-select v-model="taskForm.assignee_ids" multiple placeholder="选择成员" style="width: 100%">
            <el-option
              v-for="m in members"
              :key="m.user_id"
              :label="m.username"
              :value="m.user_id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateTask = false">取消</el-button>
        <el-button type="primary" @click="handleCreateTask">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { computed } from 'vue'
</script>

<style scoped>
.project-dashboard {
  max-width: 1200px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
