<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api'

const router = useRouter()
const isDesktop = ref<boolean>(false)
const lastAction = ref<string>('')
const selectedFile = ref<string>('')
const saveFileName = ref<string>('demo.txt')
const fileHistory = ref<Array<{ action: string, path: string, time: string }>>([])

onMounted(() => {
  isDesktop.value = api.isAvailable()
})

const openFile = async () => {
  if (!isDesktop.value) return

  try {
    const filePath = await api.openFileDialog({
      '所有文件': ['*'],
      '文本文件': ['txt', 'md'],
      '图片文件': ['jpg', 'png', 'gif', 'bmp'],
      '文档文件': ['doc', 'docx', 'pdf'],
      '代码文件': ['js', 'ts', 'vue', 'py', 'html', 'css']
    })

    if (filePath) {
      selectedFile.value = filePath
      lastAction.value = `已选择文件: ${filePath}`
      fileHistory.value.unshift({
        action: '打开',
        path: filePath,
        time: new Date().toLocaleTimeString()
      })

      // 显示通知
      await api.showNotification('文件选择', `已选择文件: ${filePath}`)
    }
  } catch (error) {
    console.error('打开文件对话框失败:', error)
    lastAction.value = '打开文件失败'
  }
}

const saveFile = async () => {
  if (!isDesktop.value) return

  try {
    const filePath = await api.saveFileDialog(saveFileName.value, {
      '文本文件': ['txt'],
      'Markdown文件': ['md'],
      'JSON文件': ['json'],
      'CSV文件': ['csv']
    })

    if (filePath) {
      lastAction.value = `文件已保存到: ${filePath}`
      fileHistory.value.unshift({
        action: '保存',
        path: filePath,
        time: new Date().toLocaleTimeString()
      })

      // 显示通知
      await api.showNotification('文件保存', `文件已保存到: ${filePath}`)
    }
  } catch (error) {
    console.error('保存文件对话框失败:', error)
    lastAction.value = '保存文件失败'
  }
}

const saveAsFile = async () => {
  if (!isDesktop.value) return

  try {
    const filePath = await api.saveFileDialog('', {
      '所有文件': ['*'],
      '文本文件': ['txt'],
      'Markdown文件': ['md'],
      '配置文件': ['ini', 'conf', 'cfg'],
      '数据文件': ['json', 'xml', 'csv']
    })

    if (filePath) {
      lastAction.value = `文件另存为: ${filePath}`
      fileHistory.value.unshift({
        action: '另存为',
        path: filePath,
        time: new Date().toLocaleTimeString()
      })

      await api.showNotification('文件另存为', `文件已保存到: ${filePath}`)
    }
  } catch (error) {
    console.error('另存为文件对话框失败:', error)
    lastAction.value = '另存为文件失败'
  }
}

const openDirectory = async () => {
  if (!isDesktop.value) return

  try {
    // 注意：pywebview的openFileDialog不支持选择目录
    // 这里我们使用文件选择器来模拟目录选择
    const dirPath = await api.openFileDialog({
      '配置文件': ['conf', 'ini'],
      '数据文件': ['json', 'csv']
    })

    if (dirPath) {
      const directory = dirPath.substring(0, dirPath.lastIndexOf('\\') || dirPath.lastIndexOf('/') + 1)
      selectedFile.value = directory
      lastAction.value = `已选择目录: ${directory}`
      fileHistory.value.unshift({
        action: '打开目录',
        path: directory,
        time: new Date().toLocaleTimeString()
      })

      await api.showNotification('目录选择', `已选择目录: ${directory}`)
    }
  } catch (error) {
    console.error('打开目录失败:', error)
    lastAction.value = '打开目录失败'
  }
}

const clearHistory = () => {
  fileHistory.value = []
  lastAction.value = '历史记录已清空'
}

const goBack = () => {
  router.push('/')
}
</script>

<template>
  <div class="file-manager-page">
    <header class="page-header">
      <button @click="goBack" class="back-btn">← 返回主页</button>
      <h1>📁 文件管理</h1>
      <div class="app-info">
        <span v-if="isDesktop" class="desktop-badge">桌面应用</span>
        <span v-else class="web-badge">Web版本</span>
      </div>
    </header>

    <main class="main-content">
      <!-- 文件操作面板 -->
      <section class="file-operations" v-if="isDesktop">
        <h2>文件操作</h2>

        <!-- 基本操作 -->
        <div class="operation-section">
          <h3>基本操作</h3>
          <div class="button-grid">
            <button @click="openFile" class="operation-btn primary">
              📂 打开文件
            </button>
            <button @click="saveFile" class="operation-btn success">
              💾 保存文件
            </button>
            <button @click="saveAsFile" class="operation-btn info">
              📄 另存为
            </button>
            <button @click="openDirectory" class="operation-btn secondary">
              📁 选择目录
            </button>
          </div>
        </div>

        <!-- 保存设置 -->
        <div class="save-settings">
          <h3>保存设置</h3>
          <div class="form-group">
            <label for="save-file-name">默认文件名:</label>
            <input id="save-file-name" v-model="saveFileName" type="text" placeholder="输入默认保存文件名" />
          </div>
        </div>
      </section>

      <!-- Web模式提示 -->
      <section class="web-notice" v-else>
        <div class="notice-card">
          <h2>🌐 Web模式限制</h2>
          <p>文件操作功能仅在桌面模式下可用。要使用此功能，请运行桌面版本。</p>
        </div>
      </section>

      <!-- 当前选择状态 -->
      <section class="current-selection" v-if="isDesktop">
        <h2>当前选择</h2>
        <div class="selection-info">
          <div class="selection-item" v-if="selectedFile">
            <strong>选中文件:</strong>
            <span class="file-path">{{ selectedFile }}</span>
          </div>
          <div class="selection-item" v-else>
            <em>尚未选择任何文件</em>
          </div>
        </div>
      </section>

      <!-- 操作状态 -->
      <section class="action-status" v-if="lastAction">
        <h2>操作状态</h2>
        <div class="status-message">
          {{ lastAction }}
        </div>
      </section>

      <!-- 操作历史 -->
      <section class="file-history" v-if="isDesktop">
        <div class="history-header">
          <h2>操作历史</h2>
          <button @click="clearHistory" class="clear-btn" v-if="fileHistory.length > 0">
            清空历史
          </button>
        </div>

        <div v-if="fileHistory.length === 0" class="empty-history">
          <p>暂无操作历史</p>
        </div>

        <div v-else class="history-list">
          <div v-for="(item, index) in fileHistory" :key="index" class="history-item">
            <div class="history-header">
              <span class="action-badge" :class="item.action.toLowerCase()">
                {{ item.action }}
              </span>
              <span class="time">{{ item.time }}</span>
            </div>
            <div class="file-path">{{ item.path }}</div>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<style scoped>
.file-manager-page {
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

.file-operations {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.file-operations h2 {
  margin: 0 0 1.5rem 0;
  color: #1f2937;
  font-size: 1.5rem;
  font-weight: 600;
}

.operation-section {
  margin-bottom: 2rem;
}

.operation-section h3 {
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

.operation-btn {
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

.operation-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.operation-btn.primary {
  background: #3b82f6;
  color: white;
}

.operation-btn.primary:hover {
  background: #2563eb;
}

.operation-btn.success {
  background: #10b981;
  color: white;
}

.operation-btn.success:hover {
  background: #059669;
}

.operation-btn.info {
  background: #06b6d4;
  color: white;
}

.operation-btn.info:hover {
  background: #0891b2;
}

.operation-btn.secondary {
  background: #6b7280;
  color: white;
}

.operation-btn.secondary:hover {
  background: #4b5563;
}

.save-settings {
  border-top: 1px solid #e5e7eb;
  padding-top: 2rem;
}

.save-settings h3 {
  margin: 0 0 1rem 0;
  color: #374151;
  font-size: 1.125rem;
  font-weight: 500;
}

.form-group {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.form-group label {
  color: #374151;
  font-weight: 500;
  min-width: 120px;
}

.form-group input {
  flex: 1;
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.875rem;
}

.form-group input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
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

.current-selection,
.action-status,
.file-history {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.current-selection h2,
.action-status h2,
.file-history h2 {
  margin: 0 0 1.5rem 0;
  color: #1f2937;
  font-size: 1.5rem;
  font-weight: 600;
}

.selection-info {
  background: #f8fafc;
  border-radius: 8px;
  padding: 1.5rem;
  border-left: 4px solid #3b82f6;
}

.selection-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  color: #374151;
  line-height: 1.5;
}

.file-path {
  font-family: monospace;
  background: #f1f5f9;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.875rem;
  word-break: break-all;
}

.status-message {
  background: #f0fdf4;
  border: 1px solid #10b981;
  border-radius: 8px;
  padding: 1rem;
  color: #065f46;
  line-height: 1.5;
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
  gap: 1rem;
}

.history-item {
  background: #f9fafb;
  border-radius: 8px;
  padding: 1rem;
  border-left: 4px solid #3b82f6;
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

.action-badge.打开 {
  background: #dbeafe;
  color: #1e40af;
}

.action-badge.保存 {
  background: #d1fae5;
  color: #065f46;
}

.action-badge.另存为 {
  background: #cffafe;
  color: #155e75;
}

.action-badge.打开目录 {
  background: #e9d5ff;
  color: #6b21a8;
}

.time {
  font-size: 0.75rem;
  color: #6b7280;
}
</style>
