const theme = require('./utils/theme')

App({
  globalData: {
    userId: 'mock-user-001',
    baseUrl: 'http://localhost:8000',
    isDark: false,
  },

  onLaunch() {
    // 初始化主题
    const isDark = theme.getTheme()
    this.globalData.isDark = isDark

    // 首次启动跳转开屏页
    const hasLaunched = wx.getStorageSync('hasLaunched')
    if (!hasLaunched) {
      wx.reLaunch({ url: '/pages/splash/index' })
    }
  },
})
