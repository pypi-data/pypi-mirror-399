<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api'
import {
  Notification,
  Monitor,
  WarningFilled,
  InfoFilled,
  SuccessFilled,
  CircleCloseFilled,
  Bell,
  Clock,
  Document
} from '@element-plus/icons-vue'

const router = useRouter()
const isDesktop = ref<boolean>(false)
const notificationsEnabled = ref<boolean>(true)
const lastNotification = ref<string>('')
const notificationHistory = ref<Array<{ title: string, body: string, time: string }>>([])
const customTitle = ref<string>('')
const customBody = ref<string>('')

onMounted(() => {
  isDesktop.value = api.isAvailable()
})

const showNotification = async (title: string = 'PyWebApp Demo', body: string = '这是一个来自桌面应用的通知！') => {
  if (notificationsEnabled.value && isDesktop.value) {
    try {
      await api.showNotification(title, body)
      lastNotification.value = `${title}: ${body}`
      notificationHistory.value.unshift({
        title,
        body,
        time: new Date().toLocaleTimeString()
      })
      if (notificationHistory.value.length > 10) {
        notificationHistory.value.pop()
      }
    } catch (error) {
      console.error('显示通知失败:', error)
    }
  }
}

const showCustomNotification = () => {
  if (customTitle.value && customBody.value) {
    showNotification(customTitle.value, customBody.value)
    customTitle.value = ''
    customBody.value = ''
  } else {
    showNotification()
  }
}

const clearHistory = () => {
  notificationHistory.value = []
}
</script>

<template>
  <div class="notifications-container">
    <!-- 页面标题 -->
    <el-page-header @back="router.push('/')" title="返回主页">
      <template #content>
        <div class="page-header-content">
          <el-icon class="header-icon">
            <Notification />
          </el-icon>
          <span>系统通知管理</span>
          <el-tag :type="isDesktop ? 'success' : 'warning'" size="small">
            <el-icon>
              <Monitor />
            </el-icon>
            {{ isDesktop ? '桌面应用' : 'Web版本' }}
          </el-tag>
        </div>
      </template>
    </el-page-header>

    <!-- 桌面模式内容 -->
    <div v-if="isDesktop">
      <!-- 通知控制面板 -->
      <el-card class="control-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <el-icon>
              <Bell />
            </el-icon>
            <span>通知控制</span>
            <el-switch v-model="notificationsEnabled" active-text="启用通知" inactive-text="禁用通知"
              style="margin-left: auto;" />
          </div>
        </template>

        <!-- 快速通知按钮 -->
        <div class="quick-actions">
          <h4>快速通知</h4>
          <el-row :gutter="16">
            <el-col :xs="24" :sm="12" :md="6">
              <el-button type="primary" :icon="InfoFilled" @click="showNotification('信息', '这是一条信息通知')" class="quick-btn"
                size="large" :disabled="!notificationsEnabled">
                信息通知
              </el-button>
            </el-col>
            <el-col :xs="24" :sm="12" :md="6">
              <el-button type="success" :icon="SuccessFilled" @click="showNotification('成功', '操作成功完成！')"
                class="quick-btn" size="large" :disabled="!notificationsEnabled">
                成功通知
              </el-button>
            </el-col>
            <el-col :xs="24" :sm="12" :md="6">
              <el-button type="warning" :icon="WarningFilled" @click="showNotification('警告', '请注意检查相关设置')"
                class="quick-btn" size="large" :disabled="!notificationsEnabled">
                警告通知
              </el-button>
            </el-col>
            <el-col :xs="24" :sm="12" :md="6">
              <el-button type="danger" :icon="CircleCloseFilled" @click="showNotification('错误', '发生了错误，请重试')"
                class="quick-btn" size="large" :disabled="!notificationsEnabled">
                错误通知
              </el-button>
            </el-col>
          </el-row>
        </div>

        <!-- 自定义通知 -->
        <el-divider />
        <div class="custom-notification">
          <h4>自定义通知</h4>
          <el-form :model="{ title: customTitle, body: customBody }" label-width="80px">
            <el-form-item label="通知标题">
              <el-input v-model="customTitle" placeholder="输入通知标题" clearable :disabled="!notificationsEnabled" />
            </el-form-item>
            <el-form-item label="通知内容">
              <el-input v-model="customBody" type="textarea" placeholder="输入通知内容" :rows="3" resize="none"
                :disabled="!notificationsEnabled" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="showCustomNotification"
                :disabled="!notificationsEnabled || !customTitle || !customBody" :icon="Notification">
                发送通知
              </el-button>
            </el-form-item>
          </el-form>
        </div>
      </el-card>

      <!-- 通知历史 -->
      <el-row :gutter="20" class="content-row">
        <el-col :span="16">
          <el-card class="history-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <el-icon>
                  <Clock />
                </el-icon>
                <span>通知历史</span>
                <el-button v-if="notificationHistory.length > 0" type="danger" size="small" @click="clearHistory" text>
                  清空历史
                </el-button>
              </div>
            </template>

            <el-empty v-if="notificationHistory.length === 0" description="暂无通知历史" />

            <div v-else class="history-list">
              <el-timeline>
                <el-timeline-item v-for="(notification, index) in notificationHistory" :key="index"
                  :timestamp="notification.time" placement="top">
                  <el-card class="history-item" shadow="never">
                    <template #header>
                      <div class="history-header">
                        <span class="notification-title">{{ notification.title }}</span>
                        <el-tag size="small" type="info">{{ notification.time }}</el-tag>
                      </div>
                    </template>
                    <p class="notification-content">{{ notification.body }}</p>
                  </el-card>
                </el-timeline-item>
              </el-timeline>
            </div>
          </el-card>
        </el-col>

        <el-col :span="8">
          <el-card class="status-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <el-icon>
                  <Document />
                </el-icon>
                <span>通知状态</span>
              </div>
            </template>

            <div class="status-content">
              <el-descriptions :column="1" border>
                <el-descriptions-item label="通知状态">
                  <el-tag :type="notificationsEnabled ? 'success' : 'danger'">
                    {{ notificationsEnabled ? '已启用' : '已禁用' }}
                  </el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="历史记录">
                  <el-tag type="info">{{ notificationHistory.length }} 条</el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="运行模式">
                  <el-tag type="success">桌面应用</el-tag>
                </el-descriptions-item>
              </el-descriptions>

              <el-divider />

              <div v-if="lastNotification" class="last-notification">
                <h5>最后发送的通知</h5>
                <el-alert :title="lastNotification" type="success" :closable="false" show-icon />
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- Web模式提示 -->
    <el-alert v-else type="warning" :closable="false" show-icon class="web-notice">
      <template #title>
        <div class="notice-title">
          <el-icon>
            <WarningFilled />
          </el-icon>
          Web模式限制
        </div>
      </template>
      <div class="notice-content">
        <p>通知功能仅在桌面模式下可用。要使用此功能，请构建并运行桌面版本：</p>
        <pre class="code-block">cd src/pywebapp_demo/frontend
npm run build
cd ../../..
python -m pywebapp_demo.cli</pre>
      </div>
    </el-alert>
  </div>
</template>

<style scoped>
.notifications-container {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
  height: 100%;
  overflow-y: auto;
}

.page-header-content {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-icon {
  font-size: 20px;
  color: #409EFF;
}

/* 卡片通用样式 */
.control-card,
.history-card,
.status-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 16px;
}

/* 快速操作区域 */
.quick-actions {
  margin-bottom: 24px;
}

.quick-actions h4 {
  margin: 0 0 16px 0;
  color: #303133;
  font-size: 14px;
  font-weight: 600;
}

.quick-btn {
  width: 100%;
  margin-bottom: 12px;
}

/* 自定义通知区域 */
.custom-notification h4 {
  margin: 0 0 16px 0;
  color: #303133;
  font-size: 14px;
  font-weight: 600;
}

/* 内容行 */
.content-row {
  margin-bottom: 20px;
}

/* 历史记录 */
.history-list {
  max-height: 500px;
  overflow-y: auto;
}

.history-item {
  margin-bottom: 8px;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.notification-title {
  font-weight: 600;
  color: #303133;
}

.notification-content {
  margin: 0;
  color: #606266;
  line-height: 1.5;
}

/* 状态卡片 */
.status-content {
  padding: 8px 0;
}

.last-notification {
  margin-top: 16px;
}

.last-notification h5 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 14px;
  font-weight: 600;
}

/* Web模式提示 */
.web-notice {
  margin-top: 20px;
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
  .notifications-container {
    padding: 16px;
  }

  .page-header-content {
    flex-direction: column;
    gap: 8px;
    text-align: center;
  }

  .content-row {
    margin-bottom: 0;
  }
}
</style>
