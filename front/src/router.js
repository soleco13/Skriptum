import { createRouter, createWebHistory } from 'vue-router'
import Landing from './views/Landing.vue'

const routes = [
  {
    path: '/',
    name: 'Landing',
    component: Landing
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('./views/Login.vue')
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('./views/Register.vue')
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('./views/Dashboard.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/documents',
    name: 'Documents',
    component: () => import('./views/Documents.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/documents/:id/edit',
    name: 'DocumentEdit',
    component: () => import('./views/DocumentEdit.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/processes',
    name: 'Processes',
    component: () => import('./views/Processes.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/tasks',
    name: 'Tasks',
    component: () => import('./views/Tasks.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('./views/Profile.vue'),
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Защита маршрутов - проверка авторизации
router.beforeEach((to, from, next) => {
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  const isAuthenticated = !!localStorage.getItem('token') || !!sessionStorage.getItem('token')
  
  if (requiresAuth && !isAuthenticated) {
    // Если маршрут требует авторизации, а пользователь не авторизован,
    // перенаправляем на страницу входа
    next('/login')
  } else if (to.path === '/' && isAuthenticated) {
    // Если пользователь авторизован и пытается перейти на лендинг,
    // перенаправляем на дашборд
    next('/dashboard')
  } else {
    // В остальных случаях разрешаем переход
    next()
  }
})

export default router