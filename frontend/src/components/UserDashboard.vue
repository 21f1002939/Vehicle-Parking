<template>
  <div class="user-dashboard">
    <Navbar />
    
    <div class="dashboard-container">
      <h1>🚗 My Dashboard</h1>

      <div v-if="loading" class="loading">Loading dashboard...</div>

      <div v-else>
        <!-- User Statistics -->
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-icon">💰</div>
            <div class="stat-content">
              <h3>Total Spent</h3>
              <p class="stat-number">₹{{ dashboardData.statistics?.total_spent || 0 }}</p>
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-icon">📍</div>
            <div class="stat-content">
              <h3>Active Bookings</h3>
              <p class="stat-number">{{ dashboardData.statistics?.active_bookings || 0 }}</p>
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-icon">📊</div>
            <div class="stat-content">
              <h3>Total Bookings</h3>
              <p class="stat-number">{{ dashboardData.statistics?.total_bookings || 0 }}</p>
            </div>
          </div>
        </div>

        <!-- Active Reservations -->
        <div class="section">
          <h2>🅿️ Active Reservations</h2>
          
          <div v-if="dashboardData.active_reservations && dashboardData.active_reservations.length > 0" class="reservations-grid">
            <div
              v-for="reservation in dashboardData.active_reservations"
              :key="reservation.id"
              class="reservation-card active"
            >
              <div class="reservation-header">
                <h3>{{ reservation.parking_lot }}</h3>
                <span class="status-badge active">ACTIVE</span>
              </div>
              
              <div class="reservation-details">
                <p><strong>Spot:</strong> {{ reservation.spot_number }}</p>
                <p><strong>Vehicle:</strong> {{ reservation.vehicle_number || 'N/A' }}</p>
                <p><strong>Parked Since:</strong> {{ formatDateTime(reservation.parked_since) }}</p>
                <p><strong>Duration:</strong> {{ reservation.duration_hours.toFixed(2) }} hours</p>
                <p class="current-cost"><strong>Current Cost:</strong> ₹{{ reservation.current_cost.toFixed(2) }}</p>
              </div>

              <button @click="releaseSpot(reservation.id)" class="btn-release">
                Release Spot
              </button>
            </div>
          </div>

          <div v-else class="no-data">
            <p>No active reservations</p>
            <router-link to="/user/book" class="btn-primary">Book a Parking Spot</router-link>
          </div>
        </div>

        <!-- Recent History -->
        <div class="section">
          <h2>📋 Recent History</h2>
          
          <div v-if="dashboardData.recent_history && dashboardData.recent_history.length > 0" class="history-list">
            <div
              v-for="history in dashboardData.recent_history"
              :key="history.id"
              class="history-item"
            >
              <div class="history-info">
                <h4>{{ history.parking_lot }}</h4>
                <p>Spot: {{ history.spot_number }}</p>
                <small>{{ formatDateTime(history.parked_at) }} - {{ formatDateTime(history.left_at) }}</small>
              </div>
              <div class="history-stats">
                <div class="duration">{{ history.duration_hours.toFixed(2) }} hrs</div>
                <div class="cost">₹{{ history.cost.toFixed(2) }}</div>
              </div>
            </div>
          </div>

          <div v-else class="no-data">
            No booking history
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../axios'
import Navbar from './Navbar.vue'

const router = useRouter()
const loading = ref(true)
const dashboardData = ref({})

const loadDashboard = async () => {
  try {
    const response = await api.get('/api/user/dashboard')

    if (response.data.status === 'success') {
      dashboardData.value = response.data.dashboard
    }
  } catch (error) {
    console.error('Failed to load dashboard:', error)
  } finally {
    loading.value = false
  }
}

const releaseSpot = async (reservationId) => {
  if (!confirm('Are you sure you want to release this parking spot?')) return

  try {
    const response = await api.post(`/api/user/release-spot/${reservationId}`)

    if (response.data.status === 'success') {
      alert(`Spot released! Total cost: ₹${response.data.receipt.total_cost}`)
      loadDashboard()
    }
  } catch (error) {
    alert(error.response?.data?.message || 'Failed to release spot')
  }
}

const formatDateTime = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleString()
}

onMounted(() => {
  loadDashboard()
})
</script>

<style scoped>
.user-dashboard {
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
  color: #667eea;
}

.section {
  margin-bottom: 40px;
}

.section h2 {
  color: #333;
  margin-bottom: 20px;
}

.reservations-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 20px;
}

.reservation-card {
  background: white;
  padding: 25px;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  border-left: 4px solid #ff9800;
}

.reservation-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.reservation-header h3 {
  margin: 0;
  color: #333;
}

.status-badge {
  padding: 5px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.status-badge.active {
  background: #fff3e0;
  color: #ff9800;
}

.reservation-details p {
  margin: 10px 0;
  color: #666;
}

.current-cost {
  font-size: 18px;
  color: #4CAF50;
  margin-top: 15px;
}

.btn-release {
  width: 100%;
  margin-top: 20px;
  padding: 12px;
  background: #f44336;
  color: white;
  border: none;
  border-radius: 5px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.3s;
}

.btn-release:hover {
  background: #d32f2f;
}

.history-list {
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.history-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #f0f0f0;
}

.history-item:last-child {
  border-bottom: none;
}

.history-info h4 {
  margin: 0 0 5px 0;
  color: #333;
}

.history-info p {
  margin: 5px 0;
  color: #666;
  font-size: 14px;
}

.history-info small {
  color: #999;
  font-size: 12px;
}

.history-stats {
  text-align: right;
}

.duration {
  color: #666;
  font-size: 14px;
  margin-bottom: 5px;
}

.cost {
  font-size: 20px;
  font-weight: bold;
  color: #4CAF50;
}

.no-data {
  text-align: center;
  padding: 50px;
  color: #666;
  background: white;
  border-radius: 10px;
}

.btn-primary {
  display: inline-block;
  margin-top: 20px;
  padding: 12px 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  text-decoration: none;
  border-radius: 5px;
  font-weight: 600;
}

.loading {
  text-align: center;
  padding: 50px;
  color: #666;
}
</style>
