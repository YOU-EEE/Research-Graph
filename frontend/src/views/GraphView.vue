<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import cytoscape from 'cytoscape'
import { getGraph } from '../api/graph'
import { ElMessage } from 'element-plus'

const route = useRoute()
const cyContainer = ref(null)
const cyInstance = ref(null)
const nodeDetail = ref(null)
const loading = ref(false)
const searchQuery = ref('')

// 筛选条件
const nodeTypeFilter = ref('')
const edgeTypeFilter = ref('')

// 节点类型颜色映射
const nodeColors = {
  paper: '#409eff',
  author: '#67c23a',
  venue: '#e6a23c',
  tag: '#f56c6c',
  concept: '#909399',
  note: '#b37feb',
  project: '#ff6b6b',
  user: '#36cfc9',
}

// 节点类型形状映射
const nodeShapes = {
  paper: 'round-rectangle',
  author: 'ellipse',
  venue: 'diamond',
  tag: 'triangle',
  concept: 'hexagon',
  note: 'rectangle',
  project: 'star',
  user: 'ellipse',
}

const nodeTypeOptions = [
  { label: '全部类型', value: '' },
  { label: '论文', value: 'paper' },
  { label: '作者', value: 'author' },
  { label: '会议', value: 'venue' },
  { label: '标签', value: 'tag' },
  { label: '概念', value: 'concept' },
  { label: '笔记', value: 'note' },
  { label: '项目', value: 'project' },
]

const edgeTypeOptions = [
  { label: '全部类型', value: '' },
  { label: 'authored_by', value: 'authored_by' },
  { label: 'published_in', value: 'published_in' },
  { label: 'has_tag', value: 'has_tag' },
  { label: 'has_note', value: 'has_note' },
  { label: 'mentions_concept', value: 'mentions_concept' },
  { label: 'links_to', value: 'links_to' },
  { label: 'cites', value: 'cites' },
  { label: 'same_topic', value: 'same_topic' },
  { label: 'method_related', value: 'method_related' },
  { label: 'improves', value: 'improves' },
  { label: 'compares_with', value: 'compares_with' },
  { label: 'assigned_to', value: 'assigned_to' },
]

const layoutOptions = [
  { label: '力导向 (cose)', value: 'cose' },
  { label: '同心圆 (concentric)', value: 'concentric' },
  { label: '网格 (grid)', value: 'grid' },
  { label: '环形 (circle)', value: 'circle' },
  { label: '层次 (breadthfirst)', value: 'breadthfirst' },
]

const currentLayout = ref('cose')

async function loadGraph() {
  loading.value = true
  try {
    const params = {}
    const projectId = route.query.project_id
    if (projectId) params.project_id = projectId
    if (nodeTypeFilter.value) params.node_type = nodeTypeFilter.value
    if (edgeTypeFilter.value) params.edge_type = edgeTypeFilter.value

    const { data } = await getGraph(params)
    renderGraph(data)
  } catch (e) {
    ElMessage.error('加载图谱数据失败: ' + (e.userMessage || e.message))
  } finally {
    loading.value = false
  }
}

function renderGraph(data) {
  if (!cyContainer.value) return

  // 销毁旧实例
  if (cyInstance.value) {
    cyInstance.value.destroy()
  }

  const elements = []

  // 添加节点
  for (const node of data.nodes) {
    elements.push({
      data: {
        id: node.id,
        label: node.label.length > 30 ? node.label.slice(0, 30) + '…' : node.label,
        fullLabel: node.label,
        nodeType: node.type,
        ...node.data,
      },
      classes: node.type,
    })
  }

  // 添加边
  for (const edge of data.edges) {
    elements.push({
      data: {
        id: edge.id,
        source: edge.source,
        target: edge.target,
        label: edge.type,
        edgeType: edge.type,
        weight: edge.weight,
      },
      classes: edge.type,
    })
  }

  const cy = cytoscape({
    container: cyContainer.value,
    elements,
    style: getCytoscapeStyle(),
    layout: { name: currentLayout.value },
    minZoom: 0.1,
    maxZoom: 3,
    wheelSensitivity: 0.3,
  })

  // 点击节点查看详情
  cy.on('tap', 'node', (evt) => {
    const node = evt.target
    nodeDetail.value = {
      id: node.id(),
      label: node.data('fullLabel') || node.data('label'),
      type: node.data('nodeType'),
      data: { ...node.data() },
    }
  })

  cy.on('tap', (evt) => {
    if (evt.target === cy) {
      nodeDetail.value = null
    }
  })

  cyInstance.value = cy
}

function getCytoscapeStyle() {
  return [
    // 节点样式
    ...Object.entries(nodeColors).map(([type, color]) => ({
      selector: `node.${type}`,
      style: {
        'background-color': color,
        label: 'data(label)',
        'text-valign': 'bottom',
        'text-halign': 'center',
        'font-size': '10px',
        'text-wrap': 'wrap',
        'text-max-width': '120px',
        color: '#303133',
        'border-width': 2,
        'border-color': color,
      },
    })),
    // 边样式
    {
      selector: 'edge',
      style: {
        width: 1.5,
        'line-color': '#c0c4cc',
        'target-arrow-color': '#c0c4cc',
        'target-arrow-shape': 'triangle',
        'curve-style': 'bezier',
        label: 'data(label)',
        'font-size': '8px',
        color: '#909399',
        'text-rotation': 'autorotate',
      },
    },
    // 高亮邻居
    {
      selector: 'node.highlighted',
      style: {
        'border-width': 4,
        'border-color': '#ff6b6b',
        'border-opacity': 0.8,
      },
    },
    {
      selector: 'node.dimmed',
      style: {
        opacity: 0.3,
      },
    },
    {
      selector: 'edge.dimmed',
      style: {
        opacity: 0.1,
      },
    },
    {
      selector: 'edge.highlighted',
      style: {
        width: 3,
        'line-color': '#ff6b6b',
      },
    },
  ]
}

function handleSearch() {
  if (!cyInstance.value || !searchQuery.value.trim()) {
    // 清除高亮
    cyInstance.value?.elements().removeClass('dimmed highlighted')
    return
  }

  const cy = cyInstance.value
  const query = searchQuery.value.toLowerCase()

  // 重置
  cy.elements().removeClass('dimmed highlighted')

  // 找到匹配的节点
  const matches = cy.nodes().filter((n) => {
    const label = (n.data('fullLabel') || n.data('label') || '').toLowerCase()
    return label.includes(query)
  })

  if (matches.empty()) {
    ElMessage.info('未找到匹配节点')
    return
  }

  // 高亮匹配节点及其邻居
  const neighbors = matches.neighborhood()
  const toHighlight = matches.union(neighbors)

  cy.elements().addClass('dimmed')
  toHighlight.removeClass('dimmed')
  matches.addClass('highlighted')
  neighbors.edges().addClass('highlighted')
}

function applyLayout(layoutName) {
  currentLayout.value = layoutName
  if (cyInstance.value) {
    cyInstance.value.layout({ name: layoutName }).run()
  }
}

function refreshLayout() {
  if (cyInstance.value) {
    cyInstance.value.layout({ name: currentLayout.value }).run()
  }
}

function resetView() {
  if (cyInstance.value) {
    cyInstance.value.fit()
    cyInstance.value.center()
  }
}

watch([nodeTypeFilter, edgeTypeFilter], () => {
  loadGraph()
})

onMounted(() => {
  loadGraph()
})

onUnmounted(() => {
  if (cyInstance.value) {
    cyInstance.value.destroy()
  }
})
</script>

<template>
  <div class="graph-page">
    <!-- 工具栏 -->
    <div class="graph-toolbar">
      <div class="toolbar-left">
        <el-input
          v-model="searchQuery"
          placeholder="搜索节点..."
          clearable
          @keyup.enter="handleSearch"
          @clear="handleSearch"
          style="width: 220px"
        >
          <template #append>
            <el-button @click="handleSearch">搜索</el-button>
          </template>
        </el-input>
        <el-select v-model="nodeTypeFilter" placeholder="节点类型" style="width: 130px">
          <el-option v-for="opt in nodeTypeOptions" :key="opt.value" :label="opt.label" :value="opt.value" />
        </el-select>
        <el-select v-model="edgeTypeFilter" placeholder="边类型" style="width: 140px">
          <el-option v-for="opt in edgeTypeOptions" :key="opt.value" :label="opt.label" :value="opt.value" />
        </el-select>
      </div>
      <div class="toolbar-right">
        <el-select v-model="currentLayout" @change="applyLayout" style="width: 160px">
          <el-option v-for="opt in layoutOptions" :key="opt.value" :label="opt.label" :value="opt.value" />
        </el-select>
        <el-button @click="refreshLayout">刷新布局</el-button>
        <el-button @click="resetView">重置视图</el-button>
        <el-button @click="loadGraph" :loading="loading">刷新数据</el-button>
      </div>
    </div>

    <!-- 主区域 -->
    <div class="graph-main">
      <!-- Cytoscape 画布 -->
      <div class="cy-container" ref="cyContainer" v-loading="loading" />

      <!-- 节点详情面板 -->
      <div class="detail-panel" v-if="nodeDetail">
        <h3>节点详情</h3>
        <el-descriptions :column="1" size="small" border>
          <el-descriptions-item label="ID">{{ nodeDetail.id }}</el-descriptions-item>
          <el-descriptions-item label="名称">{{ nodeDetail.label }}</el-descriptions-item>
          <el-descriptions-item label="类型">
            <el-tag :color="nodeColors[nodeDetail.type]" effect="dark" size="small">
              {{ nodeDetail.type }}
            </el-tag>
          </el-descriptions-item>
          <template v-if="nodeDetail.data">
            <el-descriptions-item v-if="nodeDetail.data.year" label="年份">
              {{ nodeDetail.data.year }}
            </el-descriptions-item>
            <el-descriptions-item v-if="nodeDetail.data.venue" label="会议">
              {{ nodeDetail.data.venue }}
            </el-descriptions-item>
            <el-descriptions-item v-if="nodeDetail.data.affiliation" label="单位">
              {{ nodeDetail.data.affiliation }}
            </el-descriptions-item>
            <el-descriptions-item v-if="nodeDetail.data.note_type" label="笔记类型">
              {{ nodeDetail.data.note_type }}
            </el-descriptions-item>
            <el-descriptions-item v-if="nodeDetail.data.description" label="描述">
              {{ nodeDetail.data.description }}
            </el-descriptions-item>
            <el-descriptions-item v-if="nodeDetail.data.color" label="颜色">
              <el-color-picker :model-value="nodeDetail.data.color" disabled size="small" />
            </el-descriptions-item>
            <el-descriptions-item v-if="nodeDetail.data.venue_type" label="会议类型">
              {{ nodeDetail.data.venue_type }}
            </el-descriptions-item>
            <el-descriptions-item v-if="nodeDetail.data.reading_status" label="阅读状态">
              {{ nodeDetail.data.reading_status }}
            </el-descriptions-item>
          </template>
        </el-descriptions>
      </div>
    </div>

    <!-- 图例 -->
    <div class="graph-legend">
      <span v-for="(color, type) in nodeColors" :key="type" class="legend-item">
        <span class="legend-dot" :style="{ background: color }" />
        {{ type }}
      </span>
    </div>
  </div>
</template>

<style scoped>
.graph-page {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 120px);
}
.graph-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  padding: 12px 0;
  border-bottom: 1px solid #ebeef5;
}
.toolbar-left,
.toolbar-right {
  display: flex;
  gap: 8px;
  align-items: center;
  flex-wrap: wrap;
}
.graph-main {
  flex: 1;
  display: flex;
  gap: 0;
  position: relative;
  overflow: hidden;
}
.cy-container {
  flex: 1;
  min-height: 400px;
  background: #fafafa;
  border: 1px solid #ebeef5;
  border-radius: 4px;
}
.detail-panel {
  width: 300px;
  padding: 16px;
  background: #fff;
  border-left: 1px solid #ebeef5;
  overflow-y: auto;
  flex-shrink: 0;
}
.detail-panel h3 {
  margin: 0 0 12px;
  font-size: 16px;
  color: #303133;
}
.graph-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  padding: 8px 0;
  border-top: 1px solid #ebeef5;
}
.legend-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #606266;
}
.legend-dot {
  display: inline-block;
  width: 12px;
  height: 12px;
  border-radius: 50%;
}
</style>
