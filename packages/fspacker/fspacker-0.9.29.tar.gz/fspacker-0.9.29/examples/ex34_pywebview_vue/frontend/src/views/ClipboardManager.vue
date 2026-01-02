<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api'

const router = useRouter()
const isDesktop = ref<boolean>(false)
const clipboardText = ref<string>('')
const customText = ref<string>('')
const clipboardHistory = ref<Array<{content: string, time: string, action: string}>>([])
const isAutoRefresh = ref<boolean>(false)
const refreshInterval = ref<number | null>(null)

onMounted(() => {
  isDesktop.value = api.isAvailable()
  if (isDesktop.value) {
    refreshClipboard()
  }
})

const refreshClipboard = async () => {
  if (!isDesktop.value) return

  try {
    const text = await api.getClipboardText()
    if (text !== clipboardText.value) {
      clipboardHistory.value.unshift({
        content: text,
        time: new Date().toLocaleTimeString(),
        action: '获取'
      })
      if (clipboardHistory.value.length > 20) {
        clipboardHistory.value.pop()
      }
    }
    clipboardText.value = text
  } catch (error) {
    console.error('获取剪贴板失败:', error)
  }
}

const copyToClipboard = async (text: string) => {
  if (!isDesktop.value) return

  try {
    const success = await api.setClipboardText(text)
    if (success) {
      clipboardHistory.value.unshift({
        content: text,
        time: new Date().toLocaleTimeString(),
        action: '设置'
      })
      if (clipboardHistory.value.length > 20) {
        clipboardHistory.value.pop()
      }

      await api.showNotification('剪贴板', '文本已复制到剪贴板')
      refreshClipboard()
    }
  } catch (error) {
    console.error('复制到剪贴板失败:', error)
  }
}

const copyCurrentText = () => {
  if (clipboardText.value) {
    copyToClipboard(clipboardText.value)
  }
}

const copyCustomText = () => {
  if (customText.value) {
    copyToClipboard(customText.value)
    customText.value = ''
  }
}

const clearClipboard = async () => {
  if (!isDesktop.value) return

  try {
    const success = await api.setClipboardText('')
    if (success) {
      clipboardHistory.value.unshift({
        content: '(已清空)',
        time: new Date().toLocaleTimeString(),
        action: '清空'
      })
      clipboardText.value = ''
      await api.showNotification('剪贴板', '剪贴板已清空')
    }
  } catch (error) {
    console.error('清空剪贴板失败:', error)
  }
}

const toggleAutoRefresh = () => {
  isAutoRefresh.value = !isAutoRefresh.value

  if (isAutoRefresh.value) {
    refreshInterval.value = setInterval(refreshClipboard, 1000) // 每秒刷新一次
  } else {
    if (refreshInterval.value) {
      clearInterval(refreshInterval.value)
      refreshInterval.value = null
    }
  }
}

const copyFromHistory = (item: {content: string, time: string, action: string}) => {
  if (item.content && item.content !== '(已清空)') {
    copyToClipboard(item.content)
  }
}

const clearHistory = () => {
  clipboardHistory.value = []
}

const goBack = () => {
  router.push('/')
}
</script>

<template>
  <div class="clipboard-manager-page">
    <header class="page-header">
      <button @click="goBack" class="back-btn">← 返回主页</button>
      <h1>📋 剪贴板管理</h1>
      <div class="app-info">
        <span v-if="isDesktop" class="desktop-badge">桌面应用</span>
        <span v-else class="web-badge">Web版本</span>
      </div>
    </header>

    <main class="main-content" v-if="isDesktop">
      <!-- 控制面板 -->
      <section class="control-panel">
        <h2>剪贴板控制</h2>
        <div class="controls">
          <button @click="refreshClipboard" class="refresh-btn">
            🔄 刷新
          </button>
          <button @click="toggleAutoRefresh" :class="['auto-refresh-btn', { active: isAutoRefresh }]">
            ⏱️ {{ isAutoRefresh ? '停止自动刷新' : '开始自动刷新' }}
          </button>
          <button @click="clearClipboard" class="clear-btn">
            🗑️ 清空剪贴板
          </button>
        </div>
      </section>

      <!-- 当前剪贴板内容 -->
      <section class="current-clipboard">
        <h2>当前剪贴板内容</h2>
        <div class="clipboard-content">
          <textarea
            v-model="clipboardText"
            readonly
            class="clipboard-textarea"
            placeholder="剪贴板为空"
            rows="8"
          ></textarea>
          <div class="clipboard-actions">
            <button @click="copyCurrentText" :disabled="!clipboardText" class="copy-btn">
              📋 复制内容
            </button>
            <button @click="refreshClipboard" class="refresh-small-btn">
              🔄 刷新
            </button>
          </div>
        </div>
        <div class="content-info">
          <span class="char-count">{{ clipboardText.length }} 字符</span>
          <span class="line-count">{{ clipboardText.split('\n').length }} 行</span>
        </div>
      </section>

      <!-- 自定义文本 -->
      <section class="custom-text">
        <h2>自定义文本</h2>
        <div class="custom-content">
          <textarea
            v-model="customText"
            class="custom-textarea"
            placeholder="输入要复制到剪贴板的文本..."
            rows="4"
          ></textarea>
          <div class="custom-actions">
            <button @click="copyCustomText" :disabled="!customText" class="copy-btn">
              📋 复制到剪贴板
            </button>
            <button @click="customText = ''" class="clear-custom-btn">
              清空输入
            </button>
          </div>
        </div>
      </section>

      <!-- 快速文本 -->
      <section class="quick-texts">
        <h2>快速文本</h2>
        <div class="quick-grid">
          <button @click="copyToClipboard('Hello World')" class="quick-btn">
            Hello World
          </button>
          <button @click="copyToClipboard('https://github.com')" class="quick-btn">
            GitHub链接
          </button>
          <button @click="copyToClipboard(new Date().toISOString())" class="quick-btn">
            当前时间
          </button>
          <button @click="copyToClipboard('🚀 Awesome!')" class="quick-btn">
            表情符号
          </button>
        </div>
      </section>

      <!-- 剪贴板历史 -->
      <section class="clipboard-history">
        <div class="history-header">
          <h2>操作历史</h2>
          <button @click="clearHistory" class="clear-history-btn" v-if="clipboardHistory.length > 0">
            清空历史
          </button>
        </div>

        <div v-if="clipboardHistory.length === 0" class="empty-history">
          <p>暂无操作历史</p>
        </div>

        <div v-else class="history-list">
          <div
            v-for="(item, index) in clipboardHistory"
            :key="index"
            class="history-item"
            @click="copyFromHistory(item)"
          >
            <div class="history-header">
              <span class="action-badge" :class="item.action.toLowerCase()">
                {{ item.action }}
              </span>
              <span class="time">{{ item.time }}</span>
            </div>
            <div class="history-content">
              <div class="content-preview">
                {{ item.content.substring(0, 100) }}
                <span v-if="item.content.length > 100">...</span>
              </div>
              <div class="content-meta">
                <span class="char-count">{{ item.content.length }} 字符</span>
              </div>
            </div>
          </div>
        </div>
      </section>
    </main>

    <!-- Web模式提示 -->
    <div v-else class="web-notice">
      <div class="notice-card">
        <h2>🌐 Web模式限制</h2>
        <p>剪贴板管理功能仅在桌面模式下可用。要使用此功能，请运行桌面版本。</p>
        <pre><code>python start.py</code></pre>
      </div>
    </div>
  </div>
</template>

<style scoped>
.clipboard-manager-page {
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

.control-panel,
.current-clipboard,
.custom-text,
.quick-texts,
.clipboard-history {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.control-panel h2,
.current-clipboard h2,
.custom-text h2,
.quick-texts h2,
.clipboard-history h2 {
  margin: 0 0 1.5rem 0;
  color: #1f2937;
  font-size: 1.5rem;
  font-weight: 600;
}

.controls {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.refresh-btn,
.auto-refresh-btn,
.clear-btn,
.copy-btn,
.clear-custom-btn,
.clear-history-btn {
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

.refresh-btn:hover {
  background: #059669;
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

.clear-btn,
.clear-custom-btn,
.clear-history-btn {
  background: #ef4444;
  color: white;
}

.clear-btn:hover,
.clear-custom-btn:hover,
.clear-history-btn:hover {
  background: #dc2626;
}

.copy-btn {
  background: #3b82f6;
  color: white;
}

.copy-btn:hover:not(:disabled) {
  background: #2563eb;
}

.copy-btn:disabled {
  background: #9ca3af;
  cursor: not-allowed;
}

.clipboard-content,
.custom-content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.clipboard-textarea,
.custom-textarea {
  width: 100%;
  padding: 1rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 0.875rem;
  resize: vertical;
  background: #f8fafc;
}

.clipboard-textarea:focus,
.custom-textarea:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.clipboard-textarea {
  background: #f8fafc;
  color: #374151;
}

.custom-textarea {
  background: white;
  color: #1f2937;
}

.clipboard-actions,
.custom-actions {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.refresh-small-btn {
  padding: 0.5rem 1rem;
  background: #6b7280;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
  transition: background-color 0.2s;
}

.refresh-small-btn:hover {
  background: #4b5563;
}

.content-info {
  display: flex;
  gap: 2rem;
  color: #6b7280;
  font-size: 0.875rem;
}

.char-count,
.line-count {
  padding: 0.25rem 0.75rem;
  background: #f3f4f6;
  border-radius: 4px;
}

.quick-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.quick-btn {
  padding: 1rem;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  background: white;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
}

.quick-btn:hover {
  border-color: #3b82f6;
  background: #eff6ff;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.empty-history {
  text-align: center;
  padding: 2rem;
  color: #6b7280;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.history-item {
  background: #f8fafc;
  border-radius: 8px;
  padding: 1rem;
  cursor: pointer;
  transition: all 0.2s;
  border-left: 4px solid #3b82f6;
}

.history-item:hover {
  background: #f1f5f9;
  border-left-color: #2563eb;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.action-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.action-badge.获取 {
  background: #dbeafe;
  color: #1e40af;
}

.action-badge.设置 {
  background: #d1fae5;
  color: #065f46;
}

.action-badge.清空 {
  background: #fef2f2;
  color: #991b1b;
}

.time {
  font-size: 0.75rem;
  color: #6b7280;
}

.history-content {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.content-preview {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 0.875rem;
  color: #374151;
  line-height: 1.4;
  word-break: break-word;
}

.content-meta {
  display: flex;
  justify-content: flex-end;
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

@media (max-width: 768px) {
  .clipboard-manager-page {
    padding: 1rem;
  }

  .controls {
    flex-direction: column;
  }

  .quick-grid {
    grid-template-columns: 1fr;
  }

  .content-info {
    flex-direction: column;
    gap: 0.5rem;
  }
}
</style>
