import { createRouter, createWebHashHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/overview',
  },
  {
    path: '/overview',
    name: 'Overview',
    component: () => import('@/views/Overview.vue'),
    meta: { title: '概览' },
  },
  {
    path: '/characters',
    name: 'CharacterManagement',
    component: () => import('@/views/CharacterManagement.vue'),
    meta: { title: '角色卡管理' },
  },
  {
    path: '/lorebook',
    name: 'LorebookManagement',
    component: () => import('@/views/LorebookManagement.vue'),
    meta: { title: '世界书管理' },
  },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

export default router
