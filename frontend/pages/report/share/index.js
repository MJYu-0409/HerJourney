import { api } from '../../../utils/api'

Page({
  data: {
    interpretation: '',
    chartSeries: [],
    symptomEntries: [],  // [{key, name, text}]
    showChart: false,
    showAI: false,
    isAnonymous: true,
    submitting: false,
  },

  onLoad() {
    const app = getApp()
    const shareData = (app.globalData || {}).shareData || {}
    const {
      interpretation = '',
      chartSeries = [],
      selectedSymptoms = [],
    } = shareData

    const symptomEntries = selectedSymptoms.map(s => ({
      key: s.key,
      name: s.name,
      text: '',
    }))

    this.setData({ interpretation, chartSeries, symptomEntries })
  },

  toggleChart() {
    this.setData({ showChart: !this.data.showChart })
  },

  toggleAI() {
    this.setData({ showAI: !this.data.showAI })
  },

  onSymptomInput(e) {
    const idx = e.currentTarget.dataset.idx
    const symptomEntries = this.data.symptomEntries.map((s, i) =>
      i === idx ? { ...s, text: e.detail.value } : s
    )
    this.setData({ symptomEntries })
  },

  toggleAnonymous(e) {
    this.setData({ isAnonymous: e.detail.value })
  },

  async onShare() {
    if (this.data.submitting) return

    const { symptomEntries } = this.data
    const lines = symptomEntries.map(s =>
      s.text ? `【${s.name}】${s.text}` : `【${s.name}】`
    )
    const content = lines.join('\n')

    if (!content.trim()) {
      wx.showToast({ title: '请填写至少一条感受', icon: 'none' })
      return
    }

    this.setData({ submitting: true })
    try {
      await api.sharePost({
        post_type: 'report',
        title: '我的旅程分享',
        content,
        tags: ['#旅程', '#症状记录'],
      })
      wx.showToast({ title: '分享成功 🌸', icon: 'none', duration: 2000 })
      setTimeout(() => {
        wx.switchTab({ url: '/pages/community/index' })
      }, 1800)
    } catch (_) {
      wx.showToast({ title: '分享失败，请重试', icon: 'none' })
    } finally {
      this.setData({ submitting: false })
    }
  },
})
