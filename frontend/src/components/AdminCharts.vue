<template>
  <div class="admin-charts">
    <Navbar />
    
    <div class="content-container">
      <h1>📈 Analytics & Charts</h1>

      <div v-if="loading" class="loading">Loading analytics...</div>

      <div v-else>
        <!-- Summary Statistics -->
        <div class="section">
          <h2>Overall Summary</h2>
          <div class="summary-grid">
            <div class="summary-card">
              <div class="summary-label">Total Parking Lots</div>
              <div class="summary-value">{{ chartData.length }}</div>
            </div>
            <div class="summary-card">
              <div class="summary-label">Total Spots</div>
              <div class="summary-value">{{ totalSpots }}</div>
            </div>
            <div class="summary-card">
              <div class="summary-label">Total Occupied</div>
              <div class="summary-value occupied">{{ totalOccupied }}</div>
            </div>
            <div class="summary-card">
              <div class="summary-label">Total Revenue</div>
              <div class="summary-value revenue">₹{{ totalRevenue.toFixed(2) }}</div>
            </div>
            <div class="summary-card">
              <div class="summary-label">Average Occupancy</div>
              <div class="summary-value">{{ averageOccupancy.toFixed(2) }}%</div>
            </div>
          </div>
        </div>

        <!-- Chart.js Visualizations -->
        <div v-if="chartData.length > 0" class="section">
          <h2>Visual Analytics</h2>
          
          <div class="charts-row">
            <!-- Occupancy Comparison Chart -->
            <div class="chart-container">
              <h3>Parking Lot Occupancy Comparison</h3>
              <Bar :data="occupancyChartData" :options="barChartOptions" />
            </div>

            <!-- Revenue Chart -->
            <div class="chart-container">
              <h3>Revenue by Parking Lot</h3>
              <Doughnut :data="revenueChartData" :options="doughnutChartOptions" />
            </div>

            <!-- Availability vs Occupied -->
            <div class="chart-container">
              <h3>Overall Spot Distribution</h3>
              <Pie :data="distributionChartData" :options="pieChartOptions" />
            </div>
          </div>

          <!-- Occupancy Rate Line Chart -->
          <div class="chart-container-full">
            <h3>Occupancy Rate Comparison</h3>
            <Line :data="occupancyRateChartData" :options="lineChartOptions" />
          </div>
        </div>

        <!-- Parking Lot Details Cards -->
        <div class="section">
          <h2>Parking Lot Performance Details</h2>
          
          <div v-if="chartData.length > 0" class="charts-grid">
            <div
              v-for="lot in chartData"
              :key="lot.name"
              class="chart-card"
            >
              <h3>{{ lot.name }}</h3>
              
              <div class="chart-stats">
                <div class="stat-row">
                  <span class="label">Total Spots:</span>
                  <span class="value">{{ lot.total_spots }}</span>
                </div>
                <div class="stat-row">
                  <span class="label">Occupied:</span>
                  <span class="value occupied">{{ lot.occupied_spots }}</span>
                </div>
                <div class="stat-row">
                  <span class="label">Available:</span>
                  <span class="value available">{{ lot.available_spots }}</span>
                </div>
                <div class="stat-row">
                  <span class="label">Occupancy Rate:</span>
                  <span class="value">{{ lot.occupancy_rate }}%</span>
                </div>
              </div>

              <div class="progress-bar">
                <div
                  class="progress-fill"
                  :style="{ width: lot.occupancy_rate + '%' }"
                ></div>
              </div>

              <div class="revenue-section">
                <div class="revenue-label">Total Revenue</div>
                <div class="revenue-value">₹{{ lot.revenue.toFixed(2) }}</div>
              </div>
            </div>
          </div>

          <div v-else class="no-data">
            No data available for charts
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Bar, Doughnut, Pie, Line } from 'vue-chartjs'
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
const chartData = ref([])

const totalSpots = computed(() => {
  return chartData.value.reduce((sum, lot) => sum + lot.total_spots, 0)
})

const totalOccupied = computed(() => {
  return chartData.value.reduce((sum, lot) => sum + lot.occupied_spots, 0)
})

const totalRevenue = computed(() => {
  return chartData.value.reduce((sum, lot) => sum + lot.revenue, 0)
})

const averageOccupancy = computed(() => {
  if (chartData.value.length === 0) return 0
  const sum = chartData.value.reduce((sum, lot) => sum + lot.occupancy_rate, 0)
  return sum / chartData.value.length
})

const occupancyChartData = computed(() => ({
  labels: chartData.value.map(lot => lot.name),
  datasets: [
    {
      label: 'Occupied Spots',
      backgroundColor: '#f87979',
      data: chartData.value.map(lot => lot.occupied_spots)
    },
    {
      label: 'Available Spots',
      backgroundColor: '#7acbf9',
      data: chartData.value.map(lot => lot.available_spots)
    }
  ]
}))

const revenueChartData = computed(() => ({
  labels: chartData.value.map(lot => lot.name),
  datasets: [
    {
      label: 'Revenue (₹)',
      backgroundColor: [
        '#FF6384',
        '#36A2EB',
        '#FFCE56',
        '#4BC0C0',
        '#9966FF',
        '#FF9F40'
      ],
      data: chartData.value.map(lot => lot.revenue)
    }
  ]
}))

const distributionChartData = computed(() => ({
  labels: ['Occupied', 'Available'],
  datasets: [
    {
      backgroundColor: ['#f87979', '#7acbf9'],
      data: [totalOccupied.value, totalSpots.value - totalOccupied.value]
    }
  ]
}))

const occupancyRateChartData = computed(() => ({
  labels: chartData.value.map(lot => lot.name),
  datasets: [
    {
      label: 'Occupancy Rate (%)',
      borderColor: '#667eea',
      backgroundColor: 'rgba(102, 126, 234, 0.1)',
      data: chartData.value.map(lot => lot.occupancy_rate),
      tension: 0.4,
      fill: true
    }
  ]
}))

const barChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: true,
      position: 'top'
    },
    title: {
      display: false
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

const pieChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: true,
      position: 'top'
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
      beginAtZero: true,
      max: 100
    }
  }
}

const loadCharts = async () => {
  try {
    const response = await api.get('/api/admin/charts/parking-lots')

    if (response.data.status === 'success') {
      chartData.value = response.data.charts
    }
  } catch (error) {
    console.error('Failed to load charts:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadCharts()
})
</script>

<style scoped>
.admin-charts {
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

.section {
  margin-bottom: 40px;
}

.section h2 {
  color: #333;
  margin-bottom: 20px;
}

.section h3 {
  color: #667eea;
  margin-bottom: 15px;
  font-size: 18px;
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

.chart-container-full {
  background: white;
  padding: 25px;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  margin-bottom: 30px;
  height: 400px;
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
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

.chart-card {
  background: white;
  padding: 25px;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.chart-card h3 {
  margin: 0 0 20px 0;
  color: #333;
  font-size: 18px;
}

.chart-stats {
  margin-bottom: 15px;
}

.stat-row {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.stat-row .label {
  color: #666;
  font-size: 14px;
}

.stat-row .value {
  font-weight: 600;
  color: #333;
}

.stat-row .value.occupied {
  color: #ff9800;
}

.stat-row .value.available {
  color: #4CAF50;
}

.progress-bar {
  width: 100%;
  height: 20px;
  background: #f0f0f0;
  border-radius: 10px;
  overflow: hidden;
  margin: 15px 0;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #4CAF50, #ff9800);
  transition: width 0.3s ease;
}

.revenue-section {
  margin-top: 15px;
  padding-top: 15px;
  border-top: 2px solid #f0f0f0;
  text-align: center;
}

.revenue-label {
  font-size: 14px;
  color: #666;
  margin-bottom: 5px;
}

.revenue-value {
  font-size: 24px;
  font-weight: bold;
  color: #4CAF50;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.summary-card {
  background: white;
  padding: 30px;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.summary-label {
  font-size: 14px;
  color: #666;
  margin-bottom: 10px;
}

.summary-value {
  font-size: 32px;
  font-weight: bold;
  color: #333;
}

.summary-value.occupied {
  color: #ff9800;
}

.summary-value.revenue {
  color: #4CAF50;
}

.loading, .no-data {
  text-align: center;
  padding: 50px;
  color: #666;
}
</style>
