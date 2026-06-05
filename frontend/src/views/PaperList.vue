<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Folder, Plus, Refresh, Search, Setting } from '@element-plus/icons-vue'
import PaperForm from '../components/PaperForm.vue'
import {
  addPaperToCollection,
  createCollection,
  createPaper,
  createTag,
  createVenue,
  deleteCollection,
  deletePaper,
  deleteTag,
  deleteVenue,
  fetchAuthors,
  fetchCollectionPapers,
  fetchCollections,
  fetchPapers,
  fetchTags,
  fetchVenues,
  removePaperFromCollection,
} from '../api/papers'

const router = useRouter()
const loading = ref(false)
const saving = ref(false)
const dialogOpen = ref(false)
const metadataOpen = ref(false)
const papers = ref([])
const authors = ref([])
const tags = ref([])
const venues = ref([])
const collections = ref([])
const activeCollectionId = ref(null)
const collectionPapers = ref([])
const selectedPaperId = ref(null)
const collectionTreeRef = ref(null)

const filters = reactive({
  keyword: '',
  tag: '',
  year: null,
  reading_status: '',
  limit: 50,
})

const metadataForm = reactive({
  tag_name: '',
  tag_color: '#409eff',
  venue_name: '',
  venue_type: 'conference',
  collection_name: '',
  collection_parent_id: null,
})

const collectionTree = computed(() => {
  const nodeMap = new Map()
  const roots = []

  collections.value.forEach((collection) => {
    nodeMap.set(collection.collection_id, {
      ...collection,
      id: collection.collection_id,
      label: collection.collection_name,
      children: [],
    })
  })

  nodeMap.forEach((node) => {
    if (node.parent_id && nodeMap.has(node.parent_id)) {
      nodeMap.get(node.parent_id).children.push(node)
    } else {
      roots.push(node)
    }
  })

  const sortNodes = (nodes) => {
    nodes.sort((a, b) => a.collection_name.localeCompare(b.collection_name))
    nodes.forEach((node) => sortNodes(node.children))
  }
  sortNodes(roots)
  return roots
})

const activeCollection = computed(() =>
  collections.value.find((collection) => collection.collection_id === activeCollectionId.value),
)

const collectionParentOptions = computed(() => {
  const options = [{ collection_id: null, collection_name: 'Root directory' }]
  const walk = (nodes, depth = 0) => {
    nodes.forEach((node) => {
      options.push({
        collection_id: node.collection_id,
        collection_name: `${'--'.repeat(depth)}${depth ? ' ' : ''}${node.collection_name}`,
      })
      walk(node.children, depth + 1)
    })
  }
  walk(collectionTree.value)
  return options
})

const availablePapersForCollection = computed(() => {
  const existingIds = new Set(collectionPapers.value.map((paper) => paper.paper_id))
  return papers.value.filter((paper) => !existingIds.has(paper.paper_id))
})

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
  const activeStillExists = collectionData.some(
    (collection) => collection.collection_id === activeCollectionId.value,
  )
  if (!activeStillExists) {
    activeCollectionId.value = null
  }
  if (!activeCollectionId.value && collectionData.length) {
    activeCollectionId.value = collectionData[0].collection_id
  }
}

async function loadPapers() {
  loading.value = true
  try {
    const params = {
      keyword: filters.keyword || undefined,
      tag: filters.tag || undefined,
      year: filters.year || undefined,
      reading_status: filters.reading_status || undefined,
      limit: filters.limit,
    }
    papers.value = await fetchPapers(params)
  } catch (error) {
    ElMessage.error(error.userMessage)
  } finally {
    loading.value = false
  }
}

async function refreshAll() {
  await Promise.all([loadLookups(), loadPapers()])
  await loadCollectionPapers()
}

async function submitPaper(payload) {
  if (!payload.title) {
    ElMessage.warning('Title is required')
    return
  }
  saving.value = true
  try {
    const paper = await createPaper(payload)
    ElMessage.success('Paper created')
    dialogOpen.value = false
    await refreshAll()
    router.push(`/papers/${paper.paper_id}`)
  } catch (error) {
    ElMessage.error(error.userMessage)
  } finally {
    saving.value = false
  }
}

async function confirmDelete(row) {
  try {
    await ElMessageBox.confirm(`Delete "${row.title}"?`, 'Delete paper', {
      type: 'warning',
    })
    await deletePaper(row.paper_id)
    ElMessage.success('Paper deleted')
    await loadPapers()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.userMessage || 'Delete canceled')
    }
  }
}

async function addTag() {
  if (!metadataForm.tag_name.trim()) return
  try {
    await createTag({ tag_name: metadataForm.tag_name, color: metadataForm.tag_color })
    metadataForm.tag_name = ''
    await loadLookups()
    ElMessage.success('Tag saved')
  } catch (error) {
    ElMessage.error(error.userMessage)
  }
}

async function confirmDeleteTag(tag) {
  try {
    await ElMessageBox.confirm(`Delete tag "${tag.tag_name}"?`, 'Delete tag', {
      type: 'warning',
    })
    await deleteTag(tag.tag_id)
    ElMessage.success('Tag deleted')
    await refreshAll()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.userMessage || 'Delete canceled')
    }
  }
}

async function addVenue() {
  if (!metadataForm.venue_name.trim()) return
  try {
    await createVenue({
      venue_name: metadataForm.venue_name,
      venue_type: metadataForm.venue_type,
    })
    metadataForm.venue_name = ''
    await loadLookups()
    ElMessage.success('Venue saved')
  } catch (error) {
    ElMessage.error(error.userMessage)
  }
}

async function confirmDeleteVenue(venue) {
  try {
    await ElMessageBox.confirm(
      `Delete venue "${venue.venue_name}"? Papers using it will keep no venue reference.`,
      'Delete venue',
      { type: 'warning' },
    )
    await deleteVenue(venue.venue_id)
    ElMessage.success('Venue deleted')
    await refreshAll()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.userMessage || 'Delete canceled')
    }
  }
}

async function addCollection() {
  if (!metadataForm.collection_name.trim()) return
  try {
    const collection = await createCollection({
      collection_name: metadataForm.collection_name,
      parent_id: metadataForm.collection_parent_id || null,
    })
    metadataForm.collection_name = ''
    metadataForm.collection_parent_id = collection.collection_id
    activeCollectionId.value = collection.collection_id
    await loadLookups()
    await loadCollectionPapers()
    ElMessage.success('Collection saved')
  } catch (error) {
    ElMessage.error(error.userMessage)
  }
}

function selectCollection(data) {
  activeCollectionId.value = data.collection_id
  metadataForm.collection_parent_id = data.collection_id
  loadCollectionPapers()
}

function prepareRootCollection() {
  metadataForm.collection_parent_id = null
}

function prepareChildCollection() {
  metadataForm.collection_parent_id = activeCollectionId.value
}

async function loadCollectionPapers() {
  if (!activeCollectionId.value) {
    collectionPapers.value = []
    return
  }
  try {
    collectionPapers.value = await fetchCollectionPapers(activeCollectionId.value)
  } catch (error) {
    ElMessage.error(error.userMessage)
  }
}

async function addSelectedPaperToCollection() {
  if (!activeCollectionId.value || !selectedPaperId.value) return
  try {
    await addPaperToCollection(activeCollectionId.value, selectedPaperId.value)
    selectedPaperId.value = null
    await loadCollectionPapers()
    await loadPapers()
    ElMessage.success('Paper added to collection')
  } catch (error) {
    ElMessage.error(error.userMessage)
  }
}

async function removeFromActiveCollection(paper) {
  if (!activeCollectionId.value) return
  try {
    await removePaperFromCollection(activeCollectionId.value, paper.paper_id)
    await loadCollectionPapers()
    await loadPapers()
    ElMessage.success('Paper removed from collection')
  } catch (error) {
    ElMessage.error(error.userMessage)
  }
}

async function confirmDeleteCollection(collection) {
  try {
    await ElMessageBox.confirm(
      `Delete collection "${collection.collection_name}"? Papers will not be deleted.`,
      'Delete collection',
      { type: 'warning' },
    )
    await deleteCollection(collection.collection_id)
    if (activeCollectionId.value === collection.collection_id) {
      activeCollectionId.value = null
      collectionPapers.value = []
    }
    if (metadataForm.collection_parent_id === collection.collection_id) {
      metadataForm.collection_parent_id = null
    }
    await refreshAll()
    ElMessage.success('Collection deleted')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.userMessage || 'Delete canceled')
    }
  }
}

function tagColor(tagName) {
  return tags.value.find((tag) => tag.tag_name === tagName)?.color || ''
}

onMounted(refreshAll)
</script>

<template>
  <section class="page-section">
    <div class="page-heading">
      <div>
        <h1>Papers</h1>
        <p>Manage structured metadata, authors, venues, tags, collections and files.</p>
      </div>
      <div class="heading-actions">
        <el-button :icon="Setting" @click="metadataOpen = true">Metadata</el-button>
        <el-button :icon="Refresh" @click="refreshAll">Refresh</el-button>
        <el-button type="primary" :icon="Plus" @click="dialogOpen = true">New Paper</el-button>
      </div>
    </div>

    <el-card class="tool-panel" shadow="never">
      <div class="filters">
        <el-input
          v-model="filters.keyword"
          :prefix-icon="Search"
          clearable
          placeholder="Search title"
          @keyup.enter="loadPapers"
        />
        <el-select v-model="filters.tag" clearable placeholder="Tag">
          <el-option v-for="tag in tags" :key="tag.tag_id" :label="tag.tag_name" :value="tag.tag_name" />
        </el-select>
        <el-input-number v-model="filters.year" :min="1900" :max="2100" placeholder="Year" />
        <el-select v-model="filters.reading_status" clearable placeholder="Status">
          <el-option label="Unread" value="unread" />
          <el-option label="Reading" value="reading" />
          <el-option label="Finished" value="finished" />
          <el-option label="Archived" value="archived" />
        </el-select>
        <el-button type="primary" :icon="Search" @click="loadPapers">Search</el-button>
      </div>
    </el-card>

    <el-table
      v-loading="loading"
      :data="papers"
      class="paper-table"
      row-key="paper_id"
      @row-dblclick="(row) => router.push(`/papers/${row.paper_id}`)"
    >
      <el-table-column label="Title" min-width="320">
        <template #default="{ row }">
          <div class="paper-title" @click="router.push(`/papers/${row.paper_id}`)">
            {{ row.title }}
          </div>
          <div class="paper-subline">
            {{ row.authors?.map((author) => author.author_name).join(', ') || 'No authors' }}
          </div>
        </template>
      </el-table-column>
      <el-table-column label="Year" prop="year" width="90" />
      <el-table-column label="Venue" min-width="140">
        <template #default="{ row }">
          {{ row.venue_ref?.venue_name || row.venue || '-' }}
        </template>
      </el-table-column>
      <el-table-column label="Tags" min-width="220">
        <template #default="{ row }">
          <div class="tag-list">
            <el-tag
              v-for="tag in row.tags"
              :key="tag.tag_id"
              :color="tag.color || tagColor(tag.tag_name)"
              effect="light"
              size="small"
            >
              {{ tag.tag_name }}
            </el-tag>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="Status" width="120">
        <template #default="{ row }">
          <el-tag effect="plain">{{ row.reading_status }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="Actions" width="170" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="router.push(`/papers/${row.paper_id}`)">Open</el-button>
          <el-button size="small" type="danger" plain @click="confirmDelete(row)">Delete</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogOpen" title="New Paper" width="760px">
      <PaperForm
        :authors="authors"
        :tags="tags"
        :venues="venues"
        :loading="saving"
        submit-text="Create"
        @cancel="dialogOpen = false"
        @submit="submitPaper"
      />
    </el-dialog>

    <el-dialog v-model="metadataOpen" title="Metadata Management" width="1080px">
      <div class="metadata-grid">
        <el-card shadow="never">
          <template #header>Tags</template>
          <div class="inline-form">
            <el-input v-model="metadataForm.tag_name" placeholder="Tag name" />
            <el-color-picker v-model="metadataForm.tag_color" />
            <el-button type="primary" @click="addTag">Add</el-button>
          </div>
          <el-table :data="tags" size="small" max-height="240" class="nested-table">
            <el-table-column label="Tag">
              <template #default="{ row }">
                <el-tag :color="row.color" effect="light">{{ row.tag_name }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="Actions" width="110">
              <template #default="{ row }">
                <el-button size="small" type="danger" plain @click="confirmDeleteTag(row)">
                  Delete
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>

        <el-card shadow="never">
          <template #header>Venues</template>
          <div class="inline-form">
            <el-input v-model="metadataForm.venue_name" placeholder="Venue name" />
            <el-select v-model="metadataForm.venue_type">
              <el-option label="Conference" value="conference" />
              <el-option label="Journal" value="journal" />
              <el-option label="Workshop" value="workshop" />
              <el-option label="Preprint" value="preprint" />
            </el-select>
            <el-button type="primary" @click="addVenue">Add</el-button>
          </div>
          <el-table :data="venues" size="small" max-height="220">
            <el-table-column prop="venue_name" label="Name" />
            <el-table-column prop="venue_type" label="Type" width="120" />
            <el-table-column label="Actions" width="110">
              <template #default="{ row }">
                <el-button size="small" type="danger" plain @click="confirmDeleteVenue(row)">
                  Delete
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>

        <el-card shadow="never" class="full-span">
          <template #header>Collection Directories</template>
          <div class="collection-create-row">
            <el-input v-model="metadataForm.collection_name" placeholder="New directory name" />
            <el-select v-model="metadataForm.collection_parent_id" clearable placeholder="Parent">
              <el-option
                v-for="collection in collectionParentOptions"
                :key="collection.collection_id ?? 'root'"
                :label="collection.collection_name"
                :value="collection.collection_id"
              />
            </el-select>
            <el-button type="primary" @click="addCollection">Create</el-button>
          </div>

          <div class="collection-manager">
            <div class="collection-list-panel">
              <div class="tree-toolbar">
                <el-button size="small" @click="prepareRootCollection">New Root</el-button>
                <el-button size="small" :disabled="!activeCollectionId" @click="prepareChildCollection">
                  New Child
                </el-button>
              </div>
              <el-tree
                ref="collectionTreeRef"
                :data="collectionTree"
                node-key="collection_id"
                default-expand-all
                highlight-current
                :current-node-key="activeCollectionId"
                empty-text="No collection directories"
                @node-click="selectCollection"
              >
                <template #default="{ data }">
                  <div class="collection-tree-node">
                    <span class="collection-node-label">
                      <el-icon><Folder /></el-icon>
                      <span>{{ data.collection_name }}</span>
                    </span>
                    <el-button
                      size="small"
                      type="danger"
                      link
                      @click.stop="confirmDeleteCollection(data)"
                    >
                      Delete
                    </el-button>
                  </div>
                </template>
              </el-tree>
              <div v-if="!collections.length" class="empty-text">No collections yet</div>
            </div>

            <div class="collection-detail-panel">
              <div class="collection-detail-heading">
                <div>
                  <h2>{{ activeCollection?.collection_name || 'No directory selected' }}</h2>
                  <p>
                    {{
                      activeCollection
                        ? 'Papers assigned to this directory'
                        : 'Select or create a directory to manage papers'
                    }}
                  </p>
                </div>
              </div>
              <div class="collection-add-paper">
                <el-select
                  v-model="selectedPaperId"
                  clearable
                  filterable
                  placeholder="Choose a paper to add"
                >
                  <el-option
                    v-for="paper in availablePapersForCollection"
                    :key="paper.paper_id"
                    :label="paper.title"
                    :value="paper.paper_id"
                  />
                </el-select>
                <el-button
                  type="primary"
                  :disabled="!activeCollectionId || !selectedPaperId"
                  @click="addSelectedPaperToCollection"
                >
                  Add Paper
                </el-button>
              </div>

              <el-table :data="collectionPapers" size="small" max-height="280" class="nested-table">
                <el-table-column label="Paper">
                  <template #default="{ row }">
                    <div class="paper-title" @click="router.push(`/papers/${row.paper_id}`)">
                      {{ row.title }}
                    </div>
                    <div class="paper-subline">
                      {{ row.authors?.map((author) => author.author_name).join(', ') || 'No authors' }}
                    </div>
                  </template>
                </el-table-column>
                <el-table-column prop="year" label="Year" width="80" />
                <el-table-column label="Actions" width="110">
                  <template #default="{ row }">
                    <el-button size="small" type="danger" plain @click="removeFromActiveCollection(row)">
                      Remove
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </div>
        </el-card>
      </div>
    </el-dialog>
  </section>
</template>
