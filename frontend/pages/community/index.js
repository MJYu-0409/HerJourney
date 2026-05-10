const theme = require('../../utils/theme')

const MOCK_POSTS = [
  {
    id: "post-10004",
    title: "分享一个小技巧",
    content: "睡前把手机放客厅，真的有用。\n\n不是不看手机就睡着了，是醒了之后抓不到手机，就只能躺着。\n\n躺着躺着，又睡着了。\n\n简单粗暴，但有效。",
    emotion: "轻松",
    emotionColor: "#7AB5A0",
    symptoms: ["失眠", "恢复阶段"],
    stage: "围绝经期",
    tags: ["#技巧", "#睡眠", "#分享"],
    responses: 42,
    createdAt: "2026-05-07T20:10:17.782114"
  },
  {
    id: "post-10019",
    title: "复工了，但学会了说不",
    content: "复工两周了。\n\n有同事让我帮一个项目，我拒绝了。\n\n以前从来不会拒绝的。\n\n现在知道了，说\"不\"不会死，但硬撑会。\n\n身体给的信号，得听。",
    emotion: "轻松中带点硬气",
    emotionColor: "#8E7AB5",
    symptoms: ["恢复阶段", "焦虑"],
    stage: "围绝经期",
    tags: ["#复工", "#学会拒绝", "#恢复"],
    responses: 48,
    createdAt: "2026-05-05T03:45:05.782114"
  },
  {
    id: "post-10024",
    title: "最近平静了很多",
    content: "最近真的平静了很多。\n\n还是会醒，但不慌了。\n\n还是会热，但不烦了。\n\n像学会了跟自己相处。\n\n不是对抗，是共处。\n\n这花了八个月。",
    emotion: "平静中带着感慨",
    emotionColor: "#B8C7D9",
    symptoms: ["夜醒", "恢复阶段"],
    stage: "围绝经期",
    tags: ["#平静", "#恢复", "#共处"],
    responses: 51,
    createdAt: "2026-05-05T02:20:01.782114"
  },
  {
    id: "post-10014",
    title: "一年了，说说现在的情况",
    content: "距离第一次发帖刚好一年。\n\n潮热：偶尔，不碍事了。\n睡眠：能睡整觉了，偶尔会醒。\n情绪：稳定多了，不再莫名其妙想哭。\n\n不是回到20岁的状态，是接受了50岁的状态。\n\n不跟自己较劲了。",
    emotion: "释然",
    emotionColor: "#E7C8D5",
    symptoms: ["恢复阶段"],
    stage: "绝经后",
    tags: ["#一年总结", "#恢复", "#绝经后"],
    responses: 56,
    createdAt: "2026-04-30T21:15:05.782114"
  },
  {
    id: "post-10023",
    title: "又崩溃了，但知道会过去",
    content: "昨天又崩溃了。\n\n无缘无故的，下午坐在沙发上就开始哭。\n\n但奇怪的是，我知道它会过去。\n\n以前崩溃的时候觉得世界末日了，现在知道，过两天就好。\n\n这种\"知道会过去\"的感觉，本身就是一种进步。\n\n虽然当时还是很难受。",
    emotion: "痛苦中带着笃定",
    emotionColor: "#B5A07A",
    symptoms: ["情绪波动", "焦虑"],
    stage: "围绝经期",
    tags: ["#崩溃", "#情绪波动", "#进步"],
    responses: 24,
    createdAt: "2026-04-10T15:30:38.782114"
  },
  {
    id: "post-10008",
    title: "去看了医生，开了点药",
    content: "终于鼓起勇气去看了妇科。\n\n医生很温柔，说围绝经期很正常，给我开了点中药调理。\n\n还说如果症状严重影响生活，可以考虑激素替代疗法，但要先做检查。\n\n先吃药看看，一个月之后复查。\n\n有医生兜底，心里踏实多了。",
    emotion: "踏实又有点忐忑",
    emotionColor: "#7A9EB5",
    symptoms: ["潮热", "失眠", "焦虑"],
    stage: "围绝经期",
    tags: ["#就医", "#药物", "#围绝经期"],
    responses: 19,
    createdAt: "2026-03-26T02:00:47.782114"
  },
  {
    id: "post-10028",
    title: "现在好多了，劝姐妹们别想太多",
    content: "熬了大半年，现在好多了。\n\n潮热还有，但没那么频繁了。\n\n睡眠也还行，虽然还是容易醒，但醒了能再睡着。\n\n我觉得吧，这玩意儿你越在意它越厉害。\n\n别想太多，该吃吃该喝喝，日子照样过。\n\n姐妹们，放宽心。",
    emotion: "豁达",
    emotionColor: "#7AB5A0",
    symptoms: ["恢复阶段", "潮热"],
    stage: "绝经后",
    tags: ["#恢复", "#心态", "#绝经后"],
    responses: 38,
    createdAt: "2026-03-11T09:20:41.782114"
  },
  {
    id: "post-10017",
    title: "HR找我谈话了",
    content: "上午HR找我谈话，说注意到我最近状态不好，问我需不需要调整工作量。\n\n我说不用，我能handle。\n\n但说完就后悔了。\n\n明明handle不住了，还在硬撑。\n\n为什么说不出口呢。",
    emotion: "疲惫加倔强",
    emotionColor: "#B5A07A",
    symptoms: ["焦虑", "疲惫"],
    stage: "围绝经期",
    tags: ["#工作", "#HR", "#burnout"],
    responses: 35,
    createdAt: "2026-02-19T12:00:02.782114"
  },
  {
    id: "post-10022",
    title: "试了心理咨询，有点用",
    content: "去做了六次心理咨询。\n\n不是那种\"聊完就好了\"的用，是慢慢看懂了自己的情绪。\n\n原来那些无缘无故的哭，不是软弱，是身体在释放压力。\n\n咨询师说，更年期情绪波动很正常，不要自责。\n\n这句话对我很重要。\n\n以前总觉得是自己不够坚强。",
    emotion: "释然中有点心酸",
    emotionColor: "#E7C8D5",
    symptoms: ["情绪波动", "焦虑", "恢复阶段"],
    stage: "围绝经期",
    tags: ["#心理咨询", "#情绪", "#恢复"],
    responses: 28,
    createdAt: "2026-01-30T01:55:32.782114"
  },
  {
    id: "post-10016",
    title: "这个月请了三天病假，因为根本起不来",
    content: "不是懒。是真的累。\n\n起床像爬山，走两步就喘，下午开会眼皮打架。\n\n以前加班到凌晨都没事，现在正常下班回家就瘫了。\n\n周末睡了两天，还是累。\n\n不是困，是累。不一样的。\n\nHR问我是不是burnout。\n\n可能是吧。也可能是身体在报警。",
    emotion: "疲惫无力",
    emotionColor: "#B5A07A",
    symptoms: ["疲惫", "失眠", "焦虑"],
    stage: "围绝经期",
    tags: ["#疲惫", "#工作", "#burnout"],
    responses: 27,
    createdAt: "2025-12-11T01:30:27.782114"
  },
  {
    id: "post-10021",
    title: "还是哭，但少了",
    content: "上次发帖是两个月前。\n\n那时候半夜醒来就哭。\n\n现在还是会醒，但不哭了。\n\n就是醒着，躺着，等天亮。\n\n也不是好起来了，是习惯了。\n\n像跟一个不速之客共处一室，刚开始怕，现在知道他不会走了，就算了。\n\n算了。",
    emotion: "淡淡的麻木",
    emotionColor: "#B8C7D9",
    symptoms: ["夜醒", "恢复阶段"],
    stage: "围绝经期",
    tags: ["#夜醒", "#适应", "#情绪"],
    responses: 33,
    createdAt: "2025-11-11T04:00:14.782114"
  },
  {
    id: "post-10020",
    title: "有人跟我一样吗，半夜醒了就开始哭",
    content: "也不是因为什么事。\n\n就是醒了，看看手机，凌晨两点。\n\n然后眼泪就自己出来了。\n\n也不是难过，就是...想哭。\n\n哭一会儿又好了，又睡着了。\n\n第二天早上起来，眼睛肿的，老公问怎么了，我说没睡好。\n\n不能说。说了他也不懂。",
    emotion: "莫名的悲伤",
    emotionColor: "#B8C7D9",
    symptoms: ["夜醒", "情绪波动"],
    stage: "围绝经期",
    tags: ["#夜醒", "#情绪", "#哭泣"],
    responses: 45,
    createdAt: "2025-09-12T00:10:13.782114"
  }
];

function formatTimeAgo(isoString) {
  const now = new Date('2026-05-10T12:00:00');
  const past = new Date(isoString);
  const diffMs = now - past;
  const diffSec = Math.floor(diffMs / 1000);
  const diffMin = Math.floor(diffSec / 60);
  const diffHour = Math.floor(diffMin / 60);
  const diffDay = Math.floor(diffHour / 24);

  if (diffDay > 365) {
    return Math.floor(diffDay / 365) + '年前';
  } else if (diffDay > 30) {
    return Math.floor(diffDay / 30) + '个月前';
  } else if (diffDay > 0) {
    return diffDay + '天前';
  } else if (diffHour > 0) {
    return diffHour + '小时前';
  } else if (diffMin > 0) {
    return diffMin + '分钟前';
  } else {
    return '刚刚';
  }
}

Page({
  data: {
    posts: [],
    filteredPosts: [],
    activeTag: '全部',
    tags: ['全部', '睡眠', '情绪波动', '潮热', '恢复', '就医', '工作'],
    expandedPosts: {},
    searchKeyword: '',
    isDark: false,
  },

  onLoad() {
    this.loadPosts();
  },

  onShow() {
    theme.syncPageTheme(this)
  },

  loadPosts() {
    const posts = MOCK_POSTS.map(post => ({
      ...post,
      timeAgo: formatTimeAgo(post.createdAt),
      resonated: false,
      stayed: false,
      resonateCount: Math.floor(Math.random() * 80) + 5
    }));
    this.setData({
      posts,
      filteredPosts: posts
    });
  },

  onTagTap(e) {
    const tag = e.currentTarget.dataset.tag;
    this.setData({ activeTag: tag });
    this.applyFilter(tag, this.data.searchKeyword);
  },

  applyFilter(tag, keyword) {
    let result = this.data.posts;

    if (tag && tag !== '全部') {
      const tagMap = {
        '睡眠': ['失眠', '夜醒', '睡眠'],
        '情绪波动': ['情绪波动', '焦虑', '烦躁', '情绪'],
        '潮热': ['潮热', '盗汗'],
        '恢复': ['恢复阶段'],
        '就医': ['就医', '药物', '心理咨询'],
        '工作': ['工作', 'HR', 'burnout']
      };
      const keywords = tagMap[tag] || [tag];
      result = result.filter(post => {
        const inSymptoms = post.symptoms.some(s =>
          keywords.some(k => s.indexOf(k) !== -1)
        );
        const inTags = post.tags.some(t =>
          keywords.some(k => t.indexOf(k) !== -1)
        );
        const inContent = keywords.some(k =>
          post.title.indexOf(k) !== -1 || post.content.indexOf(k) !== -1
        );
        return inSymptoms || inTags || inContent;
      });
    }

    if (keyword && keyword.trim()) {
      const kw = keyword.trim().toLowerCase();
      result = result.filter(post => {
        const inTitle = post.title.toLowerCase().indexOf(kw) !== -1;
        const inContent = post.content.toLowerCase().indexOf(kw) !== -1;
        const inTags = post.tags.some(t => t.toLowerCase().indexOf(kw) !== -1);
        const inSymptoms = post.symptoms.some(s => s.toLowerCase().indexOf(kw) !== -1);
        const inStage = post.stage.toLowerCase().indexOf(kw) !== -1;
        const inEmotion = post.emotion.toLowerCase().indexOf(kw) !== -1;
        return inTitle || inContent || inTags || inSymptoms || inStage || inEmotion;
      });
    }

    this.setData({ filteredPosts: result });
  },

  onSearchInput(e) {
    const keyword = e.detail.value;
    this.setData({ searchKeyword: keyword });
    this.applyFilter(this.data.activeTag, keyword);
  },

  onSearchConfirm(e) {
    const keyword = e.detail.value;
    this.setData({ searchKeyword: keyword });
    this.applyFilter(this.data.activeTag, keyword);
  },

  onSearchClear() {
    this.setData({ searchKeyword: '' });
    this.applyFilter(this.data.activeTag, '');
  },

  onExpandTap(e) {
    const id = e.currentTarget.dataset.id;
    const expandedPosts = { ...this.data.expandedPosts };
    expandedPosts[id] = !expandedPosts[id];
    this.setData({ expandedPosts });
  },

  onResonateTap(e) {
    const index = e.currentTarget.dataset.index;
    const post = this.data.filteredPosts[index];
    const newPosts = [...this.data.filteredPosts];
    newPosts[index] = {
      ...post,
      resonated: !post.resonated,
      resonateCount: post.resonated ? post.resonateCount - 1 : post.resonateCount + 1
    };
    this.setData({ filteredPosts: newPosts });
  },

  onRespondTap(e) {
    const id = e.currentTarget.dataset.id;
    wx.showToast({
      title: '回应功能即将上线',
      icon: 'none'
    });
  },

  onStayTap(e) {
    const index = e.currentTarget.dataset.index;
    const post = this.data.filteredPosts[index];
    const newPosts = [...this.data.filteredPosts];
    newPosts[index] = {
      ...post,
      stayed: !post.stayed
    };
    this.setData({ filteredPosts: newPosts });
    wx.showToast({
      title: post.stayed ? '已从留下来移除' : '已留下来',
      icon: 'none'
    });
  }
});
