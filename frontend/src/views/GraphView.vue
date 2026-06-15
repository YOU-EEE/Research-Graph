<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
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
const stats = ref({ nodes: 0, edges: 0 })
const showEdgeLabels = ref(false)

// ── 节点类型定义 (简化: 颜色 + 中英文 + 基础形状) ──
const typeMeta = {
  paper:    { color: '#5B8FF9', cn: '论文',   shape: 'round-rectangle' },
  author:   { color: '#5AD8A6', cn: '作者',   shape: 'ellipse' },
  venue:    { color: '#F6BD16', cn: '会议',   shape: 'diamond' },
  tag:      { color: '#E8684A', cn: '标签',   shape: 'triangle' },
  concept:  { color: '#9270CA', cn: '概念',   shape: 'hexagon' },
  note:     { color: '#6DC8EC', cn: '笔记',   shape: 'rectangle' },
  project:  { color: '#FF6B9D', cn: '项目',   shape: 'round-rectangle' },
  user:     { color: '#269A99', cn: '用户',   shape: 'ellipse' },
  cluster:  { color: '#FF9845', cn: '聚类',   shape: 'hexagon' },
}

// ── 节点大小(按重要程度) ──
const nodeSizes = {
  paper: 22, author: 16, venue: 16, tag: 14,
  concept: 16, note: 20, project: 22, user: 16, cluster: 26,
}

const edgeMeta = {
  authored_by:       { cn: '作者' },
  published_in:      { cn: '发表于' },
  has_tag:           { cn: '标签' },
  has_note:          { cn: '笔记' },
  mentions_concept:  { cn: '提及概念' },
  links_to:          { cn: '笔记链接' },
  cites:             { cn: '引用' },
  same_topic:        { cn: '同主题' },
  method_related:    { cn: '方法相关' },
  improves:          { cn: '改进' },
  compares_with:     { cn: '对比' },
  assigned_to:       { cn: '分配任务' },
  semantic_similar:  { cn: '语义相似' },
  belongs_to:        { cn: '归属聚类' },
}

// ── 筛选 ──
const nodeTypeFilter = ref('')
const edgeTypeFilter = ref('')
const currentLayout = ref('cose')

const nodeTypeOptions = [
  { label: '全部类型', value: '' },
  ...Object.entries(typeMeta).map(([k, v]) => ({ label: v.cn, value: k })),
]
const edgeTypeOptions = [
  { label: '全部类型', value: '' },
  ...Object.entries(edgeMeta).map(([k, v]) => ({ label: v.cn, value: k })),
]
const layoutOptions = [
  { label: '同心圆', value: 'cose' },
  { label: '力导向', value: 'concentric' },
  { label: '环形', value: 'circle' },
  { label: '层次', value: 'breadthfirst' },
]

// ── 缓存数据，切换 cose 时复用重建 ──
let lastGraphData = null

// ── 加载 ──
async function loadGraph() {
  loading.value = true
  nodeDetail.value = null
  try {
    const params = {}
    const pid = route.query.project_id
    if (pid) params.project_id = pid
    if (nodeTypeFilter.value) params.node_type = nodeTypeFilter.value
    if (edgeTypeFilter.value) params.edge_type = edgeTypeFilter.value

    const { data } = await getGraph(params)
    lastGraphData = data
    stats.value = { nodes: data.nodes.length, edges: data.edges.length }
    await nextTick()
    renderGraph(data)
  } catch (e) {
    ElMessage.error('加载失败: ' + (e.userMessage || e.message))
  } finally {
    loading.value = false
  }
}

function renderGraph(data) {
  if (!cyContainer.value) return
  if (cyInstance.value) cyInstance.value.destroy()

  const elements = []
  for (const n of data.nodes) {
    const label = n.label.length > 18 ? n.label.slice(0, 18) + '…' : n.label
    elements.push({
      data: { id: n.id, label, fullLabel: n.label, nodeType: n.type, ...n.data },
      classes: n.type,
    })
  }
  for (const e of data.edges) {
    const lbl = showEdgeLabels.value ? (edgeMeta[e.type]?.cn || '') : ''
    elements.push({
      data: {
        id: e.id, source: e.source, target: e.target,
        label: lbl, edgeType: e.type, weight: e.weight || 0.5,
      },
      classes: e.type,
    })
  }

  // ── 多阶段渐进布局（cose 模式）──
  // 观察：依次展示"同心圆→环形→层次→力导向"后力导向最美观。
  // 根因：concentric 按度分层但同环无关节点仍挤在一起；
  //       breadthfirst 按图拓扑遍历——有边连接的节点自然相邻，
  //       这是 cose 力导向最理想的起点。
  // 方案：concentric → circle → breadthfirst → cose（前 3 步无动画）。
  const PRE_LAYOUTS = currentLayout.value === 'cose'
    ? ['concentric', 'circle', 'breadthfirst']
    : []
  let cosePhaseIdx = 0

  const cy = cytoscape({
    container: cyContainer.value,
    elements,
    style: buildStyles(),
    layout: PRE_LAYOUTS.length > 0
      ? { name: PRE_LAYOUTS[0], fit: true, padding: 50, animate: false }
      : makeLayout(currentLayout.value),
    minZoom: 0.05,
    maxZoom: 4,
    wheelSensitivity: 0.3,
  })

  const onLayoutStop = () => {
    if (PRE_LAYOUTS.length === 0) {
      cy.fit(undefined, 40)
      return
    }
    cosePhaseIdx++
    if (cosePhaseIdx < PRE_LAYOUTS.length) {
      cy.layout({
        name: PRE_LAYOUTS[cosePhaseIdx],
        fit: true, padding: 50, animate: false,
      }).run()
    } else if (cosePhaseIdx === PRE_LAYOUTS.length) {
      cy.layout(makeLayout('cose')).run()
    } else {
      cy.fit(undefined, 40)
    }
  }
  cy.on('layoutstop', onLayoutStop)

  // --- 事件 ---
  cy.on('tap', 'node', (evt) => {
    const node = evt.target
    const ce = node.connectedEdges()
    const et = {}
    ce.forEach(e => { const t = e.data('edgeType'); et[t] = (et[t] || 0) + 1 })
    nodeDetail.value = {
      id: node.id(), label: node.data('fullLabel') || node.data('label'),
      type: node.data('nodeType'), degree: ce.length, edgeTypes: et,
      data: { ...node.data() },
    }
    // 聚焦到该节点
    cy.elements().removeClass('dimmed highlighted')
    cy.elements().addClass('dimmed')
    node.removeClass('dimmed').addClass('highlighted')
    node.neighborhood().removeClass('dimmed')
    node.connectedEdges().addClass('highlighted').forEach(e => {
      e.style({ label: edgeMeta[e.data('edgeType')]?.cn || '' })
    })
  })

  cy.on('tap', (evt) => {
    if (evt.target === cy) {
      nodeDetail.value = null
      cy.elements().removeClass('dimmed highlighted')
      cy.elements().edges().style('label', '')
    }
  })

  cyInstance.value = cy
}

function makeLayout(name) {
  const base = { name, animate: true, animationDuration: 800, fit: true, padding: 60 }
  if (name === 'cose') return {
    ...base,
    nodeRepulsion: () => 40000,
    idealEdgeLength: () => 180,
    edgeElasticity: () => 0.2,
    gravity: 8,
    numIter: 4000,
    initialTemp: 200,
    coolingFactor: 0.88,
    minTemp: 0.3,
  }
  return base
}

function buildStyles() {
  const s = []

  // 节点
  for (const [type, meta] of Object.entries(typeMeta)) {
    const sz = nodeSizes[type] || 26
    s.push({
      selector: `node.${type}`,
      style: {
        'background-color': meta.color,
        'background-opacity': 0.25,
        'border-color': meta.color,
        'border-width': 1.5,
        'border-opacity': 0.7,
        shape: meta.shape,
        width: sz,
        height: sz,
        label: 'data(label)',
        'text-valign': 'bottom',
        'text-halign': 'center',
        'font-size': '9px',
        'font-family': 'system-ui, sans-serif',
        'text-wrap': 'wrap',
        'text-max-width': '100px',
        'text-margin-y': 3,
        color: '#555',
        'overlay-opacity': 0,
      },
    })
  }

  // 边
  s.push({
    selector: 'edge',
    style: {
      width: 0.6,
      'line-color': '#d0d7de',
      'target-arrow-color': '#b0b8c0',
      'target-arrow-shape': 'triangle',
      'arrow-scale': 0.4,
      'curve-style': 'bezier',
      label: 'data(label)',
      'font-size': '7px',
      color: '#999',
      'text-background-color': '#fff',
      'text-background-opacity': 0.85,
      'text-background-padding': '1px',
      'text-background-shape': 'round-rectangle',
      'text-rotation': 'autorotate',
      'text-margin-y': -6,
      opacity: 0.25,
    },
  })

  // 语义相似边用虚线
  s.push({
    selector: 'edge.semantic_similar',
    style: { 'line-style': 'dashed', 'line-dash-pattern': [6, 4], 'line-color': '#b39ddb', 'target-arrow-color': '#b39ddb' },
  })

  // 高亮
  s.push({ selector: 'node.highlighted', style: { 'border-width': 5, 'border-color': '#f5222d', 'border-opacity': 1 } })
  s.push({ selector: 'node.dimmed', style: { opacity: 0.1 } })
  s.push({ selector: 'edge.dimmed', style: { opacity: 0.03 } })
  s.push({ selector: 'edge.highlighted', style: { width: 2.5, 'line-color': '#f5222d', 'target-arrow-color': '#f5222d', opacity: 1 } })

  return s
}

// ── 操作 ──
function handleSearch() {
  if (!cyInstance.value) return
  const cy = cyInstance.value
  cy.elements().removeClass('dimmed highlighted')
  cy.elements().edges().style('label', '')

  if (!searchQuery.value.trim()) return

  const query = searchQuery.value.toLowerCase()
  const matches = cy.nodes().filter(n =>
    (n.data('fullLabel') || n.data('label') || '').toLowerCase().includes(query)
  )
  if (matches.empty()) { ElMessage.info('未找到匹配节点'); return }

  const nh = matches.neighborhood()
  cy.elements().addClass('dimmed')
  matches.union(nh).removeClass('dimmed')
  matches.addClass('highlighted')
  nh.edges().addClass('highlighted').forEach(e => {
    e.style({ label: edgeMeta[e.data('edgeType')]?.cn || '' })
  })

  cy.animate({ center: { eles: matches }, zoom: Math.max(cy.zoom(), 0.7), duration: 400 })
}

function applyLayout(name) {
  currentLayout.value = name
  // 切到 cose：重建 cy 实例。节点归零 → 3 轮预布局 → cose。
  // 这样无论从同心圆/环形/层次切过来，起点一致，cose 结果也一致。
  if (name === 'cose' && lastGraphData) {
    nextTick(() => renderGraph(lastGraphData))
    return
  }
  if (cyInstance.value) cyInstance.value.layout(makeLayout(name)).run()
}

function refreshLayout() {
  if (!cyInstance.value) return
  if (currentLayout.value === 'cose' && lastGraphData) {
    nextTick(() => renderGraph(lastGraphData))
    return
  }
  cyInstance.value.layout(makeLayout(currentLayout.value)).run()
}

function resetView() {
  if (cyInstance.value) cyInstance.value.fit(undefined, 40)
}

function toggleEdgeLabels() {
  showEdgeLabels.value = !showEdgeLabels.value
  if (cyInstance.value) {
    const lbl = showEdgeLabels.value
    cyInstance.value.edges().forEach(e => {
      e.style('label', lbl ? (edgeMeta[e.data('edgeType')]?.cn || '') : '')
    })
  }
}

const typeCn = computed(() => {
  const m = {}
  for (const [k, v] of Object.entries(typeMeta)) m[k] = v.cn
  return m
})

watch([nodeTypeFilter, edgeTypeFilter], () => loadGraph())
onMounted(() => loadGraph())
onUnmounted(() => { if (cyInstance.value) cyInstance.value.destroy() })
</script>

<template>
  <div class="gp">
    <!-- top bar -->
    <div class="tb">
      <div class="tb-l">
        <span class="tb-title">知识图谱</span>
        <span class="tb-stat">{{ stats.nodes }} 节点</span>
        <span class="tb-stat">{{ stats.edges }} 边</span>
      </div>
      <div class="tb-r">
        <el-input v-model="searchQuery" placeholder="搜索…" clearable size="small"
          @keyup.enter="handleSearch" @clear="handleSearch" style="width:140px" />
        <el-select v-model="nodeTypeFilter" placeholder="节点" size="small" style="width:100px">
          <el-option v-for="o in nodeTypeOptions" :key="o.value" :label="o.label" :value="o.value" />
        </el-select>
        <el-select v-model="edgeTypeFilter" placeholder="边" size="small" style="width:110px">
          <el-option v-for="o in edgeTypeOptions" :key="o.value" :label="o.label" :value="o.value" />
        </el-select>
        <el-select v-model="currentLayout" @change="applyLayout" size="small" style="width:110px">
          <el-option v-for="o in layoutOptions" :key="o.value" :label="o.label" :value="o.value" />
        </el-select>
        <el-button size="small" @click="refreshLayout">重排</el-button>
        <el-button size="small" @click="resetView">居中</el-button>
        <el-button size="small" @click="toggleEdgeLabels" :type="showEdgeLabels ? 'primary' : 'default'" plain>
          边标签
        </el-button>
      </div>
    </div>

    <!-- canvas -->
    <div class="main">
      <div class="cy" ref="cyContainer" v-loading="loading" element-loading-text="加载中…" />

      <!-- detail -->
      <transition name="fade">
        <aside class="dp" v-if="nodeDetail" key="dp">
          <div class="dp-top">
            <span class="dp-dot" :style="{ background: typeMeta[nodeDetail.type]?.color || '#999' }"></span>
            <span class="dp-type">{{ typeCn[nodeDetail.type] || nodeDetail.type }}</span>
            <span class="dp-deg">{{ nodeDetail.degree }} 条边</span>
            <el-button text size="small" @click="nodeDetail = null" style="margin-left:auto">✕</el-button>
          </div>
          <div class="dp-bd">
            <div class="dp-name">{{ nodeDetail.label }}</div>

            <div class="dp-meta" v-if="nodeDetail.data">
              <div class="dm-r" v-if="nodeDetail.data.year"><span class="dm-k">年份</span><span class="dm-v">{{ nodeDetail.data.year }}</span></div>
              <div class="dm-r" v-if="nodeDetail.data.venue"><span class="dm-k">会议</span><span class="dm-v">{{ nodeDetail.data.venue }}</span></div>
              <div class="dm-r" v-if="nodeDetail.data.affiliation"><span class="dm-k">单位</span><span class="dm-v">{{ nodeDetail.data.affiliation }}</span></div>
              <div class="dm-r" v-if="nodeDetail.data.reading_status"><span class="dm-k">状态</span><span class="dm-v">{{ nodeDetail.data.reading_status }}</span></div>
              <div class="dm-r" v-if="nodeDetail.data.note_type"><span class="dm-k">笔记</span><span class="dm-v">{{ nodeDetail.data.note_type }}</span></div>
              <div class="dm-r" v-if="nodeDetail.data.num_papers"><span class="dm-k">论文数</span><span class="dm-v">{{ nodeDetail.data.num_papers }}</span></div>
              <div class="dm-r" v-if="nodeDetail.data.method"><span class="dm-k">方法</span><span class="dm-v">{{ nodeDetail.data.method }}</span></div>
              <div class="dm-blk" v-if="nodeDetail.data.description">
                <span class="dm-k">描述</span>
                <p class="dm-desc">{{ nodeDetail.data.description }}</p>
              </div>
            </div>

            <div v-if="nodeDetail.edgeTypes && Object.keys(nodeDetail.edgeTypes).length">
              <div class="dp-sub">关联关系</div>
              <div class="chip-wrap">
                <span v-for="(cnt, et) in nodeDetail.edgeTypes" :key="et" class="chip"
                  :style="{ borderColor: typeMeta[nodeDetail.type]?.color || '#999', color: typeMeta[nodeDetail.type]?.color || '#666' }">
                  {{ edgeMeta[et]?.cn || et }} ×{{ cnt }}
                </span>
              </div>
            </div>
          </div>
        </aside>
      </transition>
    </div>

    <!-- legend -->
    <div class="leg">
      <span v-for="(m, t) in typeMeta" :key="t" class="leg-it">
        <span class="leg-dot" :style="{ background: m.color }" />
        {{ m.cn }}
      </span>
    </div>
  </div>
</template>

<style scoped>
/* === layout === */
.gp { display:flex; flex-direction:column; height:calc(100vh - 110px); background:#fff; border-radius:6px; overflow:hidden; border:1px solid #e8ecf1; }

/* === top bar === */
.tb { display:flex; align-items:center; justify-content:space-between; gap:8px; padding:7px 12px; background:#fafbfc; border-bottom:1px solid #e8ecf1; flex-shrink:0; }
.tb-l { display:flex; align-items:center; gap:10px; }
.tb-title { font-size:14px; font-weight:600; color:#1a1a2e; }
.tb-stat { font-size:11px; color:#909399; }
.tb-r { display:flex; align-items:center; gap:5px; flex-wrap:wrap; }

/* === canvas === */
.main { flex:1; display:flex; min-height:0; }
.cy { flex:1; background:#f8f9fb; cursor:grab; }
.cy:active { cursor:grabbing; }

/* === detail panel === */
.dp { width:280px; background:#fff; border-left:1px solid #e8ecf1; display:flex; flex-direction:column; overflow-y:auto; flex-shrink:0; }
.dp-top { display:flex; align-items:center; gap:8px; padding:10px 12px; border-bottom:1px solid #f0f2f5; position:sticky; top:0; background:#fff; }
.dp-dot { width:10px; height:10px; border-radius:50%; flex-shrink:0; }
.dp-type { font-size:12px; font-weight:600; color:#606266; }
.dp-deg { font-size:11px; color:#909399; }
.dp-bd { padding:12px; display:flex; flex-direction:column; gap:10px; }
.dp-name { font-size:14px; font-weight:600; color:#1a1a2e; line-height:1.4; word-break:break-word; }
.dp-meta { display:flex; flex-direction:column; gap:1px; }
.dm-r { display:flex; align-items:center; gap:8px; padding:4px 0; border-bottom:1px solid #fafafa; }
.dm-k { font-size:11px; color:#909399; min-width:32px; flex-shrink:0; }
.dm-v { font-size:12px; color:#303133; }
.dm-blk { padding:4px 0; border-bottom:1px solid #fafafa; }
.dm-desc { margin:3px 0 0; font-size:12px; color:#606266; line-height:1.6; }
.dp-sub { font-size:10px; font-weight:600; color:#909399; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:2px; }
.chip-wrap { display:flex; flex-wrap:wrap; gap:4px; }
.chip { font-size:10px; padding:1px 6px; border:1px solid; border-radius:6px; }

/* === legend === */
.leg { display:flex; align-items:center; flex-wrap:wrap; gap:12px; padding:4px 12px; background:#fafbfc; border-top:1px solid #e8ecf1; flex-shrink:0; }
.leg-it { display:flex; align-items:center; gap:4px; font-size:11px; color:#606266; }
.leg-dot { width:10px; height:10px; border-radius:2px; flex-shrink:0; }

/* === transitions === */
.fade-enter-active, .fade-leave-active { transition: all 0.25s ease; }
.fade-enter-from, .fade-leave-to { transform: translateX(60px); opacity:0; }
</style>
