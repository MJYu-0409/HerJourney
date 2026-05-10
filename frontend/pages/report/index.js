import { api } from '../../utils/api'

// Consistent color per symptom key
const SYMPTOM_COLORS = {
  hot_flash:           '#7B6CA0',
  sleep_disorder:      '#7EC8E3',
  anxiety:             '#E8A0B4',
  dizziness:           '#F5C842',
  fatigue:             '#90C8A0',
  mood_swing:          '#F0A080',
  night_sweat:         '#C4A8D8',
  palpitation:         '#70B8C0',
  depression:          '#B8A0E8',
  joint_pain:          '#E8C490',
  muscle_pain:         '#A8D4B8',
  headache:            '#E8A8A8',
  breast_pain:         '#D4A8C8',
  vaginal_dryness:     '#A8C4D4',
  urinary_issue:       '#C4D4A8',
  weight_gain:         '#D4C4A8',
  skin_change:         '#E8D4A8',
  hair_loss:           '#A8B8C8',
  memory_issue:        '#C8A8D4',
  concentration_issue: '#A8D4C8',
  libido_change:       '#D4A8B8',
  menstrual_change:    '#B8C8E8',
}
const FALLBACK_COLORS = ['#7B6CA0','#7EC8E3','#E8A0B4','#F5C842','#90C8A0','#F0A080']

function colorFor(key, idx) {
  return SYMPTOM_COLORS[key] || FALLBACK_COLORS[idx % FALLBACK_COLORS.length]
}

const TIME_RANGES = [
  { label: '近7天',  days: 7  },
  { label: '近30天', days: 30 },
  { label: '近3月',  days: 90 },
  { label: '自定义', days: -1 },
]

function todayStr() {
  const d = new Date()
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`
}

Page({
  data: {
    // Time range
    TIME_RANGES,
    selectedDays: 30,
    customStart: '',
    todayStr: todayStr(),

    // Symptom selector
    symptomBtnLabel: '多遇症状',
    allSymptoms: [],      // [{key, name, avg_score, days_reported}]
    selectedKeys: [],     // currently shown symptom keys

    // Chart
    chartData: null,      // raw API {since, until, symptoms}
    chartSeries: [],      // [{key, name, color, dataPoints}]
    chartLoading: false,

    // AI
    interpretation: '',
    aiLoading: false,
    conditionsChanged: false,

    // Picker popup
    showSymptomPicker: false,
    pickerSymptoms: [],   // [{key, name, selected}] — in-picker copy
  },

  _isFirstLoad: true,

  onLoad() {
    wx.setNavigationBarTitle({ title: '旅程' })
    this._loadChart(30)
  },

  // ── Data loading ───────────────────────────────────────────────────────────

  async _loadChart(days, customStartDate) {
    this.setData({ chartLoading: true })
    try {
      let effectiveDays = days
      if (days === -1 && customStartDate) {
        const diff = Math.ceil((Date.now() - new Date(customStartDate)) / 86400000)
        effectiveDays = Math.max(1, diff)
      } else if (days === -1) {
        this.setData({ chartLoading: false })
        return
      }

      const res = await api.getChart(effectiveDays)
      this.setData({ chartData: res })
      this._syncSymptoms(res.symptoms || [])
      this._rebuildSeries()

      if (this._isFirstLoad) {
        this._isFirstLoad = false
        await this._generateAI()
      }
    } catch (e) {
      wx.showToast({ title: '数据加载失败', icon: 'none' })
    } finally {
      this.setData({ chartLoading: false })
    }
  },

  // Build/merge allSymptoms from API response; preserve selection when possible
  _syncSymptoms(apiSymptoms) {
    // Sort by avg_score * days_reported (severity × persistence)
    const sorted = [...apiSymptoms].sort(
      (a, b) => b.avg_score * b.days_reported - a.avg_score * a.days_reported
    )
    const allSymptoms = sorted.map(s => ({ key: s.key, name: s.name, avg_score: s.avg_score, days_reported: s.days_reported }))

    // Default selection: preserve previous OR auto-select top 3
    let selectedKeys
    const stillValid = this.data.selectedKeys.filter(k => sorted.some(s => s.key === k))
    selectedKeys = stillValid.length > 0 ? stillValid : sorted.slice(0, 3).map(s => s.key)

    this.setData({ allSymptoms, selectedKeys })
    this._updateBtnLabel(allSymptoms, selectedKeys)
  },

  // Build chartSeries from current chartData + selectedKeys
  _rebuildSeries() {
    const { chartData, selectedKeys } = this.data
    if (!chartData) return
    const series = selectedKeys
      .map((key, idx) => {
        const found = (chartData.symptoms || []).find(s => s.key === key)
        if (!found) return null
        return {
          key,
          name: found.name,
          color: colorFor(key, idx),
          dataPoints: (found.data_points || []).map(p => ({
            date: String(p.date),
            score: p.score,
          })),
        }
      })
      .filter(Boolean)
    this.setData({ chartSeries: series })
  },

  // ── AI generation ──────────────────────────────────────────────────────────

  async _generateAI() {
    const { selectedDays, selectedKeys, customStart } = this.data
    if (!selectedKeys.length) return

    let days = selectedDays
    if (days === -1 && customStart) {
      days = Math.max(1, Math.ceil((Date.now() - new Date(customStart)) / 86400000))
    } else if (days === -1) return

    this.setData({ aiLoading: true, conditionsChanged: false })
    try {
      const res = await api.generateReport(days, selectedKeys)
      this.setData({ interpretation: res.interpretation })
    } catch (e) {
      wx.showToast({ title: 'AI解读生成失败', icon: 'none' })
    } finally {
      this.setData({ aiLoading: false })
    }
  },

  regenerate() {
    this._generateAI()
  },

  // ── Time range ─────────────────────────────────────────────────────────────

  async onTimeRange(e) {
    const days = e.currentTarget.dataset.days
    if (days === this.data.selectedDays) return
    this.setData({ selectedDays: days, conditionsChanged: false })
    if (days !== -1) {
      await this._loadChart(days)
      this.setData({ conditionsChanged: true })
    }
  },

  async onCustomStart(e) {
    const customStart = e.detail.value
    this.setData({ customStart })
    await this._loadChart(-1, customStart)
    this.setData({ conditionsChanged: true })
  },

  // ── Symptom picker ─────────────────────────────────────────────────────────

  openSymptomPicker() {
    const { allSymptoms, selectedKeys } = this.data
    const selectedSet = new Set(selectedKeys)
    const pickerSymptoms = allSymptoms.map(s => ({
      ...s,
      selected: selectedSet.has(s.key),
    }))
    this.setData({ pickerSymptoms, showSymptomPicker: true })
  },

  closeSymptomPicker() {
    this.setData({ showSymptomPicker: false })
  },

  toggleSymptom(e) {
    const key = e.currentTarget.dataset.key
    const pickerSymptoms = this.data.pickerSymptoms.map(s =>
      s.key === key ? { ...s, selected: !s.selected } : s
    )
    this.setData({ pickerSymptoms })
  },

  confirmSymptoms() {
    const selectedKeys = this.data.pickerSymptoms
      .filter(s => s.selected)
      .map(s => s.key)

    if (!selectedKeys.length) {
      wx.showToast({ title: '请至少选择一种症状', icon: 'none' })
      return
    }

    this.setData({
      selectedKeys,
      showSymptomPicker: false,
      conditionsChanged: true,
    })
    this._updateBtnLabel(this.data.allSymptoms, selectedKeys)
    this._rebuildSeries()
  },

  // ── Helpers ────────────────────────────────────────────────────────────────

  _updateBtnLabel(allSymptoms, selectedKeys) {
    const names = selectedKeys.map(k => {
      const s = allSymptoms.find(a => a.key === k)
      return s ? s.name : k
    })
    let label
    if (!names.length) {
      label = '多遇症状'
    } else if (names.length <= 2) {
      label = names.join('、')
    } else {
      label = `${names.slice(0, 2).join('、')}等${names.length}种`
    }
    this.setData({ symptomBtnLabel: label })
  },
})
