<script setup>
import { Document, FolderOpened, UploadFilled } from '@element-plus/icons-vue'
</script>

<template>
  <el-container class="app-shell">
    <el-aside class="sidebar" width="232px">
      <div class="brand">
        <div class="brand-mark">RG</div>
        <div>
          <div class="brand-title">ResearchGraph</div>
          <div class="brand-subtitle">Literature Core</div>
        </div>
      </div>

      <el-menu router :default-active="$route.path" class="nav-menu">
        <el-menu-item index="/papers">
          <el-icon><Document /></el-icon>
          <span>Papers</span>
        </el-menu-item>
        <el-menu-item index="/import/bibtex">
          <el-icon><UploadFilled /></el-icon>
          <span>BibTeX Import</span>
        </el-menu-item>
        <el-menu-item index="/papers">
          <el-icon><FolderOpened /></el-icon>
          <span>Collections</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="topbar">
        <div>
          <div class="topbar-title">Zotero-like 文献管理</div>
          <div class="topbar-subtitle">Papers, authors, venues, tags, attachments and BibTeX</div>
        </div>
        <el-tag effect="plain">FastAPI / SQLite</el-tag>
      </el-header>

      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>
