<script setup>
import { ref, onMounted, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { listTasks, updateTaskStatus, createComment, listComments, deleteTask } from '../api/projects'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Check, ChatDotRound, Delete } from '@element-plus/icons-vue'

const router = useRouter()
const tasks = ref([])
const loading = ref(false)
const statusFilter = ref('')
const showComments = ref(false)
const currentTaskId = ref(null)
const comments = ref([])
const commentForm = reactive({ target_type: 'task', target_id: null, content: '' })

const statusOptions = [
  { label: '全部', value: '' },
  { label: '待开始', value: 'todo' },
  { label: '阅读中', value: 'reading' },
  { label: '已完成', value: 'done' },
  { label: '已报告', value: 'reported' },
]

const statusColors = {
  todo: 'info',
  reading: 'warning',
  done: 'success',
  reported: '',
}

async function loadTasks() {
  loading.value = true
  try {
    const params = {}
    if (statusFilter.value) params.status = statusFilter.value
    const { data } = await listTasks(params)
    tasks.value = data
  } catch (e) {
    ElMessage.error('加载任务失败')
  } finally {
    loading.value = false
  }
}

async function handleStatusChange(taskId, newStatus) {
  try {
    await updateTaskStatus(taskId, { status: newStatus })
    ElMessage.success('状态已更新')
    loadTasks()
  } catch (e) {
    ElMessage.error(e.userMessage || '更新失败')
  }
}

async function handleShowComments(taskId) {
  currentTaskId.value = taskId
  commentForm.target_id = taskId
  try {
    const { data } = await listComments({ target_type: 'task', target_id: taskId })
    comments.value = data
    showComments.value = true
  } catch (e) {
    ElMessage.error('加载评论失败')
  }
}

async function handleAddComment() {
  try {
    await createComment({ ...commentForm })
    ElMessage.success('评论已添加')
    commentForm.content = ''
    // 重新加载评论
    const { data } = await listComments({
      target_type: 'task',
      target_id: currentTaskId.value,
    })
    comments.value = data
  } catch (e) {
    ElMessage.error('评论失败')
  }
}

async function handleDeleteTask(taskId) {
  try {
    await ElMessageBox.confirm('确定要删除该任务吗？', '确认')
    await deleteTask(taskId)
    ElMessage.success('任务已删除')
    loadTasks()
  } catch { /* cancelled */ }
}

onMounted(loadTasks)
</script>

<template>
  <div class="task-list-page">
    <div class="page-header">
      <h1>阅读任务</h1>
      <el-select v-model="statusFilter" placeholder="筛选状态" @change="loadTasks" style="width: 140px">
        <el-option
          v-for="opt in statusOptions"
          :key="opt.value"
          :label="opt.label"
          :value="opt.value"
        />
      </el-select>
    </div>

    <el-table :data="tasks" v-loading="loading" stripe>
      <el-table-column prop="title" label="任务名称" show-overflow-tooltip min-width="180" />
      <el-table-column prop="paper_title" label="对应论文" show-overflow-tooltip min-width="200" />
      <el-table-column label="负责人" width="120">
        <template #default="{ row }">
          <el-tag
            v-for="a in row.assignees"
            :key="a.user_id"
            size="small"
            :type="statusColors[a.role] || 'info'"
            style="margin: 1px"
          >
            {{ a.username }}
          </el-tag>
          <span v-if="!row.assignees?.length" style="color: #909399">-</span>
        </template>
      </el-table-column>
      <el-table-column prop="deadline" label="截止时间" width="110" />
      <el-table-column label="任务状态" width="130">
        <template #default="{ row }">
          <el-select
            :model-value="row.assignees?.[0]?.role || 'todo'"
            size="small"
            @change="(val) => handleStatusChange(row.task_id, val)"
          >
            <el-option label="待开始" value="todo" />
            <el-option label="阅读中" value="reading" />
            <el-option label="已完成" value="done" />
            <el-option label="已报告" value="reported" />
          </el-select>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="160">
        <template #default="{ row }">
          <el-button
            type="success"
            size="small"
            @click="handleStatusChange(row.task_id, 'done')"
            :disabled="row.assignees?.[0]?.role === 'done' || row.assignees?.[0]?.role === 'reported'"
          >
            完成
          </el-button>
          <el-button type="warning" size="small" :icon="ChatDotRound" circle @click="handleShowComments(row.task_id)" />
          <el-button type="danger" size="small" :icon="Delete" circle @click="handleDeleteTask(row.task_id)" />
        </template>
      </el-table-column>
    </el-table>

    <!-- 评论对话框 -->
    <el-dialog v-model="showComments" title="评论" width="500px">
      <div class="comments-list" v-if="comments.length">
        <div v-for="c in comments" :key="c.comment_id" class="comment-item">
          <div class="comment-header">
            <strong>{{ c.username }}</strong>
            <span class="comment-time">{{ c.created_at }}</span>
          </div>
          <div class="comment-body">{{ c.content }}</div>
        </div>
      </div>
      <el-empty v-else description="暂无评论" />
      <el-divider />
      <div class="comment-input">
        <el-input
          v-model="commentForm.content"
          type="textarea"
          :rows="2"
          placeholder="输入评论..."
        />
        <el-button type="primary" @click="handleAddComment" style="margin-top: 8px">
          发送
        </el-button>
      </div>
    </el-dialog>
  </div>
</template>

<style scoped>
.task-list-page h1 {
  font-size: 24px;
  color: #303133;
}
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.comment-item {
  padding: 8px 0;
  border-bottom: 1px solid #ebeef5;
}
.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}
.comment-time {
  font-size: 12px;
  color: #909399;
}
.comment-body {
  font-size: 14px;
  color: #606266;
}
</style>
