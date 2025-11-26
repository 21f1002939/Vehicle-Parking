<template>
  <div class="admin-users">
    <Navbar />
    
    <div class="content-container">
      <h1>👥 Users Management</h1>

      <div v-if="loading" class="loading">Loading users...</div>

      <div v-else>
        <div class="users-stats">
          <div class="stat-card">
            <h3>Total Users</h3>
            <p class="stat-number">{{ users.length }}</p>
          </div>
          <div class="stat-card">
            <h3>Active Users</h3>
            <p class="stat-number">{{ activeUsers }}</p>
          </div>
          <div class="stat-card">
            <h3>Total Reservations</h3>
            <p class="stat-number">{{ totalReservations }}</p>
          </div>
        </div>

        <div v-if="users.length > 0" class="users-table-container">
          <table class="users-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Username</th>
                <th>Email</th>
                <th>Phone</th>
                <th>Status</th>
                <th>Total Reservations</th>
                <th>Active Bookings</th>
                <th>Joined Date</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in users" :key="user.id">
                <td>{{ user.id }}</td>
                <td>{{ user.username }}</td>
                <td>{{ user.email }}</td>
                <td>{{ user.phone_number || 'N/A' }}</td>
                <td>
                  <span :class="['status-badge', user.is_active ? 'active' : 'inactive']">
                    {{ user.is_active ? 'Active' : 'Inactive' }}
                  </span>
                </td>
                <td>{{ user.total_reservations }}</td>
                <td>{{ user.active_reservations }}</td>
                <td>{{ formatDate(user.created_at) }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-else class="no-data">
          <p>No users registered yet</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../axios'
import Navbar from './Navbar.vue'

const loading = ref(true)
const users = ref([])

const activeUsers = computed(() => {
  return users.value.filter(u => u.is_active).length
})

const totalReservations = computed(() => {
  return users.value.reduce((sum, u) => sum + u.total_reservations, 0)
})

const loadUsers = async () => {
  try {
    const response = await api.get('/api/admin/users')

    if (response.data.status === 'success') {
      users.value = response.data.users
    }
  } catch (error) {
    console.error('Failed to load users:', error)
  } finally {
    loading.value = false
  }
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString()
}

onMounted(() => {
  loadUsers()
})
</script>

<style scoped>
.admin-users {
  min-height: 100vh;
  background: #f5f5f5;
}

.content-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

h1 {
  color: #333;
  margin-bottom: 30px;
}

.users-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: white;
  padding: 25px;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.stat-card h3 {
  margin: 0 0 15px 0;
  color: #666;
  font-size: 14px;
}

.stat-number {
  margin: 0;
  font-size: 36px;
  font-weight: bold;
  color: #667eea;
}

.users-table-container {
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  overflow-x: auto;
}

.users-table {
  width: 100%;
  border-collapse: collapse;
}

.users-table th,
.users-table td {
  padding: 15px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.users-table th {
  background: #f9f9f9;
  font-weight: 600;
  color: #333;
}

.users-table tbody tr:hover {
  background: #f9f9f9;
}

.status-badge {
  padding: 5px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.status-badge.active {
  background: #e8f5e9;
  color: #4CAF50;
}

.status-badge.inactive {
  background: #ffebee;
  color: #f44336;
}

.loading, .no-data {
  text-align: center;
  padding: 50px;
  color: #666;
}
</style>
