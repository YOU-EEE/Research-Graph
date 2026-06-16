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
    <div class="note-toolbar">
      <el-button :icon="ArrowLeft" @click="router.push('/notes')">Back</el-button>
      <div class="note-toolbar-actions">
        <el-segmented
          v-model="previewMode"
          class="mode-switch"
          :options="[
            { label: 'Split', value: 'split' },
            { label: 'Edit', value: 'edit' },
            { label: 'Preview', value: 'preview' },
          ]"
        />
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
              <el-select v-model="form.paper_id" clearable filterable placeholder="Linked paper" class="paper-select">
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

          <div class="editor-card">
            <div class="editor-grid" :class="`mode-${previewMode}`">
              <section v-if="previewMode !== 'preview'" class="editor-pane">
                <div class="pane-heading">
                  <span>Markdown</span>
                  <small>{{ form.content.length }} chars</small>
                </div>
                <el-input
                  v-model="form.content"
                  type="textarea"
                  resize="none"
                  class="markdown-input"
                  placeholder="Use [[Concept Name]] to create concept links."
                />
              </section>
              <section v-if="previewMode !== 'edit'" class="preview-pane">
                <div class="pane-heading">
                  <span>Preview</span>
                  <small>{{ wikiLinks.length }} links</small>
                </div>
                <MdPreview :model-value="form.content" />
              </section>
            </div>
          </div>
        </section>

        <aside class="note-side">
          <el-card shadow="never" class="side-card">
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

          <el-card shadow="never" class="side-card">
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

          <el-card shadow="never" class="side-card">
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
.page-section {
  gap: 14px;
}

.note-toolbar {
  position: sticky;
  top: 0;
  z-index: 12;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  border: 1px solid #dde3ec;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.94);
  padding: 10px 12px;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.05);
  backdrop-filter: blur(10px);
}

.note-toolbar-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: flex-end;
}

.mode-switch {
  --el-segmented-item-selected-bg-color: var(--primary);
  --el-segmented-item-selected-color: #fff;
  --el-segmented-item-hover-bg-color: #eaf2ff;
  min-width: 260px;
}

.note-shell {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 360px;
  gap: 20px;
  align-items: start;
  max-width: 1680px;
  margin: 0 auto;
  width: 100%;
}

.note-main,
.note-side {
  min-width: 0;
}

.note-side {
  display: flex;
  flex-direction: column;
  gap: 12px;
  position: sticky;
  top: 88px;
}

.note-meta {
  display: grid;
  gap: 12px;
  margin-bottom: 14px;
  border: 1px solid #dde3ec;
  border-radius: 8px;
  background: #fff;
  padding: 14px 16px;
}

.note-title-input :deep(.el-input__wrapper) {
  padding: 0;
  border-radius: 0;
  background: transparent;
  box-shadow: none;
}

.note-title-input :deep(.el-input__inner) {
  height: 46px;
  color: #111827;
  font-size: 30px;
  font-weight: 700;
  letter-spacing: 0;
  line-height: 1.2;
}

.note-meta-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 180px;
  gap: 12px;
}

.editor-card {
  border: 1px solid #dde3ec;
  border-radius: 8px;
  overflow: hidden;
  background: #fff;
  box-shadow: 0 12px 28px rgba(15, 23, 42, 0.04);
}

.editor-grid {
  display: grid;
  min-height: calc(100vh - 290px);
  background: #fff;
}

.editor-grid.mode-split {
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
}

.editor-grid.mode-edit,
.editor-grid.mode-preview {
  grid-template-columns: 1fr;
}

.editor-pane,
.preview-pane {
  display: flex;
  min-width: 0;
  min-height: calc(100vh - 290px);
  flex-direction: column;
  background: #fff;
}

.pane-heading {
  display: flex;
  height: 42px;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #edf0f5;
  background: #f8fafc;
  padding: 0 14px;
  color: #374151;
  font-size: 13px;
  font-weight: 700;
}

.pane-heading small {
  color: var(--muted);
  font-size: 12px;
  font-weight: 500;
}

.markdown-input {
  flex: 1;
}

.markdown-input :deep(.el-textarea__inner) {
  height: 100%;
  min-height: calc(100vh - 332px) !important;
  border: 0;
  border-radius: 0;
  box-shadow: none;
  font-family: "Cascadia Code", "JetBrains Mono", Consolas, monospace;
  font-size: 14px;
  line-height: 1.85;
  padding: 18px 22px;
  color: #334155;
  background: #fcfdff;
}

.preview-pane {
  overflow: auto;
  border-left: 1px solid var(--line);
}

.mode-preview .preview-pane {
  border-left: 0;
}

.preview-pane :deep(.md-editor-preview-wrapper) {
  flex: 1;
  padding: 20px 24px;
}

.preview-pane :deep(.md-editor-preview) {
  color: #1f2937;
  font-size: 16px;
  line-height: 1.85;
}

.preview-pane :deep(.md-editor-preview p) {
  margin: 0 0 14px;
}

.preview-pane :deep(.katex-display) {
  overflow-x: auto;
  overflow-y: hidden;
  padding: 6px 0;
}

.side-card {
  border-color: #dde3ec;
  border-radius: 8px;
}

.side-card :deep(.el-card__header) {
  padding: 12px 14px;
  color: #374151;
  font-size: 13px;
  font-weight: 700;
}

.side-card :deep(.el-card__header span) {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.side-card :deep(.el-card__body) {
  padding: 14px;
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
  gap: 4px;
  border: 1px solid var(--line);
  border-radius: 6px;
  background: #f9fafb;
  padding: 10px;
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

  .note-toolbar,
  .note-toolbar-actions {
    align-items: stretch;
    flex-direction: column;
  }

  .mode-switch {
    min-width: 0;
  }

  .note-side {
    position: static;
  }

  .preview-pane {
    border-left: 0;
    border-top: 1px solid var(--line);
  }
}
</style>
