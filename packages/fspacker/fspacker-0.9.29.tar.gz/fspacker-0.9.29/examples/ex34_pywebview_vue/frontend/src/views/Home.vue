<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api'
import {
  House,
  Notification,
  Folder,
  Monitor,
  InfoFilled,
  TrendCharts,
  CopyDocument,
  Link,
  WarningFilled,
  Cpu,
  Coin
} from '@element-plus/icons-vue'

const router = useRouter()
const isDesktop = ref<boolean>(false)
const systemInfo = ref<Record<string, any>>({})
const appVersion = ref<string>('')
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

onMounted(async () => {
  isDesktop.value = api.isAvailable()

  try {
    systemInfo.value = await api.getSystemInfo()
    appVersion.value = await api.getAppVersion()

    if (isDesktop.value) {
      cpuUsage.value = await api.getCpuUsage()
      memoryInfo.value = await api.getMemoryInfo()
      diskInfo.value = await api.getDiskInfo()
    } else {
      systemInfo.value = {
        platform: navigator.platform || 'Web浏览器',
        architecture: 'Web',
        version: navigator.userAgent || '未知',
        python_version: '不适用',
        machine: 'Web设备'
      }
    }
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
})

const formatBytes = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const navigationCards = [
  {
    title: '系统通知',
    description: '显示桌面通知，支持自定义内容和样式',
    icon: Notification,
    route: '/notifications',
    desktopOnly: true,
    color: '#E6A23C'
  },
  {
    title: '文件管理',
    description: '文件选择器、保存对话框等功能',
    icon: Folder,
    route: '/file-manager',
    desktopOnly: true,
    color: '#67C23A'
  },
  {
    title: '窗口控制',
    description: '最小化、最大化、关闭窗口操作',
    icon: Monitor,
    route: '/window-manager',
    desktopOnly: true,
    color: '#409EFF'
  },
  {
    title: '系统信息',
    description: '查看详细的系统硬件和软件信息',
    icon: InfoFilled,
    route: '/system-info',
    desktopOnly: false,
    color: '#909399'
  },
  {
    title: '系统监控',
    description: '实时监控CPU、内存、磁盘使用情况',
    icon: TrendCharts,
    route: '/system-monitor',
    desktopOnly: false,
    color: '#F56C6C'
  },
  {
    title: '剪贴板管理',
    description: '查看和管理剪贴板历史内容',
    icon: CopyDocument,
    route: '/clipboard-manager',
    desktopOnly: true,
    color: '#909399'
  },
  {
    title: '浏览器启动',
    description: '在默认浏览器中打开指定链接',
    icon: Link,
    route: '/browser',
    desktopOnly: false,
    color: '#67C23A'
  }
]

const navigateTo = (route: string) => {
  router.push(route)
}
</script>

<template>
  <div class="home-container">
    <!-- 系统状态概览 -->
    <el-row v-if="isDesktop" :gutter="20" class="status-row">
      <el-col :xs="24" :sm="12" :md="8">
        <el-card class="status-card" shadow="hover">
          <div class="status-content">
            <div class="status-header">
              <el-icon class="status-icon cpu">
                <Cpu />
              </el-icon>
              <div class="status-title">CPU 使用率</div>
            </div>
            <div class="status-value">{{ cpuUsage.toFixed(1) }}%</div>
            <el-progress :percentage="cpuUsage"
              :color="cpuUsage > 80 ? '#F56C6C' : cpuUsage > 60 ? '#E6A23C' : '#67C23A'" :show-text="false" />
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :md="8" v-if="memoryInfo.total">
        <el-card class="status-card" shadow="hover">
          <div class="status-content">
            <div class="status-header">
              <el-icon class="status-icon memory">
                <Cpu />
              </el-icon>
              <div class="status-title">内存使用</div>
            </div>
            <div class="status-value">{{ memoryInfo.percent?.toFixed(1) }}%</div>
            <el-progress :percentage="memoryInfo.percent"
              :color="memoryInfo.percent > 80 ? '#F56C6C' : memoryInfo.percent > 60 ? '#E6A23C' : '#67C23A'"
              :show-text="false" />
            <div class="status-detail">
              {{ formatBytes(memoryInfo.used) }} / {{ formatBytes(memoryInfo.total) }}
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :md="8" v-if="diskInfo.total">
        <el-card class="status-card" shadow="hover">
          <div class="status-content">
            <div class="status-header">
              <el-icon class="status-icon disk">
                <Coin />
              </el-icon>
              <div class="status-title">磁盘使用</div>
            </div>
            <div class="status-value">{{ diskInfo.percent?.toFixed(1) }}%</div>
            <el-progress :percentage="diskInfo.percent"
              :color="diskInfo.percent > 80 ? '#F56C6C' : diskInfo.percent > 60 ? '#E6A23C' : '#67C23A'"
              :show-text="false" />
            <div class="status-detail">
              {{ formatBytes(diskInfo.used) }} / {{ formatBytes(diskInfo.total) }}
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 欢迎信息 -->
    <el-card class="welcome-card" shadow="never">
      <div class="welcome-content">
        <div class="welcome-header">
          <div class="welcome-title">
            <el-icon class="welcome-icon">
              <House />
            </el-icon>
            <h2>欢迎使用 PyWebApp Demo</h2>
          </div>
          <div class="welcome-badges">
            <el-tag :type="isDesktop ? 'success' : 'warning'" size="large">
              <el-icon>
                <Monitor />
              </el-icon>
              {{ isDesktop ? '桌面应用' : 'Web版本' }}
            </el-tag>
            <el-tag v-if="appVersion" type="primary" size="large">
              v{{ appVersion }}
            </el-tag>
          </div>
        </div>
        <el-divider />
        <p class="welcome-desc">
          基于 pywebview 和 Vue 3 + Element Plus 构建的现代化桌面应用示例，
          提供丰富的系统交互功能和优雅的用户界面。
        </p>
      </div>
    </el-card>

    <!-- 功能导航卡片 -->
    <div class="navigation-section">
      <h3 class="section-title">功能模块</h3>
      <el-row :gutter="20">
        <el-col v-for="card in navigationCards" :key="card.route" :xs="24" :sm="12" :md="8" :lg="6">
          <el-card class="nav-card" shadow="hover" :class="{ 'card-disabled': card.desktopOnly && !isDesktop }"
            @click="navigateTo(card.route)">
            <div class="nav-content">
              <div class="nav-icon-wrapper" :style="{ backgroundColor: card.color + '20', color: card.color }">
                <el-icon class="nav-icon">
                  <component :is="card.icon" />
                </el-icon>
              </div>
              <div class="nav-info">
                <h4>{{ card.title }}</h4>
                <p>{{ card.description }}</p>
                <div class="nav-badge">
                  <el-tag v-if="card.desktopOnly && !isDesktop" type="info" size="small">
                    桌面模式
                  </el-tag>
                  <el-tag v-else type="success" size="small">
                    可用
                  </el-tag>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- Web模式提示 -->
    <el-alert v-if="!isDesktop" type="info" :closable="false" show-icon class="web-notice">
      <template #title>
        <div class="notice-title">
          <el-icon>
            <WarningFilled />
          </el-icon>
          Web版本说明
        </div>
      </template>
      <div class="notice-content">
        <p>当前运行在Web模式下，部分桌面应用功能不可用。要体验完整功能，请构建并运行桌面版本：</p>
        <pre class="code-block">cd src/pywebapp_demo/frontend
npm run build
cd ../../..
python -m pywebapp_demo.cli</pre>
      </div>
    </el-alert>
  </div>
</template>

<style scoped>
.home-container {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
  height: 100%;
  overflow-y: auto;
}

/* 系统状态卡片 */
.status-row {
  margin-bottom: 24px;
}

.status-card {
  height: 140px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.status-card:hover {
  transform: translateY(-2px);
}

.status-content {
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.status-header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.status-icon {
  font-size: 24px;
}

.status-icon.cpu {
  color: #F56C6C;
}

.status-icon.memory {
  color: #67C23A;
}

.status-icon.disk {
  color: #E6A23C;
}

.status-title {
  font-size: 16px;
  font-weight: 500;
  color: #606266;
}

.status-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
  margin: 12px 0;
}

.status-detail {
  font-size: 12px;
  color: #909399;
  margin-top: 8px;
}

/* 欢迎卡片 */
.welcome-card {
  margin-bottom: 32px;
  border: none;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.welcome-content {
  padding: 24px;
}

.welcome-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.welcome-title {
  display: flex;
  align-items: center;
  gap: 16px;
}

.welcome-icon {
  font-size: 32px;
}

.welcome-title h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
}

.welcome-badges {
  display: flex;
  gap: 12px;
}

.welcome-desc {
  font-size: 16px;
  line-height: 1.6;
  margin: 0;
  opacity: 0.9;
}

/* 功能导航区域 */
.navigation-section {
  margin-bottom: 32px;
}

.section-title {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 20px;
  padding-bottom: 8px;
  border-bottom: 2px solid #E4E7ED;
}

.nav-card {
  margin-bottom: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  height: 160px;
}

.nav-card:hover:not(.card-disabled) {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
}

.card-disabled {
  opacity: 0.6;
  cursor: not-allowed;
  background: #F5F7FA;
}

.nav-content {
  height: 100%;
  display: flex;
  align-items: center;
  gap: 16px;
}

.nav-icon-wrapper {
  width: 64px;
  height: 64px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.nav-icon {
  font-size: 32px;
}

.nav-info {
  flex: 1;
}

.nav-info h4 {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.nav-info p {
  margin: 0 0 12px 0;
  font-size: 13px;
  color: #606266;
  line-height: 1.4;
}

.nav-badge {
  display: flex;
  justify-content: flex-start;
}

/* Web版本提示 */
.web-notice {
  margin-top: 24px;
}

.notice-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
}

.notice-content p {
  margin: 8px 0;
  line-height: 1.6;
}

.code-block {
  display: block;
  margin: 12px 0;
  padding: 16px;
  background: #F5F7FA;
  border-radius: 6px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 13px;
  line-height: 1.4;
  color: #303133;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .home-container {
    padding: 16px;
  }

  .welcome-header {
    flex-direction: column;
    gap: 16px;
    text-align: center;
  }

  .welcome-title {
    flex-direction: column;
    gap: 8px;
  }

  .nav-content {
    flex-direction: column;
    text-align: center;
  }

  .nav-badge {
    justify-content: center;
  }
}
</style>
