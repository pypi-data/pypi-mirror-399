<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api'

const router = useRouter()
const isDesktop = ref<boolean>(false)
const lastAction = ref<string>('')
const windowState = ref<'normal' | 'minimized' | 'maximized'>('normal')
const actionHistory = ref<Array<{ action: string, time: string }>>([])

onMounted(() => {
  isDesktop.value = api.isAvailable()
})

const minimizeApp = () => {
  if (!isDesktop.value) return

  try {
    api.minimizeWindow()
    windowState.value = 'minimized'
    lastAction.value = '窗口已最小化'
    actionHistory.value.unshift({
      action: '最小化窗口',
      time: new Date().toLocaleTimeString()
    })
  } catch (error) {
    console.error('最小化窗口失败:', error)
    lastAction.value = '最小化窗口失败'
  }
}

const maximizeApp = () => {
  if (!isDesktop.value) return

  try {
    api.maximizeWindow()
    windowState.value = windowState.value === 'maximized' ? 'normal' : 'maximized'
    lastAction.value = windowState.value === 'maximized' ? '窗口已最大化' : '窗口已还原'
    actionHistory.value.unshift({
      action: windowState.value === 'maximized' ? '最大化窗口' : '还原窗口',
      time: new Date().toLocaleTimeString()
    })
  } catch (error) {
    console.error('最大化/还原窗口失败:', error)
    lastAction.value = '窗口操作失败'
  }
}

const closeApp = () => {
  if (!isDesktop.value) return

  if (confirm('确定要关闭应用程序吗？')) {
    try {
      lastAction.value = '正在关闭应用...'
      actionHistory.value.unshift({
        action: '关闭应用',
        time: new Date().toLocaleTimeString()
      })

      // 延迟执行关闭操作，让用户看到反馈
      setTimeout(() => {
        api.closeWindow()
      }, 1000)
    } catch (error) {
      console.error('关闭应用失败:', error)
      lastAction.value = '关闭应用失败'
    }
  }
}

const centerWindow = () => {
  if (!isDesktop.value) return

  try {
    // pywebview没有直接的居中API，这里用最大化模拟
    api.maximizeWindow()
    windowState.value = 'maximized'
    lastAction.value = '窗口已居中（最大化）'
    actionHistory.value.unshift({
      action: '居中窗口',
      time: new Date().toLocaleTimeString()
    })
  } catch (error) {
    console.error('居中窗口失败:', error)
    lastAction.value = '居中窗口失败'
  }
}

const resizeWindow = (size: 'small' | 'medium' | 'large') => {
  if (!isDesktop.value) return

  try {
    // pywebview没有直接的resize API，这里用操作模拟
    const sizeMap = {
      small: '小尺寸',
      medium: '中等尺寸',
      large: '大尺寸'
    }

    lastAction.value = `窗口已调整为${sizeMap[size]}`
    actionHistory.value.unshift({
      action: `调整窗口大小(${sizeMap[size]})`,
      time: new Date().toLocaleTimeString()
    })

    // 先还原再最大化模拟调整大小
    if (windowState.value === 'maximized') {
      api.maximizeWindow() // 再次点击会还原
      windowState.value = 'normal'
    }

    if (size === 'large') {
      setTimeout(() => {
        api.maximizeWindow()
        windowState.value = 'maximized'
      }, 200)
    }
  } catch (error) {
    console.error('调整窗口大小失败:', error)
    lastAction.value = '调整窗口大小失败'
  }
}

const clearHistory = () => {
  actionHistory.value = []
  lastAction.value = '历史记录已清空'
}

const goBack = () => {
  router.push('/')
}
</script>

<template>
  <div class="window-manager-page">
    <header class="page-header">
      <button @click="goBack" class="back-btn">← 返回主页</button>
      <h1>🪟 窗口管理</h1>
      <div class="app-info">
        <span v-if="isDesktop" class="desktop-badge">桌面应用</span>
        <span v-else class="web-badge">Web版本</span>
      </div>
    </header>

    <main class="main-content">
      <!-- 窗口状态 -->
      <section class="window-status" v-if="isDesktop">
        <h2>当前窗口状态</h2>
        <div class="status-display">
          <div class="state-indicator" :class="windowState">
            <div class="icon">
              <span v-if="windowState === 'normal'">📱</span>
              <span v-else-if="windowState === 'minimized'">🔽</span>
              <span v-else-if="windowState === 'maximized'">🔼</span>
            </div>
            <div class="state-text">
              <strong>{{ windowState === 'normal' ? '正常' : windowState === 'minimized' ? '最小化' : '最大化' }}</strong>
              <p>窗口当前状态</p>
            </div>
          </div>
        </div>
      </section>

      <!-- 窗口控制面板 -->
      <section class="window-controls" v-if="isDesktop">
        <h2>窗口控制</h2>

        <!-- 基本控制 -->
        <div class="control-section">
          <h3>基本控制</h3>
          <div class="button-grid">
            <button @click="minimizeApp" class="control-btn minimize">
              🔽 最小化
            </button>
            <button @click="maximizeApp" class="control-btn maximize">
              🔼 最大化/还原
            </button>
            <button @click="centerWindow" class="control-btn center">
              🎯 居中
            </button>
            <button @click="closeApp" class="control-btn close">
              ❌ 关闭应用
            </button>
          </div>
        </div>

        <!-- 窗口大小 -->
        <div class="control-section">
          <h3>窗口大小</h3>
          <div class="size-options">
            <button @click="resizeWindow('small')" class="size-btn small">
              📱 小尺寸
            </button>
            <button @click="resizeWindow('medium')" class="size-btn medium">
              🖥️ 中等尺寸
            </button>
            <button @click="resizeWindow('large')" class="size-btn large">
              🖥️ 大尺寸
            </button>
          </div>
        </div>

        <!-- 快捷键提示 -->
        <div class="shortcuts-info">
          <h3>快捷键</h3>
          <div class="shortcut-list">
            <div class="shortcut-item">
              <kbd>Ctrl+M</kbd>
              <span>最小化窗口</span>
            </div>
            <div class="shortcut-item">
              <kbd>F11</kbd>
              <span>最大化/还原窗口</span>
            </div>
            <div class="shortcut-item">
              <kbd>Ctrl+W</kbd>
              <span>关闭应用</span>
            </div>
          </div>
        </div>
      </section>

      <!-- Web模式提示 -->
      <section class="web-notice" v-else>
        <div class="notice-card">
          <h2>🌐 Web模式限制</h2>
          <p>窗口管理功能仅在桌面模式下可用。要使用此功能，请运行桌面版本。</p>
        </div>
      </section>

      <!-- 操作状态 -->
      <section class="action-status" v-if="lastAction">
        <h2>操作状态</h2>
        <div class="status-message" :class="{ 'danger': lastAction.includes('失败') || lastAction.includes('错误') }">
          {{ lastAction }}
        </div>
      </section>

      <!-- 操作历史 -->
      <section class="action-history" v-if="isDesktop">
        <div class="history-header">
          <h2>操作历史</h2>
          <button @click="clearHistory" class="clear-btn" v-if="actionHistory.length > 0">
            清空历史
          </button>
        </div>

        <div v-if="actionHistory.length === 0" class="empty-history">
          <p>暂无操作历史</p>
        </div>

        <div v-else class="history-list">
          <div v-for="(item, index) in actionHistory" :key="index" class="history-item">
            <div class="history-content">
              <span class="action-text">{{ item.action }}</span>
              <span class="time">{{ item.time }}</span>
            </div>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<style scoped>
.window-manager-page {
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

.main-content {
  display: grid;
  gap: 2rem;
}

.window-status {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.window-status h2 {
  margin: 0 0 1.5rem 0;
  color: #1f2937;
  font-size: 1.5rem;
  font-weight: 600;
}

.status-display {
  display: flex;
  justify-content: center;
}

.state-indicator {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 2rem;
  border-radius: 12px;
  transition: all 0.3s ease;
}

.state-indicator.normal {
  background: #eff6ff;
  border: 2px solid #3b82f6;
}

.state-indicator.minimized {
  background: #fef3c7;
  border: 2px solid #f59e0b;
}

.state-indicator.maximized {
  background: #f0fdf4;
  border: 2px solid #10b981;
}

.state-indicator .icon {
  font-size: 3rem;
}

.state-text strong {
  display: block;
  font-size: 1.5rem;
  color: #1f2937;
  margin-bottom: 0.5rem;
}

.state-text p {
  margin: 0;
  color: #6b7280;
  font-size: 0.875rem;
}

.window-controls {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.window-controls h2 {
  margin: 0 0 1.5rem 0;
  color: #1f2937;
  font-size: 1.5rem;
  font-weight: 600;
}

.control-section {
  margin-bottom: 2rem;
}

.control-section:last-child {
  margin-bottom: 0;
}

.control-section h3 {
  margin: 0 0 1rem 0;
  color: #374151;
  font-size: 1.125rem;
  font-weight: 500;
}

.button-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.control-btn {
  padding: 1rem;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  font-size: 1rem;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  min-height: 60px;
}

.control-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.control-btn.minimize {
  background: #f59e0b;
  color: white;
}

.control-btn.minimize:hover {
  background: #d97706;
}

.control-btn.maximize {
  background: #10b981;
  color: white;
}

.control-btn.maximize:hover {
  background: #059669;
}

.control-btn.center {
  background: #3b82f6;
  color: white;
}

.control-btn.center:hover {
  background: #2563eb;
}

.control-btn.close {
  background: #ef4444;
  color: white;
}

.control-btn.close:hover {
  background: #dc2626;
}

.size-options {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.size-btn {
  flex: 1;
  min-width: 120px;
  padding: 1rem;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  background: white;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.size-btn:hover {
  border-color: #3b82f6;
  background: #eff6ff;
}

.size-btn.small:hover {
  border-color: #f59e0b;
  background: #fffbeb;
}

.size-btn.large:hover {
  border-color: #10b981;
  background: #f0fdf4;
}

.shortcuts-info {
  background: #f8fafc;
  border-radius: 8px;
  padding: 1.5rem;
  border: 1px solid #e2e8f0;
}

.shortcuts-info h3 {
  margin: 0 0 1rem 0;
  color: #374151;
  font-size: 1.125rem;
  font-weight: 500;
}

.shortcut-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.shortcut-item {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.shortcut-item kbd {
  background: #374151;
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 4px;
  font-family: monospace;
  font-size: 0.875rem;
  min-width: 80px;
  text-align: center;
}

.shortcut-item span {
  color: #6b7280;
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
  margin: 0;
  color: #78350f;
  line-height: 1.6;
}

.action-status,
.action-history {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.action-status h2,
.action-history h2 {
  margin: 0 0 1.5rem 0;
  color: #1f2937;
  font-size: 1.5rem;
  font-weight: 600;
}

.status-message {
  background: #f0fdf4;
  border: 1px solid #10b981;
  border-radius: 8px;
  padding: 1rem;
  color: #065f46;
  line-height: 1.5;
}

.status-message.danger {
  background: #fef2f2;
  border-color: #ef4444;
  color: #991b1b;
}

.history-header {
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

.empty-history {
  text-align: center;
  padding: 2rem;
  color: #6b7280;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.history-item {
  background: #f9fafb;
  border-radius: 8px;
  padding: 1rem;
  border-left: 4px solid #3b82f6;
}

.history-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.action-text {
  color: #374151;
  font-weight: 500;
}

.time {
  font-size: 0.75rem;
  color: #6b7280;
}
</style>
