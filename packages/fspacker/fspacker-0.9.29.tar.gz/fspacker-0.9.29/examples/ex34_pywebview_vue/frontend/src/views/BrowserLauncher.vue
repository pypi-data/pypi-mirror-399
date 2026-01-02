<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api'

const router = useRouter()
const isDesktop = ref<boolean>(false)
const customUrl = ref<string>('')
const lastOpenedUrl = ref<string>('')
const urlHistory = ref<Array<{ url: string, time: string }>>([])

const quickLinks = [
  { name: 'GitHub', url: 'https://github.com', icon: '🐙' },
  { name: 'Google', url: 'https://www.google.com', icon: '🔍' },
  { name: 'Stack Overflow', url: 'https://stackoverflow.com', icon: '📚' },
  { name: 'MDN Web Docs', url: 'https://developer.mozilla.org', icon: '📖' },
  { name: 'Vue.js', url: 'https://vuejs.org', icon: '💚' },
  { name: 'Python', url: 'https://www.python.org', icon: '🐍' },
  { name: 'YouTube', url: 'https://www.youtube.com', icon: '📺' },
  { name: 'Twitter', url: 'https://twitter.com', icon: '🐦' }
]

onMounted(() => {
  isDesktop.value = api.isAvailable()
})

const openUrl = async (url: string) => {
  if (!isDesktop.value) {
    // Web模式下直接在新窗口打开
    window.open(url, '_blank')
    addToHistory(url)
    return
  }

  try {
    const success = await api.openUrl(url)
    if (success) {
      lastOpenedUrl.value = url
      addToHistory(url)
      await api.showNotification('浏览器', `已打开: ${url}`)
    }
  } catch (error) {
    console.error('打开URL失败:', error)
  }
}

const openCustomUrl = () => {
  if (customUrl.value) {
    // 验证URL格式
    let url = customUrl.value.trim()
    if (!url.startsWith('http://') && !url.startsWith('https://')) {
      url = 'https://' + url
    }

    openUrl(url)
    customUrl.value = ''
  }
}

const addToHistory = (url: string) => {
  urlHistory.value.unshift({
    url,
    time: new Date().toLocaleTimeString()
  })

  if (urlHistory.value.length > 10) {
    urlHistory.value.pop()
  }
}

const clearHistory = () => {
  urlHistory.value = []
}

const getUrlIcon = (url: string): string => {
  const domain = url.replace(/^https?:\/\//, '').split('/')[0].toLowerCase()

  if (domain.includes('github')) return '🐙'
  if (domain.includes('google')) return '🔍'
  if (domain.includes('stackoverflow')) return '📚'
  if (domain.includes('developer.mozilla')) return '📖'
  if (domain.includes('vuejs')) return '💚'
  if (domain.includes('python')) return '🐍'
  if (domain.includes('youtube')) return '📺'
  if (domain.includes('twitter')) return '🐦'
  if (domain.includes('linkedin')) return '💼'
  if (domain.includes('facebook')) return '📘'
  if (domain.includes('instagram')) return '📷'

  return '🌐'
}

const goBack = () => {
  router.push('/')
}
</script>

<template>
  <div class="browser-launcher-page">
    <header class="page-header">
      <button @click="goBack" class="back-btn">← 返回主页</button>
      <h1>🌐 浏览器启动</h1>
      <div class="app-info">
        <span v-if="isDesktop" class="desktop-badge">桌面应用</span>
        <span v-else class="web-badge">Web版本</span>
      </div>
    </header>

    <main class="main-content">
      <!-- 自定义URL输入 -->
      <section class="custom-url">
        <h2>🌍 打开网址</h2>
        <div class="url-input-container">
          <input v-model="customUrl" type="text" placeholder="输入网址 (例如: google.com)" class="url-input"
            @keyup.enter="openCustomUrl" />
          <button @click="openCustomUrl" :disabled="!customUrl" class="open-btn">
            🚀 打开
          </button>
        </div>
        <p class="url-hint">提示: 可以直接输入域名，系统会自动添加 https://</p>
      </section>

      <!-- 快速链接 -->
      <section class="quick-links">
        <h2>⚡ 快速链接</h2>
        <div class="links-grid">
          <div v-for="link in quickLinks" :key="link.url" class="link-card" @click="openUrl(link.url)">
            <div class="link-icon">{{ link.icon }}</div>
            <h3>{{ link.name }}</h3>
            <p>{{ link.url }}</p>
          </div>
        </div>
      </section>

      <!-- 最近打开 -->
      <section class="recent-urls" v-if="urlHistory.length > 0">
        <div class="section-header">
          <h2>🕐 最近打开</h2>
          <button @click="clearHistory" class="clear-btn">
            清空历史
          </button>
        </div>
        <div class="history-list">
          <div v-for="(item, index) in urlHistory" :key="index" class="history-item" @click="openUrl(item.url)">
            <div class="history-icon">{{ getUrlIcon(item.url) }}</div>
            <div class="history-info">
              <div class="history-url">{{ item.url }}</div>
              <div class="history-time">{{ item.time }}</div>
            </div>
            <button @click.stop="openUrl(item.url)" class="reopen-btn">
              再次打开
            </button>
          </div>
        </div>
      </section>

      <!-- 最后打开状态 -->
      <section class="last-opened" v-if="lastOpenedUrl">
        <h2>📍 最后打开</h2>
        <div class="last-url-card">
          <div class="last-url-icon">{{ getUrlIcon(lastOpenedUrl) }}</div>
          <div class="last-url-info">
            <div class="last-url">{{ lastOpenedUrl }}</div>
            <button @click="openUrl(lastOpenedUrl)" class="reopen-last-btn">
              🔄 再次打开
            </button>
          </div>
        </div>
      </section>

      <!-- 使用说明 -->
      <section class="usage-info">
        <h2>ℹ️ 使用说明</h2>
        <div class="info-content">
          <div class="info-item">
            <strong>桌面模式:</strong> 使用系统默认浏览器打开链接
          </div>
          <div class="info-item">
            <strong>Web模式:</strong> 在新标签页中打开链接
          </div>
          <div class="info-item">
            <strong>快捷键:</strong> Ctrl+G 可以快速打开GitHub
          </div>
          <div class="info-item">
            <strong>URL格式:</strong> 支持完整URL或简写域名
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<style scoped>
.browser-launcher-page {
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

.custom-url,
.quick-links,
.recent-urls,
.last-opened,
.usage-info {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.custom-url h2,
.quick-links h2,
.recent-urls h2,
.last-opened h2,
.usage-info h2 {
  margin: 0 0 1.5rem 0;
  color: #1f2937;
  font-size: 1.5rem;
  font-weight: 600;
}

.url-input-container {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.url-input {
  flex: 1;
  min-width: 200px;
  padding: 0.75rem 1rem;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.2s;
}

.url-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.open-btn {
  padding: 0.75rem 1.5rem;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
  white-space: nowrap;
}

.open-btn:hover:not(:disabled) {
  background: #2563eb;
  transform: translateY(-1px);
}

.open-btn:disabled {
  background: #9ca3af;
  cursor: not-allowed;
}

.url-hint {
  color: #6b7280;
  font-size: 0.875rem;
  margin: 0;
}

.links-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.link-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 1.5rem;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.link-card:hover {
  border-color: #3b82f6;
  background: #eff6ff;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.link-icon {
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

.link-card h3 {
  margin: 0 0 0.5rem 0;
  color: #1f2937;
  font-size: 1.125rem;
  font-weight: 600;
}

.link-card p {
  margin: 0;
  color: #6b7280;
  font-size: 0.875rem;
  word-break: break-all;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.clear-btn {
  background: #ef4444;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
  transition: background-color 0.2s;
}

.clear-btn:hover {
  background: #dc2626;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.history-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: #f8fafc;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  border-left: 4px solid #3b82f6;
}

.history-item:hover {
  background: #f1f5f9;
  border-left-color: #2563eb;
}

.history-icon {
  font-size: 1.5rem;
  flex-shrink: 0;
}

.history-info {
  flex: 1;
}

.history-url {
  font-weight: 500;
  color: #1f2937;
  margin-bottom: 0.25rem;
  word-break: break-all;
}

.history-time {
  font-size: 0.75rem;
  color: #6b7280;
}

.reopen-btn {
  background: #10b981;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
  transition: background-color 0.2s;
}

.reopen-btn:hover {
  background: #059669;
}

.last-url-card {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  padding: 1.5rem;
  background: #eff6ff;
  border: 2px solid #3b82f6;
  border-radius: 12px;
}

.last-url-icon {
  font-size: 2rem;
  flex-shrink: 0;
}

.last-url-info {
  flex: 1;
}

.last-url {
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 1rem;
  word-break: break-all;
}

.reopen-last-btn {
  background: #3b82f6;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
}

.reopen-last-btn:hover {
  background: #2563eb;
}

.info-content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.info-item {
  padding: 1rem;
  background: #f8fafc;
  border-radius: 8px;
  border-left: 4px solid #6b7280;
  color: #374151;
  line-height: 1.5;
}

.info-item strong {
  color: #1f2937;
}

@media (max-width: 768px) {
  .browser-launcher-page {
    padding: 1rem;
  }

  .url-input-container {
    flex-direction: column;
  }

  .links-grid {
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  }

  .last-url-card {
    flex-direction: column;
    text-align: center;
  }
}
</style>
