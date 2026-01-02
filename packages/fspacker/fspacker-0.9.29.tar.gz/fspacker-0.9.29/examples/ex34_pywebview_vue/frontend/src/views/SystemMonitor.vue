<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api'

const router = useRouter()
const isDesktop = ref<boolean>(false)
const cpuUsage = ref<number>(0)
const memoryInfo = ref<Record<string, any>>({
  total: 0,
  used: 0,
  available: 0,
  percent: 0
})
const diskInfo = ref<Record<string, any>>({
  total: 0,
  used: 0,
  free: 0,
  percent: 0
})
const isLoading = ref<boolean>(false)
const isAutoRefresh = ref<boolean>(false)
const refreshInterval = ref<number | null>(null)
const lastUpdateTime = ref<string>('')

onMounted(async () => {
  isDesktop.value = api.isAvailable()
  await refreshMonitorData()
})

onUnmounted(() => {
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value)
  }
})

const refreshMonitorData = async () => {
  if (!isDesktop.value) return

  isLoading.value = true

  try {
    const [cpu, memory, disk] = await Promise.all([
      api.getCpuUsage(),
      api.getMemoryInfo(),
      api.getDiskInfo()
    ])

    cpuUsage.value = cpu
    memoryInfo.value = memory
    diskInfo.value = disk
    lastUpdateTime.value = new Date().toLocaleTimeString()
  } catch (error) {
    console.error('获取监控数据失败:', error)
  }

  isLoading.value = false
}

const toggleAutoRefresh = () => {
  isAutoRefresh.value = !isAutoRefresh.value

  if (isAutoRefresh.value) {
    refreshInterval.value = setInterval(refreshMonitorData, 2000) // 每2秒刷新一次
  } else {
    if (refreshInterval.value) {
      clearInterval(refreshInterval.value)
      refreshInterval.value = null
    }
  }
}

const formatBytes = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const getUsageColor = (percent: number): string => {
  if (percent < 50) return '#10b981' // 绿色
  if (percent < 80) return '#f59e0b' // 橙色
  return '#ef4444' // 红色
}

const getUsageLevel = (percent: number): string => {
  if (percent < 50) return '正常'
  if (percent < 80) return '警告'
  return '危险'
}

const goBack = () => {
  router.push('/')
}
</script>

<template>
  <div class="system-monitor-page">
    <header class="page-header">
      <button @click="goBack" class="back-btn">← 返回主页</button>
      <h1>📊 系统监控</h1>
      <div class="app-info">
        <span v-if="isDesktop" class="desktop-badge">桌面应用</span>
        <span v-else class="web-badge">Web版本</span>
      </div>
    </header>

    <main class="main-content">
      <!-- 控制面板 -->
      <section class="control-panel" v-if="isDesktop">
        <h2>监控控制</h2>
        <div class="controls">
          <button @click="refreshMonitorData" :disabled="isLoading" class="refresh-btn">
            🔄 {{ isLoading ? '刷新中...' : '手动刷新' }}
          </button>
          <button @click="toggleAutoRefresh" :class="['auto-refresh-btn', { active: isAutoRefresh }]">
            ⏱️ {{ isAutoRefresh ? '停止自动刷新' : '开始自动刷新' }}
          </button>
        </div>
        <div class="status-info" v-if="lastUpdateTime">
          最后更新时间: {{ lastUpdateTime }}
        </div>
      </section>

      <!-- Web模式提示 -->
      <section class="web-notice" v-else>
        <div class="notice-card">
          <h2>🌐 Web模式限制</h2>
          <p>系统监控功能仅在桌面模式下可用。要查看系统监控数据，请运行桌面版本。</p>
          <pre><code>python start.py</code></pre>
        </div>
      </section>

      <!-- 监控数据面板 -->
      <div v-if="isDesktop">
        <!-- CPU监控 -->
        <section class="monitor-section cpu">
          <div class="monitor-header">
            <h2>💻 CPU使用率</h2>
            <div class="monitor-badge" :style="{ backgroundColor: getUsageColor(cpuUsage) }">
              {{ getUsageLevel(cpuUsage) }}
            </div>
          </div>
          <div class="monitor-display">
            <div class="usage-circle">
              <div class="circle-progress" :style="{
                background: `conic-gradient(${getUsageColor(cpuUsage)} ${cpuUsage * 3.6}deg, #e5e7eb ${cpuUsage * 3.6}deg)`
              }">
                <div class="circle-inner">
                  <span class="usage-value">{{ cpuUsage.toFixed(1) }}%</span>
                </div>
              </div>
            </div>
            <div class="usage-details">
              <div class="detail-item">
                <span class="label">当前使用率:</span>
                <span class="value" :style="{ color: getUsageColor(cpuUsage) }">{{ cpuUsage.toFixed(1) }}%</span>
              </div>
              <div class="detail-item">
                <span class="label">状态:</span>
                <span class="value" :style="{ color: getUsageColor(cpuUsage) }">{{ getUsageLevel(cpuUsage) }}</span>
              </div>
            </div>
          </div>
        </section>

        <!-- 内存监控 -->
        <section class="monitor-section memory" v-if="memoryInfo.total">
          <div class="monitor-header">
            <h2>🧠 内存使用</h2>
            <div class="monitor-badge" :style="{ backgroundColor: getUsageColor(memoryInfo.percent) }">
              {{ getUsageLevel(memoryInfo.percent) }}
            </div>
          </div>
          <div class="monitor-display">
            <div class="usage-circle">
              <div class="circle-progress" :style="{
                background: `conic-gradient(${getUsageColor(memoryInfo.percent)} ${memoryInfo.percent * 3.6}deg, #e5e7eb ${memoryInfo.percent * 3.6}deg)`
              }">
                <div class="circle-inner">
                  <span class="usage-value">{{ memoryInfo.percent.toFixed(1) }}%</span>
                </div>
              </div>
            </div>
            <div class="usage-details">
              <div class="detail-item">
                <span class="label">已使用:</span>
                <span class="value">{{ formatBytes(memoryInfo.used) }}</span>
              </div>
              <div class="detail-item">
                <span class="label">总量:</span>
                <span class="value">{{ formatBytes(memoryInfo.total) }}</span>
              </div>
              <div class="detail-item">
                <span class="label">可用:</span>
                <span class="value">{{ formatBytes(memoryInfo.available) }}</span>
              </div>
              <div class="progress-bar-container">
                <div class="progress-bar">
                  <div class="progress-fill memory" :style="{
                    width: memoryInfo.percent + '%',
                    backgroundColor: getUsageColor(memoryInfo.percent)
                  }"></div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- 磁盘监控 -->
        <section class="monitor-section disk" v-if="diskInfo.total">
          <div class="monitor-header">
            <h2>💾 磁盘使用</h2>
            <div class="monitor-badge" :style="{ backgroundColor: getUsageColor(diskInfo.percent) }">
              {{ getUsageLevel(diskInfo.percent) }}
            </div>
          </div>
          <div class="monitor-display">
            <div class="usage-circle">
              <div class="circle-progress" :style="{
                background: `conic-gradient(${getUsageColor(diskInfo.percent)} ${diskInfo.percent * 3.6}deg, #e5e7eb ${diskInfo.percent * 3.6}deg)`
              }">
                <div class="circle-inner">
                  <span class="usage-value">{{ diskInfo.percent.toFixed(1) }}%</span>
                </div>
              </div>
            </div>
            <div class="usage-details">
              <div class="detail-item">
                <span class="label">已使用:</span>
                <span class="value">{{ formatBytes(diskInfo.used) }}</span>
              </div>
              <div class="detail-item">
                <span class="label">总量:</span>
                <span class="value">{{ formatBytes(diskInfo.total) }}</span>
              </div>
              <div class="detail-item">
                <span class="label">可用:</span>
                <span class="value">{{ formatBytes(diskInfo.free) }}</span>
              </div>
              <div class="progress-bar-container">
                <div class="progress-bar">
                  <div class="progress-fill disk" :style="{
                    width: diskInfo.percent + '%',
                    backgroundColor: getUsageColor(diskInfo.percent)
                  }"></div>
                </div>
              </div>
            </div>
          </div>
        </section>
      </div>
    </main>
  </div>
</template>

<style scoped>
.system-monitor-page {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #e5e7eb;
}

.back-btn {
  background: #3b82f6;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
  transition: background-color 0.2s;
}

.back-btn:hover {
  background: #2563eb;
}

.page-header h1 {
  margin: 0;
  color: #1f2937;
  font-size: 2rem;
  flex: 1;
}

.app-info {
  display: flex;
  gap: 0.5rem;
}

.desktop-badge,
.web-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.875rem;
  font-weight: 600;
}

.desktop-badge {
  background: #10b981;
  color: white;
}

.web-badge {
  background: #f59e0b;
  color: white;
}

.main-content {
  display: grid;
  gap: 2rem;
}

.control-panel {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.control-panel h2 {
  margin: 0 0 1.5rem 0;
  color: #1f2937;
  font-size: 1.5rem;
  font-weight: 600;
}

.controls {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.refresh-btn,
.auto-refresh-btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
}

.refresh-btn {
  background: #10b981;
  color: white;
}

.refresh-btn:hover:not(:disabled) {
  background: #059669;
}

.refresh-btn:disabled {
  background: #9ca3af;
  cursor: not-allowed;
}

.auto-refresh-btn {
  background: #6b7280;
  color: white;
}

.auto-refresh-btn:hover {
  background: #4b5563;
}

.auto-refresh-btn.active {
  background: #3b82f6;
}

.auto-refresh-btn.active:hover {
  background: #2563eb;
}

.status-info {
  color: #6b7280;
  font-size: 0.875rem;
}

.web-notice {
  text-align: center;
}

.notice-card {
  background: #fef3c7;
  border: 2px solid #f59e0b;
  border-radius: 12px;
  padding: 2rem;
}

.notice-card h2 {
  margin: 0 0 1rem 0;
  color: #92400e;
  font-size: 1.5rem;
  font-weight: 600;
}

.notice-card p {
  margin: 0 0 1rem 0;
  color: #78350f;
  line-height: 1.6;
}

.monitor-section {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.monitor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.monitor-header h2 {
  margin: 0;
  color: #1f2937;
  font-size: 1.5rem;
  font-weight: 600;
}

.monitor-badge {
  padding: 0.5rem 1rem;
  border-radius: 9999px;
  color: white;
  font-weight: 600;
  font-size: 0.875rem;
}

.monitor-display {
  display: flex;
  gap: 3rem;
  align-items: center;
  flex-wrap: wrap;
}

.usage-circle {
  flex-shrink: 0;
}

.circle-progress {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.circle-inner {
  width: 90px;
  height: 90px;
  background: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.usage-value {
  font-size: 1.25rem;
  font-weight: bold;
  color: #1f2937;
}

.usage-details {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background: #f8fafc;
  border-radius: 8px;
}

.detail-item .label {
  color: #6b7280;
  font-weight: 500;
}

.detail-item .value {
  font-weight: 600;
  color: #1f2937;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
}

.progress-bar-container {
  margin-top: 0.5rem;
}

.progress-bar {
  width: 100%;
  height: 12px;
  background: #e5e7eb;
  border-radius: 6px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  transition: width 0.3s ease;
}

@media (max-width: 768px) {
  .system-monitor-page {
    padding: 1rem;
  }

  .monitor-display {
    gap: 2rem;
    flex-direction: column;
    text-align: center;
  }

  .circle-progress {
    width: 100px;
    height: 100px;
  }

  .circle-inner {
    width: 75px;
    height: 75px;
  }

  .usage-value {
    font-size: 1rem;
  }
}
</style>
