import { api } from '../../utils/api'

const DEFAULT_TOPICS = [
  { emoji: '🔥', text: '潮热盗汗总是突然来袭，怎么应对？' },
  { emoji: '💊', text: '激素替代治疗有什么影响，适合我吗？' },
  { emoji: '😴', text: '睡眠越来越差，凌晨总会醒，怎么办？' },
  { emoji: '😔', text: '情绪很容易波动，感觉自己变了一个人。' },
  { emoji: '🦴', text: '关节疼痛、骨质流失，该如何保护自己？' },
]

function formatTime(date) {
  const d = date instanceof Date ? date : new Date(date)
  const h = String(d.getHours()).padStart(2, '0')
  const m = String(d.getMinutes()).padStart(2, '0')
  return `${h}:${m}`
}

Page({
  data: {
    messages: [],
    loading: false,
    recording: false,
    sessionId: null,
    scrollAnchor: '',
    insightText: '',
    defaultTopics: DEFAULT_TOPICS,
  },

  onLoad() {
    wx.setNavigationBarTitle({ title: '小伴' })
    this._loadInsight()
  },

  onShow() {
    // 键盘收起时重置布局
    wx.hideKeyboard()
  },

  // ── 洞察横幅 ──────────────────────────────────────────────────────────────

  async _loadInsight() {
    try {
      const stats = await api.getStats()
      if (stats.top_symptoms && stats.top_symptoms.length > 0) {
        const top = stats.top_symptoms[0]
        this.setData({
          insightText: `近30天，你的${top.name}平均评分 ${top.avg_score} 分，我一直在关注你。`,
        })
      }
    } catch (_) {
      // 静默失败，不影响聊天
    }
  },

  // ── 话题建议点击 ───────────────────────────────────────────────────────────

  onTopicTap(e) {
    const { topic } = e.currentTarget.dataset
    this._sendMessage(topic)
  },

  // ── 输入栏事件 ─────────────────────────────────────────────────────────────

  onSend(e) {
    const { value } = e.detail
    if (!value || !value.trim()) return
    this._sendMessage(value.trim())
  },

  onVoiceEnd(e) {
    const { tempFilePath, cancelled } = e.detail
    this.setData({ recording: false })
    if (cancelled || !tempFilePath) return
    // Demo：直接用提示文字，真实版本需调用语音识别接口
    this._sendMessage('[语音消息]')
  },

  onMediaChoose(e) {
    const { type } = e.detail
    wx.showToast({ title: `已选择${type}`, icon: 'none', duration: 1500 })
  },

  // ── 核心发送逻辑 ──────────────────────────────────────────────────────────

  async _sendMessage(content) {
    if (this.data.loading) return

    const userMsg = {
      id: `u-${Date.now()}`,
      role: 'user',
      content,
      timeStr: formatTime(new Date()),
      animIn: true,
    }

    this.setData({ scrollAnchor: '' })
    this.setData({
      messages: [...this.data.messages, userMsg],
      loading: true,
      scrollAnchor: 'scroll-bottom',
    })

    try {
      const res = await api.sendMessage(this.data.sessionId, content)
      const aiMsg = {
        id: `a-${Date.now()}`,
        role: 'assistant',
        content: res.content,
        timeStr: formatTime(new Date(res.created_at)),
        animIn: true,
      }

      // 先清空再赋值，避免 WeChat scroll-view 同值不重新触发滚动
      this.setData({ scrollAnchor: '' })
      this.setData({
        messages: [...this.data.messages, aiMsg],
        sessionId: res.session_id,
        loading: false,
        scrollAnchor: 'scroll-bottom',
      })
    } catch (err) {
      wx.showToast({ title: '发送失败，请重试', icon: 'none' })
      this.setData({ loading: false })
    }
  },

  // ── 语音录制遮罩 ──────────────────────────────────────────────────────────

  onRecordingChange(e) {
    this.setData({ recording: e.detail.recording })
  },
})
