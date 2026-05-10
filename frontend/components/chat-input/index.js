const recorderManager = wx.getRecorderManager()

Component({
  properties: {
    disabled: { type: Boolean, value: false },
  },

  data: {
    mode: 'text',        // 'text' | 'voice'
    inputValue: '',
    hasText: false,
    pressing: false,
    showExtra: false,
    keyboardShow: false,
    // 语音录制状态
    voiceStartY: 0,
    voiceCancelled: false,
  },

  lifetimes: {
    attached() {
      recorderManager.onStop((res) => {
        this.triggerEvent('voiceEnd', {
          tempFilePath: res.tempFilePath,
          duration: res.duration,
          cancelled: this.data.voiceCancelled,
        })
      })
      recorderManager.onError(() => {
        this.setData({ pressing: false })
        wx.showToast({ title: '录音失败', icon: 'none' })
      })
    },
  },

  methods: {
    // ── 模式切换 ────────────────────────────────────────────────────────────

    toggleMode() {
      const next = this.data.mode === 'text' ? 'voice' : 'text'
      this.setData({ mode: next, showExtra: false })
    },

    // ── 文字输入 ────────────────────────────────────────────────────────────

    onInput(e) {
      const v = e.detail.value
      this.setData({ inputValue: v, hasText: v.trim().length > 0 })
    },

    onFocus() {
      this.setData({ keyboardShow: true, showExtra: false })
    },

    onBlur() {
      this.setData({ keyboardShow: false })
    },

    onConfirm() {
      this._doSend()
    },

    onSendTap() {
      this._doSend()
    },

    _doSend() {
      const v = this.data.inputValue.trim()
      if (!v || this.data.disabled) return
      this.triggerEvent('send', { value: v })
      this.setData({ inputValue: '', hasText: false })
    },

    // ── 语音录制 ────────────────────────────────────────────────────────────

    onTouchStart(e) {
      if (this.data.disabled) return
      const startY = e.touches[0].clientY
      this.setData({ pressing: true, voiceStartY: startY, voiceCancelled: false })
      this.triggerEvent('recordingChange', { recording: true })

      wx.authorize({ scope: 'scope.record' }).then(() => {
        recorderManager.start({ duration: 60000, format: 'mp3', sampleRate: 16000 })
      }).catch(() => {
        this.setData({ pressing: false })
        wx.showModal({
          title: '需要麦克风权限',
          content: '请在设置中开启麦克风权限',
          showCancel: false,
        })
      })
    },

    onTouchMove(e) {
      if (!this.data.pressing) return
      const dy = this.data.voiceStartY - e.touches[0].clientY
      const cancelled = dy > 80
      this.setData({ voiceCancelled: cancelled })
    },

    onTouchEnd() {
      if (!this.data.pressing) return
      this.setData({ pressing: false })
      this.triggerEvent('recordingChange', { recording: false })
      recorderManager.stop()
    },

    // ── 扩展面板 ────────────────────────────────────────────────────────────

    onPlusTap() {
      wx.hideKeyboard()
      this.setData({ showExtra: !this.data.showExtra })
    },

    chooseImage() {
      wx.chooseMedia({
        count: 9,
        mediaType: ['image'],
        sourceType: ['album', 'camera'],
        success: (res) => {
          this.triggerEvent('mediaChoose', { type: '图片', files: res.tempFiles })
          this.setData({ showExtra: false })
        },
      })
    },

    chooseVideo() {
      wx.chooseMedia({
        count: 1,
        mediaType: ['video'],
        sourceType: ['album', 'camera'],
        maxDuration: 60,
        success: (res) => {
          this.triggerEvent('mediaChoose', { type: '视频', files: res.tempFiles })
          this.setData({ showExtra: false })
        },
      })
    },

    onFileTap() {
      wx.showToast({ title: '文件上传暂未开放', icon: 'none' })
    },

    onLocationTap() {
      wx.showToast({ title: '位置暂未开放', icon: 'none' })
    },
  },
})
