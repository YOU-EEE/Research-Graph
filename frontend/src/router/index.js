import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Dashboard from '../views/Dashboard.vue'
import PaperList from '../views/PaperList.vue'
import PaperDetail from '../views/PaperDetail.vue'
import BibtexImport from '../views/BibtexImport.vue'
import ProjectList from '../views/ProjectList.vue'
import ProjectDashboard from '../views/ProjectDashboard.vue'
import TaskList from '../views/TaskList.vue'
import GraphView from '../views/GraphView.vue'
import NoteList from '../views/NoteList.vue'
import NoteEditor from '../views/NoteEditor.vue'
import ConceptList from '../views/ConceptList.vue'
import ConceptDetail from '../views/ConceptDetail.vue'

const routes = [
  { path: '/login', name: 'login', component: Login, meta: { noAuth: true } },
  { path: '/dashboard', name: 'dashboard', component: Dashboard },
  { path: '/papers', name: 'papers', component: PaperList },
  { path: '/papers/:id', name: 'paper-detail', component: PaperDetail, props: true },
  { path: '/import/bibtex', name: 'bibtex-import', component: BibtexImport },
  { path: '/projects', name: 'projects', component: ProjectList },
  { path: '/projects/:id', name: 'project-dashboard', component: ProjectDashboard },
  { path: '/tasks', name: 'tasks', component: TaskList },
  { path: '/graph', name: 'graph', component: GraphView },
  { path: '/notes', name: 'notes', component: NoteList },
  { path: '/notes/:id', name: 'note-editor', component: NoteEditor, props: true },
  { path: '/concepts', name: 'concepts', component: ConceptList },
  { path: '/concepts/:id', name: 'concept-detail', component: ConceptDetail, props: true },
  { path: '/', redirect: '/dashboard' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由守卫：未登录时跳转登录页
router.beforeEach((to, from, next) => {
  const user = localStorage.getItem('user')
  if (!to.meta.noAuth && !user) {
    next('/login')
  } else if (to.path === '/login' && user) {
    next('/dashboard')
  } else {
    next()
  }
})

export default router
