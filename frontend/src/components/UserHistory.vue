<template>
  <div class="user-history">
    <Navbar />
    
    <div class="content-container">
      <div class="header-section">
        <h1>📋 Booking History</h1>
        <button @click="exportHistory" class="btn-export" :disabled="exporting">
          {{ exporting ? '⏳ Exporting...' : '📥 Export CSV' }}
        </button>
      </div>

      <div v-if="loading" class="loading">Loading history...</div>

      <div v-else>
        <!-- Summary Stats -->
        <div class="summary-section" v-if="chartData">
          <div class="summary-card">
            <h3>Total Parkings</h3>
            <p class="summary-value">{{ chartData.summary?.total_parkings || 0 }}</p>
          </div>
          <div class="summary-card">
            <h3>Total Hours</h3>
            <p class="summary-value">{{ chartData.summary?.total_hours || 0 }}</p>
          </div>
          <div class="summary-card">
            <h3>Total Spent</h3>
            <p class="summary-value">₹{{ chartData.summary?.total_spent || 0 }}</p>
          </div>
          <div class="summary-card">
            <h3>Avg Cost/Visit</h3>
            <p class="summary-value">₹{{ chartData.summary?.average_cost_per_visit?.toFixed(2) || 0 }}</p>
          </div>
        </div>

        <!-- Chart.js Visualizations -->
        <div class="section" v-if="chartData?.by_parking_lot?.length > 0">
          <h2>Visual Analytics</h2>
          
          <div class="charts-row">
            <!-- Usage by Parking Lot Chart -->
            <div class="chart-container">
              <h3>Visits by Parking Lot</h3>
              <Bar :data="visitsChartData" :options="barChartOptions" />
            </div>

            <!-- Cost Distribution -->
            <div class="chart-container">
              <h3>Spending Distribution</h3>
              <Doughnut :data="costChartData" :options="doughnutChartOptions" />
            </div>

            <!-- Hours Comparison -->
            <div class="chart-container">
              <h3>Time Spent at Each Location</h3>
              <Line :data="hoursChartData" :options="lineChartOptions" />
            </div>
          </div>
        </div>

        <!-- Usage by Parking Lot Cards -->
        <div class="section" v-if="chartData?.by_parking_lot?.length > 0">
          <h2>Usage by Parking Lot - Details</h2>
          <div class="usage-grid">
            <div
              v-for="usage in chartData.by_parking_lot"
              :key="usage.parking_lot"
              class="usage-card"
            >
              <h4>{{ usage.parking_lot }}</h4>
              <div class="usage-stats">
                <div class="usage-row">
                  <span>Visits:</span>
                  <strong>{{ usage.visits }}</strong>
                </div>
                <div class="usage-row">
                  <span>Total Hours:</span>
                  <strong>{{ usage.total_hours.toFixed(2) }}</strong>
                </div>
                <div class="usage-row">
                  <span>Total Cost:</span>
                  <strong class="cost">₹{{ usage.total_cost.toFixed(2) }}</strong>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- History Table (from dashboard API) -->
        <div class="section" v-if="dashboardData?.recent_history?.length > 0">
          <h2>Recent Bookings</h2>
          <div class="history-table-container">
            <table class="history-table">
              <thead>
                <tr>
                  <th>Parking Lot</th>
                  <th>Spot</th>
                  <th>Parked At</th>
                  <th>Left At</th>
                  <th>Duration</th>
                  <th>Cost</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="booking in dashboardData.recent_history" :key="booking.id">
                  <td>{{ booking.parking_lot }}</td>
                  <td>{{ booking.spot_number }}</td>
                  <td>{{ formatDateTime(booking.parked_at) }}</td>
                  <td>{{ formatDateTime(booking.left_at) }}</td>
                  <td>{{ booking.duration_hours.toFixed(2) }} hrs</td>
                  <td class="cost">₹{{ booking.cost.toFixed(2) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div v-if="!dashboardData?.recent_history?.length" class="no-data">
          <p>No booking history found</p>
          <router-link to="/user/book" class="btn-primary">Book Your First Parking</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Bar, Doughnut, Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
  ArcElement,
  LineElement,
  PointElement
} from 'chart.js'
import api from '../axios'
import Navbar from './Navbar.vue'

ChartJS.register(
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
  ArcElement,
  LineElement,
  PointElement
)

const loading = ref(true)
const exporting = ref(false)
const chartData = ref(null)
const dashboardData = ref(null)

const visitsChartData = computed(() => {
  if (!chartData.value?.by_parking_lot) return { labels: [], datasets: [] }
  return {
    labels: chartData.value.by_parking_lot.map(u => u.parking_lot),
    datasets: [
      {
        label: 'Number of Visits',
        backgroundColor: '#667eea',
        data: chartData.value.by_parking_lot.map(u => u.visits)
      }
    ]
  }
})

const costChartData = computed(() => {
  if (!chartData.value?.by_parking_lot) return { labels: [], datasets: [] }
  return {
    labels: chartData.value.by_parking_lot.map(u => u.parking_lot),
    datasets: [
      {
        label: 'Total Cost (₹)',
        backgroundColor: [
          '#FF6384',
          '#36A2EB',
          '#FFCE56',
          '#4BC0C0',
          '#9966FF',
          '#FF9F40'
        ],
        data: chartData.value.by_parking_lot.map(u => u.total_cost)
      }
    ]
  }
})

const hoursChartData = computed(() => {
  if (!chartData.value?.by_parking_lot) return { labels: [], datasets: [] }
  return {
    labels: chartData.value.by_parking_lot.map(u => u.parking_lot),
    datasets: [
      {
        label: 'Total Hours',
        borderColor: '#764ba2',
        backgroundColor: 'rgba(118, 75, 162, 0.1)',
        data: chartData.value.by_parking_lot.map(u => u.total_hours),
        tension: 0.4,
        fill: true
      }
    ]
  }
})

const barChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: true,
      position: 'top'
    }
  },
  scales: {
    y: {
      beginAtZero: true
    }
  }
}

const doughnutChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: true,
      position: 'right'
    }
  }
}

const lineChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: true,
      position: 'top'
    }
  },
  scales: {
    y: {
      beginAtZero: true
    }
  }
}

const loadHistory = async () => {
  try {
    // Load chart data
    const chartResponse = await api.get('/api/user/charts/my-usage')
    if (chartResponse.data.status === 'success') {
      chartData.value = chartResponse.data.charts
    }

    // Load dashboard data for history table
    const dashboardResponse = await api.get('/api/user/dashboard')
    if (dashboardResponse.data.status === 'success') {
      dashboardData.value = dashboardResponse.data.dashboard
    }
  } catch (error) {
    console.error('Failed to load history:', error)
  } finally {
    loading.value = false
  }
}

const exportHistory = async () => {
  exporting.value = true
  try {
    const response = await api.post('/api/user/export-history')
    if (response.data.status === 'success') {
      // Create blob from CSV data
      const blob = new Blob([response.data.csv_data], { type: 'text/csv' })
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `parking_history_${new Date().toISOString().split('T')[0]}.csv`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
      alert('CSV file downloaded successfully!')
    } else {
      alert('Export failed: ' + response.data.message)
    }
  } catch (error) {
    console.error('Failed to export history:', error)
    alert('Failed to export. Please try again.')
  } finally {
    exporting.value = false
  }
}

const formatDateTime = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleString()
}

onMounted(() => {
  loadHistory()
})
</script>

<style scoped>
.user-history {
  min-height: 100vh;
  background: #f5f5f5;
}

.content-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.charts-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 30px;
}

.chart-container {
  background: white;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  height: 350px;
}

.chart-container h3 {
  color: #667eea;
  margin-bottom: 15px;
  font-size: 18px;
}

@media (max-width: 1024px) {
  .charts-row {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .charts-row {
    grid-template-columns: 1fr;
  }
  
  .chart-container {
    height: 300px;
  }
}

.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  flex-wrap: wrap;
  gap: 15px;
}

h1 {
  color: #333;
  margin: 0;
}

.btn-export {
  padding: 12px 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.btn-export:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-export:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.summary-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.summary-card {
  background: white;
  padding: 25px;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.summary-card h3 {
  margin: 0 0 15px 0;
  color: #666;
  font-size: 14px;
}

.summary-value {
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

.usage-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.usage-card {
  background: white;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.usage-card h4 {
  margin: 0 0 15px 0;
  color: #333;
}

.usage-stats {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.usage-row {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.usage-row:last-child {
  border-bottom: none;
}

.usage-row span {
  color: #666;
}

.usage-row strong.cost {
  color: #4CAF50;
  font-size: 16px;
}

.history-table-container {
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  overflow-x: auto;
}

.history-table {
  width: 100%;
  border-collapse: collapse;
}

.history-table th,
.history-table td {
  padding: 15px;
  text-align: left;
  border-bottom: 1px solid #f0f0f0;
}

.history-table th {
  background: #f9f9f9;
  font-weight: 600;
  color: #333;
}

.history-table tbody tr:hover {
  background: #f9f9f9;
}

.history-table td.cost {
  font-weight: bold;
  color: #4CAF50;
}

.loading, .no-data {
  text-align: center;
  padding: 50px;
  color: #666;
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
</style>
