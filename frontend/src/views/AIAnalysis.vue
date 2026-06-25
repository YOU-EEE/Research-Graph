<script setup>
import { ref, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { MagicStick, Check, Refresh } from '@element-plus/icons-vue'
import { fetchPapers } from '../api/papers'
import {
  generateTagSuggestions,
  getTagSuggestions,
  acceptTagSuggestion,
  generateSimilarity,
  getSimilarity,
  generateRelationSuggestions,
  getRelationSuggestions,
  acceptRelationSuggestion,
  generateClusters,
  getClusters,
} from '../api/ai'

const papers = ref([])
const selectedPaperId = ref(null)
const mode = ref('local')
const topK = ref(5)
const numClusters = ref(3)

const tagSuggestions = ref([])
const similarPapers = ref([])
const relationSuggestions = ref([])
const clusters = ref([])

const loading = ref({ tags: false, similar: false, relations: false, clusters: false })

const selectedPaper = computed(() =>
  papers.value.find((p) => p.paper_id === selectedPaperId.value),
)

function pct(score) {
  if (score === null || score === undefined) return '-'
  return `${(score * 100).toFixed(1)}%`
}

const relationTypeColor = {
  same_topic: 'info',
  method_related: 'success',
  improves: 'warning',
  possible_baseline: 'primary',
  compares_with: 'danger',
}

async function loadPapers() {
  try {
    papers.value = await fetchPapers({ limit: 200 })
    if (papers.value.length && !selectedPaperId.value) {
      selectedPaperId.value = papers.value[0].paper_id
      onPaperChange()
    }
  } catch (e) {
    ElMessage.error(e.userMessage || '加载论文列表失败')
  }
}

async function onPaperChange() {
  if (!selectedPaperId.value) return
  // 切换论文后拉取已有的建议（不重新计算）
  try {
    const [tags, sims, rels] = await Promise.all([
      getTagSuggestions(selectedPaperId.value),
      getSimilarity(selectedPaperId.value),
      getRelationSuggestions(selectedPaperId.value),
    ])
    tagSuggestions.value = tags
    similarPapers.value = sims
    relationSuggestions.value = rels
  } catch (e) {
    /* 论文尚无建议时静默 */
  }
}

async function runTags() {
  if (!selectedPaperId.value) return ElMessage.warning('请先选择论文')
  loading.value.tags = true
  try {
    tagSuggestions.value = await generateTagSuggestions(selectedPaperId.value, mode.value)
    if (!tagSuggestions.value.length) ElMessage.info('未匹配到可推荐的标签')
  } catch (e) {
    ElMessage.error(e.userMessage || '标签推荐失败')
  } finally {
    loading.value.tags = false
  }
}

async function onAcceptTag(row) {
  try {
    await acceptTagSuggestion(row.suggestion_id)
    row.is_accepted = true
    ElMessage.success(`已采纳标签「${row.tag_name}」`)
  } catch (e) {
    ElMessage.error(e.userMessage || '采纳失败')
  }
}

async function runSimilarity() {
  if (!selectedPaperId.value) return ElMessage.warning('请先选择论文')
  loading.value.similar = true
  try {
    similarPapers.value = await generateSimilarity(
      selectedPaperId.value,
      mode.value,
      topK.value,
    )
    if (!similarPapers.value.length) ElMessage.info('未找到相似论文（语料过小或相似度过低）')
  } catch (e) {
    ElMessage.error(e.userMessage || '相似论文推荐失败')
  } finally {
    loading.value.similar = false
  }
}

async function runRelations() {
  if (!selectedPaperId.value) return ElMessage.warning('请先选择论文')
  loading.value.relations = true
  try {
    relationSuggestions.value = await generateRelationSuggestions(
      selectedPaperId.value,
      mode.value,
    )
    if (!relationSuggestions.value.length) ElMessage.info('未生成关系建议')
  } catch (e) {
    ElMessage.error(e.userMessage || '关系补边失败')
  } finally {
    loading.value.relations = false
  }
}

async function onAcceptRelation(row) {
  try {
    await acceptRelationSuggestion(row.suggestion_id)
    row.is_accepted = true
    ElMessage.success('关系已写入 paper_relations')
  } catch (e) {
    ElMessage.error(e.userMessage || '采纳失败')
  }
}

async function runClusters() {
  loading.value.clusters = true
  try {
    clusters.value = await generateClusters({
      project_id: null,
      num_clusters: numClusters.value,
      mode: mode.value,
    })
    if (!clusters.value.length) ElMessage.info('聚类结果为空')
  } catch (e) {
    ElMessage.error(e.userMessage || '主题聚类失败')
  } finally {
    loading.value.clusters = false
  }
}

onMounted(async () => {
  await loadPapers()
  try {
    clusters.value = await getClusters()
  } catch (e) {
    /* 尚无聚类时静默 */
  }
})
</script>

<template>
  <div class="ai-page">
    <div class="page-header">
      <h1>AI 科研分析</h1>
    </div>

    <!-- 控制栏 -->
    <el-card shadow="never" class="control-bar">
      <div class="control-row">
        <div class="control-item">
          <span class="label">目标论文</span>
          <el-select
            v-model="selectedPaperId"
            filterable
            placeholder="选择一篇论文"
            style="width: 360px"
            @change="onPaperChange"
          >
            <el-option
              v-for="p in papers"
              :key="p.paper_id"
              :label="`#${p.paper_id} ${p.title}`"
              :value="p.paper_id"
            />
          </el-select>
        </div>
        <div class="control-item">
          <span class="label">分析模式</span>
          <el-radio-group v-model="mode">
            <el-radio-button label="local">本地</el-radio-button>
            <el-radio-button label="cloud">云端</el-radio-button>
          </el-radio-group>
        </div>
      </div>
      <p v-if="selectedPaper" class="paper-hint">
        当前：<strong>{{ selectedPaper.title }}</strong>
        <span v-if="selectedPaper.year">（{{ selectedPaper.year }}）</span>
      </p>
    </el-card>

    <el-row :gutter="16">
      <!-- 1. 自动标签推荐 -->
      <el-col :span="12">
        <el-card class="ai-card">
          <template #header>
            <div class="card-header">
              <span>① 自动标签推荐</span>
              <el-button
                type="primary"
                size="small"
                :icon="MagicStick"
                :loading="loading.tags"
                @click="runTags"
              >
                生成
              </el-button>
            </div>
          </template>
          <el-table :data="tagSuggestions" size="small" empty-text="点击「生成」获取推荐">
            <el-table-column prop="tag_name" label="标签" min-width="120">
              <template #default="{ row }">
                <el-tag size="small" :type="row.is_accepted ? 'success' : 'info'">
                  {{ row.tag_name }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="置信度" width="90" align="center">
              <template #default="{ row }">{{ pct(row.confidence) }}</template>
            </el-table-column>
            <el-table-column prop="reason" label="推荐原因" min-width="180" show-overflow-tooltip />
            <el-table-column label="操作" width="90" align="center">
              <template #default="{ row }">
                <el-button
                  v-if="!row.is_accepted"
                  size="small"
                  type="success"
                  :icon="Check"
                  @click="onAcceptTag(row)"
                >
                  采纳
                </el-button>
                <el-tag v-else size="small" type="success">已采纳</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <!-- 2. 相似论文推荐 -->
      <el-col :span="12">
        <el-card class="ai-card">
          <template #header>
            <div class="card-header">
              <span>② 相似论文推荐</span>
              <div>
                <el-input-number
                  v-model="topK"
                  :min="1"
                  :max="20"
                  size="small"
                  controls-position="right"
                  style="width: 90px; margin-right: 8px"
                />
                <el-button
                  type="primary"
                  size="small"
                  :icon="MagicStick"
                  :loading="loading.similar"
                  @click="runSimilarity"
                >
                  计算
                </el-button>
              </div>
            </div>
          </template>
          <el-table :data="similarPapers" size="small" empty-text="点击「计算」获取相似论文">
            <el-table-column prop="title" label="论文" min-width="200" show-overflow-tooltip />
            <el-table-column prop="year" label="年份" width="70" align="center" />
            <el-table-column label="相似度" width="120" align="center">
              <template #default="{ row }">
                <el-progress
                  :percentage="Math.round(row.similarity_score * 100)"
                  :stroke-width="10"
                  :show-text="false"
                />
                <span class="sim-text">{{ pct(row.similarity_score) }}</span>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" style="margin-top: 16px">
      <!-- 3. 关系补边推荐 -->
      <el-col :span="12">
        <el-card class="ai-card">
          <template #header>
            <div class="card-header">
              <span>③ 知识图谱关系补边</span>
              <el-button
                type="primary"
                size="small"
                :icon="MagicStick"
                :loading="loading.relations"
                @click="runRelations"
              >
                生成
              </el-button>
            </div>
          </template>
          <el-table :data="relationSuggestions" size="small" empty-text="点击「生成」获取关系建议">
            <el-table-column prop="target_title" label="目标论文" min-width="160" show-overflow-tooltip />
            <el-table-column label="关系" width="130" align="center">
              <template #default="{ row }">
                <el-tag size="small" :type="relationTypeColor[row.relation_type] || 'info'">
                  {{ row.relation_type }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="置信度" width="80" align="center">
              <template #default="{ row }">{{ pct(row.confidence) }}</template>
            </el-table-column>
            <el-table-column label="操作" width="90" align="center">
              <template #default="{ row }">
                <el-button
                  v-if="!row.is_accepted"
                  size="small"
                  type="success"
                  :icon="Check"
                  @click="onAcceptRelation(row)"
                >
                  确认
                </el-button>
                <el-tag v-else size="small" type="success">已确认</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <!-- 4. Related Work 主题聚类 -->
      <el-col :span="12">
        <el-card class="ai-card">
          <template #header>
            <div class="card-header">
              <span>④ Related Work 主题聚类</span>
              <div>
                <el-input-number
                  v-model="numClusters"
                  :min="2"
                  :max="8"
                  size="small"
                  controls-position="right"
                  style="width: 90px; margin-right: 8px"
                />
                <el-button
                  type="primary"
                  size="small"
                  :icon="Refresh"
                  :loading="loading.clusters"
                  @click="runClusters"
                >
                  聚类
                </el-button>
              </div>
            </div>
          </template>
          <el-empty v-if="!clusters.length" description="点击「聚类」生成主题分组" :image-size="60" />
          <el-collapse v-else accordion>
            <el-collapse-item
              v-for="c in clusters"
              :key="c.cluster_id"
              :name="c.cluster_id"
            >
              <template #title>
                <span class="cluster-title">{{ c.label }}</span>
                <el-tag size="small" type="info" style="margin-left: 8px">
                  {{ c.num_papers }} 篇
                </el-tag>
              </template>
              <p class="cluster-desc">{{ c.description }}</p>
              <ul class="cluster-papers">
                <li v-for="p in c.papers" :key="p.paper_id">
                  {{ p.title }}
                  <span class="member-score">{{ pct(p.membership_score) }}</span>
                </li>
              </ul>
            </el-collapse-item>
          </el-collapse>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped>
.ai-page h1 {
  font-size: 24px;
  color: #303133;
}
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.control-bar {
  margin-bottom: 16px;
}
.control-row {
  display: flex;
  gap: 32px;
  flex-wrap: wrap;
  align-items: center;
}
.control-item {
  display: flex;
  align-items: center;
  gap: 10px;
}
.control-item .label {
  color: #606266;
  font-size: 13px;
}
.paper-hint {
  margin: 12px 0 0;
  color: #909399;
  font-size: 13px;
}
.ai-card {
  margin-bottom: 16px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}
.sim-text {
  font-size: 11px;
  color: #909399;
}
.cluster-title {
  font-weight: 600;
  color: #303133;
}
.cluster-desc {
  color: #606266;
  font-size: 13px;
  margin: 4px 0 8px;
}
.cluster-papers {
  margin: 0;
  padding-left: 18px;
}
.cluster-papers li {
  font-size: 13px;
  color: #303133;
  margin-bottom: 4px;
}
.member-score {
  color: #909399;
  font-size: 11px;
  margin-left: 6px;
}
</style>
