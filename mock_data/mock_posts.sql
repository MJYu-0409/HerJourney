-- 社区帖子 Mock 数据
DELETE FROM posts WHERE user_id IS NOT NULL;  -- 保留可能的官方帖

INSERT INTO posts (id, user_id, post_type, title, content, images, voice_url, tags, is_ai_generated, status, likes, views, created_at, published_at) VALUES ('4083d376-1741-438c-bc39-b83c915aa02c', 'user-8094', 'report', '我的30天症状报告：潮热改善明显', '连续打卡30天后，生成了我的第一份症状报告。

数据显示：
- 潮热：从平均4.2分降到2.1分 ⬇️
- 盗汗：从3.8分降到1.9分 ⬇️
- 睡眠：从4.5分降到2.8分 ⬇️
- 情绪：基本稳定在3分左右

AI 解读说我的心血管相关症状呈现明显下降趋势，建议继续保持当前的作息和运动习惯。

把这份报告分享到社区，希望能给有类似症状的姐妹一些参考。', NULL, NULL, '["#症状报告", "#潮热", "#数据记录", "#围绝经期"]', false, 'published', 168, 1738, '2026-05-10T11:01:21.836528', '2026-05-10T11:01:21.836528');
INSERT INTO posts (id, user_id, post_type, title, content, images, voice_url, tags, is_ai_generated, status, likes, views, created_at, published_at) VALUES ('229cb10b-f141-4584-8bac-53146e077d7d', 'user-9904', 'general', '有没有推荐的更年期保健品？', '最近想补充一些营养素，大豆异黄酮和钙片是必买的，还在考虑要不要加维生素D。姐妹们有什么推荐或者踩坑经验吗？', NULL, NULL, '["#保健品", "#求助", "#围绝经期"]', false, 'published', 147, 1284, '2026-05-10T09:36:21.836528', '2026-05-10T09:36:21.836528');
INSERT INTO posts (id, user_id, post_type, title, content, images, voice_url, tags, is_ai_generated, status, likes, views, created_at, published_at) VALUES ('bb46aa86-d88a-491f-bc0b-44cf6dcfbaa0', 'user-1931', 'experience', '失眠的日子，我是怎么熬过来的', '更年期失眠真的太折磨人了。以前躺下就能睡着，现在半夜两三点眼睛还睁得大大的。

分享一下我的"睡眠修复计划"：

- 固定作息：不管几点睡着，早上七点准时起床
- 午睡控制：最多20分钟，下午三点后不再睡
- 卧室改造：换了遮光窗帘，买了白噪音机
- 放松训练：睡前做渐进式肌肉放松

最重要的，是接受"现在睡眠质量不如以前"这个事实。不焦虑，反而更容易睡着。', NULL, NULL, '["#睡眠障碍", "#失眠", "#情绪管理", "#围绝经期"]', false, 'published', 174, 1524, '2026-05-10T09:17:21.836528', '2026-05-10T09:17:21.836528');
INSERT INTO posts (id, user_id, post_type, title, content, images, voice_url, tags, is_ai_generated, status, likes, views, created_at, published_at) VALUES ('9676fcda-2485-4fae-b82c-59ba20008487', 'user-9075', 'report', '我的30天症状报告：潮热改善明显', '连续打卡30天后，生成了我的第一份症状报告。

数据显示：
- 潮热：从平均4.2分降到2.1分 ⬇️
- 盗汗：从3.8分降到1.9分 ⬇️
- 睡眠：从4.5分降到2.8分 ⬇️
- 情绪：基本稳定在3分左右

AI 解读说我的心血管相关症状呈现明显下降趋势，建议继续保持当前的作息和运动习惯。

把这份报告分享到社区，希望能给有类似症状的姐妹一些参考。', NULL, NULL, '["#症状报告", "#潮热", "#数据记录", "#围绝经期"]', false, 'published', 143, 1700, '2026-05-10T04:59:21.836528', '2026-05-10T04:59:21.836528');
INSERT INTO posts (id, user_id, post_type, title, content, images, voice_url, tags, is_ai_generated, status, likes, views, created_at, published_at) VALUES ('f9b3ab50-3973-4974-a177-36064971e5c0', 'user-9535', 'experience', '失眠的日子，我是怎么熬过来的', '更年期失眠真的太折磨人了。以前躺下就能睡着，现在半夜两三点眼睛还睁得大大的。

分享一下我的"睡眠修复计划"：

- 固定作息：不管几点睡着，早上七点准时起床
- 午睡控制：最多20分钟，下午三点后不再睡
- 卧室改造：换了遮光窗帘，买了白噪音机
- 放松训练：睡前做渐进式肌肉放松

最重要的，是接受"现在睡眠质量不如以前"这个事实。不焦虑，反而更容易睡着。', NULL, NULL, '["#睡眠障碍", "#失眠", "#情绪管理", "#围绝经期"]', false, 'published', 74, 1102, '2026-05-10T03:39:21.836528', '2026-05-10T03:39:21.836528');
INSERT INTO posts (id, user_id, post_type, title, content, images, voice_url, tags, is_ai_generated, status, likes, views, created_at, published_at) VALUES ('04e99a5b-5248-4d46-a452-1b513da49888', 'user-1901', 'general', '今天去医院做了骨密度检查', '医生建议围绝经期女性每年做一次骨密度检查，今天去做了，结果正常。医生说要多补钙、多晒太阳、适当运动。姐妹们有定期检查吗？', NULL, NULL, '["#骨骼健康", "#医院检查", "#围绝经期"]', false, 'published', 140, 982, '2026-05-10T02:41:21.836528', '2026-05-10T02:41:21.836528');
INSERT INTO posts (id, user_id, post_type, title, content, images, voice_url, tags, is_ai_generated, status, likes, views, created_at, published_at) VALUES ('8d0b122b-1e94-4e3c-bb10-e5e4ea6acb70', 'user-5453', 'report', '围绝经期第一个月的数据记录', '刚开始用小程序记录症状，第一个月的数据出来了。

整体来看，我的症状集中在几个方面：
1. 心血管：潮热和盗汗比较严重
2. 情绪：烦躁和焦虑交替出现
3. 睡眠：入睡困难，容易早醒

通过记录发现，经期前后症状会加重，这是一个规律。下个月准备重点调整饮食，看看能不能有改善。', NULL, NULL, '["#症状报告", "#围绝经期", "#数据记录"]', false, 'published', 281, 1945, '2026-05-10T01:42:21.836528', '2026-05-10T01:42:21.836528');
INSERT INTO posts (id, user_id, post_type, title, content, images, voice_url, tags, is_ai_generated, status, likes, views, created_at, published_at) VALUES ('e1b56dc5-35d2-4baf-8601-33c4ac650b4f', 'user-1964', 'experience', '潮热盗汗三个月后，我终于找到了缓解方法', '从去年秋天开始，潮热和盗汗突然找上门来。最严重的时候，一天要换两三件衣服，晚上更是睡不安稳。

我试过好几种方法，最后发现这三招对我最有效：

1. 穿分层衣服：棉质打底+薄外套，热的时候能快速脱掉
2. 睡前泡脚：用40度左右的温水泡15分钟，反而能让身体更容易降温
3. 饮食调整：少喝咖啡和酒，多吃豆制品

现在三个月过去了，虽然还会潮热，但频率和强度都明显降低了。姐妹们不要慌，这是一个可以管理的过程。', NULL, NULL, '["#潮热", "#盗汗", "#经验分享", "#围绝经期"]', false, 'published', 23, 180, '2026-05-10T01:01:21.836528', '2026-05-10T01:01:21.836528');
INSERT INTO posts (id, user_id, post_type, title, content, images, voice_url, tags, is_ai_generated, status, likes, views, created_at, published_at) VALUES ('cb8b98b2-c452-41b9-bf7f-66515b927a4a', 'user-9646', 'general', '有没有推荐的更年期保健品？', '最近想补充一些营养素，大豆异黄酮和钙片是必买的，还在考虑要不要加维生素D。姐妹们有什么推荐或者踩坑经验吗？', NULL, NULL, '["#保健品", "#求助", "#围绝经期"]', false, 'published', 106, 1304, '2026-05-09T23:46:21.836528', '2026-05-09T23:46:21.836528');
INSERT INTO posts (id, user_id, post_type, title, content, images, voice_url, tags, is_ai_generated, status, likes, views, created_at, published_at) VALUES ('0bf8a6fa-1578-4fd0-b1de-5faa28d1ad69', 'user-2212', 'experience', '给刚进入更年期的姐妹：这些症状都是正常的', '48岁那年，我第一次出现潮热的时候，以为自己得了什么大病。跑了好几次医院，检查结果都是"正常"。

后来我才慢慢了解，这些都是更年期的正常表现：
- 突然的潮热和出汗
- 情绪波动，容易烦躁
- 记忆力下降，忘东忘西
- 睡眠质量变差
- 关节疼痛

知道这是正常的，心理压力就小了很多。现在我用"她伴"每天记录症状，看着数据慢慢变化，心里有底多了。', NULL, NULL, '["#更年期", "#科普", "#新手指南", "#围绝经期"]', false, 'published', 209, 1781, '2026-05-09T22:59:21.836528', '2026-05-09T22:59:21.836528');
INSERT INTO posts (id, user_id, post_type, title, content, images, voice_url, tags, is_ai_generated, status, likes, views, created_at, published_at) VALUES ('54a01c40-8fb9-4ff7-bb35-2127f9ab03c0', NULL, 'official', '【科普】什么是围绝经期？', '围绝经期（Perimenopause）是指女性从生育期过渡到绝经期的阶段，通常发生在45-55岁之间。

主要特征：
- 月经周期开始变得不规律
- 雌激素水平波动和下降
- 出现各种身体和心理症状

常见症状包括潮热、盗汗、情绪波动、睡眠障碍等。

围绝经期通常持续2-8年，最后连续12个月没有月经即为绝经。

本内容仅供健康参考，不构成医疗建议。如有疑问请咨询专业医生。', NULL, NULL, '["#官方科普", "#围绝经期", "#基础知识"]', false, 'published', 259, 2057, '2026-05-10T11:39:21.836528', '2026-05-10T11:39:21.836528');
INSERT INTO posts (id, user_id, post_type, title, content, images, voice_url, tags, is_ai_generated, status, likes, views, created_at, published_at) VALUES ('484fddc4-6d80-481c-b761-5864cdb9d072', NULL, 'official', '【科普】激素替代疗法（HRT）安全吗？', '激素替代疗法（HRT）是缓解更年期症状的有效手段之一，但并非适合所有人。

适用人群：
- 症状严重影响生活质量
- 无乳腺癌、血栓等禁忌症
- 在医生指导下使用

注意事项：
- 需在专业医生评估后使用
- 定期复查，调整剂量
- 短期使用风险较低

是否使用 HRT 是一个需要与医生共同决策的问题。', NULL, NULL, '["#官方科普", "#激素替代疗法", "#医疗建议"]', false, 'published', 128, 1771, '2026-05-10T11:39:21.836528', '2026-05-10T11:39:21.836528');