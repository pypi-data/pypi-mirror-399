/**
 * PyWebView API - 用于与Python后端通信的接口
 */

declare global {
  interface Window {
    pywebview?: {
      api: {
        // 系统相关API
        show_notification: (title: string, body: string) => Promise<void>
        get_system_info: () => Promise<Record<string, any>>

        // 文件操作API
        open_file_dialog: (filters?: Record<string, string[]>) => Promise<string>
        save_file_dialog: (default_path?: string, filters?: Record<string, string[]>) => Promise<string>

        // 应用控制API
        minimize_window: () => Promise<void>
        maximize_window: () => Promise<void>
        close_window: () => Promise<void>

        // 自定义业务API
        get_app_version: () => Promise<string>

        // 系统监控API
        get_cpu_usage: () => Promise<number>
        get_memory_info: () => Promise<Record<string, any>>
        get_disk_info: () => Promise<Record<string, any>>

        // 浏览器和剪贴板API
        open_url: (url: string) => Promise<boolean>
        get_clipboard_text: () => Promise<string>
        set_clipboard_text: (text: string) => Promise<boolean>
      }
    }
  }
}

// API封装类
export class PyWebViewAPI {
  private static instance: PyWebViewAPI

  static getInstance(): PyWebViewAPI {
    if (!PyWebViewAPI.instance) {
      PyWebViewAPI.instance = new PyWebViewAPI()
    }
    return PyWebViewAPI.instance
  }

  private get api() {
    return window.pywebview?.api
  }

  // 检查API是否可用
  isAvailable(): boolean {
    return !!window.pywebview?.api
  }

  // 显示通知
  async showNotification(title: string, body: string): Promise<void> {
    if (this.isAvailable()) {
      return this.api!.show_notification(title, body)
    }
    console.log(`通知: ${title} - ${body}`)
  }

  // 获取系统信息
  async getSystemInfo(): Promise<Record<string, any>> {
    if (this.isAvailable()) {
      return this.api!.get_system_info()
    }
    return { platform: 'web', userAgent: navigator.userAgent }
  }

  // 打开文件对话框
  async openFileDialog(filters?: Record<string, string[]>): Promise<string> {
    if (this.isAvailable()) {
      return this.api!.open_file_dialog(filters)
    }
    throw new Error('文件对话框仅在桌面应用中可用')
  }

  // 保存文件对话框
  async saveFileDialog(defaultPath?: string, filters?: Record<string, string[]>): Promise<string> {
    if (this.isAvailable()) {
      return this.api!.save_file_dialog(defaultPath, filters)
    }
    throw new Error('文件对话框仅在桌面应用中可用')
  }

  // 窗口控制
  async minimizeWindow(): Promise<void> {
    if (this.isAvailable()) {
      return this.api!.minimize_window()
    }
  }

  async maximizeWindow(): Promise<void> {
    if (this.isAvailable()) {
      return this.api!.maximize_window()
    }
  }

  async closeWindow(): Promise<void> {
    if (this.isAvailable()) {
      return this.api!.close_window()
    }
  }

  // 获取应用版本
  async getAppVersion(): Promise<string> {
    if (this.isAvailable()) {
      return this.api!.get_app_version()
    }
    return '1.0.0-web'
  }

  // 获取CPU使用率
  async getCpuUsage(): Promise<number> {
    if (this.isAvailable()) {
      return this.api!.get_cpu_usage()
    }
    return 0
  }

  // 获取内存信息
  async getMemoryInfo(): Promise<Record<string, any>> {
    if (this.isAvailable()) {
      return this.api!.get_memory_info()
    }
    return { error: 'Not available in web mode' }
  }

  // 获取磁盘信息
  async getDiskInfo(): Promise<Record<string, any>> {
    if (this.isAvailable()) {
      return this.api!.get_disk_info()
    }
    return { error: 'Not available in web mode' }
  }

  // 打开URL
  async openUrl(url: string): Promise<boolean> {
    if (this.isAvailable()) {
      return this.api!.open_url(url)
    }
    window.open(url, '_blank')
    return true
  }

  // 获取剪贴板文本
  async getClipboardText(): Promise<string> {
    if (this.isAvailable()) {
      return this.api!.get_clipboard_text()
    }
    try {
      return await navigator.clipboard.readText()
    } catch {
      return ''
    }
  }

  // 设置剪贴板文本
  async setClipboardText(text: string): Promise<boolean> {
    if (this.isAvailable()) {
      return this.api!.set_clipboard_text(text)
    }
    try {
      await navigator.clipboard.writeText(text)
      return true
    } catch {
      return false
    }
  }
}

export const api = PyWebViewAPI.getInstance()
