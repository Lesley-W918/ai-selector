"""
ai_selector.py — AI 产品大白话筛选工具 v2.0
专为非技术背景小白设计

新增：
  · 产品库扩展至 20 款（覆盖五大模态）
  · 用户真实投票持久化（存储在 votes.json）
  · 每人每产品只能投一次（基于浏览器 session）
  · 侧边栏实时口碑榜

运行方法：
    pip install streamlit
    streamlit run ai_selector.py
"""

import streamlit as st
import re
import json
from pathlib import Path

# ──────────────────────────────────────────────
# 页面配置
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="AI Selector",
    page_icon="✦",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ──────────────────────────────────────────────
# 全局样式 v3 — 图二风格：极简黑白、大字标题、手机优先
# ──────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@700;900&family=Noto+Sans+SC:wght@300;400;500&display=swap');

/* ── 基础 ── */
html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background-color: #F7F5F0 !important;
    color: #1A1A1A;
    font-family: 'Noto Sans SC', 'PingFang SC', sans-serif;
}
[data-testid="stHeader"]         { background: transparent !important; }
[data-testid="stSidebar"]        { background: #F7F5F0 !important; }
[data-testid="stMainBlockContainer"] { max-width: 680px; padding: 0 16px; }
section[data-testid="stMain"] > div { padding-top: 0; }

/* 隐藏 Streamlit 默认装饰 */
#MainMenu, footer, [data-testid="stToolbar"] { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }

/* ── Hero 区 ── */
.hero-eyebrow {
    text-align: center;
    font-size: 0.7rem; letter-spacing: 3px; font-weight: 500;
    color: #1A1A1A; text-transform: uppercase;
    background: #1A1A1A; color: #F7F5F0;
    display: inline-block; padding: 4px 14px; border-radius: 20px;
    margin: 2.5rem auto 1.2rem; display: block; width: fit-content;
}
.hero-title {
    text-align: center;
    font-family: 'Noto Serif SC', 'STSong', serif;
    font-size: clamp(2.4rem, 8vw, 3.6rem);
    font-weight: 900; line-height: 1.15;
    color: #1A1A1A; letter-spacing: -1px;
    margin: 0 0 1rem;
}
.hero-sub {
    text-align: center; font-size: 0.92rem;
    color: #888; line-height: 1.8;
    margin-bottom: 2.8rem;
    font-weight: 300;
}

/* ── 模态卡片 ── */
.modal-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 10px;
    margin-bottom: 2.4rem;
}
.modal-item {
    background: #FFFFFF;
    border: 1.5px solid #E8E4DC;
    border-radius: 16px;
    padding: 18px 8px 14px;
    display: flex; flex-direction: column;
    align-items: center; gap: 8px;
    cursor: pointer;
    transition: all 0.15s ease;
    text-decoration: none;
}
.modal-item:hover {
    border-color: #1A1A1A;
    box-shadow: 0 4px 16px rgba(0,0,0,0.08);
    transform: translateY(-2px);
}
.modal-item.active {
    background: #1A1A1A;
    border-color: #1A1A1A;
}
.modal-item.active .modal-icon-svg { filter: invert(1); }
.modal-item.active .modal-lbl { color: #FFFFFF; }
.modal-icon-svg {
    width: 28px; height: 28px;
    opacity: 0.75;
}
.modal-lbl {
    font-size: 0.78rem; color: #555;
    font-weight: 500; letter-spacing: 0.3px;
}

/* ── 搜索框 ── */
.search-wrap {
    position: relative;
    background: #FFFFFF;
    border: 1.5px solid #E8E4DC;
    border-radius: 50px;
    display: flex; align-items: center;
    padding: 0 20px;
    margin-bottom: 0.5rem;
    transition: border-color 0.2s, box-shadow 0.2s;
    box-shadow: 0 2px 12px rgba(0,0,0,0.04);
}
.search-wrap:focus-within {
    border-color: #1A1A1A;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
}
/* 覆盖 Streamlit input 样式 */
[data-testid="stTextInput"] input {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    font-size: 1rem !important;
    font-family: 'Noto Sans SC', sans-serif !important;
    color: #1A1A1A !important;
    padding: 16px 0 !important;
}
[data-testid="stTextInput"] > div > div {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}
[data-testid="stTextInput"] { margin-bottom: 0 !important; }

.search-hint {
    text-align: center; font-size: 0.78rem; color: #C0BAB0;
    margin-bottom: 2rem; font-weight: 300;
}

/* ── 产품 카드 ── */
.card {
    background: #FFFFFF;
    border-radius: 20px;
    padding: 24px 24px 18px;
    margin-bottom: 16px;
    border: 1.5px solid #ECEAE4;
    transition: all 0.18s ease;
}
.card:hover {
    border-color: #1A1A1A;
    box-shadow: 0 8px 32px rgba(0,0,0,0.08);
    transform: translateY(-2px);
}

/* 产品顶部：封面色块 + 名称 */
.card-top {
    display: flex; align-items: flex-start;
    justify-content: space-between;
    margin-bottom: 14px;
}
.card-avatar {
    width: 52px; height: 52px; border-radius: 14px;
    background: #F0EDE6;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.6rem; flex-shrink: 0;
    border: 1px solid #E8E4DC;
}
.card-meta { flex: 1; padding-left: 14px; }
.card-name {
    font-size: 1.15rem; font-weight: 700;
    color: #1A1A1A; line-height: 1.2;
    margin-bottom: 3px;
}
.card-quote {
    font-size: 0.82rem; color: #999;
    font-style: italic; line-height: 1.5;
}

/* 描述 */
.card-desc {
    font-size: 0.9rem; color: #555; line-height: 1.8;
    margin-bottom: 16px; font-weight: 300;
}

/* 标签 */
.tag-row { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 14px; }
.tag {
    padding: 3px 12px; border-radius: 20px;
    font-size: 0.72rem; font-weight: 500; letter-spacing: 0.2px;
}
.tag-easy     { background: #EDFAF1; color: #2D7A4F; border: 1px solid #C3EFCF; }
.tag-medium   { background: #FFF9EC; color: #A0660A; border: 1px solid #FBDFA0; }
.tag-hard     { background: #FEF0F0; color: #C0392B; border: 1px solid #F5C6C6; }
.tag-free     { background: #EEF4FF; color: #2255CC; border: 1px solid #C5D8FF; }
.tag-paid     { background: #F4F0FF; color: #6633CC; border: 1px solid #D6C5FF; }
.tag-freemium { background: #EDFAFA; color: #0A7A7A; border: 1px solid #AADEDE; }
.tag-cn       { background: #EDFAF1; color: #2D7A4F; border: 1px solid #C3EFCF; }
.tag-nocn     { background: #FEF0F0; color: #C0392B; border: 1px solid #F5C6C6; }
.tag-partial  { background: #FFF9EC; color: #A0660A; border: 1px solid #FBDFA0; }

/* 投票条 */
.vote-bar-wrap { margin-bottom: 6px; }
.vote-label {
    font-size: 0.72rem; color: #C0BAB0; margin-bottom: 6px;
    display: flex; justify-content: space-between; align-items: center;
}
.vote-track {
    height: 6px; border-radius: 6px;
    background: #F0EDE8; overflow: hidden; display: flex;
}
.vote-green { background: #4CAF50; }
.vote-red   { background: #EF5350; }
.vote-pct   {
    display: flex; justify-content: space-between;
    font-size: 0.7rem; color: #C0BAB0; margin-top: 4px;
}
.vote-count { font-size: 0.68rem; color: #D0CCC4; text-align: right; margin-top: 2px; }

/* 真香/避雷详情 */
.scenario-block { padding: 4px 0 8px; }
.scenario-good { color: #2D7A4F; font-weight: 600; margin-bottom: 6px; font-size: 0.88rem; }
.scenario-bad  { color: #C0392B; font-weight: 600; margin-bottom: 6px; font-size: 0.88rem; margin-top: 14px; }
.scenario-item { font-size: 0.84rem; color: #666; margin: 4px 0 4px 14px; line-height: 1.65; }

/* 分割线 */
.divider { border: none; border-top: 1px solid #ECEAE4; margin: 1.6rem 0; }

/* 空状态 */
.empty-state {
    text-align: center; padding: 4rem 0; color: #C0BAB0;
    font-size: 0.95rem; line-height: 2;
}

/* 已投票 badge */
.voted-badge {
    font-size: 0.65rem; background: #F0EDE6; color: #999;
    border-radius: 8px; padding: 2px 8px; margin-left: 6px;
    font-style: normal;
}

/* 结果小标题 */
.result-heading {
    font-size: 0.78rem; color: #AAA; letter-spacing: 1.5px;
    text-transform: uppercase; font-weight: 500;
    margin-bottom: 1.2rem; margin-top: 0.4rem;
}

/* ── 手机适配 ── */
@media (max-width: 480px) {
    .hero-title { font-size: 2rem; }
    .modal-grid { grid-template-columns: repeat(5, 1fr); gap: 6px; }
    .modal-item { padding: 12px 4px 10px; border-radius: 12px; }
    .modal-icon-svg { width: 22px; height: 22px; }
    .modal-lbl { font-size: 0.68rem; }
    .card { padding: 18px 16px 14px; }
    [data-testid="stMainBlockContainer"] { padding: 0 10px; }
}
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# 投票持久化系统
# ──────────────────────────────────────────────
VOTES_FILE = Path("votes.json")

def load_votes() -> dict:
    """从 votes.json 加载投票数据"""
    if VOTES_FILE.exists():
        try:
            with open(VOTES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_votes(votes: dict):
    """将投票数据写入 votes.json"""
    with open(VOTES_FILE, "w", encoding="utf-8") as f:
        json.dump(votes, f, ensure_ascii=False, indent=2)

def get_vote_stats(product_id: str) -> tuple:
    """
    返回 (真香票数, 避雷票数, 总票数)
    以产品预设 vote_green% × 50票 为基准底数，叠加真实投票
    """
    votes = st.session_state.get("votes_db", {})
    p = next((x for x in PRODUCTS if x["id"] == product_id), None)
    if not p:
        return 0, 0, 1
    base        = 50
    base_green  = round(p["vote_green"] / 100 * base)
    base_red    = base - base_green
    real_green  = votes.get(product_id, {}).get("green", 0)
    real_red    = votes.get(product_id, {}).get("red",   0)
    total_green = base_green + real_green
    total_red   = base_red   + real_red
    total       = total_green + total_red
    return total_green, total_red, total

def cast_vote(product_id: str, vote_type: str) -> bool:
    """记录投票；同 session 内每产品只能投一次，返回是否成功"""
    voted_set = st.session_state.setdefault("voted_products", set())
    if product_id in voted_set:
        return False
    votes = st.session_state.get("votes_db", {})
    votes.setdefault(product_id, {"green": 0, "red": 0})
    votes[product_id][vote_type] += 1
    st.session_state["votes_db"] = votes
    save_votes(votes)
    voted_set.add(product_id)
    return True


# ──────────────────────────────────────────────
# 产品数据库（20 款，五大模态）
# ──────────────────────────────────────────────
PRODUCTS = [

    # ════ 文字类（5 款）════
    {
        "id": "chatgpt", "name": "ChatGPT", "emoji": "💬", "modal": "文字",
        "tagline": "OpenAI 出品，全球最知名的 AI 对话助手",
        "desc": "就像有个全能朋友 24 小时陪你聊天、帮你改作文、写邮件、想方案。说人话就能用，不需要任何技术背景。",
        "difficulty": "easy", "price_tag": "freemium", "cn_friendly": "partial", "vote_green": 78,
        "keywords": ["写作", "聊天", "邮件", "汇报", "改文章", "作文", "文案", "助手", "回复"],
        "good": ["需要快速起草一封正式邮件或信函", "想把粗糙想法整理成流畅文章", "遇到不懂的概念，想要简单易懂的解释", "需要头脑风暴列出各种方案"],
        "bad":  ["需要访问实时新闻或股票价格", "要处理涉及个人隐私的敏感文件", "在大陆网络下需要稳定访问（经常不稳定）"],
    },
    {
        "id": "kimi", "name": "Kimi", "emoji": "🌙", "modal": "文字",
        "tagline": "月之暗面出品，大陆最好用的长文档 AI",
        "desc": "特别擅长读超长文件，把厚合同或报告丢给它，帮你找重点、做总结。大陆直接用，不用翻墙。",
        "difficulty": "easy", "price_tag": "freemium", "cn_friendly": "cn", "vote_green": 82,
        "keywords": ["合同", "文档", "总结", "报告", "论文", "长文", "阅读", "大陆", "国内", "PDF"],
        "good": ["手里有超长 PDF 或合同，想快速提取关键信息", "需要把英文文件翻译并总结成中文要点", "在国内网络想要稳定好用的 AI 助手", "学生党想分析论文、梳理知识点"],
        "bad":  ["需要生成图片或处理音视频内容", "想要进行深度创意写作（风格不如 GPT-4 灵活）"],
    },
    {
        "id": "claude", "name": "Claude", "emoji": "🤝", "modal": "文字",
        "tagline": "Anthropic 出品，最擅长长篇写作与深度分析",
        "desc": "特别适合写长文章、分析复杂问题、读超长资料。回答很有条理，不乱说，适合需要认真思考的任务。",
        "difficulty": "easy", "price_tag": "freemium", "cn_friendly": "partial", "vote_green": 80,
        "keywords": ["分析", "长文", "写作", "阅读", "研究", "报告", "总结", "深度", "思考", "逻辑"],
        "good": ["需要对复杂问题进行深入分析和拆解", "想写一篇有逻辑有结构的长文章或报告", "需要 AI 认真读懂你给的长资料再回答"],
        "bad":  ["需要联网搜索最新信息（免费版不能联网）", "在大陆网络下需要稳定访问"],
    },
    {
        "id": "notion_ai", "name": "Notion AI", "emoji": "📝", "modal": "文字",
        "tagline": "Notion 内置 AI，笔记写作一体化",
        "desc": "已经在用 Notion 记笔记？AI 功能直接嵌在里面——一键帮你扩写、缩短、改语气，不用切换任何软件。",
        "difficulty": "easy", "price_tag": "paid", "cn_friendly": "partial", "vote_green": 65,
        "keywords": ["笔记", "写作", "整理", "Notion", "日记", "项目管理", "工作", "计划"],
        "good": ["本来就在用 Notion 管理工作或生活笔记", "需要把零散的会议记录整理成结构化文档", "想在同一个地方写作并获得 AI 润色建议"],
        "bad":  ["从没用过 Notion，光学工具就要花不少时间", "只是偶尔写写东西，不值得为此单独付费"],
    },
    {
        "id": "xunfei", "name": "讯飞星火", "emoji": "🔥", "modal": "文字",
        "tagline": "科大讯飞出品，大陆原生 AI 语音写作助手",
        "desc": "国内老牌 AI 厂商出品，语音识别超强，聊天写作也不错。特别适合需要语音输入的场景，手机 App 体验流畅。",
        "difficulty": "easy", "price_tag": "freemium", "cn_friendly": "cn", "vote_green": 71,
        "keywords": ["语音", "写作", "大陆", "国内", "手机", "办公", "汇报", "作文", "朗读"],
        "good": ["习惯用语音输入，想边说边让 AI 帮你整理", "在国内网络，需要稳定且免费的 AI 助手", "学生党需要作文批改和辅导"],
        "bad":  ["需要处理复杂的英文内容（中文明显更强）", "对话风格比较正式，不太像朋友聊天"],
    },

    # ════ 图片类（4 款）════
    {
        "id": "midjourney", "name": "Midjourney", "emoji": "🎨", "modal": "图片",
        "tagline": "目前画风最美的 AI 绘图工具",
        "desc": "输入一段描述，几秒钟就能生成像艺术家画的高质量图片。适合做海报、插画、头像、贺卡背景图。",
        "difficulty": "medium", "price_tag": "paid", "cn_friendly": "partial", "vote_green": 85,
        "keywords": ["画图", "插画", "海报", "贺卡", "图片", "设计", "头像", "背景", "绘画", "电子贺卡", "艺术"],
        "good": ["想给亲人做一张漂亮的定制电子贺卡", "需要高质量的活动海报或封面图", "想把文字描述变成一幅画", "做自媒体需要源源不断的配图素材"],
        "bad":  ["想画真实存在的人物（容易出错变形）", "需要精准修改图片中的某个细节", "完全不想付费，只想免费体验"],
    },
    {
        "id": "canva_ai", "name": "Canva AI", "emoji": "✏️", "modal": "图片",
        "tagline": "设计小白的救星，模板 + AI 二合一",
        "desc": "不懂设计也能做出好看的东西。选一个模板，让 AI 帮你填内容、换图片，生日邀请函、朋友圈海报、简历都能轻松搞定。",
        "difficulty": "easy", "price_tag": "freemium", "cn_friendly": "partial", "vote_green": 80,
        "keywords": ["海报", "简历", "邀请函", "朋友圈", "设计", "模板", "生日", "贺卡", "电子贺卡", "图片"],
        "good": ["需要制作生日贺卡、活动邀请函、朋友圈海报", "完全没有设计基础但想要专业效果", "需要快速制作简历或个人介绍页"],
        "bad":  ["需要非常复杂的专业设计（还是要学 PS）", "想要完全原创的、无模板痕迹的作品"],
    },
    {
        "id": "stable_diffusion", "name": "Stable Diffusion", "emoji": "🌊", "modal": "图片",
        "tagline": "完全免费可本地部署的开源绘图工具",
        "desc": "开源免费，可以安装到自己电脑上用，画多少都不要钱。但需要电脑配置不错，安装过程稍复杂，适合愿意折腾的人。",
        "difficulty": "hard", "price_tag": "free", "cn_friendly": "cn", "vote_green": 72,
        "keywords": ["免费", "画图", "开源", "本地", "插画", "图片", "二次元", "动漫", "无限生成"],
        "good": ["愿意折腾，想要完全免费、无限生成图片", "对画图有较高要求，想要更多自定义控制", "对二次元或特定画风有需求"],
        "bad":  ["电脑配置一般，安装可能失败", "想要开箱即用、不折腾的体验", "完全没有技术背景的小白"],
    },
    {
        "id": "meitu_ai", "name": "美图秀秀 AI", "emoji": "💄", "modal": "图片",
        "tagline": "国内最好用的 AI 修图美化工具",
        "desc": "手机上直接用，一键 AI 美颜、换背景、消除路人、老照片修复。适合不懂设计但经常需要修图的普通用户。",
        "difficulty": "easy", "price_tag": "freemium", "cn_friendly": "cn", "vote_green": 76,
        "keywords": ["修图", "美颜", "照片", "换背景", "老照片", "手机", "国内", "大陆", "消除", "修复"],
        "good": ["想修复模糊或泛黄的老照片", "需要去掉照片里多余的路人或杂物", "日常自拍想要自然好看的美颜效果"],
        "bad":  ["需要从零创作全新的艺术图片（不是修图工具）", "追求专业摄影级别的后期处理"],
    },

    # ════ 音频类（4 款）════
    {
        "id": "elevenlabs", "name": "ElevenLabs", "emoji": "🎙️", "modal": "音频",
        "tagline": "最像真人的 AI 配音工具",
        "desc": "输入一段文字，几秒钟就能生成非常自然的人声朗读。可以选择各种音色、语速、情绪，给视频配音、做有声书都很好用。",
        "difficulty": "easy", "price_tag": "freemium", "cn_friendly": "partial", "vote_green": 88,
        "keywords": ["配音", "朗读", "声音", "有声书", "视频配音", "语音", "说话", "会说话", "电子贺卡", "祝福", "文字转语音"],
        "good": ["想给贺卡或视频加一段温暖的语音祝福", "做自媒体视频需要真人感的旁白配音", "想把文章变成有声内容，方便边走路边听"],
        "bad":  ["需要中文方言配音（对普通话以外支持有限）", "想用自己的声音克隆（需要额外设置）"],
    },
    {
        "id": "whisper", "name": "Whisper / 飞书妙记", "emoji": "🎤", "modal": "音频",
        "tagline": "会议录音自动变成文字稿",
        "desc": "开会、上课、聊天录音之后，丢进去就能自动转成文字，还能识别不同的说话人，再也不用手动做会议记录了。",
        "difficulty": "easy", "price_tag": "freemium", "cn_friendly": "cn", "vote_green": 90,
        "keywords": ["录音", "会议", "转文字", "字幕", "听写", "记录", "速记", "上课", "采访", "语音转文字"],
        "good": ["开会太多，想让 AI 自动整理会议要点", "采访、课堂录音需要快速转成文字稿", "视频或播客需要生成字幕文件"],
        "bad":  ["录音质量很差、噪音很多（识别准确率下降）", "需要实时同声传译（目前做不到）"],
    },
    {
        "id": "suno", "name": "Suno", "emoji": "🎵", "modal": "音频",
        "tagline": "输入歌词，AI 帮你谱曲演唱",
        "desc": "你写几句歌词或者描述想要的风格，Suno 就能生成一首完整的歌，有旋律有人声，感觉真的是 AI 在唱歌，非常神奇。",
        "difficulty": "easy", "price_tag": "freemium", "cn_friendly": "partial", "vote_green": 83,
        "keywords": ["音乐", "歌曲", "作曲", "唱歌", "歌词", "原创", "旋律", "背景音乐", "创作"],
        "good": ["想给自己或朋友做一首独一无二的原创歌曲", "需要视频的背景音乐，不想用版权素材", "纯粹好奇想体验 AI 作曲的神奇感"],
        "bad":  ["需要对歌曲进行精细编辑和调整（控制粒度有限）", "对音乐质量要求极高的专业场景"],
    },
    {
        "id": "notta", "name": "Notta", "emoji": "📋", "modal": "音频",
        "tagline": "中文最准的实时语音转文字工具",
        "desc": "中文识别率极高，开会时手机一放，实时就能看到文字版对话。支持多种语言混说，还能自动生成会议摘要。",
        "difficulty": "easy", "price_tag": "freemium", "cn_friendly": "cn", "vote_green": 79,
        "keywords": ["会议", "转文字", "录音", "摘要", "记录", "实时", "中文", "速记", "国内", "语音"],
        "good": ["需要中英文混合的会议实时记录", "想要自动生成简洁的会议摘要和待办事项", "经常出差开会，不方便手动记笔记"],
        "bad":  ["录音环境嘈杂（背景噪音影响识别）", "想同时做音乐或其他音频创作"],
    },

    # ════ 视频类（4 款）════
    {
        "id": "runway", "name": "Runway Gen-3", "emoji": "🎬", "modal": "视频",
        "tagline": "输入文字或图片，直接生成短视频",
        "desc": "你描述一个场景，它就能生成一段几秒钟的高质量视频片段。特别适合做创意短片素材和艺术感内容。",
        "difficulty": "medium", "price_tag": "paid", "cn_friendly": "partial", "vote_green": 75,
        "keywords": ["视频", "短片", "动画", "素材", "创意", "短视频", "文字生成视频", "影片", "特效"],
        "good": ["自媒体创作者需要独特的 B 格视频素材", "想把静态图片变成有动感的短视频", "做创意广告或品牌宣传片的辅助素材"],
        "bad":  ["想生成超过 10 秒的完整剧情视频", "需要视频里有清晰可辨认的人脸", "预算有限，这个费用比较贵"],
    },
    {
        "id": "heygen", "name": "HeyGen", "emoji": "👤", "modal": "视频",
        "tagline": "让数字人替你出镜讲话",
        "desc": "不想自己出镜？选一个虚拟人物，输入你要说的话，它会帮你生成一段像真人播报的视频。做企业介绍、课程视频特别方便。",
        "difficulty": "medium", "price_tag": "paid", "cn_friendly": "partial", "vote_green": 70,
        "keywords": ["数字人", "播报", "虚拟主播", "不出镜", "企业视频", "课程视频", "培训", "主播", "讲解"],
        "good": ["不想自己出镜但需要制作讲解类视频", "需要快速制作多语言版本的产品介绍", "做内部培训材料，想要有人物出镜的效果"],
        "bad":  ["对真实感要求极高（仔细看还是能看出 AI 痕迹）", "想用自己的形象克隆（需要付高级套餐）"],
    },
    {
        "id": "capcut_ai", "name": "剪映 AI", "emoji": "✂️", "modal": "视频",
        "tagline": "抖音官方剪辑工具，AI 功能最接地气",
        "desc": "手机电脑都能用，自动字幕、一键成片、AI 配音、去背景，功能全面且大部分免费。国内用户首选剪视频工具。",
        "difficulty": "easy", "price_tag": "freemium", "cn_friendly": "cn", "vote_green": 86,
        "keywords": ["剪辑", "视频", "字幕", "短视频", "抖音", "一键成片", "配音", "国内", "大陆", "手机", "剪片"],
        "good": ["想剪抖音或视频号的短视频，要字幕和配音", "需要快速把照片和视频素材拼成一个完整视频", "第一次做视频，想要简单上手的工具"],
        "bad":  ["需要专业级别的精细剪辑（还是要用 Premiere）", "内容需要发布在海外平台，部分素材有版权限制"],
    },
    {
        "id": "pika", "name": "Pika", "emoji": "⚡", "modal": "视频",
        "tagline": "最容易上手的 AI 图转视频工具",
        "desc": "把一张静态图片上传，描述你想要的动态效果，Pika 就能让图片动起来。做动态表情包、给照片加动效特别好玩。",
        "difficulty": "easy", "price_tag": "freemium", "cn_friendly": "partial", "vote_green": 73,
        "keywords": ["图片变视频", "动画", "动态", "表情包", "短视频", "特效", "照片动起来", "动效"],
        "good": ["想让静态照片变成有动感的短视频", "做有趣的动态表情包或创意内容", "想体验 AI 视频但不想花太多钱"],
        "bad":  ["需要超过几秒的长视频（生成片段较短）", "对视频的具体细节要求很精准（随机性较高）"],
    },

    # ════ 综合类（3 款）════
    {
        "id": "doubao", "name": "豆包", "emoji": "🫘", "modal": "综合",
        "tagline": "字节跳动出品，大陆最好用的综合 AI 助手",
        "desc": "聊天、写作、画图、做 PPT、分析文件，一个 App 全搞定。大陆直接用，免费功能很多，手机端体验特别流畅，送给爸妈用超合适。",
        "difficulty": "easy", "price_tag": "freemium", "cn_friendly": "cn", "vote_green": 87,
        "keywords": ["综合", "国内", "大陆", "全能", "PPT", "聊天", "画图", "送老人", "爷爷", "奶奶", "家人", "电子贺卡", "会说话", "手机"],
        "good": ["给不懂技术的父母或老人推荐第一个 AI 工具", "在国内网络，想要一个什么都能做的 AI 助手", "想做电子贺卡并加上语音祝福", "日常办公需要写文案、做汇报、找灵感"],
        "bad":  ["需要非常前沿的英文内容创作（中文强，英文稍弱）", "对数据隐私非常敏感（国内产品数据存储在境内）"],
    },
    {
        "id": "wenxin", "name": "文心一言", "emoji": "🖊️", "modal": "综合",
        "tagline": "百度出品，中文理解最深的综合 AI",
        "desc": "百度深耕中文多年，对中国文化、历史、诗词的理解特别到位。大陆直连，还能联网搜索最新信息，适合学生和职场人士。",
        "difficulty": "easy", "price_tag": "freemium", "cn_friendly": "cn", "vote_green": 73,
        "keywords": ["综合", "国内", "大陆", "中文", "百度", "联网", "搜索", "学生", "办公", "写作", "诗词"],
        "good": ["需要联网搜索最新资讯并整理成报告", "对中文诗词、历史文化有问答需求", "学生党需要作业辅导和知识讲解"],
        "bad":  ["需要生成高质量的创意图片", "对话回答有时过于谨慎，不够直接"],
    },
    {
        "id": "copilot", "name": "Microsoft Copilot", "emoji": "🪟", "modal": "综合",
        "tagline": "微软出品，Office 全家桶的 AI 管家",
        "desc": "如果你天天用 Word、Excel、PPT，那 Copilot 就是你的神器——直接在这些软件里帮你写内容、做表格、总结邮件，完全不用切换。",
        "difficulty": "medium", "price_tag": "paid", "cn_friendly": "partial", "vote_green": 74,
        "keywords": ["Word", "Excel", "PPT", "Office", "办公", "表格", "邮件", "微软", "企业", "职场", "公式"],
        "good": ["每天大量使用 Word、Excel、Outlook 处理工作", "公司已购买微软 365，想直接用 AI 提效", "需要在 Excel 里自动分析数据、写公式"],
        "bad":  ["不用微软全家桶，那这个钱就白花了", "个人用户觉得订阅费用偏高"],
    },
]


# ──────────────────────────────────────────────
# 意图识别
# ──────────────────────────────────────────────
def intent_recognition(user_input: str, modal_filter: str | None) -> list:
    if not user_input.strip():
        if modal_filter and modal_filter != "综合":
            return [p for p in PRODUCTS if p["modal"] == modal_filter]
        return PRODUCTS

    text = user_input.lower()
    stopwords = {"我", "想", "要", "的", "一个", "一张", "帮", "做", "给", "用", "来",
                 "吗", "啊", "呢", "吧", "了", "是", "可以", "能", "能不能", "怎么", "如何"}
    tokens = set(re.split(r"[\s，。！？、,.]+", text)) - stopwords

    scores: dict = {}
    for p in PRODUCTS:
        if modal_filter and modal_filter != "综合" and p["modal"] != modal_filter:
            continue
        score = 0.0
        for kw in p["keywords"]:
            if kw in text:
                score += 3
        for token in tokens:
            if len(token) < 2:
                continue
            for kw in p["keywords"]:
                if token in kw or kw in token:
                    score += 1
        if p["cn_friendly"] == "cn":
            score += 0.5
        scores[p["id"]] = score

    ranked = sorted(
        [p for p in PRODUCTS if p["id"] in scores],
        key=lambda p: scores[p["id"]],
        reverse=True,
    )
    ranked = [p for p in ranked if scores[p["id"]] > 0]
    if not ranked and modal_filter and modal_filter != "综合":
        ranked = [p for p in PRODUCTS if p["modal"] == modal_filter]
    return ranked or PRODUCTS


# ──────────────────────────────────────────────
# 辅助渲染
# ──────────────────────────────────────────────
DIFFICULTY_MAP = {
    "easy":   ("🟢 新手友好",  "tag-easy"),
    "medium": ("🟡 稍需摸索", "tag-medium"),
    "hard":   ("🔴 有点门槛", "tag-hard"),
}
PRICE_MAP = {
    "free":     ("🆓 完全免费",  "tag-free"),
    "freemium": ("⚡ 免费可用",  "tag-freemium"),
    "paid":     ("💳 需要付费",  "tag-paid"),
}
CN_MAP = {
    "cn":      ("🇨🇳 大陆直连",     "tag-cn"),
    "partial": ("⚠️ 偶尔需要梯子", "tag-partial"),
    "nocn":    ("🚫 需要翻墙",      "tag-nocn"),
}

def render_tags(p: dict) -> str:
    dl, dc = DIFFICULTY_MAP[p["difficulty"]]
    pl, pc = PRICE_MAP[p["price_tag"]]
    cl, cc = CN_MAP[p["cn_friendly"]]
    return f'<div class="tag-row"><span class="tag {dc}">{dl}</span><span class="tag {pc}">{pl}</span><span class="tag {cc}">{cl}</span></div>'

def render_vote_bar(green: int, red: int, total: int) -> str:
    g_pct = round(green / total * 100) if total > 0 else 50
    r_pct = 100 - g_pct
    return f"""
    <div class="vote-bar-wrap">
        <div class="vote-label">
            <span>红绿灯投票</span>
            <span style="color:#D0CCC4;font-size:0.68rem;">{total} 票</span>
        </div>
        <div class="vote-track">
            <div class="vote-green" style="width:{g_pct}%"></div>
            <div class="vote-red"   style="width:{r_pct}%"></div>
        </div>
        <div class="vote-pct"><span>👍 {g_pct}%</span><span>{r_pct}% 👎</span></div>
    </div>"""

def render_scenario(p: dict) -> str:
    good = "".join(f'<div class="scenario-item">· {x}</div>' for x in p["good"])
    bad  = "".join(f'<div class="scenario-item">· {x}</div>' for x in p["bad"])
    return f'<div class="scenario-block"><div class="scenario-good">👍 真香：这些情况超好用</div>{good}<div class="scenario-bad">👎 避雷：这些情况别选它</div>{bad}</div>'

def render_product_card(p: dict):
    pid = p["id"]
    green, red, total = get_vote_stats(pid)
    already_voted = pid in st.session_state.get("voted_products", set())
    voted_badge = '<span class="voted-badge">✓ 已投</span>' if already_voted else ""

    # 引言句：取 tagline 的后半段作为卡片引语
    quote = p["tagline"]

    st.markdown(f"""
    <div class="card">
        <div class="card-top">
            <div class="card-avatar">{p['emoji']}</div>
            <div class="card-meta">
                <div class="card-name">{p['name']}{voted_badge}</div>
                <div class="card-quote">"{quote}"</div>
            </div>
        </div>
        <div class="card-desc">{p['desc']}</div>
        {render_tags(p)}
        {render_vote_bar(green, red, total)}
    </div>""", unsafe_allow_html=True)

    if not already_voted:
        vc1, vc2, vc3 = st.columns([1, 1, 3])
        with vc1:
            if st.button("👍 真香", key=f"g_{pid}", use_container_width=True):
                if cast_vote(pid, "green"):
                    st.rerun()
        with vc2:
            if st.button("👎 避雷", key=f"r_{pid}", use_container_width=True):
                if cast_vote(pid, "red"):
                    st.rerun()
    else:
        st.caption("✅ 已记录，感谢投票")

    with st.expander(f"收起对比  ↕  {p['name']}"):
        st.markdown(render_scenario(p), unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# Session 初始化
# ──────────────────────────────────────────────
if "selected_modal" not in st.session_state:
    st.session_state.selected_modal = None
if "votes_db" not in st.session_state:
    st.session_state.votes_db = load_votes()
if "voted_products" not in st.session_state:
    st.session_state.voted_products = set()


# ──────────────────────────────────────────────
# 侧边栏：实时口碑榜
# ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🏆 实时口碑排行榜")
    st.caption("真实用户投票 · 每人每款投一次")
    st.divider()

    ranking = []
    for p in PRODUCTS:
        g, r, t = get_vote_stats(p["id"])
        pct = round(g / t * 100) if t > 0 else 50
        ranking.append((p["name"], p["emoji"], pct, t, p["modal"]))
    ranking.sort(key=lambda x: x[2], reverse=True)

    for rank, (name, emoji, pct, total, modal) in enumerate(ranking, 1):
        medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else f"**{rank}.**"
        st.markdown(
            f"{medal} {emoji} **{name}**  \n"
            f"<span style='font-size:0.78rem;color:#aaa;'>{modal} · 👍{pct}% · {total}票</span>",
            unsafe_allow_html=True,
        )
        st.progress(pct / 100)

    st.divider()
    total_votes = sum(
        st.session_state["votes_db"].get(p["id"], {}).get("green", 0) +
        st.session_state["votes_db"].get(p["id"], {}).get("red", 0)
        for p in PRODUCTS
    )
    st.caption(f"📊 累计收到真实投票：{total_votes} 票")


# ──────────────────────────────────────────────
# 主页面 — 图二风格布局
# ──────────────────────────────────────────────

# Hero
st.markdown('<div class="hero-eyebrow">AI SELECTOR</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-title">让 AI 选型回归直觉</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-sub">不谈参数，不聊算力。只用大白话告诉你，<br>哪个 AI 才是你的「真香」选择。</div>',
    unsafe_allow_html=True
)

# ── 第一步：模态卡片（纯 HTML，手机友好）──
MODAL_ICONS = {
    "文字": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M4 7h16M4 12h10M4 17h13"/></svg>""",
    "图片": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="3" y="3" width="18" height="18" rx="3"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="m21 15-5-5L5 21"/></svg>""",
    "音频": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/></svg>""",
    "视频": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="2" y="6" width="15" height="12" rx="2"/><path d="m17 10 5-3v10l-5-3"/></svg>""",
    "综合": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="2" y="2" width="9" height="9" rx="1.5"/><rect x="13" y="2" width="9" height="9" rx="1.5"/><rect x="2" y="13" width="9" height="9" rx="1.5"/><rect x="13" y="13" width="9" height="9" rx="1.5"/></svg>""",
}

modal_items_html = ""
for label, svg in MODAL_ICONS.items():
    is_active = st.session_state.selected_modal == label
    active_cls = "active" if is_active else ""
    modal_items_html += f"""
    <div class="modal-item {active_cls}" onclick="
        var inputs = window.parent.document.querySelectorAll('input[type=text]');
    ">
        <div class="modal-icon-svg">{svg}</div>
        <div class="modal-lbl">{label}</div>
    </div>"""

# 用 Streamlit 按钮实现点击（HTML 版仅视觉）
cols = st.columns(5, gap="small")
MODALS = list(MODAL_ICONS.keys())
for i, label in enumerate(MODALS):
    with cols[i]:
        is_active = st.session_state.selected_modal == label
        svg = MODAL_ICONS[label]
        btn_html = f"""
        <div style="
            background:{'#1A1A1A' if is_active else '#FFFFFF'};
            border:1.5px solid {'#1A1A1A' if is_active else '#E8E4DC'};
            border-radius:16px; padding:16px 6px 12px;
            display:flex; flex-direction:column; align-items:center; gap:7px;
            cursor:pointer; transition:all 0.15s;
        ">
            <div style="width:26px;height:26px;{'filter:invert(1);' if is_active else 'opacity:0.6;'}">{svg}</div>
            <div style="font-size:0.75rem;color:{'#FFFFFF' if is_active else '#666'};font-weight:500;">{label}</div>
        </div>"""
        st.markdown(btn_html, unsafe_allow_html=True)
        # 隐藏原生按钮文字，只用来捕获点击
        if st.button("　", key=f"modal_{label}", use_container_width=True,
                     help=f"筛选{label}类 AI 工具"):
            st.session_state.selected_modal = label if not is_active else None
            st.rerun()

# 隐藏原生按钮的视觉，只保留点击区域
st.markdown("""
<style>
/* 把每个模态列的原生按钮叠在 HTML card 上，透明不可见 */
div[data-testid="column"] button {
    position: relative; margin-top: -70px;
    opacity: 0; height: 70px; width: 100%;
    cursor: pointer !important;
}
</style>""", unsafe_allow_html=True)

if st.session_state.selected_modal:
    st.markdown(
        f'<div style="text-align:center;font-size:0.8rem;color:#888;margin:8px 0 16px;">'
        f'已选择 · <b>{st.session_state.selected_modal}</b> · 可继续描述，或直接查看推荐</div>',
        unsafe_allow_html=True
    )

st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

# ── 第二步：搜索框 ──
user_query = st.text_input(
    label="search",
    placeholder="🔍  用大白话描述你想解决的问题...",
    label_visibility="collapsed",
)
st.markdown('<div class="search-hint">描述越具体，推荐越准确 · 例如「给爷爷做会说话的电子贺卡」</div>', unsafe_allow_html=True)

# ── 第三步：结果 ──
if st.session_state.selected_modal or user_query.strip():
    results = intent_recognition(user_query, st.session_state.selected_modal)

    if user_query.strip():
        st.markdown(f'<div class="result-heading">根据「{user_query}」找到 {len(results)} 款工具</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="result-heading">{st.session_state.selected_modal} 类工具 · 共 {len(results)} 款</div>', unsafe_allow_html=True)

    if not results:
        st.markdown('<div class="empty-state">暂未找到匹配工具<br>换个描述方式试试？</div>', unsafe_allow_html=True)
    else:
        for p in results:
            render_product_card(p)
else:
    st.markdown("""
    <div class="empty-state">
        点击上方类型卡片<br>
        或直接描述你的需求<br>
        <span style="font-size:0.78rem;color:#D0CCC4;">例如：帮我做电子贺卡 / 会议自动记录</span>
    </div>""", unsafe_allow_html=True)

# 页脚
st.markdown(
    "<div style='text-align:center;color:#D0CCC4;font-size:0.72rem;padding:2rem 0 1rem;'>"
    "AI Selector · 收录 20 款工具 · 仅供参考"
    "</div>",
    unsafe_allow_html=True,
)
