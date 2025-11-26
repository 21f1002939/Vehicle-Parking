<template>
  <nav class="navbar">
    <div class="nav-container">
      <div class="nav-brand">
        🚗 Parking App
      </div>

      <div class="nav-links">
        <template v-if="user">
          <!-- Admin Navigation -->
          <template v-if="user.role === 'admin'">
            <router-link to="/admin/dashboard" class="nav-link">Dashboard</router-link>
            <router-link to="/admin/parking-lots" class="nav-link">Parking Lots</router-link>
            <router-link to="/admin/users" class="nav-link">Users</router-link>
            <router-link to="/admin/charts" class="nav-link">Analytics</router-link>
          </template>

          <!-- User Navigation -->
          <template v-else>
            <router-link to="/user/dashboard" class="nav-link">Dashboard</router-link>
            <router-link to="/user/book" class="nav-link">Book Parking</router-link>
            <router-link to="/user/history" class="nav-link">History</router-link>
          </template>

          <div class="user-menu">
            <span class="username">{{ user.username }}</span>
            <button @click="handleLogout" class="logout-btn">Logout</button>
          </div>
        </template>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../axios'

const router = useRouter()
const user = ref(null)

onMounted(() => {
  const userData = localStorage.getItem('user')
  if (userData) {
    user.value = JSON.parse(userData)
  }
})

const handleLogout = async () => {
  try {
    await api.post('/api/auth/logout')
    
    localStorage.removeItem('user')
    router.push('/login')
  } catch (error) {
    console.error('Logout error:', error)
    localStorage.removeItem('user')
    router.push('/login')
  }
}
</script>

<style scoped>
.navbar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 1000;
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 15px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.nav-brand {
  font-size: 24px;
  font-weight: bold;
  color: white;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 20px;
}

.nav-link {
  color: white;
  text-decoration: none;
  padding: 8px 16px;
  border-radius: 5px;
  transition: background 0.3s;
}

.nav-link:hover {
  background: rgba(255, 255, 255, 0.2);
}

.nav-link.router-link-active {
  background: rgba(255, 255, 255, 0.3);
  font-weight: 600;
}

.user-menu {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-left: 20px;
  padding-left: 20px;
  border-left: 1px solid rgba(255, 255, 255, 0.3);
}

.username {
  color: white;
  font-weight: 500;
}

.logout-btn {
  padding: 8px 16px;
  background: white;
  color: #667eea;
  border: none;
  border-radius: 5px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s;
}

.logout-btn:hover {
  transform: translateY(-2px);
}
</style>
