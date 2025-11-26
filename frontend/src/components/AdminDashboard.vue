<template>
  <div class="admin-dashboard">
    <Navbar />
    
    <div class="dashboard-container">
      <h1>👤 Admin Dashboard</h1>
      
      <div v-if="loading" class="loading">Loading dashboard...</div>
      
      <div v-else>
        <!-- Statistics Cards -->
        <div class="stats-grid">
          <div class="stat-card parking-lots">
            <div class="stat-icon">🏢</div>
            <div class="stat-content">
              <h3>Parking Lots</h3>
              <p class="stat-number">{{ dashboardData.parking_lots?.total || 0 }}</p>
            </div>
          </div>

          <div class="stat-card parking-spots">
            <div class="stat-icon">🅿️</div>
            <div class="stat-content">
              <h3>Total Spots</h3>
              <p class="stat-number">{{ dashboardData.parking_spots?.total || 0 }}</p>
              <small>Available: {{ dashboardData.parking_spots?.available || 0 }} | 
                     Occupied: {{ dashboardData.parking_spots?.occupied || 0 }}</small>
            </div>
          </div>

          <div class="stat-card users">
            <div class="stat-icon">👥</div>
            <div class="stat-content">
              <h3>Total Users</h3>
              <p class="stat-number">{{ dashboardData.users?.total || 0 }}</p>
            </div>
          </div>

          <div class="stat-card reservations">
            <div class="stat-icon">📊</div>
            <div class="stat-content">
              <h3>Reservations</h3>
              <p class="stat-number">{{ dashboardData.reservations?.total || 0 }}</p>
              <small>Active: {{ dashboardData.reservations?.active || 0 }} | 
                     Completed: {{ dashboardData.reservations?.completed || 0 }}</small>
            </div>
          </div>
        </div>

        <!-- Quick Actions -->
        <div class="quick-actions">
          <h2>Quick Actions</h2>
          <div class="actions-grid">
            <button class="action-btn" @click="$router.push('/admin/parking-lots')">
              <span class="icon">🏢</span>
              Manage Parking Lots
            </button>
            <button class="action-btn" @click="$router.push('/admin/users')">
              <span class="icon">👥</span>
              Manage Users
            </button>
            <button class="action-btn" @click="$router.push('/admin/charts')">
              <span class="icon">📈</span>
              View Analytics
            </button>
          </div>
        </div>

        <!-- Recent Activity -->
        <div class="recent-activity">
          <h2>Recent Activity</h2>
          <div v-if="dashboardData.recent_activity && dashboardData.recent_activity.length > 0" class="activity-list">
            <div
              v-for="activity in dashboardData.recent_activity"
              :key="activity.id"
              class="activity-item"
            >
              <div class="activity-info">
                <strong>{{ activity.user }}</strong> - {{ activity.parking_lot }}
                <br />
                <small>Spot: {{ activity.spot }} | Status: 
                  <span :class="'status-' + activity.status">{{ activity.status }}</span>
                </small>
              </div>
              <div class="activity-meta">
                <small>{{ formatDate(activity.parking_time) }}</small>
                <div v-if="activity.cost" class="cost">₹{{ activity.cost }}</div>
              </div>
            </div>
          </div>
          <div v-else class="no-data">No recent activity</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../axios'
import Navbar from './Navbar.vue'

const loading = ref(true)
const dashboardData = ref({})

const loadDashboard = async () => {
  try {
    const response = await api.get('/api/admin/dashboard')

    if (response.data.status === 'success') {
      dashboardData.value = response.data.dashboard
    }
  } catch (error) {
    console.error('Failed to load dashboard:', error)
  } finally {
    loading.value = false
  }
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleString()
}

onMounted(() => {
  loadDashboard()
})
</script>

<style scoped>
.admin-dashboard {
  min-height: 100vh;
  background: #f5f5f5;
}

.dashboard-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

h1 {
  color: #333;
  margin-bottom: 30px;
}

.loading {
  text-align: center;
  padding: 50px;
  font-size: 18px;
  color: #666;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: white;
  padding: 25px;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 15px;
}

.stat-icon {
  font-size: 40px;
}

.stat-content h3 {
  margin: 0 0 10px 0;
  color: #666;
  font-size: 14px;
}

.stat-number {
  margin: 0;
  font-size: 32px;
  font-weight: bold;
  color: #333;
}

.stat-card small {
  color: #999;
  font-size: 12px;
}

.quick-actions {
  background: white;
  padding: 25px;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  margin-bottom: 30px;
}

.quick-actions h2 {
  margin: 0 0 20px 0;
  color: #333;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.action-btn {
  padding: 15px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 10px;
  transition: transform 0.2s;
}

.action-btn:hover {
  transform: translateY(-2px);
}

.action-btn .icon {
  font-size: 24px;
}

.recent-activity {
  background: white;
  padding: 25px;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.recent-activity h2 {
  margin: 0 0 20px 0;
  color: #333;
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.activity-item {
  padding: 15px;
  background: #f9f9f9;
  border-radius: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.activity-info {
  flex: 1;
}

.activity-meta {
  text-align: right;
}

.cost {
  font-weight: bold;
  color: #4CAF50;
  margin-top: 5px;
}

.status-active {
  color: #ff9800;
  font-weight: bold;
}

.status-completed {
  color: #4CAF50;
  font-weight: bold;
}

.no-data {
  text-align: center;
  padding: 40px;
  color: #999;
}
</style>
