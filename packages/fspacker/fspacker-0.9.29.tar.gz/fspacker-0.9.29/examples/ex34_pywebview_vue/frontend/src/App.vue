<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { api } from './api'
import {
  Expand,
  Fold,
  Notification,
  Folder,
  Monitor,
  InfoFilled,
  TrendCharts,
  CopyDocument,
  Link,
  House,
  Key,
} from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const isDesktop = ref<boolean>(false)
const shortcutsVisible = ref<boolean>(false)
const isCollapse = ref(false)

// 快捷键映射
const shortcuts = ref<Record<string, string>>({
  'Ctrl+N': '通知页面',
  'Ctrl+O': '文件管理',
  'Ctrl+S': '文件管理',
  'Ctrl+M': '窗口管理',
  'Ctrl+W': '关闭应用',
  'F11': '窗口管理',
  'Ctrl+H': '显示/隐藏快捷键',
  'Ctrl+R': '系统监控',
  'Ctrl+C': '剪贴板管理',
  'Ctrl+G': '浏览器启动'
})

// 侧边栏菜单配置
const menuItems = [
  {
    index: '/',
    title: '主页',
    icon: House,
    desktopOnly: false
  },
  {
    index: '/notifications',
    title: '系统通知',
    icon: Notification,
    desktopOnly: true
  },
  {
    index: '/file-manager',
    title: '文件管理',
    icon: Folder,
    desktopOnly: true
  },
  {
    index: '/window-manager',
    title: '窗口控制',
    icon: Monitor,
    desktopOnly: true
  },
  {
    index: '/system-info',
    title: '系统信息',
    icon: InfoFilled,
    desktopOnly: false
  },
  {
    index: '/system-monitor',
    title: '系统监控',
    icon: TrendCharts,
    desktopOnly: false
  },
  {
    index: '/clipboard-manager',
    title: '剪贴板管理',
    icon: CopyDocument,
    desktopOnly: true
  },
  {
    index: '/browser',
    title: '浏览器启动',
    icon: Link,
    desktopOnly: false
  }
]

onMounted(() => {
  isDesktop.value = api.isAvailable()
  console.log('API可用性:', isDesktop.value)
  console.log('PyWebView对象:', window.pywebview)

  // 添加键盘事件监听器
  document.addEventListener('keydown', handleKeyDown)
})

onUnmounted(() => {
  // 移除键盘事件监听器
  document.removeEventListener('keydown', handleKeyDown)
})

const handleKeyDown = async (event: KeyboardEvent) => {
  // 构建快捷键字符串
  const keys = []
  if (event.ctrlKey) keys.push('Ctrl')
  if (event.altKey) keys.push('Alt')
  if (event.shiftKey) keys.push('Shift')
  if (event.metaKey) keys.push('Meta')

  // 处理功能键
  let key = event.key
  if (key === ' ') key = 'Space'
  if (key.startsWith('F') && key.length > 1) key = key // F1-F12
  if (key.length === 1) key = key.toUpperCase() // 字母键

  keys.push(key)
  const shortcut = keys.join('+')

  // 处理快捷键 - 导航到相应页面
  switch (shortcut) {
    case 'Ctrl+N':
      event.preventDefault()
      if (isDesktop.value) router.push('/notifications')
      break
    case 'Ctrl+O':
    case 'Ctrl+S':
      event.preventDefault()
      if (isDesktop.value) router.push('/file-manager')
      break
    case 'Ctrl+M':
    case 'F11':
      event.preventDefault()
      if (isDesktop.value) router.push('/window-manager')
      break
    case 'Ctrl+W':
      event.preventDefault()
      if (isDesktop.value) api.closeWindow()
      break
    case 'Ctrl+H':
      event.preventDefault()
      shortcutsVisible.value = !shortcutsVisible.value
      break
    case 'Ctrl+R':
      event.preventDefault()
      router.push('/system-monitor')
      break
    case 'Ctrl+C':
      event.preventDefault()
      if (isDesktop.value) router.push('/clipboard-manager')
      break
    case 'Ctrl+G':
      event.preventDefault()
      router.push('/browser')
      break
  }
}

const handleMenuSelect = (index: string) => {
  router.push(index)
}

const toggleSidebar = () => {
  isCollapse.value = !isCollapse.value
}

const filterMenuItems = () => {
  return menuItems.filter(item => !item.desktopOnly || isDesktop.value)
}
</script>

<template>
  <div class="app-container">
    <!-- 顶部导航栏 -->
    <el-header class="app-header">
      <div class="header-left">
        <el-button :icon="isCollapse ? Expand : Fold" @click="toggleSidebar" text size="large" class="sidebar-toggle" />
        <div class="app-title">
          <el-icon class="title-icon">
            <Monitor />
          </el-icon>
          <span>PyWebApp Demo</span>
        </div>
      </div>

      <div class="header-center">
        <el-tag :type="isDesktop ? 'success' : 'warning'" size="large">
          <el-icon>
            <Monitor />
          </el-icon>
          {{ isDesktop ? '桌面应用' : 'Web版本' }}
        </el-tag>
      </div>

      <div class="header-right">
        <el-button :icon="Key" @click="shortcutsVisible = !shortcutsVisible" text size="large" title="显示快捷键 (Ctrl+H)">
          快捷键
        </el-button>
      </div>
    </el-header>

    <el-container class="main-container">
      <!-- 侧边栏 -->
      <el-aside :width="isCollapse ? '64px' : '200px'" class="app-sidebar">
        <el-menu :default-active="route.path" :collapse="isCollapse" :unique-opened="true" @select="handleMenuSelect"
          class="sidebar-menu" router>
          <el-menu-item v-for="item in filterMenuItems()" :key="item.index" :index="item.index"
            :disabled="item.desktopOnly && !isDesktop">
            <el-icon>
              <component :is="item.icon" />
            </el-icon>
            <template #title>
              <span>{{ item.title }}</span>
              <el-tag v-if="item.desktopOnly && !isDesktop" size="small" type="info" class="menu-tag">
                桌面
              </el-tag>
            </template>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <!-- 主内容区域 -->
      <el-main class="app-main">
        <router-view />
      </el-main>
    </el-container>

    <!-- 快捷键对话框 -->
    <el-dialog v-model="shortcutsVisible" title="⌨️ 键盘快捷键" width="600px" :show-close="true" class="shortcuts-dialog">
      <div class="shortcuts-content">
        <el-table :data="Object.entries(shortcuts).map(([key, value]) => ({ key, value }))" stripe>
          <el-table-column prop="key" label="快捷键" width="150">
            <template #default="{ row }">
              <el-tag type="primary">{{ row.key }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="value" label="功能" />
        </el-table>
      </div>
    </el-dialog>
  </div>
</template>

<style scoped>
.app-container {
  width: 100vw;
  height: 100vh;
  display: flex;
  flex-direction: column;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  overflow: hidden;
}

.app-header {
  background: #ffffff;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  height: 60px;
  flex-shrink: 0;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
  z-index: 1000;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.sidebar-toggle {
  color: #606266;
}

.app-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.title-icon {
  font-size: 20px;
  color: #409eff;
}

.header-center {
  flex: 1;
  display: flex;
  justify-content: center;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.main-container {
  flex: 1;
  overflow: hidden;
  height: calc(100vh - 60px);
  min-height: 0; /* 确保flex子项可以收缩 */
}

.app-sidebar {
  background: #ffffff;
  border-right: 1px solid #e4e7ed;
  transition: width 0.3s ease;
  overflow: hidden;
  height: 100%;
}

.sidebar-menu {
  border: none;
  height: 100%;
}

.sidebar-menu:not(.el-menu--collapse) {
  width: 200px;
}

.menu-tag {
  margin-left: 8px;
}

.app-main {
  background: #f5f7fa;
  padding: 0;
  overflow-y: auto;
  height: 100%;
  min-height: 0; /* 确保flex子项可以收缩 */
}

.shortcuts-dialog :deep(.el-dialog__header) {
  text-align: center;
  font-size: 18px;
  font-weight: 600;
}

.shortcuts-content {
  max-height: 400px;
  overflow-y: auto;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .app-header {
    padding: 0 12px;
  }

  .app-title span {
    display: none;
  }

  .header-center {
    display: none;
  }

  .header-right {
    gap: 8px;
  }

  .app-sidebar {
    position: absolute;
    top: 60px;
    left: 0;
    bottom: 0;
    z-index: 999;
    box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);
  }
}
</style>
