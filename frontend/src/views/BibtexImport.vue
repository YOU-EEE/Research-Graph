<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { DocumentAdd, UploadFilled } from '@element-plus/icons-vue'
import { importBibtex, importBibtexFile } from '../api/papers'

const router = useRouter()
const rawBibtex = ref(`@article{demo2026,
  title={ResearchGraph Literature Management Demo},
  author={Alice Chen and Bob Li},
  year={2026},
  journal={arXiv},
  abstract={A local paper management demo entry.},
  keywords={Database, Literature Management}
}`)
const loading = ref(false)
const result = ref(null)

async function submitText() {
  if (!rawBibtex.value.trim()) {
    ElMessage.warning('BibTeX content is required')
    return
  }
  loading.value = true
  try {
    result.value = await importBibtex(rawBibtex.value)
    ElMessage.success(`Imported ${result.value.imported_count} paper(s)`)
  } catch (error) {
    ElMessage.error(error.userMessage)
  } finally {
    loading.value = false
  }
}

async function submitFile(options) {
  loading.value = true
  try {
    result.value = await importBibtexFile(options.file)
    ElMessage.success(`Imported ${result.value.imported_count} paper(s)`)
  } catch (error) {
    ElMessage.error(error.userMessage)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <section class="page-section">
    <div class="page-heading">
      <div>
        <h1>BibTeX Import</h1>
        <p>Parse BibTeX into papers, venues, authors, tags and raw BibTeX entries in one backend transaction.</p>
      </div>
    </div>

    <div class="import-layout">
      <el-card shadow="never">
        <template #header>Paste BibTeX</template>
        <el-input v-model="rawBibtex" type="textarea" :rows="18" spellcheck="false" />
        <div class="form-actions">
          <el-button type="primary" :icon="DocumentAdd" :loading="loading" @click="submitText">
            Import Text
          </el-button>
        </div>
      </el-card>

      <el-card shadow="never">
        <template #header>Upload .bib File</template>
        <el-upload drag :http-request="submitFile" :show-file-list="false" accept=".bib,.txt">
          <el-icon class="upload-icon"><UploadFilled /></el-icon>
          <div class="el-upload__text">Drop a BibTeX file here or click to upload</div>
        </el-upload>

        <div v-if="result" class="import-result">
          <h2>Import Result</h2>
          <p>{{ result.imported_count }} paper(s) imported.</p>
          <div class="collection-row">
            <el-button
              v-for="paperId in result.paper_ids"
              :key="paperId"
              type="primary"
              plain
              @click="router.push(`/papers/${paperId}`)"
            >
              Open Paper #{{ paperId }}
            </el-button>
          </div>
        </div>
      </el-card>
    </div>
  </section>
</template>
