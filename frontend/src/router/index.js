import { createRouter, createWebHistory } from 'vue-router'

// Auth Pages
import LoginPage from '../components/LoginPage.vue'
import RegisterPage from '../components/RegisterPage.vue'

// Admin Pages
import AdminDashboard from '../components/AdminDashboard.vue'
import AdminParkingLots from '../components/AdminParkingLots.vue'
import AdminParkingLotDetails from '../components/AdminParkingLotDetails.vue'
import AdminUsers from '../components/AdminUsers.vue'
import AdminCharts from '../components/AdminCharts.vue'

// User Pages
import UserDashboard from '../components/UserDashboard.vue'
import UserBooking from '../components/UserBooking.vue'
import UserHistory from '../components/UserHistory.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/login'
    },
    {
      path: '/login',
      name: 'Login',
      component: LoginPage
    },
    {
      path: '/register',
      name: 'Register',
      component: RegisterPage
    },
    // Admin Routes
    {
      path: '/admin/dashboard',
      name: 'AdminDashboard',
      component: AdminDashboard,
      meta: { requiresAuth: true, role: 'admin' }
    },
    {
      path: '/admin/parking-lots',
      name: 'AdminParkingLots',
      component: AdminParkingLots,
      meta: { requiresAuth: true, role: 'admin' }
    },
    {
      path: '/admin/parking-lots/:id',
      name: 'AdminParkingLotDetails',
      component: AdminParkingLotDetails,
      meta: { requiresAuth: true, role: 'admin' }
    },
    {
      path: '/admin/users',
      name: 'AdminUsers',
      component: AdminUsers,
      meta: { requiresAuth: true, role: 'admin' }
    },
    {
      path: '/admin/charts',
      name: 'AdminCharts',
      component: AdminCharts,
      meta: { requiresAuth: true, role: 'admin' }
    },
    // User Routes
    {
      path: '/user/dashboard',
      name: 'UserDashboard',
      component: UserDashboard,
      meta: { requiresAuth: true, role: 'user' }
    },
    {
      path: '/user/book',
      name: 'UserBooking',
      component: UserBooking,
      meta: { requiresAuth: true, role: 'user' }
    },
    {
      path: '/user/history',
      name: 'UserHistory',
      component: UserHistory,
      meta: { requiresAuth: true, role: 'user' }
    }
  ]
})

// Navigation guard for authentication
router.beforeEach((to, from, next) => {
  const userStr = localStorage.getItem('user')
  const user = userStr ? JSON.parse(userStr) : null
  
  if (to.meta.requiresAuth) {
    if (!user) {
      next('/login')
    } else if (to.meta.role && to.meta.role !== user.role) {
      // Redirect to appropriate dashboard if role mismatch
      if (user.role === 'admin') {
        next('/admin/dashboard')
      } else {
        next('/user/dashboard')
      }
    } else {
      next()
    }
  } else {
    // If already logged in and trying to access login/register, redirect to dashboard
    if ((to.path === '/login' || to.path === '/register') && user) {
      if (user.role === 'admin') {
        next('/admin/dashboard')
      } else {
        next('/user/dashboard')
      }
    } else {
      next()
    }
  }
})

export default router
