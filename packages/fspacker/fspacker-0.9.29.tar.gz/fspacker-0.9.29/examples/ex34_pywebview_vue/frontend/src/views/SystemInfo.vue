<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api'

const router = useRouter()
const isDesktop = ref<boolean>(false)
const systemInfo = ref<Record<string, any>>({})
const appVersion = ref<string>('')
const webInfo = ref<Record<string, any>>({})
const isLoading = ref<boolean>(false)

onMounted(async () => {
  isLoading.value = true
  isDesktop.value = api.isAvailable()

  try {
    systemInfo.value = await api.getSystemInfo()
    appVersion.value = await api.getAppVersion()
  } catch (error) {
    console.error('获取系统信息失败:', error)
    systemInfo.value = {
      platform: '未知',
      architecture: '未知',
      version: '未知',
      python_version: '未知',
      machine: '未知'
    }
    appVersion.value = '1.0.0'
  }

  if (!isDesktop.value) {
    systemInfo.value = {
      platform: navigator.platform || 'Web浏览器',
      architecture: 'Web',
      version: navigator.userAgent || '未知',
      python_version: '不适用',
      machine: 'Web设备'
    }
  }

  // Web浏览器信息
  webInfo.value = {
    userAgent: typeof navigator !== 'undefined' ? navigator.userAgent.split(' ')[0] : 'Unknown',
    language: typeof navigator !== 'undefined' ? navigator.language : 'Unknown',
    onLine: typeof navigator !== 'undefined' ? navigator.onLine : false,
    cookieEnabled: typeof navigator !== 'undefined' ? navigator.cookieEnabled : false,
    screenResolution: typeof screen !== 'undefined' ? `${screen.width}x${screen.height}` : 'Unknown'
  }

  isLoading.value = false
})

const refreshInfo = async () => {
  isLoading.value = true

  try {
    if (isDesktop.value) {
      systemInfo.value = await api.getSystemInfo()
      appVersion.value = await api.getAppVersion()
    }
  } catch (error) {
    console.error('刷新系统信息失败:', error)
  }

  isLoading.value = false
}

const getSystemInfoLabel = (key: string): string => {
  const labels: Record<string, string> = {
    platform: '平台',
    architecture: '架构',
    version: '版本',
    python_version: 'Python版本',
    machine: '机器类型'
  }
  return labels[key] || key
}

const getWebInfoLabel = (key: string): string => {
  const labels: Record<string, string> = {
    userAgent: '用户代理',
    language: '语言',
    onLine: '在线状态',
    cookieEnabled: 'Cookie启用',
    screenResolution: '屏幕分辨率'
  }
  return labels[key] || key
}

const copyInfo = (info: Record<string, any>) => {
  const text = Object.entries(info)
    .map(([key, value]) => `${getSystemInfoLabel(key) || key}: ${value}`)
    .join('\n')

  if (navigator.clipboard) {
    navigator.clipboard.writeText(text)
  }
}

const goBack = () => {
  router.push('/')
}
</script>

<template>
  <div class="system-info-page">
    <header class="page-header">
      <button @click="goBack" class="back-btn">← 返回主页</button>
      <h1>🖥️ 系统信息</h1>
      <div class="app-info">
        <span v-if="isDesktop" class="desktop-badge">桌面应用</span>
        <span v-else class="web-badge">Web版本</span>
      </div>
    </header>

    <main class="main-content" v-if="!isLoading">
      <!-- 刷新按钮 -->
      <div class="refresh-section">
        <button @click="refreshInfo" class="refresh-btn">
          🔄 刷新信息
        </button>
      </div>

      <!-- 桌面应用信息 -->
      <section class="info-section" v-if="isDesktop">
        <div class="section-header">
          <h2>💻 桌面应用信息</h2>
          <button @click="copyInfo(systemInfo)" class="copy-btn">
            📋 复制
          </button>
        </div>

        <div class="info-grid">
          <div v-for="(value, key) in systemInfo" :key="key" class="info-item">
            <div class="info-label">{{ getSystemInfoLabel(key) }}</div>
            <div class="info-value">{{ value }}</div>
          </div>
        </div>

        <div class="info-item app-version">
          <div class="info-label">应用版本</div>
          <div class="info-value">{{ appVersion }}</div>
        </div>
      </section>

      <!-- Web浏览器信息 -->
      <section class="info-section">
        <div class="section-header">
          <h2>🌐 浏览器信息</h2>
          <button @click="copyInfo(webInfo)" class="copy-btn">
            📋 复制
          </button>
        </div>

        <div class="info-grid">
          <div v-for="(value, key) in webInfo" :key="key" class="info-item">
            <div class="info-label">{{ getWebInfoLabel(key) }}</div>
            <div class="info-value">
              <span v-if="typeof value === 'boolean'">
                {{ value ? '是' : '否' }}
              </span>
              <span v-else>{{ value }}</span>
            </div>
          </div>
        </div>
      </section>

      <!-- 应用版本信息 -->
      <section class="info-section">
        <div class="section-header">
          <h2>🚀 应用版本</h2>
        </div>

        <div class="version-info">
          <div class="version-display">
            <span class="version-number">{{ appVersion || '1.0.0' }}</span>
            <span class="version-type">{{ isDesktop ? '桌面版' : 'Web版' }}</span>
          </div>
        </div>
      </section>

      <!-- 技术栈信息 -->
      <section class="info-section">
        <div class="section-header">
          <h2>⚙️ 技术栈</h2>
        </div>

        <div class="tech-stack">
          <div class="tech-item">
            <strong>前端:</strong> Vue 3 + TypeScript + Vite
          </div>
          <div class="tech-item">
            <strong>后端:</strong> Python + PyWebView
          </div>
          <div class="tech-item">
            <strong>构建工具:</strong> Vite
          </div>
          <div class="tech-item">
            <strong>包管理:</strong> npm/pnpm
          </div>
        </div>
      </section>
    </main>

    <!-- 加载状态 -->
    <div v-else class="loading">
      <div class="loading-spinner"></div>
      <p>正在加载系统信息...</p>
    </div>
  </div>
</template>

<style scoped>
.system-info-page {
  padding: 2rem;
  max-width: 1000px;
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

.refresh-section {
  margin-bottom: 2rem;
  text-align: center;
}

.refresh-btn {
  background: #10b981;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 500;
  transition: all 0.2s;
}

.refresh-btn:hover {
  background: #059669;
  transform: translateY(-1px);
}

.main-content {
  display: grid;
  gap: 2rem;
}

.info-section {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.section-header h2 {
  margin: 0;
  color: #1f2937;
  font-size: 1.5rem;
  font-weight: 600;
}

.copy-btn {
  background: #6b7280;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
  transition: background-color 0.2s;
}

.copy-btn:hover {
  background: #4b5563;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 1rem;
  background: #f8fafc;
  border-radius: 8px;
  border-left: 4px solid #3b82f6;
}

.info-item.app-version {
  grid-column: span 2;
  border-left-color: #10b981;
  background: #f0fdf4;
}

.info-label {
  font-weight: 600;
  color: #374151;
  font-size: 0.875rem;
}

.info-value {
  color: #1f2937;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 0.875rem;
  word-break: break-all;
}

.version-info {
  display: flex;
  justify-content: center;
  padding: 2rem;
}

.version-display {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.version-number {
  font-size: 3rem;
  font-weight: bold;
  color: #3b82f6;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
}

.version-type {
  padding: 0.5rem 1rem;
  background: #eff6ff;
  color: #3b82f6;
  border-radius: 9999px;
  font-weight: 600;
  font-size: 0.875rem;
}

.tech-stack {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.tech-item {
  padding: 1rem;
  background: #f8fafc;
  border-radius: 8px;
  border-left: 4px solid #6b7280;
  color: #374151;
}

.tech-item strong {
  color: #1f2937;
  font-weight: 600;
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  gap: 1rem;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e5e7eb;
  border-top: 4px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }

  100% {
    transform: rotate(360deg);
  }
}

.loading p {
  color: #6b7280;
  font-size: 1rem;
}

@media (max-width: 768px) {
  .system-info-page {
    padding: 1rem;
  }

  .info-grid {
    grid-template-columns: 1fr;
  }

  .version-number {
    font-size: 2rem;
  }
}
</style>
