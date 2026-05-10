import { api, BASE } from '../../../utils/api'

function fullAvatar(url) {
  if (!url) return ''
  return url.startsWith('http') ? url : BASE + url
}

const STAGE_OPTIONS = [
  { value: 'premenopause', label: '绝经前期' },
  { value: 'perimenopause', label: '围绝经期' },
  { value: 'postmenopause', label: '绝经后期' },
]

Page({
  data: {
    userInfo: { nickname: '', avatar_url: '', birth_year: null, menopause_stage: '' },
    stageOptions: STAGE_OPTIONS,
    stageIndex: -1,
    saving: false,
    uploading: false,
  },

  onLoad() {
    this._loadUser()
  },

  async _loadUser() {
    try {
      const info = await api.getUserMe()
      const stageIndex = STAGE_OPTIONS.findIndex(o => o.value === info.menopause_stage)
      this.setData({
        userInfo: {
          nickname: info.nickname || '',
          avatar_url: fullAvatar(info.avatar_url) || '',
          birth_year: info.birth_year || null,
          menopause_stage: info.menopause_stage || '',
        },
        stageIndex: stageIndex >= 0 ? stageIndex : -1,
      })
    } catch (e) {
      wx.showToast({ title: '加载失败', icon: 'none' })
    }
  },

  // ── 头像更换 ──────────────────────────────────────────────────────────────

  onChangeAvatar() {
    wx.showActionSheet({
      itemList: ['从相册选择', '拍照'],
      success: (res) => {
        const sourceType = res.tapIndex === 0 ? ['album'] : ['camera']
        wx.chooseMedia({
          count: 1,
          mediaType: ['image'],
          sourceType,
          success: (mediaRes) => {
            const tempFile = mediaRes.tempFiles[0].tempFilePath
            this._doUploadAvatar(tempFile)
          },
        })
      },
    })
  },

  async _doUploadAvatar(filePath) {
    this.setData({ uploading: true })
    try {
      const res = await api.uploadAvatar(filePath)
      this.setData({ 'userInfo.avatar_url': fullAvatar(res.avatar_url) })
      wx.showToast({ title: '头像已更新', icon: 'success' })
    } catch (e) {
      wx.showToast({ title: '上传失败', icon: 'none' })
    } finally {
      this.setData({ uploading: false })
    }
  },

  // ── 表单输入 ──────────────────────────────────────────────────────────────

  onNicknameInput(e) {
    this.setData({ 'userInfo.nickname': e.detail.value })
  },

  onBirthYearInput(e) {
    const val = e.detail.value
    this.setData({ 'userInfo.birth_year': val ? parseInt(val, 10) : null })
  },

  onStageChange(e) {
    const index = parseInt(e.detail.value, 10)
    this.setData({
      stageIndex: index,
      'userInfo.menopause_stage': STAGE_OPTIONS[index].value,
    })
  },

  // ── 保存 ──────────────────────────────────────────────────────────────────

  async onSave() {
    const { nickname, birth_year, menopause_stage } = this.data.userInfo

    if (!nickname || nickname.trim().length === 0) {
      wx.showToast({ title: '请输入昵称', icon: 'none' })
      return
    }

    this.setData({ saving: true })
    try {
      await api.updateUser({
        nickname: nickname.trim(),
        birth_year,
        menopause_stage,
      })
      wx.showToast({ title: '保存成功', icon: 'success' })
      setTimeout(() => wx.navigateBack(), 800)
    } catch (e) {
      wx.showToast({ title: '保存失败', icon: 'none' })
    } finally {
      this.setData({ saving: false })
    }
  },
})
