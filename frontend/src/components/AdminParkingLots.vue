<template>
  <div class="admin-parking-lots">
    <Navbar />
    
    <div class="content-container">
      <div class="header">
        <h1>🏢 Parking Lots Management</h1>
        <button @click="showCreateModal = true" class="btn-primary">
          + Create New Parking Lot
        </button>
      </div>

      <div v-if="loading" class="loading">Loading parking lots...</div>

      <div v-else>
        <!-- Parking Lots Grid -->
        <div v-if="parkingLots.length > 0" class="lots-grid">
          <div
            v-for="lot in parkingLots"
            :key="lot.id"
            class="lot-card"
            @click="viewLotDetails(lot.id)"
          >
            <h3>{{ lot.name }}</h3>
            <div class="lot-info">
              <p><strong>📍 Address:</strong> {{ lot.address }}</p>
              <p><strong>📮 PIN:</strong> {{ lot.pin_code }}</p>
              <p><strong>💰 Price:</strong> ₹{{ lot.price }}/hour</p>
            </div>
            <div class="lot-stats">
              <div class="stat">
                <span class="label">Total Spots:</span>
                <span class="value">{{ lot.total_spots }}</span>
              </div>
              <div class="stat">
                <span class="label">Available:</span>
                <span class="value available">{{ lot.available_spots }}</span>
              </div>
              <div class="stat">
                <span class="label">Occupied:</span>
                <span class="value occupied">{{ lot.occupied_spots }}</span>
              </div>
            </div>
            <div class="lot-actions">
              <button @click.stop="editLot(lot)" class="btn-edit">Edit</button>
              <button @click.stop="deleteLot(lot)" class="btn-delete">Delete</button>
            </div>
          </div>
        </div>

        <div v-else class="no-data">
          <p>No parking lots found</p>
          <button @click="showCreateModal = true" class="btn-primary">
            Create Your First Parking Lot
          </button>
        </div>
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <div v-if="showCreateModal || showEditModal" class="modal-overlay" @click="closeModals">
      <div class="modal-content" @click.stop>
        <h2>{{ showEditModal ? 'Edit Parking Lot' : 'Create New Parking Lot' }}</h2>
        
        <form @submit.prevent="showEditModal ? updateLot() : createLot()">
          <div class="form-group">
            <label>Name</label>
            <input v-model="formData.name" type="text" required />
          </div>

          <div class="form-group">
            <label>Price per Hour (₹)</label>
            <input v-model="formData.price" type="number" step="0.01" required />
          </div>

          <div class="form-group">
            <label>Address</label>
            <textarea v-model="formData.address" required></textarea>
          </div>

          <div class="form-group">
            <label>PIN Code</label>
            <input v-model="formData.pin_code" type="text" required />
          </div>

          <div class="form-group" v-if="!showEditModal">
            <label>Number of Spots</label>
            <input v-model="formData.number_of_spots" type="number" min="1" max="1000" required />
          </div>

          <div class="form-group">
            <label>Description</label>
            <textarea v-model="formData.description"></textarea>
          </div>

          <div v-if="modalError" class="error-message">{{ modalError }}</div>

          <div class="modal-actions">
            <button type="button" @click="closeModals" class="btn-secondary">Cancel</button>
            <button type="submit" class="btn-primary">
              {{ showEditModal ? 'Update' : 'Create' }}
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
const showCreateModal = ref(false)
const showEditModal = ref(false)
const modalError = ref('')

const formData = ref({
  name: '',
  price: '',
  address: '',
  pin_code: '',
  number_of_spots: '',
  description: ''
})

const currentEditId = ref(null)

const loadParkingLots = async () => {
  try {
    const response = await api.get('/api/admin/parking-lots')

    if (response.data.status === 'success') {
      parkingLots.value = response.data.parking_lots
    }
  } catch (error) {
    console.error('Failed to load parking lots:', error)
  } finally {
    loading.value = false
  }
}

const createLot = async () => {
  modalError.value = ''
  try {
    const response = await api.post('/api/admin/parking-lots', formData.value)

    if (response.data.status === 'success') {
      closeModals()
      loadParkingLots()
    }
  } catch (error) {
    modalError.value = error.response?.data?.message || 'Failed to create parking lot'
  }
}

const editLot = (lot) => {
  currentEditId.value = lot.id
  formData.value = {
    name: lot.name,
    price: lot.price,
    address: lot.address,
    pin_code: lot.pin_code,
    description: lot.description
  }
  showEditModal.value = true
}

const updateLot = async () => {
  modalError.value = ''
  try {
    const response = await api.put(
      `/api/admin/parking-lots/${currentEditId.value}`,
      formData.value
    )

    if (response.data.status === 'success') {
      closeModals()
      loadParkingLots()
    }
  } catch (error) {
    modalError.value = error.response?.data?.message || 'Failed to update parking lot'
  }
}

const deleteLot = async (lot) => {
  if (!confirm(`Are you sure you want to delete "${lot.name}"?`)) return

  try {
    const response = await api.delete(`/api/admin/parking-lots/${lot.id}`)

    if (response.data.status === 'success') {
      loadParkingLots()
    } else {
      alert(response.data.message)
    }
  } catch (error) {
    alert(error.response?.data?.message || 'Failed to delete parking lot')
  }
}

const viewLotDetails = (lotId) => {
  router.push(`/admin/parking-lots/${lotId}`)
}

const closeModals = () => {
  showCreateModal.value = false
  showEditModal.value = false
  modalError.value = ''
  currentEditId.value = null
  formData.value = {
    name: '',
    price: '',
    address: '',
    pin_code: '',
    number_of_spots: '',
    description: ''
  }
}

onMounted(() => {
  loadParkingLots()
})
</script>

<style scoped>
.admin-parking-lots {
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
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

h1 {
  color: #333;
  margin: 0;
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
  cursor: pointer;
  transition: transform 0.2s;
}

.lot-card:hover {
  transform: translateY(-5px);
}

.lot-card h3 {
  margin: 0 0 15px 0;
  color: #333;
}

.lot-info p {
  margin: 8px 0;
  color: #666;
}

.lot-stats {
  display: flex;
  justify-content: space-between;
  margin: 20px 0;
  padding: 15px;
  background: #f9f9f9;
  border-radius: 8px;
}

.stat {
  text-align: center;
}

.stat .label {
  display: block;
  font-size: 12px;
  color: #666;
  margin-bottom: 5px;
}

.stat .value {
  display: block;
  font-size: 20px;
  font-weight: bold;
  color: #333;
}

.stat .value.available {
  color: #4CAF50;
}

.stat .value.occupied {
  color: #ff9800;
}

.lot-actions {
  display: flex;
  gap: 10px;
  margin-top: 15px;
}

.btn-edit, .btn-delete {
  flex: 1;
  padding: 10px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-weight: 600;
}

.btn-edit {
  background: #2196F3;
  color: white;
}

.btn-delete {
  background: #f44336;
  color: white;
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
  max-height: 90vh;
  overflow-y: auto;
}

.modal-content h2 {
  margin-top: 0;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 5px;
}

.form-group textarea {
  resize: vertical;
  min-height: 80px;
}

.error-message {
  background: #fee;
  color: #c33;
  padding: 12px;
  border-radius: 5px;
  margin-bottom: 20px;
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
</style>
