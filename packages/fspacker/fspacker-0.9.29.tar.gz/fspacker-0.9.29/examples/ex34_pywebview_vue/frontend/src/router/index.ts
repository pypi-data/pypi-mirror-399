import { createRouter, createWebHashHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Notifications from '../views/Notifications.vue'
import FileManager from '../views/FileManager.vue'
import WindowManager from '../views/WindowManager.vue'
import SystemInfo from '../views/SystemInfo.vue'
import SystemMonitor from '../views/SystemMonitor.vue'
import ClipboardManager from '../views/ClipboardManager.vue'
import BrowserLauncher from '../views/BrowserLauncher.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/notifications',
    name: 'Notifications',
    component: Notifications
  },
  {
    path: '/file-manager',
    name: 'FileManager',
    component: FileManager
  },
  {
    path: '/window-manager',
    name: 'WindowManager',
    component: WindowManager
  },
  {
    path: '/system-info',
    name: 'SystemInfo',
    component: SystemInfo
  },
  {
    path: '/system-monitor',
    name: 'SystemMonitor',
    component: SystemMonitor
  },
  {
    path: '/clipboard-manager',
    name: 'ClipboardManager',
    component: ClipboardManager
  },
  {
    path: '/browser',
    name: 'BrowserLauncher',
    component: BrowserLauncher
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

export default router
