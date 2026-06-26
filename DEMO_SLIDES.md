---
marp: true
theme: default
paginate: true
size: 16:9
---

<style>
section {
  font-family: "Microsoft YaHei", "Segoe UI", Arial, sans-serif;
  color: #172033;
  background: #f6f8fb;
}
h1 {
  font-size: 44px;
  color: #111827;
}
h2 {
  font-size: 34px;
  color: #111827;
}
h3 {
  font-size: 24px;
  color: #1f2937;
}
p, li {
  font-size: 22px;
  line-height: 1.55;
}
strong {
  color: #2563eb;
}
code {
  color: #1d4ed8;
}
.subtitle {
  font-size: 26px;
  color: #4b5563;
}
.muted {
  color: #6b7280;
}
.columns {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 28px;
  align-items: center;
}
.columns-45 {
  display: grid;
  grid-template-columns: 0.9fr 1.1fr;
  gap: 28px;
  align-items: center;
}
.image-frame {
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 10px;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.08);
}
.image-frame img {
  width: 100%;
  max-height: 430px;
  object-fit: contain;
  display: block;
}
.full-image img {
  width: 100%;
  max-height: 560px;
  object-fit: contain;
  display: block;
}
.pill {
  display: inline-block;
  padding: 6px 12px;
  margin: 4px 6px 4px 0;
  border-radius: 999px;
  background: #e0ecff;
  color: #1d4ed8;
  font-size: 20px;
}
.compact li {
  font-size: 21px;
}
</style>

# ResearchGraph

<p class="subtitle">科研阅读、文献管理与团队协作的知识图谱系统</p>

<span class="pill">文献管理</span>
<span class="pill">阅读笔记</span>
<span class="pill">概念卡片</span>
<span class="pill">AI 分析</span>
<span class="pill">协作任务</span>
<span class="pill">知识图谱</span>

---

## 项目定位

ResearchGraph 不是只保存论文条目的工具，而是把科研阅读过程中的信息持续沉淀为结构化知识网络。

- 将论文、作者、标签、笔记、概念、项目和任务统一管理
- 用 AI 辅助发现标签、相似论文、关系和主题聚类
- 用知识图谱把科研资料、阅读过程和协作关系可视化连接起来

---

## 系统闭环

```text
论文录入 / BibTeX 导入
-> 论文详情与元数据管理
-> 阅读笔记与概念解析
-> AI 标签、相似论文、关系补边和主题聚类
-> 项目协作与阅读任务
-> 知识图谱统一可视化
-> Dashboard 汇总状态与活动
```

**核心价值：**把分散的科研阅读活动转化为可检索、可协作、可分析、可视化的研究知识网络。

---

## 系统入口与 Dashboard

<div class="columns">
  <div>
    <h3>用户入口</h3>
    <ul>
      <li>支持登录与注册</li>
      <li>用户身份关联项目、任务和图谱请求</li>
      <li>适用于个人与团队协作场景</li>
    </ul>
  </div>
  <div class="image-frame">
    <img src="demo/微信图片_20260626094555_577_3.png" alt="登录页" />
  </div>
</div>

---

## 科研工作台

<div class="columns-45">
  <div>
    <h3>Dashboard 汇总全局状态</h3>
    <ul>
      <li>论文、笔记、项目、任务统计</li>
      <li>最近新增论文和活动日志</li>
      <li>高频标签与快捷入口</li>
      <li>各模块动作都会回流到工作台</li>
    </ul>
  </div>
  <div class="image-frame">
    <img src="demo/微信图片_20260626094555_578_3.png" alt="Dashboard 总览" />
  </div>
</div>

---

## 文献管理：结构化论文录入

<div class="columns">
  <div class="image-frame">
    <img src="demo/微信图片_20260626094555_579_3.png" alt="新建论文弹窗" />
  </div>
  <div class="image-frame">
    <img src="demo/微信图片_20260626094805_581_3.png" alt="新建论文填写示例" />
  </div>
</div>

- 录入标题、年份、状态、类型、会议/期刊、作者、标签、摘要和链接
- 作者、标签、来源被拆分为独立实体，便于检索、统计和图谱构建

---

## 文献管理：元数据与论文详情

<div class="columns">
  <div class="image-frame">
    <img src="demo/微信图片_20260626094943_582_3.png" alt="元数据管理" />
  </div>
  <div class="image-frame">
    <img src="demo/微信图片_20260626095033_583_3.png" alt="论文详情页" />
  </div>
</div>

- 标签、会议/期刊、目录统一维护
- 论文详情集中展示元数据、标签、目录、阅读笔记、附件和 BibTeX

---

## BibTeX 导入

<div class="columns-45">
  <div>
    <h3>降低文献入库成本</h3>
    <ul>
      <li>支持粘贴 BibTeX 文本</li>
      <li>支持上传 <code>.bib</code> 文件</li>
      <li>自动解析论文、作者、来源、标签和原始引用条目</li>
      <li>导入后继续参与笔记、AI 分析和知识图谱构建</li>
    </ul>
  </div>
  <div class="image-frame">
    <img src="demo/微信图片_20260626094555_580_3.png" alt="BibTeX 导入" />
  </div>
</div>

---

## 阅读笔记：记录阅读过程

<div class="columns">
  <div class="image-frame">
    <img src="demo/微信图片_20260626095109_584_3.png" alt="新建阅读笔记入口" />
  </div>
  <div class="image-frame">
    <img src="demo/微信图片_20260626095152_585_3.png" alt="新建阅读笔记填写示例" />
  </div>
</div>

- 笔记可以关联论文，也可以独立存在
- 支持 Markdown 内容
- 使用 `[[Concept Name]]` 标记概念

---

## 笔记编辑与双链解析

<div class="columns-45">
  <div>
    <h3>从文本到知识连接</h3>
    <ul>
      <li>Split / Edit / Preview 三种视图</li>
      <li>解析 wiki link 生成概念节点</li>
      <li>右侧展示 Concepts、Backlinks 和 Related Notes</li>
      <li>发现不同笔记之间的主题联系</li>
    </ul>
  </div>
  <div class="image-frame">
    <img src="demo/微信图片_20260626095220_586_3.png" alt="笔记编辑器与概念解析" />
  </div>
</div>

---

## 概念卡片

<div class="columns">
  <div class="image-frame">
    <img src="demo/微信图片_20260626095259_587_3.png" alt="概念卡片列表" />
  </div>
  <div class="image-frame">
    <img src="demo/微信图片_20260626095322_588_3.png" alt="概念详情页" />
  </div>
</div>

- 概念由笔记中的 `[[...]]` 自动生成
- 每个概念沉淀为可复用知识单元
- 概念详情展示说明和引用它的笔记

---

## AI 科研分析

<div class="columns-45">
  <div>
    <h3>四类 AI 辅助能力</h3>
    <ul class="compact">
      <li><strong>自动标签推荐：</strong>给出标签、置信度和原因</li>
      <li><strong>相似论文推荐：</strong>辅助发现 Related Work</li>
      <li><strong>关系补边：</strong>生成论文关系建议</li>
      <li><strong>主题聚类：</strong>按研究主题组织文献库</li>
    </ul>
  </div>
  <div class="image-frame">
    <img src="demo/微信图片_20260626095358_589_3.png" alt="AI 分析总览" />
  </div>
</div>

---

## 协作项目

<div class="columns-45">
  <div>
    <h3>把论文阅读组织为团队工作流</h3>
    <ul>
      <li>项目基本信息与成员列表</li>
      <li>成员角色：Admin、Member、Viewer</li>
      <li>阅读任务列表</li>
      <li>项目知识图谱入口</li>
    </ul>
  </div>
  <div class="image-frame">
    <img src="demo/微信图片_20260626095541_590_3.png" alt="项目详情页" />
  </div>
</div>

---

## 阅读任务与状态追踪

<div class="columns">
  <div class="image-frame">
    <img src="demo/微信图片_20260626095637_591_3.png" alt="创建阅读任务" />
  </div>
  <div class="image-frame">
    <img src="demo/微信图片_20260626095743_593_3.png" alt="阅读任务列表" />
  </div>
</div>

- 阅读任务关联项目、论文、负责人、截止日期和状态
- 支持状态筛选、快速完成、评论和删除

---

## 协作数据回流

<div class="columns-45">
  <div>
    <h3>Dashboard 反映协作进展</h3>
    <ul>
      <li>创建项目后项目数更新</li>
      <li>创建任务后待完成任务数更新</li>
      <li>关键动作进入最近活动日志</li>
    </ul>
  </div>
  <div class="image-frame">
    <img src="demo/微信图片_20260626095700_592_3.png" alt="Dashboard 任务活动更新" />
  </div>
</div>

---

## 知识图谱总览

<div class="columns-45">
  <div>
    <h3>统一呈现所有模块结果</h3>
    <ul class="compact">
      <li>论文、作者、会议、标签</li>
      <li>笔记、概念、项目、用户</li>
      <li>AI 聚类主题</li>
      <li>引用、标签、语义相似、任务分配等关系</li>
    </ul>
  </div>
  <div class="image-frame">
    <img src="demo/微信图片_20260626095928_594_3.png" alt="知识图谱总览" />
  </div>
</div>

---

## 图谱交互：节点高亮

<div class="columns-45">
  <div>
    <h3>从一个节点探索关联知识</h3>
    <ul>
      <li>点击节点后高亮邻居关系</li>
      <li>无关节点淡化，降低视觉噪音</li>
      <li>适合查看论文的作者、标签、笔记、概念和相似论文</li>
    </ul>
  </div>
  <div class="image-frame">
    <img src="demo/微信图片_20260626100003_595_3.png" alt="图谱节点高亮" />
  </div>
</div>

---

## 图谱交互：搜索与筛选

<div class="columns">
  <div class="image-frame">
    <img src="demo/微信图片_20260626100036_596_3.png" alt="图谱搜索高亮" />
  </div>
  <div>
    <h3>快速定位研究主题</h3>
    <ul>
      <li>关键词搜索：例如 <code>Flow</code>、<code>Diffusion</code></li>
      <li>节点类型筛选：论文、概念、标签等</li>
      <li>边类型筛选：引用、方法相关、语义相似等</li>
      <li>匹配节点及其关系会被高亮</li>
    </ul>
  </div>
</div>

---

## 图谱交互：布局切换

<div class="columns-45">
  <div>
    <h3>按分析目标切换视角</h3>
    <ul>
      <li>力导向</li>
      <li>同心圆</li>
      <li>环形</li>
      <li>层次</li>
    </ul>
    <p>结合筛选后，可聚焦论文节点之间的引用、语义相似和方法相关关系。</p>
  </div>
  <div class="image-frame">
    <img src="demo/微信图片_20260626100333_597_3.png" alt="图谱布局切换与筛选" />
  </div>
</div>

---

## 功能覆盖总结

ResearchGraph 当前已经覆盖科研文献管理中的关键场景：

- 文献录入与 BibTeX 导入降低论文入库成本
- 标签、目录和元数据支持文献组织
- 阅读笔记和概念卡片把阅读过程结构化
- AI 分析发现标签、相似论文、关系和主题聚类
- 项目与任务模块支持团队阅读协作
- 知识图谱把所有模块结果统一呈现

---

## 结论

ResearchGraph 的价值不只是“保存论文”。

它把科研阅读过程中产生的知识和协作信息持续沉淀为：

<span class="pill">可检索</span>
<span class="pill">可协作</span>
<span class="pill">可分析</span>
<span class="pill">可视化</span>

的研究知识网络。
