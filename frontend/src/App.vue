<script setup>
import { RouterView } from 'vue-router'
</script>

<template>
  <div id="app">
    <RouterView />
  </div>
</template>

<style>
/* ==================== RESET & BASE STYLES ==================== */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html {
  scroll-behavior: smooth;
}

body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background: #f5f5f5;
  color: #333;
  line-height: 1.6;
}

#app {
  width: 100%;
  min-height: 100vh;
}

/* ==================== TYPOGRAPHY ==================== */
h1, h2, h3, h4, h5, h6 {
  font-weight: 600;
  line-height: 1.2;
  color: #333;
}

h1 {
  font-size: 2rem;
}

h2 {
  font-size: 1.5rem;
}

h3 {
  font-size: 1.25rem;
}

p {
  margin-bottom: 1rem;
}

/* ==================== GLOBAL BUTTON STYLES ==================== */
button {
  font-family: inherit;
  cursor: pointer;
  transition: all 0.3s ease;
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  padding: 12px 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 5px;
  font-weight: 600;
  font-size: 14px;
  transition: transform 0.2s, box-shadow 0.2s;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
}

.btn-secondary {
  padding: 12px 24px;
  background: #f0f0f0;
  color: #333;
  border: none;
  border-radius: 5px;
  font-weight: 600;
  font-size: 14px;
}

.btn-secondary:hover:not(:disabled) {
  background: #e0e0e0;
}

.btn-danger {
  padding: 10px 20px;
  background: #f44336;
  color: white;
  border: none;
  border-radius: 5px;
  font-weight: 600;
}

.btn-danger:hover:not(:disabled) {
  background: #d32f2f;
}

/* ==================== FORM ELEMENTS ==================== */
input, textarea, select {
  font-family: inherit;
  font-size: 14px;
}

input:focus, textarea:focus, select:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

/* ==================== CARDS ==================== */
.card {
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 20px;
  transition: transform 0.2s, box-shadow 0.2s;
}

.card:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.15);
}

/* ==================== BADGES & STATUS ==================== */
.badge {
  display: inline-block;
  padding: 5px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.badge-success {
  background: #e8f5e9;
  color: #4CAF50;
}

.badge-warning {
  background: #fff3e0;
  color: #ff9800;
}

.badge-danger {
  background: #ffebee;
  color: #f44336;
}

.badge-info {
  background: #e3f2fd;
  color: #2196F3;
}

/* ==================== LOADING STATES ==================== */
.loading {
  text-align: center;
  padding: 50px;
  color: #666;
  font-size: 16px;
}

.loading::after {
  content: '...';
  animation: dots 1.5s steps(4, end) infinite;
}

@keyframes dots {
  0%, 20% { content: '.'; }
  40% { content: '..'; }
  60%, 100% { content: '...'; }
}

/* ==================== ALERTS & MESSAGES ==================== */
.alert {
  padding: 15px 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  font-size: 14px;
}

.alert-success {
  background: #e8f5e9;
  color: #2e7d32;
  border-left: 4px solid #4CAF50;
}

.alert-error {
  background: #ffebee;
  color: #c62828;
  border-left: 4px solid #f44336;
}

.alert-warning {
  background: #fff3e0;
  color: #ef6c00;
  border-left: 4px solid #ff9800;
}

.alert-info {
  background: #e3f2fd;
  color: #1565c0;
  border-left: 4px solid #2196F3;
}

/* ==================== UTILITY CLASSES ==================== */
.text-center {
  text-align: center;
}

.text-left {
  text-align: left;
}

.text-right {
  text-align: right;
}

.mt-10 { margin-top: 10px; }
.mt-20 { margin-top: 20px; }
.mt-30 { margin-top: 30px; }

.mb-10 { margin-bottom: 10px; }
.mb-20 { margin-bottom: 20px; }
.mb-30 { margin-bottom: 30px; }

.p-10 { padding: 10px; }
.p-20 { padding: 20px; }
.p-30 { padding: 30px; }

.flex {
  display: flex;
}

.flex-center {
  display: flex;
  justify-content: center;
  align-items: center;
}

.flex-between {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.gap-10 { gap: 10px; }
.gap-20 { gap: 20px; }

.w-100 { width: 100%; }
.h-100 { height: 100%; }

/* ==================== ANIMATIONS ==================== */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.fade-in {
  animation: fadeIn 0.3s ease;
}

@keyframes slideIn {
  from {
    transform: translateX(-100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.slide-in {
  animation: slideIn 0.4s ease;
}

/* ==================== SCROLLBAR STYLING ==================== */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
}

::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #555;
}

/* ==================== RESPONSIVE DESIGN ==================== */
@media (max-width: 768px) {
  h1 {
    font-size: 1.5rem;
  }
  
  h2 {
    font-size: 1.25rem;
  }
  
  .card {
    padding: 15px;
  }
}

/* ==================== PRINT STYLES ==================== */
@media print {
  .no-print {
    display: none !important;
  }
}

/* ==================== ACCESSIBILITY ==================== */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}

/* Focus visible for keyboard navigation */
*:focus-visible {
  outline: 2px solid #667eea;
  outline-offset: 2px;
}

/* ==================== PARKING APP SPECIFIC ==================== */
.parking-spot {
  transition: all 0.3s ease;
}

.parking-spot.available {
  background: #e8f5e9;
  border-color: #4CAF50;
}

.parking-spot.occupied {
  background: #fff3e0;
  border-color: #ff9800;
}

.price-tag {
  color: #4CAF50;
  font-weight: bold;
  font-size: 1.1em;
}

/* ==================== TRANSITIONS ==================== */
.v-enter-active,
.v-leave-active {
  transition: opacity 0.3s ease;
}

.v-enter-from,
.v-leave-to {
  opacity: 0;
}
</style>
