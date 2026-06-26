---
marp: true
theme: default
paginate: true
size: 16:9
header: 'ResearchGraph'
footer: '2026 · 项目功能演示'
style: |
  :root {
    --ink: #1b1e26;
    --sub: #4a4f5a;
    --muted: #9a9085;
    --line: #e3ddd2;
    --accent: #a67c45;
    --accent-soft: #c9a874;
    --paper: #f4f1ea;
  }
  section {
    font-family: "Microsoft YaHei", "PingFang SC", "Helvetica Neue", sans-serif;
    font-size: 25px;
    font-weight: 400;
    letter-spacing: 0.2px;
    line-height: 1.7;
    color: var(--sub);
    padding: 60px 74px;
    background:
      radial-gradient(1200px 500px at 85% -10%, rgba(166,124,69,0.07), transparent 60%),
      linear-gradient(160deg, #f7f4ee 0%, var(--paper) 55%, #efe9df 100%);
  }
  /* hairline frame for a refined, editorial feel */
  section::before {
    content: "";
    position: absolute;
    top: 26px; left: 26px; right: 26px; bottom: 26px;
    border: 1px solid rgba(166,124,69,0.22);
    pointer-events: none;
  }
  h1 {
    font-size: 42px;
    font-weight: 700;
    color: var(--ink);
    letter-spacing: 1px;
    margin-bottom: 0.25em;
  }
  h2 {
    font-size: 31px;
    font-weight: 700;
    color: var(--ink);
    letter-spacing: 0.6px;
    padding-bottom: 16px;
    margin-bottom: 30px;
    border-bottom: 1px solid var(--line);
  }
  h2::before {
    content: "";
    display: inline-block;
    width: 26px;
    height: 3px;
    background: linear-gradient(90deg, var(--accent), var(--accent-soft));
    vertical-align: middle;
    margin-right: 16px;
    margin-bottom: 6px;
  }
  h3 { font-size: 24px; font-weight: 600; color: var(--accent); letter-spacing: 0.4px; }
  strong { font-weight: 700; color: var(--accent); }
  ul { line-height: 2.0; list-style: none; padding-left: 0; }
  ul li::before {
    content: "";
    display: inline-block;
    width: 6px; height: 6px;
    background: var(--accent);
    transform: rotate(45deg);
    margin-right: 16px;
    margin-bottom: 3px;
  }
  blockquote {
    border: none;
    border-left: 3px solid var(--accent);
    background: rgba(166,124,69,0.06);
    margin: 26px 0 0;
    padding: 12px 22px;
    color: var(--sub);
    font-style: normal;
    font-size: 21px;
  }
  code {
    font-family: "JetBrains Mono", "Consolas", monospace;
    background: rgba(166,124,69,0.10);
    color: var(--accent);
    padding: 1px 7px;
    border-radius: 3px;
    font-size: 0.86em;
  }
  pre { background: transparent; }
  table { font-size: 20px; border-collapse: collapse; }
  th {
    font-weight: 700;
    color: var(--ink);
    text-align: left;
    border-bottom: 2px solid var(--accent);
    padding: 9px 16px;
  }
  td { border-bottom: 1px solid var(--line); padding: 9px 16px; }
  img { border-radius: 3px; box-shadow: 0 14px 40px rgba(27,30,38,0.16); }
  header {
    font-size: 13px;
    letter-spacing: 4px;
    text-transform: uppercase;
    color: var(--muted);
    font-weight: 600;
  }
  footer { font-size: 12px; letter-spacing: 1.5px; color: var(--muted); }
  section::after {
    color: var(--accent);
    font-size: 14px;
    font-weight: 600;
  }
  /* ---------- lead / cover ---------- */
  section.lead {
    color: #efe9df;
    display: flex;
    flex-direction: column;
    justify-content: center;
    background:
      radial-gradient(900px 600px at 80% 20%, rgba(166,124,69,0.22), transparent 60%),
      linear-gradient(155deg, #232730 0%, #1b1e26 55%, #14161c 100%);
  }
  section.lead::before { border-color: rgba(201,168,116,0.30); }
  section.lead h1 {
    font-size: 72px;
    font-weight: 700;
    letter-spacing: 5px;
    color: #ffffff;
    border-left: 3px solid var(--accent-soft);
    padding-left: 30px;
    margin-bottom: 0.3em;
  }
  section.lead h2 {
    border: none;
    color: var(--accent-soft);
    font-weight: 400;
    letter-spacing: 1.5px;
    padding-left: 33px;
  }
  section.lead h2::before { display: none; }
  section.lead p { padding-left: 33px; color: #b9b2a5; font-weight: 300; }
  section.lead strong { color: var(--accent-soft); }
  section.lead code { color: var(--accent-soft); background: rgba(201,168,116,0.12); }
---

<!-- _class: lead -->

# ResearchGraph

## 面向科研阅读、文献管理与团队协作的知识图谱系统

围绕「论文 - 笔记 - 概念 - AI 分析 - 协作任务 - 知识图谱」
构建统一的数据闭环

---

## 1. 项目定位

传统文献工具侧重保存论文条目与引用，**ResearchGraph 关注科研阅读中持续产生的结构化信息**：

- 📄 **论文元数据**：标题、作者、会议/期刊、年份、标签、摘要、附件
- 📝 **阅读过程**：笔记、阅读状态、概念标记、反向链接、相关笔记
- 🗂️ **知识组织**：标签、目录、概念卡片、论文关系、主题聚类
- 🤖 **AI 辅助**：标签推荐、相似论文、关系补边、Related Work 聚类
- 👥 **团队协作**：科研项目、成员、阅读任务、负责人、评论
- 🕸️ **图谱呈现**：统一可交互的知识图谱

> 核心目标：把科研阅读活动转化为不断增长的研究知识库

---

## 2. 系统入口与工作台

![bg right:48% fit](demo/微信图片_20260626094555_577_3.png)

**用户登录入口**

- 登录后项目、任务、Dashboard 与图谱请求关联到当前用户身份
- 同时支持**个人文献管理**与**多用户协作**场景

---

## 2. Dashboard 科研工作台

![bg right:52% fit](demo/微信图片_20260626094555_578_3.png)

登录后进入 **Dashboard 总览**，集中观察文献库与协作状态：

- 论文 / 笔记 / 项目数量
- 待完成任务、最近新增论文
- 最近活动日志、高频标签
- 快捷入口

> 各模块数据回流到统一总览界面

---

## 3. 文献管理 · 论文录入

![bg right:50% fit](demo/微信图片_20260626094555_579_3.png)

**新建论文弹窗**录入结构化元数据，系统把作者、标签、来源拆分为独立实体。

覆盖核心字段：

- 标题、年份、阅读状态、论文类型
- 会议/期刊、DOI、arXiv ID、URL
- 作者、标签、摘要

---

## 3.1 论文录入填写示例

![bg right:52% fit](demo/微信图片_20260626094805_581_3.png)

结构化录入后系统可支持：

- 按标题、标签、年份、阅读状态**筛选论文**
- 自动纳入知识图谱中的**论文节点**

---

## 3.2 元数据与目录管理

![bg right:52% fit](demo/微信图片_20260626094943_582_3.png)

统一页面维护**可复用的元数据资源**：

- 新增标签、设置标签颜色
- 维护会议/期刊来源
- 创建文献目录

> 标签横向分类，目录层级归档，二者结合满足不同组织习惯

---

## 3.3 论文详情页

![bg right:50% fit](demo/微信图片_20260626095033_583_3.png)

汇总单篇论文完整信息，是论文与其他模块连接的中心：

- 基础元数据、标签、所属目录
- 关联阅读笔记
- 附件上传区域
- BibTeX 原始条目

---

## 4. BibTeX 导入

![bg right:50% fit](demo/微信图片_20260626094555_580_3.png)

降低手动录入成本：

- 粘贴 BibTeX 文本或上传 `.bib` 文件
- 解析为内部论文、作者、标签、来源与原始引用条目

> 适合从 **Zotero / Google Scholar / arXiv** 迁移已有文献，导入后继续参与详情、笔记、AI 分析与图谱构建

---

## 5. 阅读笔记与概念卡片

![bg right:50% fit](demo/微信图片_20260626095109_584_3.png)

不只保存论文，更**关注阅读过程本身**。

阅读笔记列表支持搜索与新建：

- 围绕论文记录总结、问题、公式、比较、分析
- 通过 wiki link 把关键概念提取为结构化概念节点

---

## 5.1 新建阅读笔记

![bg right:52% fit](demo/微信图片_20260626095152_585_3.png)

新建笔记时可指定：

- 标题、关联论文、笔记类型
- Markdown 内容

在正文中使用 `[[Concept Name]]` 语法即可标记概念。

> 笔记不再是孤立文本，而能被解析、索引并连接到概念知识网络

---

## 5.2 Markdown 编辑与双链解析

![bg right:52% fit](demo/微信图片_20260626095220_586_3.png)

编辑器支持**分屏 / 纯编辑 / 预览**三种模式。

保存后解析概念链接，右侧展示：

- 当前笔记涉及的概念
- 反向链接、相关笔记

> 多篇笔记同时提到 `Diffusion Models`、`Flow Matching` 时，自然形成相关笔记集合

---

## 5.3 概念卡片

![bg right:50% fit](demo/微信图片_20260626095259_587_3.png)

集中展示由笔记 wiki link 生成的概念：

- 名称、描述、关联笔记数量
- 支持搜索并进入详情页

---

## 5.3 概念详情页

![bg right:52% fit](demo/微信图片_20260626095322_588_3.png)

展示概念说明与引用该概念的阅读笔记列表。

> 相当于轻量知识卡片，把分散在笔记中的概念沉淀为**可复用的研究知识单元**

---

## 6. AI 科研分析

![bg right:48% fit](demo/微信图片_20260626095358_589_3.png)

从已有论文与笔记数据中提取辅助信息，当前支持：

- 🏷️ 自动标签推荐
- 🔍 相似论文推荐
- 🔗 知识图谱关系补边
- 📚 Related Work 主题聚类

---

## 6. AI 分析 · 四大能力

| 能力 | 说明 |
|------|------|
| **自动标签推荐** | 依据标题、摘要、内容生成标签建议，含置信度与原因；**仅建议**，用户采纳后才写入 |
| **相似论文推荐** | 依据标题、摘要、相关笔记计算语义相似度，发现 Related Work |
| **关系补边** | 生成 `same_topic` / `method_related` / `possible_baseline` / `improves` / `compares_with` 等关系 |
| **主题聚类** | 按研究主题自动分组，辅助综述与章节组织 |

> 保留人工确认环节，避免 AI 结果直接污染正式文献库

---

## 7. 科研项目与协作 · 项目详情

![bg right:50% fit](demo/微信图片_20260626095541_590_3.png)

把文献阅读从个人管理扩展到**团队协作**。

项目详情页展示：

- 项目基本信息
- 成员列表与角色（管理员 / 成员 / 查看者）
- 阅读任务列表
- 项目知识图谱入口

---

## 7.2 阅读任务

![bg right:52% fit](demo/微信图片_20260626095637_591_3.png)

把具体论文分配给项目成员，任务记录包括：

- 任务名称、论文 ID、任务描述
- 截止日期、负责人

> 形成「项目 → 论文 → 负责人 → 进度状态」的协作链路

---

## 7.3 任务列表与状态追踪

![bg right:52% fit](demo/微信图片_20260626095743_593_3.png)

集中展示当前用户或团队的阅读任务：

- 按状态筛选、修改状态
- 快速完成、评论、删除

---

## 7.3 协作回流 Dashboard

![bg right:52% fit](demo/微信图片_20260626095700_592_3.png)

协作动作会回流到 Dashboard：

- 创建任务后，**待完成任务数**同步更新
- **最近活动日志**同步刷新

> ResearchGraph 不只是文献仓库，也是团队阅读计划与协作过程的记录系统

---

## 8. 知识图谱可视化

![bg right:50% fit](demo/微信图片_20260626095928_594_3.png)

**核心展示层**：把论文、作者、会议/期刊、标签、笔记、概念、项目、用户、AI 聚类主题统一建模为节点；

把作者、发表、标签、笔记、概念、引用、语义相似、任务分配等关系建模为边。

---

## 8.1 多类型节点与关系

**节点类型**

`paper` `author` `venue` `tag` `note`
`concept` `project` `user` `cluster`

**边类型**

`authored_by` `published_in` `has_tag` `has_note`
`mentions_concept` `links_to` `cites` `same_topic`
`method_related` `improves` `compares_with`
`semantic_similar` `belongs_to` `assigned_to`

> 共同表达科研项目中的知识结构、阅读过程与协作关系

---

## 8.2 节点高亮与邻居探索

![bg right:52% fit](demo/微信图片_20260626100003_595_3.png)

点击节点后高亮该节点及其邻居，淡化无关节点。

> 适合查看一篇论文关联了哪些作者、标签、笔记、概念与相似论文

---

## 8.3 搜索与筛选

![bg right:52% fit](demo/微信图片_20260626100036_596_3.png)

支持关键词搜索、节点类型筛选、边类型筛选：

- 搜索 `Flow`、`Diffusion` 等关键词
- 只查看论文、概念、标签或特定关系类型

---

## 8.4 布局切换

![bg right:52% fit](demo/微信图片_20260626100333_597_3.png)

支持**力导向 / 同心圆 / 环形 / 层次**等布局。

结合节点类型筛选，可聚焦查看某类实体关系，例如只看论文之间的引用、语义相似与方法相关关系。

---

## 8.5 项目图谱

项目详情页提供「**查看项目知识图谱**」入口。

进入后按项目聚焦，只展示与该项目相关的：

- 📄 论文
- ✅ 阅读任务
- 👥 成员
- 🔗 知识关系

> 团队可从**项目视角**观察研究材料与阅读任务的组织情况

---

## 9. 系统闭环

<div style="display:flex; gap:34px; align-items:flex-start; margin-top:6px;">

<div style="flex:1.05; display:flex; flex-direction:column; gap:9px;">

<div style="display:flex; align-items:center; gap:16px; padding:11px 20px; border-radius:10px; background:linear-gradient(135deg,#ffffff 0%,#f4efe6 100%); box-shadow:0 6px 18px rgba(27,30,38,0.07); border:1px solid #e8e1d4;"><span style="display:inline-flex; align-items:center; justify-content:center; min-width:34px; height:34px; border-radius:50%; background:linear-gradient(135deg,#a67c45,#c9a874); color:#fff; font-weight:700; font-size:16px;">01</span><span style="font-size:21px; color:#1b1e26;">论文录入 / <strong>BibTeX 导入</strong></span></div>

<div style="text-align:center; color:#c9a874; font-size:18px; line-height:0.6;">⌄</div>

<div style="display:flex; align-items:center; gap:16px; padding:11px 20px; border-radius:10px; background:linear-gradient(135deg,#ffffff 0%,#f4efe6 100%); box-shadow:0 6px 18px rgba(27,30,38,0.07); border:1px solid #e8e1d4;"><span style="display:inline-flex; align-items:center; justify-content:center; min-width:34px; height:34px; border-radius:50%; background:linear-gradient(135deg,#a67c45,#c9a874); color:#fff; font-weight:700; font-size:16px;">02</span><span style="font-size:21px; color:#1b1e26;">论文详情与<strong>元数据管理</strong></span></div>

<div style="text-align:center; color:#c9a874; font-size:18px; line-height:0.6;">⌄</div>

<div style="display:flex; align-items:center; gap:16px; padding:11px 20px; border-radius:10px; background:linear-gradient(135deg,#ffffff 0%,#f4efe6 100%); box-shadow:0 6px 18px rgba(27,30,38,0.07); border:1px solid #e8e1d4;"><span style="display:inline-flex; align-items:center; justify-content:center; min-width:34px; height:34px; border-radius:50%; background:linear-gradient(135deg,#a67c45,#c9a874); color:#fff; font-weight:700; font-size:16px;">03</span><span style="font-size:21px; color:#1b1e26;">阅读笔记与<strong>概念解析</strong></span></div>

<div style="text-align:center; color:#c9a874; font-size:18px; line-height:0.6;">⌄</div>

<div style="display:flex; align-items:center; gap:16px; padding:11px 20px; border-radius:10px; background:linear-gradient(135deg,#ffffff 0%,#f4efe6 100%); box-shadow:0 6px 18px rgba(27,30,38,0.07); border:1px solid #e8e1d4;"><span style="display:inline-flex; align-items:center; justify-content:center; min-width:34px; height:34px; border-radius:50%; background:linear-gradient(135deg,#a67c45,#c9a874); color:#fff; font-weight:700; font-size:16px;">04</span><span style="font-size:21px; color:#1b1e26;"><strong>AI</strong> 标签 / 相似论文 / 关系补边 / 主题聚类</span></div>

</div>

<div style="flex:1; display:flex; flex-direction:column; gap:9px; padding-top:43px;">

<div style="display:flex; align-items:center; gap:16px; padding:11px 20px; border-radius:10px; background:linear-gradient(135deg,#ffffff 0%,#f4efe6 100%); box-shadow:0 6px 18px rgba(27,30,38,0.07); border:1px solid #e8e1d4;"><span style="display:inline-flex; align-items:center; justify-content:center; min-width:34px; height:34px; border-radius:50%; background:linear-gradient(135deg,#a67c45,#c9a874); color:#fff; font-weight:700; font-size:16px;">05</span><span style="font-size:21px; color:#1b1e26;">项目协作与<strong>阅读任务</strong></span></div>

<div style="text-align:center; color:#c9a874; font-size:18px; line-height:0.6;">⌄</div>

<div style="display:flex; align-items:center; gap:16px; padding:11px 20px; border-radius:10px; background:linear-gradient(135deg,#ffffff 0%,#f4efe6 100%); box-shadow:0 6px 18px rgba(27,30,38,0.07); border:1px solid #e8e1d4;"><span style="display:inline-flex; align-items:center; justify-content:center; min-width:34px; height:34px; border-radius:50%; background:linear-gradient(135deg,#a67c45,#c9a874); color:#fff; font-weight:700; font-size:16px;">06</span><span style="font-size:21px; color:#1b1e26;">知识图谱<strong>统一可视化</strong></span></div>

<div style="text-align:center; color:#c9a874; font-size:18px; line-height:0.6;">⌄</div>

<div style="display:flex; align-items:center; gap:16px; padding:11px 20px; border-radius:10px; background:linear-gradient(135deg,#1b1e26 0%,#2a2f3a 100%); box-shadow:0 8px 22px rgba(27,30,38,0.22); border:1px solid #3a3f4a;"><span style="display:inline-flex; align-items:center; justify-content:center; min-width:34px; height:34px; border-radius:50%; background:linear-gradient(135deg,#c9a874,#e0c89a); color:#1b1e26; font-weight:700; font-size:16px;">07</span><span style="font-size:21px; color:#f4efe6;"><strong style="color:#e0c89a;">Dashboard</strong> 汇总状态与活动</span></div>

<div style="margin-top:8px; display:flex; align-items:center; gap:12px; padding:10px 20px; border-radius:10px; border:1px dashed #c9a874; background:rgba(166,124,69,0.06);"><span style="font-size:22px; color:#a67c45;">↻</span><span style="font-size:18px; color:#7a6a52;">数据持续回流，闭环自增长</span></div>

</div>

</div>

> 随着论文、笔记、概念、任务与 AI 分析结果增加，逐步成长为面向研究团队的**知识组织平台**

---

## 10. 总结

ResearchGraph 已覆盖科研文献管理的多个关键场景：

- ✅ 文献录入与 BibTeX 导入，**降低入库成本**
- ✅ 元数据、标签、目录，**支持文献组织**
- ✅ 阅读笔记与概念卡片，**结构化阅读过程**
- ✅ AI 分析，**发现标签、相似论文、关系与聚类**
- ✅ 项目与任务，**支持团队阅读协作**
- ✅ 知识图谱，**统一呈现所有模块结果**

---

<!-- _class: lead -->

# 谢谢观看

## ResearchGraph

把科研阅读过程中的知识与协作信息，
持续沉淀为**可检索、可协作、可分析、可视化**的研究知识网络
