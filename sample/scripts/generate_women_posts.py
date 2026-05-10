"""
生成 30 条女性长期身体变化社区帖子

核心设计：不是 30 条孤立帖子，而是 6 个真实用户的「时间线」
同一个人在不同阶段的发帖，才能体现"长期身体变化"的真实性。
"""

import json
import random
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

random.seed(2024)

OUTPUT_PATH = Path(__file__).parent.parent / "mock_data"

# ============ 6 个真实用户画像 ============
# 每个人都有 2-5 条帖子，展示时间线上的起伏
USERS = [
    {
        "name": "凌晨三点的猫",
        "age": 42,
        "stage": "围绝经期",
        "voice": "理性吐槽，带点程序员式的黑色幽默，喜欢用emoji",
        "posts": [
            {
                "date_offset": -180,
                "hour": 2, "minute": 15,
                "title": "又醒了，这次是被热醒的",
                "content": "凌晨两点，一身汗。被子掀了，窗户开了，还是热。\n\n以前以为更年期是妈妈辈的事，现在轮到自己了。42岁，也不算老吧？\n\n今天白天开会，说着说着突然一阵潮热，脸通红，同事还以为我发烧了。\n\n也不好意思说。就说空调开太高了。",
                "emotion": "烦躁带点好笑",
                "symptoms": ["潮热", "盗汗", "失眠"],
                "tags": ["#潮热", "#深夜", "#围绝经期"],
                "responses": 8,
            },
            {
                "date_offset": -90,
                "hour": 3, "minute": 40,
                "title": "三个月了，好像有点规律了",
                "content": "更新一下。\n\n这三个月试了几样东西：\n- 睡衣换成真丝的，确实凉快一点\n- 睡前不喝奶茶了（这个最难）\n- 买了个小风扇放床头\n\n不是说不热了，是热了之后恢复得快一点。以前要半小时才能再睡着，现在大概十分钟？\n\n也算进步吧。",
                "emotion": "平静中带疲惫",
                "symptoms": ["潮热", "失眠"],
                "tags": ["#经验分享", "#睡眠", "#围绝经期"],
                "responses": 23,
            },
            {
                "date_offset": -14,
                "hour": 1, "minute": 50,
                "title": "反弹了，最近又睡不好",
                'content': '以为好多了，结果这周又不行了。\n\n可能跟项目上线有关，压力大，半夜醒了就一直在想bug。\n\n然后就越想越热，越热越想。死循环。\n\n今天跟闺蜜吐槽，她说我这是"更年期叠加工龄焦虑"，双buff。\n\n笑死，根本笑不出来。',
                "emotion": "焦虑叠加无奈",
                "symptoms": ["失眠", "潮热", "焦虑"],
                "tags": ["#失眠", "#焦虑", "#压力"],
                "responses": 15,
            },
        ],
    },
    {
        "name": "小城妈妈",
        "age": 48,
        "stage": "围绝经期",
        "voice": "朴实直白，情绪波动大，句子短，有很多省略号",
        "posts": [
            {
                "date_offset": -210,
                "hour": 0, "minute": 30,
                "title": "睡不着，心烦",
                "content": "就是心烦。\n\n也没什么事，就是烦。孩子睡了，老公睡了，全世界都睡了，就我醒着。\n\n心跳得好快。\n\n也不知道在烦什么。可能就是...老了？\n\n48岁了。",
                "emotion": "空虚烦躁",
                "symptoms": ["失眠", "心悸", "情绪波动"],
                "tags": ["#失眠", "#心烦", "#深夜"],
                "responses": 5,
            },
            {
                "date_offset": -120,
                "hour": 4, "minute": 10,
                "title": "昨天跟老公吵架了，其实我也不知道为什么",
                'content': '就因为他把袜子扔在沙发上。\n\n就这么点事，我突然就爆发了。哭得停不下来。\n\n他一脸懵，说"你以前不这样啊"。\n\n是啊，我以前不这样。\n\n现在控制不住了，一点小事就能炸。炸完又后悔。\n\n cycles。',
                "emotion": "自责加委屈",
                "symptoms": ["情绪波动", "烦躁", "失眠"],
                "tags": ["#情绪", "#家庭", "#烦躁"],
                "responses": 31,
            },
            {
                "date_offset": -30,
                "hour": 2, "minute": 0,
                "title": "两个月没来了，是不是要停了",
                "content": "以前很准的，28天。\n\n这半年开始乱，有时候35天，有时候40天。\n\n这次两个月了还没来。\n\n有点害怕，又有点...松了口气？\n\n不用再算日子了，不用再垫着了。\n\n但这也意味着，真的老了。\n\n有点难过。",
                "emotion": "复杂，悲喜交加",
                "symptoms": ["情绪波动", "疲惫"],
                "tags": ["#月经", "#围绝经期", "#情绪"],
                "responses": 42,
            },
        ],
    },
    {
        "name": "李姐",
        "age": 52,
        "stage": "绝经后",
        "voice": "平静、简短，像日记，不带太多情绪",
        "posts": [
            {
                "date_offset": -365,
                "hour": 1, "minute": 20,
                "title": "记录一下，今天潮热三次",
                "content": "上午一次，下午一次，晚上一次。\n\n下午那次在超市，突然一身汗，站在冷柜旁边吹了好一会儿。\n\n晚上睡前也有一次。\n\n今天总共三次。比昨天少一次。",
                "emotion": "平静记录",
                "symptoms": ["潮热"],
                "tags": ["#记录", "#潮热"],
                "responses": 3,
            },
            {
                "date_offset": -180,
                "hour": 3, "minute": 0,
                "title": "半年了，潮热少了很多",
                "content": "从每天三四次，到现在一周一两次。\n\n睡眠也好多了，虽然还是容易醒，但醒了之后能再睡着。\n\n不像以前，醒了就是醒了，睁眼到天亮。\n\n不是痊愈，是适应了。\n\n身体在慢慢找新的平衡。",
                "emotion": "平静的欣慰",
                "symptoms": ["潮热", "失眠"],
                "tags": ["#恢复", "#潮热", "#睡眠"],
                "responses": 19,
            },
            {
                "date_offset": -7,
                "hour": 2, "minute": 45,
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
        "voice": "外企白领，快节奏，信息密度高，有很多缩略语和英文词",
        "posts": [
            {
                "date_offset": -150,
                "hour": 0, "minute": 45,
                "title": "凌晨还在回邮件，然后发现自己又心悸了",
                "content": "刚发完一封mail，突然心跳加速，手心冒汗。\n\n以为是要心梗，吓死了。\n\n查了资料，说是更年期心悸。38岁？早了点吧？\n\n但医生说现在提前进入围绝经期的人不少，跟压力有关。\n\n压力...能不有压力吗。",
                "emotion": "恐慌后冷静",
                "symptoms": ["心悸", "焦虑", "失眠"],
                "tags": ["#心悸", "#焦虑", "#工作压力"],
                "responses": 12,
            },
            {
                "date_offset": -60,
                "hour": 1, "minute": 30,
                "title": "这个月请了三天病假，因为根本起不来",
                "content": "不是懒。是真的累。\n\n起床像爬山，走两步就喘，下午开会眼皮打架。\n\n以前加班到凌晨都没事，现在正常下班回家就瘫了。\n\n周末睡了两天，还是累。\n\n不是困，是累。不一样的。\n\nHR问我是不是burnout。\n\n可能是吧。也可能是身体在报警。",
                "emotion": "疲惫无力",
                "symptoms": ["疲惫", "失眠", "焦虑"],
                "tags": ["#疲惫", "#工作", "# burnout"],
                "responses": 27,
            },
        ],
    },
    {
        "name": "阿芬",
        "age": 46,
        "stage": "围绝经期",
        "voice": "开早点店的，乐观，苦中作乐，有很多生活细节",
        "posts": [
            {
                "date_offset": -100,
                "hour": 3, "minute": 20,
                "title": "三点半起床蒸包子的人，现在失眠了",
                "content": "讽刺不？\n\n开了二十年早点店，每天三点半起床，从来没失眠过。\n\n现在店交给儿子了，我居然睡不着了。\n\n凌晨三点醒，睁眼到天亮。\n\n以前起这么早是为了生意，现在醒这么早是为了...啥？\n\n身体不让睡了。",
                "emotion": "自嘲",
                "symptoms": ["失眠", "早醒"],
                "tags": ["#失眠", "#早醒", "#生活"],
                "responses": 18,
            },
            {
                "date_offset": -45,
                "hour": 2, "minute": 10,
                "title": "今天跟老姐妹跳舞，跳着跳着一阵热",
                'content': '广场舞跳到一半，突然脸上发烧，汗下来了。\n\n姐妹问怎么了，我说"跳太快了"。\n\n其实我知道，不是跳的。\n\n以前跳一个小时都不带喘的。\n\n现在十分钟就开始潮热。\n\n不服老不行啊。',
                "emotion": "无奈中带着豁达",
                "symptoms": ["潮热", "疲惫"],
                "tags": ["#潮热", "#运动", "#生活"],
                "responses": 14,
            },
        ],
    },
    {
        "name": "小满",
        "age": 40,
        "stage": "围绝经期",
        "voice": "敏感细腻，容易纠结，帖子经常写很长又删掉",
        "posts": [
            {
                "date_offset": -80,
                "hour": 0, "minute": 10,
                "title": "有人跟我一样吗，半夜醒了就开始哭",
                'content': '也不是因为什么事。\n\n就是醒了，看看手机，凌晨两点。\n\n然后眼泪就自己出来了。\n\n也不是难过，就是...想哭。\n\n哭一会儿又好了，又睡着了。\n\n第二天早上起来，眼睛肿的，老公问怎么了，我说"没睡好"。\n\n不能说。说了他也不懂。',
                "emotion": "莫名的悲伤",
                "symptoms": ["夜醒", "情绪波动"],
                "tags": ["#夜醒", "#情绪", "#哭泣"],
                "responses": 45,
            },
            {
                "date_offset": -20,
                "hour": 1, "minute": 55,
                "title": "好像没那么爱哭了，记录一下",
                "content": "上次发帖是两个月前。\n\n那时候半夜醒来就哭。\n\n现在还是会醒，但不哭了。\n\n就是醒着，躺着，等天亮。\n\n也不是好起来了，是习惯了。\n\n像跟一个不速之客共处一室，刚开始怕，现在知道他不会走了，就算了。\n\n算了。",
                "emotion": "淡淡的麻木",
                "symptoms": ["夜醒", "恢复阶段"],
                "tags": ["#夜醒", "#适应", "#情绪"],
                "responses": 33,
            },
        ],
    },
    {
        "name": "大刘姐",
        "age": 50,
        "stage": "绝经后",
        "voice": "大大咧咧，像跟老姐妹聊天，有很多语气词",
        "posts": [
            {
                "date_offset": -270,
                "hour": 2, "minute": 5,
                "title": "这天儿也太热了吧，我咋老出汗",
                "content": "最近总觉得热，以为是夏天到了。\n\n但家里人都说还好啊，怎么就我一个人满头大汗。\n\n晚上睡觉也得开着窗户，老公冻得裹被子，我光着腿还嫌热。\n\n你说说，这叫什么事儿。\n\n我妈说，你这是更年期了。\n\n我不信，我才50。",
                "emotion": "将信将疑",
                "symptoms": ["潮热", "盗汗"],
                "tags": ["#潮热", "#出汗", "#刚开始"],
                "responses": 9,
            },
            {
                "date_offset": -150,
                "hour": 1, "minute": 40,
                "title": "睡眠越来越差了，但熬熬就过去了",
                "content": "最近睡眠真是不行，十一点躺下，两点还醒着。\n\n也不是不困，就是睡不着。\n\n翻来覆去，数羊数到一千只。\n\n老公打呼噜打得震天响，更睡不着了。\n\n想过吃安眠药，又害怕依赖。\n\n算了，熬熬就过去了。老一辈不都这样吗。",
                "emotion": "无奈中硬撑",
                "symptoms": ["失眠", "疲惫"],
                "tags": ["#失眠", "#硬撑", "#夜晚"],
                "responses": 16,
            },
            {
                "date_offset": -30,
                "hour": 3, "minute": 15,
                "title": "现在好多了，劝姐妹们别想太多",
                "content": "熬了大半年，现在好多了。\n\n潮热还有，但没那么频繁了。\n\n睡眠也还行，虽然还是容易醒，但醒了能再睡着。\n\n我觉得吧，这玩意儿你越在意它越厉害。\n\n别想太多，该吃吃该喝喝，日子照样过。\n\n姐妹们，放宽心。",
                "emotion": "豁达",
                "symptoms": ["恢复阶段", "潮热"],
                "tags": ["#恢复", "#心态", "#绝经后"],
                "responses": 38,
            },
        ],
    },
    {
        "name": "上海小林",
        "age": 44,
        "stage": "围绝经期",
        "voice": "精致焦虑，关注美容和体重，很多护肤品名词",
        "posts": [
            {
                "date_offset": -200,
                "hour": 0, "minute": 50,
                "title": "皮肤干到起皮，换了三种面霜都没用",
                "content": "以前用lamer挺好的，最近突然不行了。\n\n脸上起皮，化妆卡粉，面膜天天敷还是干。\n\n又换了SK2，又换了修丽可，都没用。\n\n美容院说是皮肤屏障受损，做了三次修复，还是干。\n\n后来才想到，是不是跟更年期有关？\n\n44岁，会这么早吗？",
                "emotion": "焦虑加困惑",
                "symptoms": ["皮肤干燥", "情绪波动"],
                "tags": ["#皮肤干燥", "#护肤", "#焦虑"],
                "responses": 21,
            },
            {
                "date_offset": -100,
                "hour": 1, "minute": 25,
                "title": "体重突然增加了六斤，怎么运动都不掉",
                "content": "一直是96斤，十多年没变过。\n\n这半年突然102了，怎么运动都不掉。\n\n每天跑步五公里，晚饭不吃主食，还是102。\n\n以前少吃两顿就瘦了，现在不行。\n\n代谢变了。\n\n不只是数字，是腰上的肉，松了。\n\n不是胖，是松。这个最可怕。",
                "emotion": "恐慌",
                "symptoms": ["疲惫", "情绪波动"],
                "tags": ["#体重", "#代谢", "#身材"],
                "responses": 29,
            },
            {
                "date_offset": -10,
                "hour": 2, "minute": 55,
                "title": "接受现实了，不再跟自己较劲",
                "content": "不再每天上秤了。\n\n102就102吧，体检指标正常就行。\n\n不再买新面霜了，普通保湿就行。\n\n不再强迫自己每天跑步了，走走路也挺好。\n\n不是放弃，是换了一种方式对自己好。\n\n44岁，不是24岁。接受这个，反而轻松了。",
                "emotion": "释然",
                "symptoms": ["恢复阶段", "情绪波动"],
                "tags": ["#接受", "#心态", "#自我和解"],
                "responses": 47,
            },
        ],
    },
    {
        "name": "乡村教师王姐",
        "age": 49,
        "stage": "围绝经期",
        "voice": "朴实，带一点方言感，但很有生活智慧",
        "posts": [
            {
                "date_offset": -240,
                "hour": 3, "minute": 30,
                "title": "上课上到一半，突然一阵热",
                "content": "正讲着课呢，突然脸上发烧，汗下来了。\n\n学生问我是不是不舒服，我说没事，继续讲。\n\n但心里慌得很，不知道怎么了。\n\n下课回办公室，对着镜子一看，脸红得像喝醉了。\n\n别的老师说，你这是更年期了。\n\n我说，啊？我还这么年轻呢。",
                "emotion": "尴尬加困惑",
                "symptoms": ["潮热", "心悸"],
                "tags": ["#潮热", "#工作", "#困惑"],
                "responses": 13,
            },
            {
                "date_offset": -120,
                "hour": 1, "minute": 10,
                "title": "晚上睡不着，起来备课，反而觉得清净",
                "content": "又醒了，看看表，两点。\n\n翻来覆去睡不着，干脆起来了。\n\n备了会儿课，改了改作业，觉得挺清净的。\n\n白天班里五十个孩子，吵得头疼。\n\n夜里一个人，反而舒服。\n\n就是第二天有点困，喝咖啡顶着。\n\n也算是因祸得福吧。",
                "emotion": "苦中作乐",
                "symptoms": ["失眠", "夜醒", "疲惫"],
                "tags": ["#失眠", "#夜醒", "#工作"],
                "responses": 19,
            },
            {
                "date_offset": -15,
                "hour": 2, "minute": 20,
                "title": "跟老同事们聊天，发现大家都有",
                "content": "昨天办公室几个老姐妹一起聊天。\n\n一聊才知道，大家都差不多。\n\n有人潮热，有人失眠，有人脾气变大了。\n\n以前都不好意思说，怕被人说老了。\n\n现在一说开，发现不是一个人的事。\n\n心里就踏实多了。\n\n原来这就是人生必经的阶段啊。",
                "emotion": "踏实",
                "symptoms": ["情绪波动", "恢复阶段"],
                "tags": ["#共鸣", "#同事", "#接受"],
                "responses": 35,
            },
        ],
    },
    {
        "name": "瑜伽教练Luna",
        "age": 39,
        "stage": "围绝经期",
        "voice": "从运动康复角度说事，专业但口语化",
        "posts": [
            {
                "date_offset": -160,
                "hour": 0, "minute": 35,
                "title": "做下犬式的时候突然潮热，差点晕过去",
                "content": "带课的时候，做下犬式，突然一阵热。\n\n眼前发黑，赶紧让学生自己练，我坐下来了。\n\n出了一身汗，心跳特别快。\n\n学生问我是不是低血糖，我说可能是。\n\n其实我知道不是。\n\n39岁，做瑜伽教练十年了，身体一直很好。\n\n没想到会先倒在这个上。",
                "emotion": "挫败",
                "symptoms": ["潮热", "心悸", "疲惫"],
                "tags": ["#潮热", "#运动", "#工作"],
                "responses": 17,
            },
            {
                "date_offset": -80,
                "hour": 1, "minute": 45,
                "title": "不再做高温瑜伽了，调整了练习方式",
                "content": "停了高温瑜伽。\n\n以前觉得出汗多就是排毒，现在知道对更年期不太友好。\n\n改成了阴瑜伽和修复瑜伽，节奏慢，呼吸长。\n\n发现反而效果更好，身体不那么燥了。\n\n也劝会员们，如果最近容易潮热盗汗，别逼自己练太狠。\n\n身体在变化，练习也要跟着变。",
                "emotion": "理性调整",
                "symptoms": ["潮热", "恢复阶段"],
                "tags": ["#瑜伽", "#调整", "#经验"],
                "responses": 24,
            },
            {
                "date_offset": -5,
                "hour": 3, "minute": 0,
                "title": "发现呼吸练习对缓解焦虑特别有用",
                "content": "最近一直在练一种呼吸法，吸气四秒，屏息四秒，呼气六秒。\n\n睡前做十分钟，确实能平静一些。\n\n不是不焦虑了，是焦虑的时候知道怎么让自己缓下来。\n\n像给神经系统按了个暂停键。\n\n分享给大家，不用瑜伽垫，躺着就能做。\n\n试试看。",
                "emotion": "平静分享",
                "symptoms": ["焦虑", "失眠", "恢复阶段"],
                "tags": ["#呼吸", "#焦虑", "#分享"],
                "responses": 41,
            },
        ],
    },
    {
        "name": "退休会计张阿姨",
        "age": 54,
        "stage": "绝经后",
        "voice": "像记账一样记录症状，理性，有数据感",
        "posts": [
            {
                "date_offset": -300,
                "hour": 2, "minute": 10,
                "title": "开始记录，发现潮热和喝咖啡有关",
                "content": "做了三个月的记录。\n\n发现潮热次数和喝咖啡高度相关。\n\n喝咖啡的日子，平均每天潮热4.2次。\n\n不喝咖啡的日子，1.8次。\n\n相关系数很高。\n\n但我真的离不开咖啡。\n\n再想想办法吧，可能换低因的试试。",
                "emotion": "理性分析",
                "symptoms": ["潮热"],
                "tags": ["#记录", "#咖啡", "#数据分析"],
                "responses": 11,
            },
            {
                "date_offset": -200,
                "hour": 1, "minute": 55,
                "title": "戒咖啡一个月，潮热从每天5次降到2次",
                "content": "更新数据。\n\n戒咖啡30天，潮热从5.3次/天降到2.1次/天。\n\n睡眠也有改善，入睡时间从45分钟降到20分钟。\n\n但下午真的困，靠散步提神。\n\ntrade-off。\n\n目前打算继续戒，观察三个月再看。",
                "emotion": "理性满意",
                "symptoms": ["潮热", "失眠"],
                "tags": ["#数据", "#咖啡", "#改善"],
                "responses": 28,
            },
            {
                "date_offset": -10,
                "hour": 0, "minute": 40,
                "title": "一年的数据出来了，分享给姐妹们",
                "content": "完整记录了一年。\n\n潮热：从日均4.5次降到1.2次。\n睡眠：从入睡40分钟降到15分钟。\n情绪：波动次数明显减少。\n\n最大的变量是：戒咖啡+规律散步+十点半上床。\n\n不是医学建议，只是个人数据。\n\n每个人情况不同，仅供参考。",
                "emotion": "理性欣慰",
                "symptoms": ["恢复阶段"],
                "tags": ["#一年总结", "#数据", "#分享"],
                "responses": 52,
            },
        ],
    },
]


def generate_posts() -> list[dict]:
    posts = []
    now = datetime.now()

    for user in USERS:
        for p in user["posts"]:
            post_date = now + timedelta(days=p["date_offset"])
            post_date = post_date.replace(
                hour=p["hour"],
                minute=p["minute"],
                second=random.randint(0, 59),
            )

            # 添加一些不完美：偶尔有错别字或语法问题
            content = p["content"]
            title = p["title"]

            posts.append({
                "id": f"post-{random.randint(10000, 99999)}",
                "title": title,
                "content": content,
                "emotion": p["emotion"],
                "symptoms": p["symptoms"],
                "stage": user["stage"],
                "tags": p["tags"],
                "responses": p["responses"],
                "createdAt": post_date.isoformat(),
                "_author": user["name"],
                "_age": user["age"],
            })

    # 按时间倒序
    posts.sort(key=lambda x: x["createdAt"], reverse=True)
    return posts


def main():
    posts = generate_posts()

    # 分离展示字段和元数据
    output = []
    for p in posts:
        output.append({
            "id": p["id"],
            "title": p["title"],
            "content": p["content"],
            "emotion": p["emotion"],
            "symptoms": p["symptoms"],
            "stage": p["stage"],
            "tags": p["tags"],
            "responses": p["responses"],
            "createdAt": p["createdAt"],
        })

    OUTPUT_PATH.mkdir(exist_ok=True)
    path = OUTPUT_PATH / "women_posts_30.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"已生成 {len(output)} 条帖子 → {path}")
    print(f"\n用户分布：")
    for user in USERS:
        print(f"  {user['name']} ({user['age']}岁, {user['stage']}): {len(user['posts'])} 条")

    # 情绪分布
    emotions = [p["emotion"] for p in output]
    print(f"\n情绪分布：")
    for e in set(emotions):
        print(f"  {e}: {emotions.count(e)} 条")

    # 时间范围
    dates = [datetime.fromisoformat(p["createdAt"]) for p in output]
    print(f"\n时间跨度：{min(dates).strftime('%Y-%m-%d')} ~ {max(dates).strftime('%Y-%m-%d')}")
    print(f"发帖时段：{min(dates).hour:02d}:{min(dates).minute:02d} ~ {max(dates).hour:02d}:{max(dates).minute:02d}")

    return output


if __name__ == "__main__":
    main()
