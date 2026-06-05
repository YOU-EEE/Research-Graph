import { createRouter, createWebHistory } from 'vue-router'
import PaperList from '../views/PaperList.vue'
import PaperDetail from '../views/PaperDetail.vue'
import BibtexImport from '../views/BibtexImport.vue'

const routes = [
  { path: '/', redirect: '/papers' },
  { path: '/papers', name: 'papers', component: PaperList },
  { path: '/papers/:id', name: 'paper-detail', component: PaperDetail, props: true },
  { path: '/import/bibtex', name: 'bibtex-import', component: BibtexImport },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
