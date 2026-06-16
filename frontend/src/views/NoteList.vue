<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Delete, EditPen, Plus, Refresh, Search } from '@element-plus/icons-vue'
import { createNote, deleteNote, fetchNotes } from '../api/notes'
import { fetchPapers } from '../api/papers'

const router = useRouter()
const loading = ref(false)
const saving = ref(false)
const notes = ref([])
const papers = ref([])
const dialogOpen = ref(false)

const filters = reactive({
  keyword: '',
  paper_id: null,
})

const form = reactive({
  paper_id: null,
  title: '',
  content: '## Summary\n\nWrite notes here. Link concepts with [[Concept Name]].',
  note_type: 'summary',
})

async function loadNotes() {
  loading.value = true
  try {
    notes.value = await fetchNotes({
      keyword: filters.keyword || undefined,
      paper_id: filters.paper_id || undefined,
    })
  } catch (error) {
    ElMessage.error(error.userMessage)
  } finally {
    loading.value = false
  }
}

async function loadPapers() {
  try {
    papers.value = await fetchPapers({ limit: 200 })
  } catch (error) {
    ElMessage.error(error.userMessage)
  }
}

function resetForm() {
  form.paper_id = filters.paper_id || null
  form.title = ''
  form.content = '## Summary\n\nWrite notes here. Link concepts with [[Concept Name]].'
  form.note_type = 'summary'
}

async function submitNote() {
  if (!form.title.trim()) {
    ElMessage.warning('Title is required')
    return
  }
  saving.value = true
  try {
    const note = await createNote({
      paper_id: form.paper_id || null,
      title: form.title,
      content: form.content,
      note_type: form.note_type,
    })
    dialogOpen.value = false
    ElMessage.success('Note created')
    router.push(`/notes/${note.note_id}`)
  } catch (error) {
    ElMessage.error(error.userMessage)
  } finally {
    saving.value = false
  }
}

async function confirmDelete(note) {
  try {
    await ElMessageBox.confirm(`Delete note "${note.title}"?`, 'Delete note', {
      type: 'warning',
    })
    await deleteNote(note.note_id)
    ElMessage.success('Note deleted')
    await loadNotes()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.userMessage || 'Delete canceled')
    }
  }
}

function openCreateDialog() {
  resetForm()
  dialogOpen.value = true
}

onMounted(async () => {
  await Promise.all([loadPapers(), loadNotes()])
})
</script>

<template>
  <section class="page-section">
    <div class="page-heading">
      <div>
        <h1>Reading Notes</h1>
        <p>Write Markdown notes, parse wiki links, and connect papers with concepts.</p>
      </div>
      <div class="heading-actions">
        <el-button :icon="Refresh" @click="loadNotes">Refresh</el-button>
        <el-button type="primary" :icon="Plus" @click="openCreateDialog">New Note</el-button>
      </div>
    </div>

    <el-card class="tool-panel" shadow="never">
      <div class="note-filters">
        <el-input
          v-model="filters.keyword"
          :prefix-icon="Search"
          clearable
          placeholder="Search notes"
          @keyup.enter="loadNotes"
        />
        <el-select v-model="filters.paper_id" clearable filterable placeholder="Paper">
          <el-option
            v-for="paper in papers"
            :key="paper.paper_id"
            :label="paper.title"
            :value="paper.paper_id"
          />
        </el-select>
        <el-button type="primary" :icon="Search" @click="loadNotes">Search</el-button>
      </div>
    </el-card>

    <el-table v-loading="loading" :data="notes" row-key="note_id" class="paper-table">
      <el-table-column label="Note" min-width="280">
        <template #default="{ row }">
          <div class="paper-title" @click="router.push(`/notes/${row.note_id}`)">
            {{ row.title }}
          </div>
          <div class="paper-subline">
            {{ row.paper_title || 'No linked paper' }}
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="note_type" label="Type" width="120" />
      <el-table-column prop="updated_at" label="Updated" width="190" />
      <el-table-column label="Actions" width="180" fixed="right">
        <template #default="{ row }">
          <el-button :icon="EditPen" size="small" @click="router.push(`/notes/${row.note_id}`)">Open</el-button>
          <el-button :icon="Delete" size="small" type="danger" plain @click="confirmDelete(row)">Delete</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogOpen" title="New Note" width="720px">
      <el-form label-position="top">
        <el-form-item label="Title" required>
          <el-input v-model="form.title" placeholder="Note title" />
        </el-form-item>
        <el-form-item label="Paper">
          <el-select v-model="form.paper_id" clearable filterable placeholder="Optional linked paper" style="width: 100%">
            <el-option
              v-for="paper in papers"
              :key="paper.paper_id"
              :label="paper.title"
              :value="paper.paper_id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="Type">
          <el-select v-model="form.note_type" style="width: 100%">
            <el-option label="Summary" value="summary" />
            <el-option label="Method" value="method" />
            <el-option label="Idea" value="idea" />
            <el-option label="Question" value="question" />
          </el-select>
        </el-form-item>
        <el-form-item label="Content">
          <el-input v-model="form.content" type="textarea" :rows="8" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogOpen = false">Cancel</el-button>
        <el-button type="primary" :loading="saving" @click="submitNote">Create</el-button>
      </template>
    </el-dialog>
  </section>
</template>

<style scoped>
.note-filters {
  display: grid;
  grid-template-columns: minmax(260px, 1fr) minmax(260px, 1fr) auto;
  gap: 12px;
  align-items: center;
}

@media (max-width: 1024px) {
  .note-filters {
    grid-template-columns: 1fr;
  }
}
</style>
