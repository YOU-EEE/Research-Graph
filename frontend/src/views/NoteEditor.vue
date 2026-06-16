<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, Connection, Delete, Document, Finished, Refresh, View } from '@element-plus/icons-vue'
import { MdPreview } from 'md-editor-v3'
import 'md-editor-v3/lib/preview.css'
import {
  deleteNote,
  fetchNote,
  fetchNoteBacklinks,
  parseNoteLinks,
  updateNote,
} from '../api/notes'
import { fetchPapers } from '../api/papers'

const route = useRoute()
const router = useRouter()
const noteId = computed(() => Number(route.params.id))
const loading = ref(false)
const saving = ref(false)
const parsing = ref(false)
const note = ref(null)
const papers = ref([])
const parseResult = ref(null)
const backlinks = ref({ inbound_notes: [], shared_concept_notes: [] })
const previewMode = ref('split')

const form = ref({
  paper_id: null,
  title: '',
  content: '',
  note_type: 'summary',
})

const wikiLinks = computed(() => {
  const matches = form.value.content.match(/\[\[([^\[\]\n]+)\]\]/g) || []
  return [...new Set(matches.map((item) => item.slice(2, -2).split('|')[0].trim()).filter(Boolean))]
})

async function loadNote() {
  loading.value = true
  try {
    note.value = await fetchNote(noteId.value)
    form.value = {
      paper_id: note.value.paper_id || null,
      title: note.value.title,
      content: note.value.content,
      note_type: note.value.note_type || 'summary',
    }
  } catch (error) {
    ElMessage.error(error.userMessage)
  } finally {
    loading.value = false
  }
}

async function loadPapers() {
  papers.value = await fetchPapers({ limit: 200 })
}

async function loadBacklinks() {
  try {
    backlinks.value = await fetchNoteBacklinks(noteId.value)
  } catch (error) {
    ElMessage.error(error.userMessage)
  }
}

async function saveNote() {
  if (!form.value.title.trim()) {
    ElMessage.warning('Title is required')
    return
  }
  saving.value = true
  try {
    note.value = await updateNote(noteId.value, {
      paper_id: form.value.paper_id || null,
      title: form.value.title,
      content: form.value.content,
      note_type: form.value.note_type,
    })
    ElMessage.success('Note saved')
    await loadBacklinks()
  } catch (error) {
    ElMessage.error(error.userMessage)
  } finally {
    saving.value = false
  }
}

async function parseLinks() {
  parsing.value = true
  try {
    await saveNote()
    parseResult.value = await parseNoteLinks(noteId.value)
    await loadBacklinks()
    ElMessage.success('Wiki links parsed')
  } catch (error) {
    ElMessage.error(error.userMessage)
  } finally {
    parsing.value = false
  }
}

async function confirmDelete() {
  try {
    await ElMessageBox.confirm(`Delete note "${form.value.title}"?`, 'Delete note', {
      type: 'warning',
    })
    await deleteNote(noteId.value)
    ElMessage.success('Note deleted')
    router.push('/notes')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.userMessage || 'Delete canceled')
    }
  }
}

function openNote(item) {
  router.push(`/notes/${item.note_id}`)
}

onMounted(async () => {
  await Promise.all([loadNote(), loadPapers(), loadBacklinks()])
})
</script>

<template>
  <section v-loading="loading" class="page-section">
    <div class="detail-toolbar">
      <el-button :icon="ArrowLeft" @click="router.push('/notes')">Back</el-button>
      <div class="detail-actions">
        <el-segmented v-model="previewMode" :options="[
          { label: 'Split', value: 'split' },
          { label: 'Edit', value: 'edit' },
          { label: 'Preview', value: 'preview' },
        ]" />
        <el-button :icon="Connection" :loading="parsing" @click="parseLinks">Parse Links</el-button>
        <el-button type="primary" :icon="Finished" :loading="saving" @click="saveNote">Save</el-button>
        <el-button type="danger" plain :icon="Delete" @click="confirmDelete">Delete</el-button>
      </div>
    </div>

    <template v-if="note">
      <div class="note-shell">
        <section class="note-main">
          <div class="note-meta">
            <el-input v-model="form.title" class="note-title-input" placeholder="Note title" />
            <div class="note-meta-row">
              <el-select v-model="form.paper_id" clearable filterable placeholder="Linked paper">
                <el-option
                  v-for="paper in papers"
                  :key="paper.paper_id"
                  :label="paper.title"
                  :value="paper.paper_id"
                />
              </el-select>
              <el-select v-model="form.note_type" placeholder="Type">
                <el-option label="Summary" value="summary" />
                <el-option label="Method" value="method" />
                <el-option label="Idea" value="idea" />
                <el-option label="Question" value="question" />
              </el-select>
            </div>
          </div>

          <div class="editor-grid" :class="`mode-${previewMode}`">
            <el-input
              v-if="previewMode !== 'preview'"
              v-model="form.content"
              type="textarea"
              resize="none"
              class="markdown-input"
              placeholder="Use [[Concept Name]] to create concept links."
            />
            <div v-if="previewMode !== 'edit'" class="preview-pane">
              <MdPreview :model-value="form.content" />
            </div>
          </div>
        </section>

        <aside class="note-side">
          <el-card shadow="never">
            <template #header>
              <span><el-icon><Connection /></el-icon> Concepts</span>
            </template>
            <div class="tag-list">
              <el-tag
                v-for="name in wikiLinks"
                :key="name"
                effect="plain"
              >
                {{ name }}
              </el-tag>
              <span v-if="!wikiLinks.length" class="empty-text">No wiki links</span>
            </div>
            <div v-if="parseResult?.concepts?.length" class="side-list">
              <div
                v-for="concept in parseResult.concepts"
                :key="concept.concept_id"
                class="side-link"
                @click="router.push(`/concepts/${concept.concept_id}`)"
              >
                {{ concept.concept_name }}
              </div>
            </div>
          </el-card>

          <el-card shadow="never">
            <template #header>
              <span><el-icon><Refresh /></el-icon> Backlinks</span>
            </template>
            <div class="side-list">
              <div
                v-for="item in backlinks.inbound_notes"
                :key="`in-${item.note_id}`"
                class="side-link"
                @click="openNote(item)"
              >
                <strong>{{ item.title }}</strong>
                <small>{{ item.paper_title || 'No paper' }}</small>
              </div>
              <span v-if="!backlinks.inbound_notes?.length" class="empty-text">No direct backlinks</span>
            </div>
          </el-card>

          <el-card shadow="never">
            <template #header>
              <span><el-icon><Document /></el-icon> Related Notes</span>
            </template>
            <div class="side-list">
              <div
                v-for="item in backlinks.shared_concept_notes"
                :key="`shared-${item.note_id}`"
                class="side-link"
                @click="openNote(item)"
              >
                <strong>{{ item.title }}</strong>
                <small>{{ item.paper_title || 'No paper' }}</small>
              </div>
              <span v-if="!backlinks.shared_concept_notes?.length" class="empty-text">No shared concepts yet</span>
            </div>
          </el-card>

          <el-button
            v-if="form.paper_id"
            :icon="View"
            @click="router.push(`/papers/${form.paper_id}`)"
          >
            Open Paper
          </el-button>
        </aside>
      </div>
    </template>
  </section>
</template>

<style scoped>
.note-shell {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 320px;
  gap: 18px;
  align-items: start;
}

.note-main,
.note-side {
  min-width: 0;
}

.note-side {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.note-meta {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 12px;
}

.note-title-input :deep(.el-input__wrapper) {
  padding: 6px 12px;
}

.note-title-input :deep(.el-input__inner) {
  height: 38px;
  font-size: 24px;
  font-weight: 700;
}

.note-meta-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 180px;
  gap: 10px;
}

.editor-grid {
  display: grid;
  min-height: calc(100vh - 250px);
  border: 1px solid var(--line);
  border-radius: 8px;
  overflow: hidden;
  background: #fff;
}

.editor-grid.mode-split {
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
}

.editor-grid.mode-edit,
.editor-grid.mode-preview {
  grid-template-columns: 1fr;
}

.markdown-input :deep(.el-textarea__inner) {
  height: 100%;
  min-height: calc(100vh - 250px) !important;
  border: 0;
  border-radius: 0;
  box-shadow: none;
  font-family: "Cascadia Code", "JetBrains Mono", Consolas, monospace;
  font-size: 14px;
  line-height: 1.7;
}

.preview-pane {
  min-width: 0;
  overflow: auto;
  border-left: 1px solid var(--line);
  background: #fff;
}

.mode-preview .preview-pane {
  border-left: 0;
}

.side-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.side-link {
  display: flex;
  cursor: pointer;
  flex-direction: column;
  gap: 2px;
  border: 1px solid var(--line);
  border-radius: 6px;
  background: #f9fafb;
  padding: 8px;
}

.side-link:hover {
  border-color: var(--primary);
  background: #eff6ff;
}

.side-link strong {
  color: #111827;
  font-size: 13px;
  line-height: 1.35;
}

.side-link small {
  color: var(--muted);
  font-size: 12px;
}

@media (max-width: 1024px) {
  .note-shell,
  .editor-grid.mode-split,
  .note-meta-row {
    grid-template-columns: 1fr;
  }

  .preview-pane {
    border-left: 0;
    border-top: 1px solid var(--line);
  }
}
</style>
