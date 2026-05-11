Page({
  onEnter() {
    wx.setStorageSync('hasLaunched', true)
    wx.switchTab({ url: '/pages/daily/index' })
  },
})
