import { api } from '../../utils/api'
const theme = require('../../utils/theme')

// ── 颜色配置 ──────────────────────────────────────────────────────────────────

const SCORE_COLORS = {
  null:  '#EDE8F4',
  1:     '#C6B4E1',
  2:     '#A58DC8',
  3:     '#8E7AB5',
  4:     '#6B5A96',
  5:     '#4A3B78',
}

const LEGEND = [
  { label: '未打卡', color: '#EDE8F4' },
  { label: '很差',   color: '#C6B4E1' },
  { label: '较差',   color: '#A58DC8' },
  { label: '一般',   color: '#8E7AB5' },
  { label: '较好',   color: '#6B5A96' },
  { label: '很好',   color: '#4A3B78' },
]

const MONTH_NAMES = ['1月','2月','3月','4月','5月','6月','7月','8月','9月','10月','11月','12月']

const QUICK_ACTIONS = [
  { icon: '/assets/icons/Generate.png', label: '记录旅程', action: 'generateReport' },
  { icon: '/assets/icons/Reports.png', label: '过往旅程', action: 'historyReport' },
  { icon: '/assets/icons/Favorites.png', label: '我的收藏', action: 'favorites' },
]

const SETTING_ITEMS = [
  { icon: '/assets/icons/settings.svg', label: '设置',      action: 'settings' },
  { icon: '/assets/icons/help.svg',    label: '帮助与反馈', action: 'help' },
  { icon: '/assets/icons/logout.svg',  label: '退出登录',  action: 'logout', danger: true },
]

// ── 像素网格计算 ──────────────────────────────────────────────────────────────

function buildScoreMap(records) {
  const map = {}
  for (const r of records) {
    const d = typeof r.survey_date === 'string' ? r.survey_date : String(r.survey_date)
    map[d] = r.overall_score
  }
  return map
}

function toDateStr(d) {
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

// cell width (28rpx) + gap (4rpx)
const CELL_STEP = 32

function buildYearGrid(year, scoreMap) {
  const jan1 = new Date(year, 0, 1)
  // Mon-based day-of-week: 0=Mon … 6=Sun
  const startDow = (jan1.getDay() + 6) % 7

  const gridStart = new Date(jan1)
  gridStart.setDate(gridStart.getDate() - startDow)

  const weeks = []
  const cur = new Date(gridStart)
  const monthFirstCol = {}
  let weekIdx = 0

  while (weekIdx <= 53) {
    const days = []
    for (let di = 0; di < 7; di++) {
      const inYear = cur.getFullYear() === year
      const dateStr = toDateStr(cur)
      const score = inYear ? (scoreMap[dateStr] ?? null) : null
      days.push({
        dateStr,
        inYear,
        score,
        color: inYear ? (SCORE_COLORS[score] || SCORE_COLORS[null]) : 'transparent',
      })
      if (inYear && cur.getDate() === 1 && monthFirstCol[cur.getMonth()] === undefined) {
        monthFirstCol[cur.getMonth()] = weekIdx
      }
      cur.setDate(cur.getDate() + 1)
    }
    weeks.push({ days })
    weekIdx++
    // Stop after we've passed Dec 31 of the target year
    if (cur.getFullYear() > year) break
  }

  const sortedMonths = Object.keys(monthFirstCol).map(Number).sort((a, b) => a - b)
  const monthSpans = sortedMonths.map((mo, i) => {
    const startCol = monthFirstCol[mo]
    const endCol = i + 1 < sortedMonths.length ? monthFirstCol[sortedMonths[i + 1]] : weeks.length
    return { label: MONTH_NAMES[mo], width: (endCol - startCol) * CELL_STEP }
  })

  return { weeks, monthSpans }
}

// ── Page ──────────────────────────────────────────────────────────────────────

Page({
  data: {
    userInfo: { nickname: '小桃', stage: '围绝经期' },
    stats: { totalDays: 0, currentStreak: 0, avgScore: null },
    selectedYear: new Date().getFullYear(),
    weeks: [],
    monthSpans: [],
    isDark: false,
    LEGEND,
    quickActions: QUICK_ACTIONS,
    settingItems: SETTING_ITEMS,
  },

  _scoreMap: {},

  onLoad() {
    this._loadAll()
  },

  onShow() {
    theme.syncPageTheme(this)
    this._refreshStats()
  },

  // ── 数据加载 ──────────────────────────────────────────────────────────────

  async _loadAll() {
    await Promise.all([this._loadUser(), this._loadPixels()])
  },

  async _loadUser() {
    try {
      const info = await api.getUserMe()
      const stageMap = {
        premenopause: '绝经前期',
        perimenopause: '围绝经期',
        postmenopause: '绝经后期',
      }
      this.setData({
        userInfo: {
          nickname: info.nickname || '姐妹',
          stage: stageMap[info.menopause_stage] || info.menopause_stage,
        },
      })
    } catch (_) {}
  },

  async _loadPixels() {
    try {
      const res = await api.getSurveyHistory(365)
      this._scoreMap = buildScoreMap(res.records || [])
      this._renderGrid(this.data.selectedYear)
    } catch (_) {}
  },

  async _refreshStats() {
    try {
      const s = await api.getProfileStats()
      this.setData({
        stats: {
          totalDays: s.total_checkin_days ?? 0,
          currentStreak: s.current_streak ?? 0,
          avgScore: s.avg_overall_score_30d ?? null,
        },
      })
    } catch (_) {}
  },

  _renderGrid(year) {
    const { weeks, monthSpans } = buildYearGrid(year, this._scoreMap)
    this.setData({ weeks, monthSpans, selectedYear: year })
  },

  // ── 年份切换 ──────────────────────────────────────────────────────────────

  prevYear() {
    this._renderGrid(this.data.selectedYear - 1)
  },

  nextYear() {
    const next = this.data.selectedYear + 1
    if (next > new Date().getFullYear()) return
    this._renderGrid(next)
  },

  // ── 格子点击 ──────────────────────────────────────────────────────────────

  onDayTap(e) {
    const { day } = e.currentTarget.dataset
    if (!day || !day.inYear) return
    const label = day.score
      ? ['', '很差', '较差', '一般', '较好', '很好'][day.score]
      : '未打卡'
    wx.showToast({ title: `${day.dateStr}  ${label}`, icon: 'none', duration: 1800 })
  },

  // ── 深夜模式 ──────────────────────────────────────────────────────────────

  toggleTheme() {
    const isDark = !this.data.isDark
    this.setData({ isDark })
    theme.setTheme(isDark)
  },

  // ── 快捷功能 ──────────────────────────────────────────────────────────────

  onQuickAction(e) {
    const { action } = e.currentTarget.dataset
    switch (action) {
      case 'generateReport':
        wx.navigateTo({ url: '/pages/report/index' })
        break
      case 'historyReport':
        wx.navigateTo({ url: '/pages/report/history' })
        break
      case 'favorites':
        wx.showToast({ title: '收藏功能即将上线', icon: 'none' })
        break
    }
  },

  // ── 设置项 ────────────────────────────────────────────────────────────────

  onSettingTap(e) {
    const { action } = e.currentTarget.dataset
    switch (action) {
      case 'settings':
        wx.showToast({ title: '设置页面即将上线', icon: 'none' })
        break
      case 'help':
        wx.showToast({ title: '帮助与反馈即将上线', icon: 'none' })
        break
      case 'logout':
        wx.showModal({
          title: '退出登录',
          content: '确定要退出吗？',
          success(res) {
            if (res.confirm) wx.reLaunch({ url: '/pages/splash/index' })
          },
        })
        break
    }
  },
})
