<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Edit, Link, View, Upload } from '@element-plus/icons-vue'
import PaperForm from '../components/PaperForm.vue'
import {
  addPaperToCollection,
  attachmentPreviewUrl,
  fetchAuthors,
  fetchCollections,
  fetchPaper,
  fetchTags,
  fetchVenues,
  updatePaper,
  uploadAttachment,
} from '../api/papers'

const route = useRoute()
const router = useRouter()
const paperId = computed(() => Number(route.params.id))
const loading = ref(false)
const saving = ref(false)
const editOpen = ref(false)
const paper = ref(null)
const authors = ref([])
const tags = ref([])
const venues = ref([])
const collections = ref([])
const selectedCollection = ref(null)
const previewOpen = ref(false)
const previewAttachment = ref(null)
const previewUrl = ref('')

async function loadPaper() {
  loading.value = true
  try {
    paper.value = await fetchPaper(paperId.value)
  } catch (error) {
    ElMessage.error(error.userMessage)
  } finally {
    loading.value = false
  }
}

async function loadLookups() {
  const [authorData, tagData, venueData, collectionData] = await Promise.all([
    fetchAuthors(),
    fetchTags(),
    fetchVenues(),
    fetchCollections(),
  ])
  authors.value = authorData
  tags.value = tagData
  venues.value = venueData
  collections.value = collectionData
}

async function savePaper(payload) {
  saving.value = true
  try {
    paper.value = await updatePaper(paperId.value, payload)
    editOpen.value = false
    ElMessage.success('Paper updated')
    await loadLookups()
  } catch (error) {
    ElMessage.error(error.userMessage)
  } finally {
    saving.value = false
  }
}

async function handleAttachment(options) {
  try {
    await uploadAttachment(paperId.value, options.file)
    ElMessage.success('Attachment uploaded')
    await loadPaper()
  } catch (error) {
    ElMessage.error(error.userMessage)
  }
}

async function addToCollection() {
  if (!selectedCollection.value) return
  try {
    await addPaperToCollection(selectedCollection.value, paperId.value)
    selectedCollection.value = null
    ElMessage.success('Paper added to collection')
    await loadPaper()
  } catch (error) {
    ElMessage.error(error.userMessage)
  }
}

function openExternal(url) {
  if (url) window.open(url, '_blank', 'noopener,noreferrer')
}

function isPdfAttachment(attachment) {
  const type = attachment.file_type || ''
  const name = attachment.file_name || ''
  return type.includes('pdf') || name.toLowerCase().endsWith('.pdf')
}

function previewFile(attachment) {
  const url = attachmentPreviewUrl(paperId.value, attachment.attachment_id)
  if (!isPdfAttachment(attachment)) {
    openExternal(url)
    return
  }
  previewAttachment.value = attachment
  previewUrl.value = url
  previewOpen.value = true
}

onMounted(async () => {
  await Promise.all([loadPaper(), loadLookups()])
})
</script>

<template>
  <section v-loading="loading" class="page-section">
    <div class="detail-toolbar">
      <el-button :icon="ArrowLeft" @click="router.push('/papers')">Back</el-button>
      <div class="detail-actions">
        <el-button :icon="Link" :disabled="!paper?.url" @click="openExternal(paper?.url)">Open URL</el-button>
        <el-button type="primary" :icon="Edit" @click="editOpen = true">Edit</el-button>
      </div>
    </div>

    <template v-if="paper">
      <div class="detail-header">
        <div>
          <h1>{{ paper.title }}</h1>
          <p>
            {{ paper.authors?.map((author) => author.author_name).join(', ') || 'No authors' }}
          </p>
        </div>
        <el-tag effect="plain" size="large">{{ paper.reading_status }}</el-tag>
      </div>

      <div class="detail-grid">
        <el-card shadow="never" class="detail-main">
          <template #header>Metadata</template>
          <dl class="metadata-list">
            <div>
              <dt>Year</dt>
              <dd>{{ paper.year || '-' }}</dd>
            </div>
            <div>
              <dt>Venue</dt>
              <dd>{{ paper.venue_ref?.venue_name || paper.venue || '-' }}</dd>
            </div>
            <div>
              <dt>Type</dt>
              <dd>{{ paper.paper_type || '-' }}</dd>
            </div>
            <div>
              <dt>DOI</dt>
              <dd>{{ paper.doi || '-' }}</dd>
            </div>
            <div>
              <dt>arXiv</dt>
              <dd>{{ paper.arxiv_id || '-' }}</dd>
            </div>
            <div>
              <dt>URL</dt>
              <dd class="breakable">{{ paper.url || '-' }}</dd>
            </div>
          </dl>

          <h2>Abstract</h2>
          <p class="abstract-text">{{ paper.abstract || 'No abstract recorded.' }}</p>
        </el-card>

        <aside class="detail-side">
          <el-card shadow="never">
            <template #header>Tags</template>
            <div class="tag-list">
              <el-tag v-for="tag in paper.tags" :key="tag.tag_id" :color="tag.color" effect="light">
                {{ tag.tag_name }}
              </el-tag>
              <span v-if="!paper.tags?.length" class="empty-text">No tags</span>
            </div>
          </el-card>

          <el-card shadow="never">
            <template #header>Collections</template>
            <div class="collection-row">
              <el-tag
                v-for="collection in paper.collections"
                :key="collection.collection_id"
                effect="plain"
              >
                {{ collection.collection_name }}
              </el-tag>
              <span v-if="!paper.collections?.length" class="empty-text">No collections</span>
            </div>
            <div class="side-action">
              <el-select v-model="selectedCollection" clearable placeholder="Choose collection">
                <el-option
                  v-for="collection in collections"
                  :key="collection.collection_id"
                  :label="collection.collection_name"
                  :value="collection.collection_id"
                />
              </el-select>
              <el-button @click="addToCollection">Add</el-button>
            </div>
          </el-card>
        </aside>
      </div>

      <div class="detail-grid lower">
        <el-card shadow="never">
          <template #header>Attachments</template>
          <el-upload :http-request="handleAttachment" :show-file-list="false">
            <el-button :icon="Upload">Upload PDF / file</el-button>
          </el-upload>
          <el-table :data="paper.attachments" size="small" class="nested-table">
            <el-table-column prop="file_name" label="File" />
            <el-table-column prop="file_type" label="Type" width="180" />
            <el-table-column prop="file_path" label="Path" />
            <el-table-column label="Preview" width="120">
              <template #default="{ row }">
                <el-button :icon="View" size="small" @click="previewFile(row)">
                  {{ isPdfAttachment(row) ? 'Preview' : 'Open' }}
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>

        <el-card shadow="never">
          <template #header>BibTeX</template>
          <div v-if="paper.bibtex_entries?.length" class="bibtex-list">
            <pre v-for="entry in paper.bibtex_entries" :key="entry.bibtex_id">{{ entry.raw_bibtex }}</pre>
          </div>
          <span v-else class="empty-text">No BibTeX entry</span>
        </el-card>
      </div>
    </template>

    <el-dialog v-model="editOpen" title="Edit Paper" width="760px">
      <PaperForm
        :model-value="paper || {}"
        :authors="authors"
        :tags="tags"
        :venues="venues"
        :loading="saving"
        submit-text="Save"
        @cancel="editOpen = false"
        @submit="savePaper"
      />
    </el-dialog>

    <el-dialog
      v-model="previewOpen"
      :title="previewAttachment?.file_name || 'PDF Preview'"
      class="pdf-preview-dialog"
      width="88vw"
      top="4vh"
    >
      <div class="pdf-preview-frame">
        <object :data="previewUrl" type="application/pdf">
          <iframe :src="previewUrl" title="PDF preview" />
        </object>
      </div>
      <template #footer>
        <el-button :icon="Link" @click="openExternal(previewUrl)">Open in New Tab</el-button>
      </template>
    </el-dialog>
  </section>
</template>
