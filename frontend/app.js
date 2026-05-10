App({
  globalData: {
    userId: 'mock-user-001',
    baseUrl: 'http://localhost:8000',
  },

  onLaunch() {
    // 首次启动跳转开屏页
    const hasLaunched = wx.getStorageSync('hasLaunched')
    if (!hasLaunched) {
      wx.reLaunch({ url: '/pages/splash/index' })
    }
  },
})
