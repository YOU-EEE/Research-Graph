<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Connection, EditPen, Finished } from '@element-plus/icons-vue'
import { fetchConcept, fetchConceptNotes, updateConcept } from '../api/notes'

const route = useRoute()
const router = useRouter()
const conceptId = computed(() => Number(route.params.id))
const loading = ref(false)
const saving = ref(false)
const editing = ref(false)
const concept = ref(null)
const notes = ref([])
const form = ref({
  concept_name: '',
  description: '',
})

async function loadConcept() {
  loading.value = true
  try {
    const [conceptData, noteData] = await Promise.all([
      fetchConcept(conceptId.value),
      fetchConceptNotes(conceptId.value),
    ])
    concept.value = conceptData
    notes.value = noteData
    form.value = {
      concept_name: conceptData.concept_name,
      description: conceptData.description || '',
    }
  } catch (error) {
    ElMessage.error(error.userMessage)
  } finally {
    loading.value = false
  }
}

async function saveConcept() {
  saving.value = true
  try {
    concept.value = await updateConcept(conceptId.value, form.value)
    editing.value = false
    ElMessage.success('Concept saved')
  } catch (error) {
    ElMessage.error(error.userMessage)
  } finally {
    saving.value = false
  }
}

onMounted(loadConcept)
</script>

<template>
  <section v-loading="loading" class="page-section">
    <div class="detail-toolbar">
      <el-button :icon="ArrowLeft" @click="router.push('/concepts')">Back</el-button>
      <div class="detail-actions">
        <el-button v-if="!editing" :icon="EditPen" @click="editing = true">Edit</el-button>
        <el-button v-else type="primary" :icon="Finished" :loading="saving" @click="saveConcept">Save</el-button>
      </div>
    </div>

    <template v-if="concept">
      <div class="concept-detail">
        <section class="concept-hero">
          <div class="concept-mark">
            <el-icon><Connection /></el-icon>
          </div>
          <div class="concept-copy">
            <template v-if="editing">
              <el-input v-model="form.concept_name" size="large" />
              <el-input
                v-model="form.description"
                type="textarea"
                :rows="4"
                placeholder="Description"
                style="margin-top: 10px"
              />
            </template>
            <template v-else>
              <h1>{{ concept.concept_name }}</h1>
              <p>{{ concept.description || 'No description yet.' }}</p>
            </template>
            <el-tag effect="plain">{{ notes.length }} linked notes</el-tag>
          </div>
        </section>

        <el-card shadow="never">
          <template #header>Referenced Notes</template>
          <el-table :data="notes" row-key="note_id">
            <el-table-column label="Note" min-width="260">
              <template #default="{ row }">
                <div class="paper-title" @click="router.push(`/notes/${row.note_id}`)">
                  {{ row.title }}
                </div>
                <div class="paper-subline">{{ row.paper_title || 'No linked paper' }}</div>
              </template>
            </el-table-column>
            <el-table-column prop="note_type" label="Type" width="120" />
            <el-table-column prop="updated_at" label="Updated" width="190" />
          </el-table>
          <el-empty v-if="!notes.length" description="No notes reference this concept" />
        </el-card>
      </div>
    </template>
  </section>
</template>

<style scoped>
.concept-detail {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.concept-hero {
  display: grid;
  grid-template-columns: 72px minmax(0, 1fr);
  gap: 16px;
  align-items: start;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: #fff;
  padding: 22px;
}

.concept-mark {
  display: grid;
  width: 72px;
  height: 72px;
  place-items: center;
  border-radius: 8px;
  background: #eef2ff;
  color: #1d4ed8;
  font-size: 30px;
}

.concept-copy h1 {
  margin: 0;
  color: #111827;
  font-size: 30px;
  letter-spacing: 0;
}

.concept-copy p {
  margin: 8px 0 14px;
  color: #4b5563;
  font-size: 14px;
  line-height: 1.7;
}

@media (max-width: 720px) {
  .concept-hero {
    grid-template-columns: 1fr;
  }
}
</style>
