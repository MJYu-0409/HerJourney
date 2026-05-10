"""
真实感社区帖子生成（30条）

核心设计：
1. 6个用户 × 5条 = 30条，覆盖6-12个月时间线
2. 发帖时间：70%深夜 + 20%白天 + 10%晚上
3. 10%超短帖（<30字），打破整齐感
4. 5-8条带 updatedAt + updateContent，模拟用户回来追加内容
5. 情绪复杂矛盾，不单一标签
"""

import json
import random
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
random.seed(42)

OUTPUT_PATH = Path(__file__).parent.parent / "mock_data"


def make_time(base_date, hour, minute):
    return base_date.replace(hour=hour, minute=minute, second=random.randint(0, 59))


USERS = [
    {
        "name": "凌晨三点的猫",
        "age": 42,
        "stage": "围绝经期",
        "posts": [
            {
                "date_offset": -300, "hour": 2, "minute": 15,
                "title": "又醒了，这次是被热醒的",
                "content": "凌晨两点，一身汗。被子掀了，窗户开了，还是热。\n\n以前以为更年期是妈妈辈的事，现在轮到自己了。42岁，也不算老吧？\n\n今天白天开会，说着说着突然一阵潮热，脸通红，同事还以为我发烧了。\n\n也不好意思说。就说空调开太高了。",
                "emotion": "烦躁带点好笑",
                "symptoms": ["潮热", "盗汗", "失眠"],
                "tags": ["#潮热", "#深夜", "#围绝经期"],
                "responses": 8,
            },
            {
                "date_offset": -180, "hour": 3, "minute": 40,
                "title": "三个月了，好像有点规律了",
                "content": "更新一下。\n\n这三个月试了几样东西：\n- 睡衣换成真丝的，确实凉快一点\n- 睡前不喝奶茶了（这个最难）\n- 买了个小风扇放床头\n\n不是说不热了，是热了之后恢复得快一点。以前要半小时才能再睡着，现在大概十分钟？\n\n也算进步吧。",
                "emotion": "平静中带疲惫",
                "symptoms": ["潮热", "失眠"],
                "tags": ["#经验分享", "#睡眠", "#围绝经期"],
                "responses": 23,
                "updatedAt_offset": 1, "updateContent": "补充：有人问真丝睡衣链接，我不是带货的，随便买的，关键词搜\"真丝睡衣\"就行，选19姆米以上的。",
            },
            {
                "date_offset": -90, "hour": 14, "minute": 20,
                "title": "反弹了，最近又睡不好",
                "content": "以为好多了，结果这周又不行了。\n\n可能跟项目上线有关，压力大，半夜醒了就一直在想bug。\n\n然后就越想越热，越热越想。死循环。\n\n今天跟闺蜜吐槽，她说我这是更年期叠加工龄焦虑，双buff。\n\n笑死，根本笑不出来。",
                "emotion": "焦虑叠加无奈",
                "symptoms": ["失眠", "潮热", "焦虑"],
                "tags": ["#失眠", "#焦虑", "#压力"],
                "responses": 15,
            },
            {
                "date_offset": -30, "hour": 1, "minute": 50,
                "title": "接受了，不再追求完美",
                "content": "最近想通了一件事。\n\n以前总觉得，睡不好就得治，潮热就得压，情绪不好就得调。\n\n现在觉得，这些症状就像天气变化，有晴有雨，不是故障，是常态。\n\n不跟自己较劲了。\n\n热了就脱，醒了就躺，烦了就发呆。\n\n反而好多了。",
                "emotion": "释然中还有点不甘",
                "symptoms": ["恢复阶段", "潮热"],
                "tags": ["#心态", "#接受", "#围绝经期"],
                "responses": 31,
            },
            {
                "date_offset": -3, "hour": 20, "minute": 10,
                "title": "分享一个小技巧",
                "content": "睡前把手机放客厅，真的有用。\n\n不是不看手机就睡着了，是醒了之后抓不到手机，就只能躺着。\n\n躺着躺着，又睡着了。\n\n简单粗暴，但有效。",
                "emotion": "轻松",
                "symptoms": ["失眠", "恢复阶段"],
                "tags": ["#技巧", "#睡眠", "#分享"],
                "responses": 42,
            },
        ],
    },
    {
        "name": "小城妈妈",
        "age": 48,
        "stage": "围绝经期",
        "posts": [
            {
                "date_offset": -280, "hour": 0, "minute": 30,
                "title": "睡不着，心烦",
                "content": "就是心烦。\n\n也没什么事，就是烦。孩子睡了，老公睡了，全世界都睡了，就我醒着。\n\n心跳得好快。\n\n也不知道在烦什么。可能就是...老了？\n\n48岁了。",
                "emotion": "空虚烦躁",
                "symptoms": ["失眠", "心悸", "情绪波动"],
                "tags": ["#失眠", "#心烦", "#深夜"],
                "responses": 5,
            },
            {
                "date_offset": -200, "hour": 10, "minute": 15,
                "title": "昨天跟老公吵架了，其实我也不知道为什么",
                "content": "就因为他把袜子扔在沙发上。\n\n就这么点事，我突然就爆发了。哭得停不下来。\n\n他一脸懵，说你以前不这样啊。\n\n是啊，我以前不这样。\n\n现在控制不住了，一点小事就能炸。炸完又后悔。",
                "emotion": "自责加委屈",
                "symptoms": ["情绪波动", "烦躁", "失眠"],
                "tags": ["#情绪", "#家庭", "#烦躁"],
                "responses": 31,
            },
            {
                "date_offset": -120, "hour": 4, "minute": 10,
                "title": "两个月没来了，是不是要停了",
                "content": "以前很准的，28天。\n\n这半年开始乱，有时候35天，有时候40天。\n\n这次两个月了还没来。\n\n有点害怕，又有点...松了口气？\n\n不用再算日子了，不用再垫着了。\n\n但这也意味着，真的老了。\n\n有点难过。",
                "emotion": "复杂，悲喜交加",
                "symptoms": ["情绪波动", "疲惫"],
                "tags": ["#月经", "#围绝经期", "#情绪"],
                "responses": 42,
            },
            {
                "date_offset": -45, "hour": 2, "minute": 0,
                "title": "去看了医生，开了点药",
                "content": "终于鼓起勇气去看了妇科。\n\n医生很温柔，说围绝经期很正常，给我开了点中药调理。\n\n还说如果症状严重影响生活，可以考虑激素替代疗法，但要先做检查。\n\n先吃药看看，一个月之后复查。\n\n有医生兜底，心里踏实多了。",
                "emotion": "踏实又有点忐忑",
                "symptoms": ["潮热", "失眠", "焦虑"],
                "tags": ["#就医", "#药物", "#围绝经期"],
                "responses": 19,
                "updatedAt_offset": 30, "updateContent": "更新：吃了一个月，潮热少了一些，但胃不太舒服。医生说正常反应，让我再坚持两周看看。",
            },
            {
                "date_offset": -7, "hour": 3, "minute": 0,
                "title": "现在挺好的",
                "content": "现在挺好的。真的。",
                "emotion": "平静",
                "symptoms": ["恢复阶段"],
                "tags": ["#恢复", "#平静"],
                "responses": 12,
            },
        ],
    },
    {
        "name": "李姐",
        "age": 52,
        "stage": "绝经后",
        "posts": [
            {
                "date_offset": -365, "hour": 1, "minute": 20,
                "title": "记录一下",
                "content": "今天潮热三次。上午一次，下午一次，晚上一次。比昨天少一次。",
                "emotion": "平静记录",
                "symptoms": ["潮热"],
                "tags": ["#记录", "#潮热"],
                "responses": 3,
            },
            {
                "date_offset": -280, "hour": 16, "minute": 45,
                "title": "戒咖啡一个月，数据出来了",
                "content": "做了对比实验。\n\n喝咖啡的日子，平均每天潮热4.2次。不喝咖啡的日子，1.8次。\n\n睡眠也有改善，入睡时间从45分钟降到20分钟。\n\n但下午真的困，靠散步提神。\n\ntrade-off。目前打算继续戒，观察三个月再看。",
                "emotion": "理性满意",
                "symptoms": ["潮热", "失眠"],
                "tags": ["#数据", "#咖啡", "#改善"],
                "responses": 28,
                "updatedAt_offset": 90, "updateContent": "三个月更新：戒咖啡+规律散步+十点半上床，潮热降到日均1.2次。最大的变量是咖啡，其次是作息。",
            },
            {
                "date_offset": -180, "hour": 2, "minute": 0,
                "title": "睡眠改善，但还是有反复",
                "content": "总的来说好多了，但不是每天都好。\n\n上周有两天没睡好，也不知道为什么。没有喝咖啡，没有情绪波动，就是睡不着。\n\n可能跟天气有关？阴天就容易醒。\n\n不再追求每天完美了，接受波动。\n\n一个月里有25天能睡好，就够了。",
                "emotion": "理性中带无奈",
                "symptoms": ["失眠", "恢复阶段"],
                "tags": ["#睡眠", "#波动", "#接受"],
                "responses": 16,
            },
            {
                "date_offset": -60, "hour": 3, "minute": 30,
                "title": "稳定了",
                "content": "稳定了。不再记录了。就这样吧。",
                "emotion": "淡淡的麻木",
                "symptoms": ["恢复阶段"],
                "tags": ["#恢复", "#平淡"],
                "responses": 7,
            },
            {
                "date_offset": -10, "hour": 21, "minute": 15,
                "title": "一年了，说说现在的情况",
                "content": "距离第一次发帖刚好一年。\n\n潮热：偶尔，不碍事了。\n睡眠：能睡整觉了，偶尔会醒。\n情绪：稳定多了，不再莫名其妙想哭。\n\n不是回到20岁的状态，是接受了50岁的状态。\n\n不跟自己较劲了。",
                "emotion": "释然",
                "symptoms": ["恢复阶段"],
                "tags": ["#一年总结", "#恢复", "#绝经后"],
                "responses": 56,
            },
        ],
    },
    {
        "name": "焦虑的Amy",
        "age": 38,
        "stage": "围绝经期",
        "posts": [
            {
                "date_offset": -200, "hour": 0, "minute": 45,
                "title": "凌晨还在回邮件，然后发现自己又心悸了",
                "content": "刚发完一封mail，突然心跳加速，手心冒汗。\n\n以为是要心梗，吓死了。\n\n查了资料，说是更年期心悸。38岁？早了点吧？\n\n但医生说现在提前进入围绝经期的人不少，跟压力有关。\n\n压力...能不有压力吗。",
                "emotion": "恐慌后冷静",
                "symptoms": ["心悸", "焦虑", "失眠"],
                "tags": ["#心悸", "#焦虑", "#工作压力"],
                "responses": 12,
            },
            {
                "date_offset": -150, "hour": 1, "minute": 30,
                "title": "这个月请了三天病假，因为根本起不来",
                "content": "不是懒。是真的累。\n\n起床像爬山，走两步就喘，下午开会眼皮打架。\n\n以前加班到凌晨都没事，现在正常下班回家就瘫了。\n\n周末睡了两天，还是累。\n\n不是困，是累。不一样的。\n\nHR问我是不是burnout。\n\n可能是吧。也可能是身体在报警。",
                "emotion": "疲惫无力",
                "symptoms": ["疲惫", "失眠", "焦虑"],
                "tags": ["#疲惫", "#工作", "#burnout"],
                "responses": 27,
            },
            {
                "date_offset": -80, "hour": 12, "minute": 0,
                "title": "HR找我谈话了",
                "content": "上午HR找我谈话，说注意到我最近状态不好，问我需不需要调整工作量。\n\n我说不用，我能handle。\n\n但说完就后悔了。\n\n明明handle不住了，还在硬撑。\n\n为什么说不出口呢。",
                "emotion": "疲惫加倔强",
                "symptoms": ["焦虑", "疲惫"],
                "tags": ["#工作", "#HR", "# burnout"],
                "responses": 35,
                "updatedAt_offset": 3, "updateContent": "更新：想了三天，终于跟领导提了减少出差。领导同意了，说身体第一。松了口气。",
            },
            {
                "date_offset": -30, "hour": 2, "minute": 15,
                "title": "调整了工作节奏，好一些了",
                "content": "减少出差之后，确实好一些。\n\n不再每天赶deadline，有了喘息的时间。\n\n下午会抽半小时去楼下走走，不是运动，就是走走。\n\n心跳还是偶尔会快，但不再恐慌了。\n\n知道它是怎么回事，就不怕了。",
                "emotion": "平静中带着庆幸",
                "symptoms": ["心悸", "焦虑", "恢复阶段"],
                "tags": ["#调整", "#恢复", "#工作"],
                "responses": 22,
            },
            {
                "date_offset": -5, "hour": 3, "minute": 45,
                "title": "复工了，但学会了说不",
                "content": "复工两周了。\n\n有同事让我帮一个项目，我拒绝了。\n\n以前从来不会拒绝的。\n\n现在知道了，说\"不\"不会死，但硬撑会。\n\n身体给的信号，得听。",
                "emotion": "轻松中带点硬气",
                "symptoms": ["恢复阶段", "焦虑"],
                "tags": ["#复工", "#学会拒绝", "#恢复"],
                "responses": 48,
            },
        ],
    },
    {
        "name": "小满",
        "age": 40,
        "stage": "围绝经期",
        "posts": [
            {
                "date_offset": -240, "hour": 0, "minute": 10,
                "title": "有人跟我一样吗，半夜醒了就开始哭",
                "content": "也不是因为什么事。\n\n就是醒了，看看手机，凌晨两点。\n\n然后眼泪就自己出来了。\n\n也不是难过，就是...想哭。\n\n哭一会儿又好了，又睡着了。\n\n第二天早上起来，眼睛肿的，老公问怎么了，我说没睡好。\n\n不能说。说了他也不懂。",
                "emotion": "莫名的悲伤",
                "symptoms": ["夜醒", "情绪波动"],
                "tags": ["#夜醒", "#情绪", "#哭泣"],
                "responses": 45,
            },
            {
                "date_offset": -180, "hour": 4, "minute": 0,
                "title": "还是哭，但少了",
                "content": "上次发帖是两个月前。\n\n那时候半夜醒来就哭。\n\n现在还是会醒，但不哭了。\n\n就是醒着，躺着，等天亮。\n\n也不是好起来了，是习惯了。\n\n像跟一个不速之客共处一室，刚开始怕，现在知道他不会走了，就算了。\n\n算了。",
                "emotion": "淡淡的麻木",
                "symptoms": ["夜醒", "恢复阶段"],
                "tags": ["#夜醒", "#适应", "#情绪"],
                "responses": 33,
            },
            {
                "date_offset": -100, "hour": 1, "minute": 55,
                "title": "试了心理咨询，有点用",
                "content": "去做了六次心理咨询。\n\n不是那种\"聊完就好了\"的用，是慢慢看懂了自己的情绪。\n\n原来那些无缘无故的哭，不是软弱，是身体在释放压力。\n\n咨询师说，更年期情绪波动很正常，不要自责。\n\n这句话对我很重要。\n\n以前总觉得是自己不够坚强。",
                "emotion": "释然中有点心酸",
                "symptoms": ["情绪波动", "焦虑", "恢复阶段"],
                "tags": ["#心理咨询", "#情绪", "#恢复"],
                "responses": 28,
            },
            {
                "date_offset": -30, "hour": 15, "minute": 30,
                "title": "又崩溃了，但知道会过去",
                "content": "昨天又崩溃了。\n\n无缘无故的，下午坐在沙发上就开始哭。\n\n但奇怪的是，我知道它会过去。\n\n以前崩溃的时候觉得世界末日了，现在知道，过两天就好。\n\n这种\"知道会过去\"的感觉，本身就是一种进步。\n\n虽然当时还是很难受。",
                "emotion": "痛苦中带着笃定",
                "symptoms": ["情绪波动", "焦虑"],
                "tags": ["#崩溃", "#情绪波动", "#进步"],
                "responses": 24,
                "updatedAt_offset": 2, "updateContent": "更新：果然，两天之后好多了。现在在看一本关于更年期的书，了解到激素波动会影响血清素水平，知道原因就不怕了。",
            },
            {
                "date_offset": -5, "hour": 2, "minute": 20,
                "title": "最近平静了很多",
                "content": "最近真的平静了很多。\n\n还是会醒，但不慌了。\n\n还是会热，但不烦了。\n\n像学会了跟自己相处。\n\n不是对抗，是共处。\n\n这花了八个月。",
                "emotion": "平静中带着感慨",
                "symptoms": ["夜醒", "恢复阶段"],
                "tags": ["#平静", "#恢复", "#共处"],
                "responses": 51,
            },
        ],
    },
    {
        "name": "大刘姐",
        "age": 50,
        "stage": "绝经后",
        "posts": [
            {
                "date_offset": -320, "hour": 2, "minute": 5,
                "title": "这天儿也太热了吧",
                "content": "最近总觉得热，以为是夏天到了。\n\n但家里人都说还好啊，怎么就我一个人满头大汗。\n\n晚上睡觉也得开着窗户，老公冻得裹被子，我光着腿还嫌热。\n\n你说说，这叫什么事儿。\n\n我妈说，你这是更年期了。\n\n我不信，我才50。",
                "emotion": "将信将疑",
                "symptoms": ["潮热", "盗汗"],
                "tags": ["#潮热", "#出汗", "#刚开始"],
                "responses": 9,
            },
            {
                "date_offset": -240, "hour": 3, "minute": 15,
                "title": "睡不着",
                "content": "睡不着。硬撑。",
                "emotion": "硬撑",
                "symptoms": ["失眠", "疲惫"],
                "tags": ["#失眠", "#硬撑"],
                "responses": 4,
            },
            {
                "date_offset": -150, "hour": 1, "minute": 40,
                "title": "去医院确认了",
                "content": "终于去医院看了。\n\n医生说是更年期，让我别紧张，很正常。\n\n开了点调理的药，说如果症状严重再考虑别的方案。\n\n心里踏实了。\n\n之前一直瞎猜，是不是得了什么大病。\n\n现在知道了，就是老了。\n\n老了就老了吧。",
                "emotion": "踏实又有点认命",
                "symptoms": ["潮热", "失眠", "焦虑"],
                "tags": ["#就医", "#确认", "#接受"],
                "responses": 14,
            },
            {
                "date_offset": -60, "hour": 9, "minute": 20,
                "title": "现在好多了，劝姐妹们别想太多",
                "content": "熬了大半年，现在好多了。\n\n潮热还有，但没那么频繁了。\n\n睡眠也还行，虽然还是容易醒，但醒了能再睡着。\n\n我觉得吧，这玩意儿你越在意它越厉害。\n\n别想太多，该吃吃该喝喝，日子照样过。\n\n姐妹们，放宽心。",
                "emotion": "豁达",
                "symptoms": ["恢复阶段", "潮热"],
                "tags": ["#恢复", "#心态", "#绝经后"],
                "responses": 38,
            },
            {
                "date_offset": -2, "hour": 22, "minute": 10,
                "title": "又热了",
                "content": "又热了。但已经无所谓了。爱咋咋地。",
                "emotion": "无所谓",
                "symptoms": ["潮热"],
                "tags": ["#潮热", "#日常"],
                "responses": 6,
            },
        ],
    },
]


def generate():
    posts = []
    now = datetime.now()
    base_id = 10000

    for user in USERS:
        for p in user["posts"]:
            post_date = now + timedelta(days=p["date_offset"])
            post_date = make_time(post_date, p["hour"], p["minute"])

            post = {
                "id": f"post-{base_id}",
                "title": p["title"],
                "content": p["content"],
                "emotion": p["emotion"],
                "symptoms": p["symptoms"],
                "stage": user["stage"],
                "tags": p["tags"],
                "responses": p["responses"],
                "createdAt": post_date.isoformat(),
                "_author": user["name"],  # 临时字段，用于后续引用处理
            }

            if "updatedAt_offset" in p:
                update_date = post_date + timedelta(days=p["updatedAt_offset"])
                post["updatedAt"] = update_date.isoformat()
                post["updateContent"] = p["updateContent"]

            posts.append(post)
            base_id += 1

    # ========== 添加引用（同用户帖子之间互相引用）==========
    for user in USERS:
        user_post_ids = [p["id"] for p in posts if p.get("_author") == user["name"]]
        # 按时间排序（从早到晚）
        user_posts_sorted = sorted(
            [p for p in posts if p.get("_author") == user["name"]],
            key=lambda x: x["createdAt"]
        )
        ids = [p["id"] for p in user_posts_sorted]
        for i in range(2, len(ids)):
            post = next(p for p in posts if p["id"] == ids[i])
            ref_id = ids[i - 2]
            post["referenceTo"] = ref_id
            # 在内容末尾追加引用提示
            ref_post = next(p for p in posts if p["id"] == ref_id)
            post["content"] += f"\n\n（翻到自己{ref_post['title']}的帖子，那时候还是{ref_post['emotion']}的状态，现在...）"

    # ========== 设置5条0回复帖 ==========
    # 优先选择超短帖和平淡的记录帖
    candidates = [p for p in posts if len(p["content"]) < 80 or "记录" in p["title"]]
    if len(candidates) >= 5:
        zero_posts = random.sample(candidates, k=5)
    else:
        zero_posts = random.sample(posts, k=5)
    for p in zero_posts:
        p["responses"] = 0

    # ========== 2条"后悔帖"（内容有明显删减痕迹）==========
    regret_candidates = [p for p in posts if len(p["content"]) > 100 and p["responses"] > 0]
    if len(regret_candidates) >= 2:
        regret_posts = random.sample(regret_candidates, k=2)
        for p in regret_posts:
            # 在内容中间插入删减标记
            lines = p["content"].split("\n\n")
            if len(lines) >= 3:
                # 在第二段后面插入删减痕迹
                p["content"] = lines[0] + "\n\n" + lines[1] + "\n\n...算了不说了，说了也没用。\n\n" + "\n\n".join(lines[2:])
            else:
                p["content"] = p["content"][:len(p["content"])//2] + "...\n\n（删了一大段，不想让人看到）"
            p["title"] = p["title"] + "（已编辑）"
            p["emotion"] = p["emotion"] + "，后悔发了"

    # 清理临时字段
    for p in posts:
        p.pop("_author", None)

    posts.sort(key=lambda x: x["createdAt"], reverse=True)
    return posts


def analyze(posts):
    print(f"\n总帖数: {len(posts)}")

    # 时间分布
    hours = [datetime.fromisoformat(p["createdAt"]).hour for p in posts]
    night = sum(1 for h in hours if 0 <= h <= 5)
    day = sum(1 for h in hours if 8 <= h <= 18)
    evening = sum(1 for h in hours if 19 <= h <= 23)
    print(f"时间分布: 深夜{night}条({night/len(posts)*100:.0f}%) | 白天{day}条({day/len(posts)*100:.0f}%) | 晚上{evening}条({evening/len(posts)*100:.0f}%)")

    # 长度分布
    lengths = [len(p["content"]) for p in posts]
    short = sum(1 for l in lengths if l < 50)
    medium = sum(1 for l in lengths if 50 <= l <= 200)
    long = sum(1 for l in lengths if l > 200)
    print(f"长度分布: 超短(<50字){short}条 | 中等(50-200字){medium}条 | 长文(>200字){long}条")

    # 更新帖
    updated = sum(1 for p in posts if "updatedAt" in p)
    print(f"带更新: {updated}条")

    # 引用帖
    referenced = sum(1 for p in posts if "referenceTo" in p)
    print(f"带引用: {referenced}条")

    # 后悔帖
    regret = sum(1 for p in posts if "已编辑" in p.get("title", ""))
    print(f"后悔帖: {regret}条")

    # 0回复帖
    zero = sum(1 for p in posts if p["responses"] == 0)
    print(f"0回复帖: {zero}条")

    # 用户分布
    print(f"\n用户分布:")
    for user in USERS:
        print(f"  {user['name']}({user['age']}岁): {len(user['posts'])}条")

    # 情绪分布
    emotions = [p["emotion"] for p in posts]
    print(f"\n情绪标签数: {len(set(emotions))}种")


def main():
    posts = generate()
    analyze(posts)

    OUTPUT_PATH.mkdir(exist_ok=True)
    path = OUTPUT_PATH / "women_posts_realistic_30.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)

    print(f"\n已生成 → {path}")


if __name__ == "__main__":
    main()
