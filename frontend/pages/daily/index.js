import { api } from '../../utils/api'
const theme = require('../../utils/theme')

// ── Constants ─────────────────────────────────────────────────────────────────

const OVERALL_OPTS = [
  { score: 1, emoji: '😊', label: '很好' },
  { score: 2, emoji: '🙂', label: '较好' },
  { score: 3, emoji: '😐', label: '一般' },
  { score: 4, emoji: '😔', label: '较差' },
  { score: 5, emoji: '😰', label: '很差' },
]

const SCORE_OPTS = [
  { score: 1, label: '无' },
  { score: 2, label: '轻' },
  { score: 3, label: '中' },
  { score: 4, label: '重' },
  { score: 5, label: '极重' },
]

const CATEGORIES = [
  {
    title: '血管舒缩症状',
    icon: '🌡',
    symptoms: [
      { key: 'hot_flash',   name: '潮热',   selected: false, score: 3 },
      { key: 'night_sweat', name: '夜间盗汗', selected: false, score: 3 },
      { key: 'palpitation', name: '心慌心悸', selected: false, score: 3 },
    ],
  },
  {
    title: '精神情绪症状',
    icon: '💭',
    symptoms: [
      { key: 'mood_swing',    name: '烦躁易怒',  selected: false, score: 3 },
      { key: 'anxiety',       name: '焦虑紧张',  selected: false, score: 3 },
      { key: 'depression',    name: '情绪低落',  selected: false, score: 3 },
      { key: 'concentration', name: '注意力涣散', selected: false, score: 3 },
    ],
  },
  {
    title: '睡眠障碍',
    icon: '🌙',
    symptoms: [
      { key: 'sleep_onset', name: '入睡困难', selected: false, score: 3 },
      { key: 'sleep_wake',  name: '夜间易醒', selected: false, score: 3 },
      { key: 'early_wake',  name: '早醒',    selected: false, score: 3 },
    ],
  },
  {
    title: '躯体症状',
    icon: '🦴',
    symptoms: [
      { key: 'vaginal_dryness',  name: '阴道干涩',   selected: false, score: 3 },
      { key: 'urinary_urgency',  name: '尿频尿急',   selected: false, score: 3 },
      { key: 'uti',              name: '反复尿路感染', selected: false, score: 3 },
      { key: 'joint_pain',       name: '关节骨骼酸痛', selected: false, score: 3 },
      { key: 'fatigue',          name: '乏力疲惫',   selected: false, score: 3 },
    ],
  },
]

const MED_OPTS = [
  { val: '中药调理',   label: '中药调理' },
  { val: '激素治疗',   label: '激素治疗' },
  { val: '钙片/维生素', label: '钙片/维生素' },
  { val: '助眠药物',   label: '助眠药物' },
  { val: '其他',       label: '其他' },
]

const FLOW_OPTS = [
  { val: 1, label: '少' },
  { val: 2, label: '中' },
  { val: 3, label: '多' },
]

const ABNORMAL_OPTS = [
  { val: 'none',       label: '无异常' },
  { val: 'prolonged',  label: '淋漓不尽' },
  { val: 'irregular',  label: '非经期出血' },
]

const WEIGHT_OPTS = [
  { val: 'increase', label: '增加' },
  { val: 'stable',   label: '稳定' },
  { val: 'decrease', label: '减少' },
]

const BP_OPTS = [
  { val: 'low',    label: '偏低' },
  { val: 'normal', label: '正常' },
  { val: 'high',   label: '偏高' },
  { val: 'very_high', label: '高' },
]

const DAY_RANGE = Array.from({ length: 14 }, (_, i) => i + 1)

// ── Helpers ───────────────────────────────────────────────────────────────────

function todayFormatted() {
  const d = new Date()
  return `${d.getFullYear()}年${d.getMonth() + 1}月${d.getDate()}日`
}

function greeting() {
  const h = new Date().getHours()
  if (h < 6)  return '深夜好'
  if (h < 12) return '早上好'
  if (h < 14) return '中午好'
  if (h < 18) return '下午好'
  return '晚上好'
}

function getISOWeekKey() {
  const d = new Date()
  d.setHours(0, 0, 0, 0)
  d.setDate(d.getDate() + 4 - (d.getDay() || 7))
  const year = d.getFullYear()
  const week = Math.ceil(((d - new Date(year, 0, 1)) / 86400000 + 1) / 7)
  return `${year}-W${week}`
}

// ── Page ──────────────────────────────────────────────────────────────────────

Page({
  data: {
    isDark: false,

    // Header
    todayLabel: todayFormatted(),
    greetingText: greeting(),
    nickname: '姐妹',
    alreadyChecked: false,

    // Form state
    overallScore: null,
    categories: CATEGORIES.map(cat => ({
      ...cat,
      symptoms: cat.symptoms.map(s => ({ ...s })),
    })),
    menstrualStatus: 'none',
    menstrualDayIdx: 0,
    menstrualFlow: null,
    menstrualPain: null,
    menstrualAbnormal: [],
    medications: [],
    notes: '',

    // Weekly
    weeklyDone: false,
    weeklyWeight: '',
    weeklyBP: '',
    weeklyJoint: null,
    weeklyLibido: '',

    // Submit
    submitting: false,

    // Constants for template
    OVERALL_OPTS,
    SCORE_OPTS,
    MED_OPTS,
    FLOW_OPTS,
    ABNORMAL_OPTS,
    WEIGHT_OPTS,
    BP_OPTS,
    DAY_RANGE,
  },

  onLoad() {
    this._checkWeekly()
    this._loadUserAndToday()
  },

  onShow() {
    theme.syncPageTheme(this)
  },

  // ── Init ──────────────────────────────────────────────────────────────────

  async _loadUserAndToday() {
    try {
      const [userInfo, todayRes] = await Promise.all([
        api.getUserMe(),
        api.getTodaySurvey(),
      ])
      this.setData({
        nickname: userInfo.nickname || '姐妹',
        alreadyChecked: todayRes.completed,
        overallScore: todayRes.overall_score || null,
      })
    } catch (_) {}
  },

  _checkWeekly() {
    const lastKey = wx.getStorageSync('weeklyCheckKey')
    this.setData({ weeklyDone: lastKey === getISOWeekKey() })
  },

  // ── Overall score ─────────────────────────────────────────────────────────

  setOverall(e) {
    this.setData({ overallScore: e.currentTarget.dataset.score })
  },

  // ── Symptom chips & scoring ───────────────────────────────────────────────

  toggleSymptom(e) {
    const { cat, idx } = e.currentTarget.dataset
    const sym = this.data.categories[cat].symptoms[idx]
    const base = `categories[${cat}].symptoms[${idx}]`
    if (!sym.selected) {
      this.setData({ [`${base}.selected`]: true })
    } else {
      this.setData({ [`${base}.selected`]: false })
    }
  },

  setScore(e) {
    const { cat, idx, score } = e.currentTarget.dataset
    this.setData({ [`categories[${cat}].symptoms[${idx}].score`]: score })
  },

  // ── Menstrual ─────────────────────────────────────────────────────────────

  setMenstrual(e) {
    this.setData({ menstrualStatus: e.currentTarget.dataset.val })
  },

  onMenstrualDay(e) {
    this.setData({ menstrualDayIdx: Number(e.detail.value) })
  },

  setFlow(e) {
    this.setData({ menstrualFlow: e.currentTarget.dataset.val })
  },

  setPain(e) {
    this.setData({ menstrualPain: e.currentTarget.dataset.score })
  },

  toggleAbnormal(e) {
    const val = e.currentTarget.dataset.val
    const list = [...this.data.menstrualAbnormal]
    const idx = list.indexOf(val)
    if (val === 'none') {
      this.setData({ menstrualAbnormal: idx === -1 ? ['none'] : [] })
      return
    }
    const noNone = list.filter(v => v !== 'none')
    if (idx === -1) noNone.push(val)
    else noNone.splice(list.indexOf(val), 1)
    this.setData({ menstrualAbnormal: noNone })
  },

  // ── Medication ────────────────────────────────────────────────────────────

  toggleMed(e) {
    const val = e.currentTarget.dataset.val
    const list = [...this.data.medications]
    const idx = list.indexOf(val)
    if (idx === -1) list.push(val)
    else list.splice(idx, 1)
    this.setData({ medications: list })
  },

  // ── Notes ─────────────────────────────────────────────────────────────────

  onNotes(e) {
    this.setData({ notes: e.detail.value })
  },

  // ── Weekly ────────────────────────────────────────────────────────────────

  setWeeklyWeight(e) { this.setData({ weeklyWeight: e.currentTarget.dataset.val }) },
  setWeeklyBP(e)     { this.setData({ weeklyBP: e.currentTarget.dataset.val }) },

  setWeeklyJoint(e) {
    this.setData({ weeklyJoint: e.currentTarget.dataset.val === 'true' })
  },

  setWeeklyLibido(e) {
    this.setData({ weeklyLibido: e.currentTarget.dataset.val })
  },

  skipWeekly() {
    wx.setStorageSync('weeklyCheckKey', getISOWeekKey())
    this.setData({ weeklyDone: true })
  },

  // ── Submit ────────────────────────────────────────────────────────────────

  async onSubmit() {
    if (this.data.submitting) return

    if (!this.data.overallScore) {
      wx.showToast({ title: '请先为今日状态打分', icon: 'none' })
      return
    }

    // Build symptoms dict from selected
    const symptoms = {}
    this.data.categories.forEach(cat => {
      cat.symptoms.forEach(sym => {
        if (sym.selected) symptoms[sym.key] = sym.score
      })
    })

    // Medication list
    const medication = this.data.medications.length ? this.data.medications : null

    // Weekly data dict
    let weekly_data = null
    if (!this.data.weeklyDone && this._weeklyHasData()) {
      const { weeklyWeight, weeklyBP, weeklyJoint, weeklyLibido } = this.data
      weekly_data = {}
      if (weeklyWeight) weekly_data.weight = weeklyWeight
      if (weeklyBP)     weekly_data.bp = weeklyBP
      if (weeklyJoint !== null) weekly_data.joint = weeklyJoint
      if (weeklyLibido) weekly_data.libido = weeklyLibido
    }

    // Menstrual
    const isPeriod = this.data.menstrualStatus === 'period'
    const body = {
      overall_score: this.data.overallScore,
      symptoms,
      medication,
      weekly_data,
      notes: this.data.notes || null,
      menstrual_status: this.data.menstrualStatus,
      menstrual_day: isPeriod ? this.data.DAY_RANGE[this.data.menstrualDayIdx] : null,
      menstrual_flow: isPeriod ? this.data.menstrualFlow : null,
      menstrual_pain: isPeriod ? this.data.menstrualPain : null,
      menstrual_abnormal: isPeriod && this.data.menstrualAbnormal.length
        ? this.data.menstrualAbnormal
        : null,
    }

    this.setData({ submitting: true })
    try {
      await api.submitSurvey(body)

      // Mark weekly done if fields were filled
      if (!this.data.weeklyDone && this._weeklyHasData()) {
        wx.setStorageSync('weeklyCheckKey', getISOWeekKey())
        this.setData({ weeklyDone: true })
      }

      wx.showToast({ title: '打卡成功 ✨', icon: 'none', duration: 2000 })
      setTimeout(() => {
        wx.switchTab({ url: '/pages/profile/index' })
      }, 1800)
    } catch (_) {
      wx.showToast({ title: '提交失败，请重试', icon: 'none' })
    } finally {
      this.setData({ submitting: false })
    }
  },

  _weeklyHasData() {
    const { weeklyWeight, weeklyBP, weeklyJoint, weeklyLibido } = this.data
    return weeklyWeight || weeklyBP || weeklyJoint !== null || weeklyLibido
  },
})
