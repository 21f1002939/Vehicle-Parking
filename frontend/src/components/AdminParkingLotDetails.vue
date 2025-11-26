<template>
  <div class="parking-lot-details">
    <Navbar />
    
    <div class="content-container">
      <div class="header">
        <button @click="$router.back()" class="btn-back">← Back</button>
        <h1 v-if="parkingLot">{{ parkingLot.name }}</h1>
      </div>

      <div v-if="loading" class="loading">Loading details...</div>

      <div v-else-if="parkingLot">
        <!-- Parking Lot Info -->
        <div class="info-section">
          <div class="info-card">
            <h3>📍 Location Information</h3>
            <p><strong>Address:</strong> {{ parkingLot.address }}</p>
            <p><strong>PIN Code:</strong> {{ parkingLot.pin_code }}</p>
            <p><strong>Price:</strong> ₹{{ parkingLot.price }}/hour</p>
            <p v-if="parkingLot.description"><strong>Description:</strong> {{ parkingLot.description }}</p>
          </div>

          <div class="stats-card">
            <h3>📊 Statistics</h3>
            <div class="stats-grid">
              <div class="stat-item">
                <span class="stat-label">Total Spots</span>
                <span class="stat-value">{{ parkingLot.total_spots }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">Available</span>
                <span class="stat-value available">{{ parkingLot.available_spots }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">Occupied</span>
                <span class="stat-value occupied">{{ parkingLot.occupied_spots }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Parking Spots Grid -->
        <div class="spots-section">
          <h2>Parking Spots</h2>
          <div class="spots-grid">
            <div
              v-for="spot in parkingLot.spots"
              :key="spot.id"
              :class="['spot-card', spot.status === 'A' ? 'available' : 'occupied']"
            >
              <div class="spot-number">{{ spot.spot_number }}</div>
              <div class="spot-status">
                {{ spot.status === 'A' ? 'Available' : 'Occupied' }}
              </div>
              <div v-if="spot.reservation" class="spot-reservation">
                <p><strong>User:</strong> {{ spot.reservation.user }}</p>
                <p><strong>Vehicle:</strong> {{ spot.reservation.vehicle_number }}</p>
                <p><strong>Duration:</strong> {{ spot.reservation.duration_hours.toFixed(2) }} hrs</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="error">Failed to load parking lot details</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../axios'
import Navbar from './Navbar.vue'

const route = useRoute()
const loading = ref(true)
const parkingLot = ref(null)

const loadParkingLotDetails = async () => {
  try {
    const lotId = route.params.id
    const response = await api.get(`/api/admin/parking-lots/${lotId}`)

    if (response.data.status === 'success') {
      parkingLot.value = response.data.parking_lot
    }
  } catch (error) {
    console.error('Failed to load parking lot details:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadParkingLotDetails()
})
</script>

<style scoped>
.parking-lot-details {
  min-height: 100vh;
  background: #f5f5f5;
}

.content-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.header {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 30px;
}

.btn-back {
  padding: 10px 20px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-weight: 600;
}

h1 {
  margin: 0;
  color: #333;
}

.info-section {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
  margin-bottom: 30px;
}

.info-card, .stats-card {
  background: white;
  padding: 25px;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.info-card h3, .stats-card h3 {
  margin-top: 0;
  color: #333;
}

.info-card p {
  margin: 10px 0;
  color: #666;
}

.stats-grid {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  padding: 10px;
  background: #f9f9f9;
  border-radius: 5px;
}

.stat-label {
  color: #666;
}

.stat-value {
  font-weight: bold;
  font-size: 18px;
  color: #333;
}

.stat-value.available {
  color: #4CAF50;
}

.stat-value.occupied {
  color: #ff9800;
}

.spots-section h2 {
  color: #333;
  margin-bottom: 20px;
}

.spots-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 15px;
}

.spot-card {
  background: white;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.spot-card.available {
  border-left: 4px solid #4CAF50;
}

.spot-card.occupied {
  border-left: 4px solid #ff9800;
  background: #fff8e1;
}

.spot-number {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin-bottom: 10px;
}

.spot-status {
  padding: 5px 10px;
  border-radius: 5px;
  font-size: 12px;
  font-weight: 600;
  display: inline-block;
}

.spot-card.available .spot-status {
  background: #4CAF50;
  color: white;
}

.spot-card.occupied .spot-status {
  background: #ff9800;
  color: white;
}

.spot-reservation {
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid #ddd;
  font-size: 12px;
  text-align: left;
}

.spot-reservation p {
  margin: 5px 0;
  color: #666;
}

.loading, .error {
  text-align: center;
  padding: 50px;
  color: #666;
}

@media (max-width: 768px) {
  .info-section {
    grid-template-columns: 1fr;
  }
  
  .spots-grid {
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  }
}
</style>
