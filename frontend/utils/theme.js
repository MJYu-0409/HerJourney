const THEME_STORAGE_KEY = 'her_theme'

function getTheme() {
  return wx.getStorageSync(THEME_STORAGE_KEY) === 'dark'
}

function setTheme(isDark) {
  wx.setStorageSync(THEME_STORAGE_KEY, isDark ? 'dark' : 'light')
  applyNavBarColor(isDark)

  const app = getApp()
  if (app && app.globalData) {
    app.globalData.isDark = isDark
  }
}

function applyNavBarColor(isDark) {
  wx.setNavigationBarColor({
    frontColor: isDark ? '#ffffff' : '#000000',
    backgroundColor: isDark ? '#1F1B2E' : '#FAF7F4',
    animation: { duration: 200, timingFunc: 'easeIn' },
  })
}

function syncPageTheme(page) {
  const isDark = getTheme()
  page.setData({ isDark })
  applyNavBarColor(isDark)
}

module.exports = {
  getTheme,
  setTheme,
  applyNavBarColor,
  syncPageTheme,
}
