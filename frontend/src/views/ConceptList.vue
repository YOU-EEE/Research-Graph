<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Connection, Refresh, Search } from '@element-plus/icons-vue'
import { fetchConcepts } from '../api/notes'

const router = useRouter()
const loading = ref(false)
const concepts = ref([])
const filters = reactive({ keyword: '' })

async function loadConcepts() {
  loading.value = true
  try {
    concepts.value = await fetchConcepts({
      keyword: filters.keyword || undefined,
    })
  } catch (error) {
    ElMessage.error(error.userMessage)
  } finally {
    loading.value = false
  }
}

onMounted(loadConcepts)
</script>

<template>
  <section class="page-section">
    <div class="page-heading">
      <div>
        <h1>Concepts</h1>
        <p>Concept cards generated from note wiki links.</p>
      </div>
      <div class="heading-actions">
        <el-button :icon="Refresh" @click="loadConcepts">Refresh</el-button>
      </div>
    </div>

    <el-card class="tool-panel" shadow="never">
      <div class="concept-filters">
        <el-input
          v-model="filters.keyword"
          :prefix-icon="Search"
          clearable
          placeholder="Search concepts"
          @keyup.enter="loadConcepts"
        />
        <el-button type="primary" :icon="Search" @click="loadConcepts">Search</el-button>
      </div>
    </el-card>

    <div v-loading="loading" class="concept-grid">
      <article
        v-for="concept in concepts"
        :key="concept.concept_id"
        class="concept-card"
        @click="router.push(`/concepts/${concept.concept_id}`)"
      >
        <div class="concept-icon">
          <el-icon><Connection /></el-icon>
        </div>
        <div>
          <h2>{{ concept.concept_name }}</h2>
          <p>{{ concept.description || 'No description yet.' }}</p>
          <el-tag effect="plain">{{ concept.note_count }} notes</el-tag>
        </div>
      </article>
      <el-empty v-if="!concepts.length && !loading" description="No concepts yet" />
    </div>
  </section>
</template>

<style scoped>
.concept-filters {
  display: grid;
  grid-template-columns: minmax(260px, 1fr) auto;
  gap: 12px;
  align-items: center;
}

.concept-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 14px;
}

.concept-card {
  display: grid;
  cursor: pointer;
  grid-template-columns: 44px minmax(0, 1fr);
  gap: 12px;
  min-height: 140px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: #fff;
  padding: 16px;
  transition: border-color 0.18s ease, transform 0.18s ease, box-shadow 0.18s ease;
}

.concept-card:hover {
  border-color: var(--primary);
  box-shadow: 0 10px 24px rgba(37, 99, 235, 0.1);
  transform: translateY(-2px);
}

.concept-icon {
  display: grid;
  width: 44px;
  height: 44px;
  place-items: center;
  border-radius: 8px;
  background: #eef2ff;
  color: #1d4ed8;
  font-size: 20px;
}

.concept-card h2 {
  margin: 0;
  color: #111827;
  font-size: 17px;
  letter-spacing: 0;
}

.concept-card p {
  min-height: 42px;
  margin: 8px 0 12px;
  color: var(--muted);
  font-size: 13px;
  line-height: 1.5;
}

@media (max-width: 1024px) {
  .concept-filters {
    grid-template-columns: 1fr;
  }
}
</style>
