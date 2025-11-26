<template>
  <div class="user-booking">
    <Navbar />
    
    <div class="content-container">
      <h1>🅿️ Book Parking Spot</h1>

      <div v-if="loading" class="loading">Loading available parking lots...</div>

      <div v-else>
        <div v-if="parkingLots.length > 0" class="lots-grid">
          <div
            v-for="lot in parkingLots"
            :key="lot.id"
            class="lot-card"
          >
            <div class="lot-header">
              <h3>{{ lot.name }}</h3>
              <div class="price-badge">₹{{ lot.price }}/hr</div>
            </div>

            <div class="lot-info">
              <p><strong>📍 Address:</strong> {{ lot.address }}</p>
              <p><strong>📮 PIN:</strong> {{ lot.pin_code }}</p>
              <p v-if="lot.description"><strong>ℹ️ Info:</strong> {{ lot.description }}</p>
            </div>

            <div class="lot-availability">
              <div class="availability-bar">
                <div class="available-count">
                  <span class="icon">✓</span>
                  {{ lot.available_spots }} spots available
                </div>
                <div class="total-count">
                  of {{ lot.total_spots }}
                </div>
              </div>
              <div class="progress-bar">
                <div
                  class="progress-fill"
                  :style="{ width: (lot.available_spots / lot.total_spots * 100) + '%' }"
                ></div>
              </div>
            </div>

            <button
              @click="showBookingModal(lot)"
              class="btn-book"
              :disabled="lot.available_spots === 0"
            >
              {{ lot.available_spots === 0 ? 'Fully Booked' : 'Book Now' }}
            </button>
          </div>
        </div>

        <div v-else class="no-data">
          <p>No parking lots available at the moment</p>
        </div>
      </div>
    </div>

    <!-- Booking Modal -->
    <div v-if="selectedLot" class="modal-overlay" @click="closeBookingModal">
      <div class="modal-content" @click.stop>
        <h2>Book Parking at {{ selectedLot.name }}</h2>
        
        <div class="booking-info">
          <p><strong>Price:</strong> ₹{{ selectedLot.price }}/hour</p>
          <p><strong>Available Spots:</strong> {{ selectedLot.available_spots }}</p>
        </div>

        <form @submit.prevent="confirmBooking">
          <div class="form-group">
            <label>Vehicle Number (Optional)</label>
            <input
              v-model="vehicleNumber"
              type="text"
              placeholder="e.g., MH-01-AB-1234"
            />
          </div>

          <div v-if="bookingError" class="error-message">
            {{ bookingError }}
          </div>

          <div class="modal-actions">
            <button type="button" @click="closeBookingModal" class="btn-secondary">
              Cancel
            </button>
            <button type="submit" class="btn-primary" :disabled="booking">
              {{ booking ? 'Booking...' : 'Confirm Booking' }}
            </button>
          </div>
        </form>
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
const parkingLots = ref([])
const selectedLot = ref(null)
const vehicleNumber = ref('')
const booking = ref(false)
const bookingError = ref('')

const loadParkingLots = async () => {
  try {
    const response = await api.get('/api/user/parking-lots/available')

    if (response.data.status === 'success') {
      parkingLots.value = response.data.parking_lots
    }
  } catch (error) {
    console.error('Failed to load parking lots:', error)
  } finally {
    loading.value = false
  }
}

const showBookingModal = (lot) => {
  selectedLot.value = lot
  vehicleNumber.value = ''
  bookingError.value = ''
}

const closeBookingModal = () => {
  selectedLot.value = null
  vehicleNumber.value = ''
  bookingError.value = ''
}

const confirmBooking = async () => {
  booking.value = true
  bookingError.value = ''

  try {
    const response = await api.post('/api/user/book-spot', {
      lot_id: selectedLot.value.id,
      vehicle_number: vehicleNumber.value
    })

    if (response.data.status === 'success') {
      alert(`Booking successful! Spot: ${response.data.reservation.spot_number}`)
      closeBookingModal()
      router.push('/user/dashboard')
    }
  } catch (error) {
    bookingError.value = error.response?.data?.message || 'Booking failed'
  } finally {
    booking.value = false
  }
}

onMounted(() => {
  loadParkingLots()
})
</script>

<style scoped>
.user-booking {
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

.lots-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

.lot-card {
  background: white;
  padding: 25px;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.lot-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.lot-header h3 {
  margin: 0;
  color: #333;
}

.price-badge {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 8px 15px;
  border-radius: 20px;
  font-weight: 600;
}

.lot-info p {
  margin: 10px 0;
  color: #666;
  font-size: 14px;
}

.lot-availability {
  margin: 20px 0;
  padding: 15px;
  background: #f9f9f9;
  border-radius: 8px;
}

.availability-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.available-count {
  display: flex;
  align-items: center;
  gap: 5px;
  font-weight: 600;
  color: #4CAF50;
}

.available-count .icon {
  font-size: 18px;
}

.total-count {
  color: #999;
  font-size: 14px;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #4CAF50, #8BC34A);
  transition: width 0.3s;
}

.btn-book {
  width: 100%;
  padding: 14px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 5px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s;
}

.btn-book:hover:not(:disabled) {
  transform: translateY(-2px);
}

.btn-book:disabled {
  background: #ccc;
  cursor: not-allowed;
  transform: none;
}

.loading, .no-data {
  text-align: center;
  padding: 50px;
  color: #666;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000;
}

.modal-content {
  background: white;
  padding: 30px;
  border-radius: 10px;
  width: 90%;
  max-width: 500px;
}

.modal-content h2 {
  margin-top: 0;
  color: #333;
}

.booking-info {
  background: #f9f9f9;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.booking-info p {
  margin: 8px 0;
  color: #666;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #333;
}

.form-group input {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 14px;
}

.error-message {
  background: #fee;
  color: #c33;
  padding: 12px;
  border-radius: 5px;
  margin-bottom: 20px;
  text-align: center;
}

.modal-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

.btn-secondary {
  padding: 12px 24px;
  background: #ccc;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-weight: 600;
}

.btn-primary {
  padding: 12px 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-weight: 600;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
