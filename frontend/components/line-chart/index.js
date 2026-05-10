// Canvas padding (logical px)
const PAD = { l: 36, r: 12, t: 16, b: 32 }

// Build date → series-items index for tooltip
function buildDateMap(series) {
  const map = {}
  series.forEach(({ name, color, dataPoints }) => {
    ;(dataPoints || []).forEach(p => {
      if (!map[p.date]) map[p.date] = []
      map[p.date].push({ name, color, score: p.score })
    })
  })
  return map
}

// Bezier smooth line through an array of {x, y} points
function drawSmooth(ctx, pts) {
  if (!pts.length) return
  ctx.moveTo(pts[0].x, pts[0].y)
  if (pts.length === 1) return
  for (let i = 1; i < pts.length; i++) {
    const cx = (pts[i - 1].x + pts[i].x) / 2
    ctx.bezierCurveTo(cx, pts[i - 1].y, cx, pts[i].y, pts[i].x, pts[i].y)
  }
}

Component({
  properties: {
    series:  { type: Array,   value: [] },
    loading: { type: Boolean, value: false },
  },

  data: {
    tooltip: { show: false, x: 0, y: 0, date: '', items: [] },
  },

  observers: {
    'series, loading': function () { this._draw() },
  },

  lifetimes: {
    ready() { this._init() },
  },

  methods: {
    // ── Init ──────────────────────────────────────────────────────────────────

    _init() {
      this.createSelectorQuery()
        .select('#lc')
        .fields({ node: true, size: true, rect: true })
        .exec(([info]) => {
          if (!info?.node) return
          const dpr = wx.getWindowInfo().pixelRatio
          const canvas = info.node
          canvas.width  = Math.round(info.width  * dpr)
          canvas.height = Math.round(info.height * dpr)
          const ctx = canvas.getContext('2d')
          ctx.scale(dpr, dpr)
          this._canvas    = canvas
          this._ctx       = ctx
          this._W         = info.width
          this._H         = info.height
          this._rectLeft  = info.left
          this._rectTop   = info.top
          this._draw()
        })
    },

    // ── Axis helpers ──────────────────────────────────────────────────────────

    _buildAxes() {
      const series = this.data.series
      const dateSet = new Set()
      series.forEach(s => (s.dataPoints || []).forEach(p => dateSet.add(p.date)))
      const dates = [...dateSet].sort()
      if (!dates.length) return null
      const minT = +new Date(dates[0])
      const maxT = +new Date(dates[dates.length - 1])
      const rangeT = maxT === minT ? 86400000 : maxT - minT
      const plotW = this._W - PAD.l - PAD.r
      const plotH = this._H - PAD.t - PAD.b
      const toX = d => PAD.l + (+new Date(d) - minT) / rangeT * plotW
      const toY = s => PAD.t + plotH * (1 - (s - 1) / 4)
      return { dates, minT, rangeT, toX, toY, plotW, plotH }
    },

    // ── Draw ──────────────────────────────────────────────────────────────────

    _draw() {
      const ctx = this._ctx
      if (!ctx) return
      const { _W: W, _H: H } = this
      ctx.clearRect(0, 0, W, H)

      if (this.data.loading) {
        ctx.fillStyle = '#B8B0C5'
        ctx.font = '14px sans-serif'
        ctx.textAlign = 'center'
        ctx.textBaseline = 'middle'
        ctx.fillText('数据加载中…', W / 2, H / 2)
        return
      }

      const series = this.data.series || []
      const ax = this._buildAxes()
      if (!ax) return
      const { dates, toX, toY, plotW, plotH } = ax

      // ── Y grid + labels ───────────────────────────────────────────────────
      for (let score = 1; score <= 5; score++) {
        const y = toY(score)
        ctx.save()
        ctx.strokeStyle = '#EDE8F4'
        ctx.lineWidth = 1
        ctx.beginPath()
        ctx.moveTo(PAD.l, y)
        ctx.lineTo(W - PAD.r, y)
        ctx.stroke()
        ctx.fillStyle = '#B8B0C5'
        ctx.font = '11px sans-serif'
        ctx.textAlign = 'right'
        ctx.textBaseline = 'middle'
        ctx.fillText(String(score), PAD.l - 6, y)
        ctx.restore()
      }

      // ── X labels ──────────────────────────────────────────────────────────
      {
        const maxLabels = Math.max(2, Math.floor(plotW / 52))
        const step = Math.max(1, Math.floor(dates.length / maxLabels))
        const shown = new Set()
        ctx.save()
        ctx.fillStyle = '#B8B0C5'
        ctx.font = '11px sans-serif'
        ctx.textAlign = 'center'
        ctx.textBaseline = 'top'
        for (let i = 0; i < dates.length; i += step) {
          const d = new Date(dates[i])
          ctx.fillText(`${d.getMonth() + 1}/${d.getDate()}`, toX(dates[i]), H - PAD.b + 5)
          shown.add(i)
        }
        const last = dates.length - 1
        if (!shown.has(last)) {
          const d = new Date(dates[last])
          ctx.fillText(`${d.getMonth() + 1}/${d.getDate()}`, toX(dates[last]), H - PAD.b + 5)
        }
        ctx.restore()
      }

      // ── Series ────────────────────────────────────────────────────────────
      series.forEach(({ color, dataPoints }) => {
        if (!dataPoints?.length) return
        const pts = [...dataPoints]
          .sort((a, b) => (a.date < b.date ? -1 : 1))
          .map(p => ({ x: toX(p.date), y: toY(p.score) }))

        if (pts.length === 1) {
          ctx.save()
          ctx.beginPath()
          ctx.arc(pts[0].x, pts[0].y, 4, 0, Math.PI * 2)
          ctx.fillStyle = color
          ctx.fill()
          ctx.restore()
          return
        }

        // Area gradient fill
        ctx.save()
        const grad = ctx.createLinearGradient(0, PAD.t, 0, H - PAD.b)
        grad.addColorStop(0, color + '40')
        grad.addColorStop(1, color + '00')
        ctx.beginPath()
        drawSmooth(ctx, pts)
        ctx.lineTo(pts[pts.length - 1].x, H - PAD.b)
        ctx.lineTo(pts[0].x, H - PAD.b)
        ctx.closePath()
        ctx.fillStyle = grad
        ctx.fill()
        ctx.restore()

        // Line stroke
        ctx.save()
        ctx.strokeStyle = color
        ctx.lineWidth = 2
        ctx.lineJoin = 'round'
        ctx.lineCap = 'round'
        ctx.beginPath()
        drawSmooth(ctx, pts)
        ctx.stroke()
        ctx.restore()

        // Dots
        pts.forEach(p => {
          ctx.save()
          ctx.beginPath()
          ctx.arc(p.x, p.y, 3.5, 0, Math.PI * 2)
          ctx.fillStyle = '#FFFFFF'
          ctx.fill()
          ctx.strokeStyle = color
          ctx.lineWidth = 1.5
          ctx.stroke()
          ctx.restore()
        })
      })

      // ── Tooltip indicator line ────────────────────────────────────────────
      if (this._tipX !== undefined) {
        ctx.save()
        ctx.strokeStyle = 'rgba(142,122,181,0.45)'
        ctx.lineWidth = 1.5
        ctx.setLineDash([4, 4])
        ctx.beginPath()
        ctx.moveTo(this._tipX, PAD.t)
        ctx.lineTo(this._tipX, H - PAD.b)
        ctx.stroke()
        // Highlight dots at this x for each series
        series.forEach(({ color, dataPoints }) => {
          const allDates = ax.dates
          let closest = null, minD = Infinity
          ;(dataPoints || []).forEach(p => {
            const dist = Math.abs(toX(p.date) - this._tipX)
            if (dist < minD) { minD = dist; closest = p }
          })
          if (closest && minD < 16) {
            ctx.beginPath()
            ctx.arc(toX(closest.date), toY(closest.score), 5, 0, Math.PI * 2)
            ctx.fillStyle = color
            ctx.fill()
          }
        })
        ctx.restore()
      }
    },

    // ── Touch ─────────────────────────────────────────────────────────────────

    onTouchStart(e) { this._onTouch(e) },
    onTouchMove(e)  { this._onTouch(e) },
    onTouchEnd()    {
      this._tipX = undefined
      this.setData({ 'tooltip.show': false })
      this._draw()
    },

    _onTouch(e) {
      if (!this._canvas || !e.touches.length) return
      const series = this.data.series
      if (!series?.length) return

      const ax = this._buildAxes()
      if (!ax) return
      const { dates, toX, toY } = ax

      const touchX = e.touches[0].clientX - (this._rectLeft || 0)

      // Find date closest to touchX
      let closest = dates[0], minDist = Infinity
      dates.forEach(d => {
        const dist = Math.abs(toX(d) - touchX)
        if (dist < minDist) { minDist = dist; closest = d }
      })

      this._tipX = toX(closest)

      // Build tooltip items (all series at this date)
      const dateMap = buildDateMap(series)
      const d = new Date(closest)
      const dateLabel = `${d.getMonth() + 1}月${d.getDate()}日`
      const items = series.map(({ name, color }) => {
        const entry = (dateMap[closest] || []).find(it => it.name === name)
        return { name, color, score: entry ? entry.score : '—' }
      })

      // Clamp tooltip so it doesn't overflow
      const tipW = 145
      let tipLeft = this._tipX + 10
      if (tipLeft + tipW > this._W - 8) tipLeft = this._tipX - tipW - 10

      this.setData({
        tooltip: {
          show: true,
          x: Math.max(4, tipLeft),
          y: 16,
          date: dateLabel,
          items,
        },
      })
      this._draw()
    },
  },
})
