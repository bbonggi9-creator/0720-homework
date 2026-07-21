import re
from pathlib import Path
from html import escape
from urllib.parse import quote

import streamlit as st

# ---------------------------------
# 기본 설정
# ---------------------------------
st.set_page_config(
    page_title="연애 프로그램 추천",
    layout="wide"
)

# ---------------------------------
# 프로그램 데이터
# ---------------------------------
PROGRAMS = [
    {
        "name": "하트 시그널",
        "broadcaster": "채널A",
        "description": "같은 공간에서 생활하는 청춘 남녀의 미묘한 호감 신호와 추리의 재미를 함께 보는 연애 프로그램",
        "primary_category": "설렘·썸 중심",
        "secondary_category": "긴장감·자극 중심",
        "reviews": [
            "미묘한 분위기와 문자 장면이 특히 설레는 프로그램이에요.",
            "누가 누구를 선택할지 추리하면서 보는 재미가 커요."
        ],
        "star_fill": 3,
        "image_url": ""
    },
    {
        "name": "모태솔로지만 연애는 하고 싶어",
        "broadcaster": "넷플릭스",
        "description": "연애가 처음인 참가자들이 자신감과 스타일을 키우며 첫 설렘을 경험하는 성장형 프로그램",
        "primary_category": "성장·공감 중심",
        "secondary_category": "설렘·썸 중심",
        "reviews": [
            "서툰 모습이 오히려 더 공감되고 응원하게 돼요.",
            "변화해 가는 과정이 보여서 몰입감이 좋아요."
        ],
        "star_fill": 4,
        "image_url": ""
    },
    {
        "name": "솔로지옥",
        "broadcaster": "넷플릭스",
        "description": "강한 매력과 긴장감 속에서 직진 로맨스를 펼치는 고립형 데이팅 프로그램",
        "primary_category": "긴장감·자극 중심",
        "secondary_category": "설렘·썸 중심",
        "reviews": [
            "전개가 빠르고 분위기가 강해서 몰입하게 돼요.",
            "출연자들의 매력과 긴장감이 확실한 프로그램이에요."
        ],
        "star_fill": 4,
        "image_url": ""
    },
    {
        "name": "나는 SOLO",
        "broadcaster": "SBS Plus / ENA",
        "description": "결혼을 진지하게 생각하는 솔로들이 현실적인 대화와 선택을 이어가는 프로그램",
        "primary_category": "결혼·현실성 중심",
        "secondary_category": "긴장감·자극 중심",
        "reviews": [
            "현실적인 대화가 많아서 더 진짜처럼 느껴져요.",
            "솔직하고 직진하는 분위기가 강해서 몰입돼요."
        ],
        "star_fill": 5,
        "image_url": ""
    },
    {
        "name": "환승연애",
        "broadcaster": "TVING",
        "description": "헤어진 연인과 새로운 인연 사이에서 감정을 다시 확인하는 감정 몰입형 프로그램",
        "primary_category": "재회·감정서사 중심",
        "secondary_category": "성장·공감 중심",
        "reviews": [
            "과거와 현재 감정이 교차해서 감정선이 진하게 느껴져요.",
            "감정 흐름이 섬세해서 오래 기억에 남는 프로그램이에요."
        ],
        "star_fill": 3,
        "image_url": ""
    }
]

ALL_CATEGORIES = [
    "설렘·썸 중심",
    "성장·공감 중심",
    "긴장감·자극 중심",
    "결혼·현실성 중심",
    "재회·감정서사 중심"
]

CATEGORY_DESCRIPTIONS = {
    "설렘·썸 중심": "두근거리는 분위기와 미묘한 호감 신호를 즐기는 취향입니다.",
    "성장·공감 중심": "서툰 감정과 변화 과정을 공감하며 보는 취향입니다.",
    "긴장감·자극 중심": "빠른 전개와 강한 긴장감이 있는 구성에 끌리는 취향입니다.",
    "결혼·현실성 중심": "현실적인 대화와 진지한 선택 과정을 선호하는 취향입니다.",
    "재회·감정서사 중심": "과거와 현재의 감정선이 깊게 이어지는 이야기를 좋아합니다."
}

CATEGORY_CLASS_MAP = {
    "설렘·썸 중심": "tag-romance",
    "성장·공감 중심": "tag-growth",
    "긴장감·자극 중심": "tag-tension",
    "결혼·현실성 중심": "tag-reality",
    "재회·감정서사 중심": "tag-reunion"
}

CATEGORY_ALIASES = {
    "긴장-자극 중심": "긴장감·자극 중심",
    "긴장자극 중심": "긴장감·자극 중심",
    "긴장-자극중심": "긴장감·자극 중심",
    "긴장자극중심": "긴장감·자극 중심",
    "재회-감정서사 중심": "재회·감정서사 중심",
    "재회감정서사 중심": "재회·감정서사 중심",
    "재회-감정서사중심": "재회·감정서사 중심",
    "재회감정서사중심": "재회·감정서사 중심",
}

IMAGE_NAME_MAP = {
    "하트 시그널": "하트시그널",
    "모태솔로지만 연애는 하고 싶어": "모태솔로지만연애는하고싶어",
    "솔로지옥": "솔로지옥",
    "나는 SOLO": "나는솔로",
    "환승연애": "환승연애",
}

# ---------------------------------
# CSS
# ---------------------------------
def normalize_category_name(value: str) -> str:
    if value in CATEGORY_ALIASES:
        return CATEGORY_ALIASES[value]

    for category in ALL_CATEGORIES:
        if value == category:
            return category

    normalized_value = re.sub(r"[\s·-]+", "", value).lower()
    for category in ALL_CATEGORIES:
        if re.sub(r"[\s·-]+", "", category).lower() == normalized_value:
            return category

    return value


def inject_css():
    st.markdown(
        """
        <style>
        :root {
            color-scheme: light dark;
            --bg: #f7f8fb;
            --card-bg: #ffffff;
            --card-bg-dark: rgba(17, 24, 39, 0.94);
            --border: #e5e7eb;
            --text-main: #111827;
            --text-sub: #4b5563;
            --accent: #e11d48;
            --soft: #f3f4f6;
        }

        @media (prefers-color-scheme: dark) {
            :root {
                --bg: #0f172a;
                --card-bg: var(--card-bg-dark);
                --border: rgba(148, 163, 184, 0.28);
                --text-main: #f9fafb;
                --text-sub: #cbd5e1;
                --accent: #fb7185;
                --soft: rgba(30, 41, 59, 0.82);
            }
        }

        html, body, [class*="css"] {
            font-family: Pretendard, "Noto Sans KR", "Apple SD Gothic Neo", sans-serif;
            background: var(--bg);
            color: var(--text-main);
        }

        .stApp {
            background: var(--bg);
        }

        .block-container {
            max-width: 1400px;
            padding-top: 2.5rem;
            padding-bottom: 3rem;
        }

        .hero-box, .section-box {
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 18px;
            padding: 24px;
            margin-bottom: 16px;
            box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
            text-align: center;
        }

        .section-box.category-box {
            background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
            border-color: #bae6fd;
        }

        .hero-box {
            background: linear-gradient(135deg, #fdf2f8 0%, #fff7ed 45%, #eef2ff 100%);
            border-color: #f9a8d4;
            padding: 32px 28px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
        }

        .hero-title {
            font-size: 2.5rem;
            font-weight: 800;
            margin: 0 0 10px 0;
            color: #111827;
            line-height: 1.25;
            letter-spacing: -0.02em;
        }

        .hero-desc {
            font-size: 1.05rem;
            line-height: 1.75;
            margin: 0 auto;
            max-width: 860px;
            color: #374151;
            text-align: center;
            display: block;
            width: 100%;
        }

        .cards-grid, .recommend-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
            gap: 12px;
            margin-top: 8px;
        }

        .program-card, .recommend-card {
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 18px;
            overflow: hidden;
            height: 100%;
            display: flex;
            flex-direction: column;
            min-height: 100%;
            text-align: center;
        }

        .poster {
            width: 100%;
            aspect-ratio: 3 / 4.2;
            object-fit: cover;
            display: block;
            background: #111827;
            border-bottom: 1px solid var(--border);
            border-radius: 0;
        }

        .card-body {
            padding: 16px;
            display: flex;
            flex-direction: column;
            gap: 8px;
            align-items: center;
            text-align: center;
        }

        .program-title {
            font-size: 1.15rem;
            font-weight: 800;
            color: var(--text-main);
            margin: 0;
            line-height: 1.4;
        }

        .broadcaster {
            font-size: 0.92rem;
            font-weight: 700;
            color: var(--accent);
            margin: 0;
        }

        .desc {
            font-size: 0.95rem;
            line-height: 1.65;
            color: var(--text-sub);
            margin: 0;
        }

        .badge-row {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 2px;
            justify-content: center;
        }

        .tag {
            display: inline-block;
            padding: 6px 10px;
            border-radius: 999px;
            font-size: 0.8rem;
            font-weight: 700;
            border: 1px solid var(--border);
            background: var(--soft);
            color: var(--text-sub);
        }

        .tag-romance { background: #fff1f2; color: #be123c; border-color: #fecdd3; }
        .tag-growth { background: #eff6ff; color: #1d4ed8; border-color: #bfdbfe; }
        .tag-tension { background: #fff7ed; color: #c2410c; border-color: #fed7aa; }
        .tag-reality { background: #f3f4f6; color: #374151; border-color: #d1d5db; }
        .tag-reunion { background: #faf5ff; color: #7e22ce; border-color: #e9d5ff; }

        @media (prefers-color-scheme: dark) {
            .tag-romance { background: rgba(190, 24, 93, 0.16); color: #fecdd3; border-color: rgba(251, 113, 133, 0.35); }
            .tag-growth { background: rgba(37, 99, 235, 0.16); color: #bfdbfe; border-color: rgba(96, 165, 250, 0.35); }
            .tag-tension { background: rgba(234, 88, 12, 0.16); color: #fdba74; border-color: rgba(251, 146, 60, 0.35); }
            .tag-reality { background: rgba(148, 163, 184, 0.14); color: #e5e7eb; border-color: rgba(148, 163, 184, 0.28); }
            .tag-reunion { background: rgba(126, 34, 206, 0.16); color: #e9d5ff; border-color: rgba(192, 132, 252, 0.35); }
        }

        .review-list {
            margin: 0;
            padding-left: 0;
            list-style: none;
            color: var(--text-sub);
            font-size: 0.92rem;
            line-height: 1.6;
        }

        .star-row {
            display: flex;
            gap: 4px;
            font-size: 1.05rem;
            color: #f59e0b;
            margin-top: 2px;
        }

        .star-empty {
            color: #cbd5e1;
        }

        @media (prefers-color-scheme: dark) {
            .hero-box {
                background: linear-gradient(135deg, rgba(190, 24, 93, 0.18) 0%, rgba(234, 88, 12, 0.16) 45%, rgba(59, 130, 246, 0.16) 100%);
                border-color: rgba(251, 113, 133, 0.35);
            }
            .hero-title { color: #f8fafc; }
            .hero-desc { color: #e2e8f0; }
            .star-empty { color: #64748b; }
        }

        .section-title {
            font-size: 1.15rem;
            font-weight: 800;
            color: var(--text-main);
            margin: 0 0 6px 0;
        }

        .helper-text {
            color: var(--text-sub);
            font-size: 0.95rem;
            line-height: 1.65;
            margin: 0;
        }

        .placeholder-box {
            width: 100%;
            min-height: 180px;
            border-radius: 12px;
            background: linear-gradient(135deg, #e2e8f0, #f8fafc);
            display: flex;
            align-items: center;
            justify-content: center;
            color: #475569;
            font-size: 0.95rem;
            font-weight: 700;
            border: 1px solid var(--border);
            margin-bottom: 10px;
        }

        .muted-text {
            color: var(--text-sub);
            font-size: 0.92rem;
            line-height: 1.6;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# ---------------------------------
# 이미지 / HTML 도우미
# ---------------------------------
# ---------------------------------
# 이미지 / HTML 도우미
# ---------------------------------
def normalize_text(text: str) -> str:
    return re.sub(r"[^0-9가-힣a-zA-Z]+", "", text).lower()


def find_image_path(program_name: str):
    candidates = [program_name]
    if program_name in IMAGE_NAME_MAP:
        candidates.append(IMAGE_NAME_MAP[program_name])

    for name in candidates:
        normalized_name = normalize_text(name)
        for path in sorted(Path(__file__).resolve().parent.iterdir()):
            if path.is_file() and normalize_text(path.stem) == normalized_name:
                return path
    return None


def make_placeholder_image(title: str) -> str:
    safe_title = escape(title)
    svg = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="800" height="1120" viewBox="0 0 800 1120">
      <rect width="100%" height="100%" fill="#0f172a" />
      <rect x="32" y="32" width="736" height="1056" rx="28" fill="#1e293b" />
      <rect x="60" y="70" width="680" height="180" rx="18" fill="#334155" />
      <text x="400" y="170" text-anchor="middle" fill="#f8fafc" font-size="34" font-family="Arial, sans-serif">{safe_title}</text>
      <text x="400" y="520" text-anchor="middle" fill="#cbd5e1" font-size="28" font-family="Arial, sans-serif">대표 이미지 자리</text>
      <text x="400" y="575" text-anchor="middle" fill="#94a3b8" font-size="20" font-family="Arial, sans-serif">연애 프로그램 추천</text>
    </svg>
    """
    return "data:image/svg+xml;charset=utf-8," + quote(svg)

# ---------------------------------
# 별점 UI
# ---------------------------------
def render_star_icons(star_fill: int) -> str:
    filled = int(star_fill)
    stars = []
    for i in range(5):
        if i < filled:
            stars.append('<span class="star-filled">★</span>')
        else:
            stars.append('<span class="star-empty">☆</span>')
    return "".join(stars)


def render_program_card(program: dict):
    image_path = find_image_path(program["name"])
    tag_class_primary = CATEGORY_CLASS_MAP.get(program["primary_category"], "tag-neutral")
    tag_class_secondary = CATEGORY_CLASS_MAP.get(program["secondary_category"], "tag-neutral")

    st.markdown("<div class='program-card'>", unsafe_allow_html=True)
    if image_path:
        st.image(image_path, use_container_width=True)
    else:
        st.markdown(f"<div class='placeholder-box'>{escape(program['name'])}</div>", unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class='card-body'>
          <p class='program-title'>{escape(program['name'])}</p>
          <p class='broadcaster'>{escape(program['broadcaster'])}</p>
          <p class='desc'>{escape(program['description'])}</p>
          <div class='badge-row'>
            <span class='tag {tag_class_primary}'>{escape(program['primary_category'])}</span>
            <span class='tag {tag_class_secondary}'>{escape(program['secondary_category'])}</span>
          </div>
          <p class='section-title' style='font-size: 0.95rem; margin-top: 4px;'>시청자 관람평</p>
          <ul class='review-list'>
            <li>{escape(program['reviews'][0])}</li>
            <li>{escape(program['reviews'][1])}</li>
          </ul>
          <p class='section-title' style='font-size: 0.95rem; margin-top: 6px; margin-bottom: 2px;'>개발자의 추천 별점</p>
          <div class='star-row'>{render_star_icons(program.get('star_fill', 4))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)


def render_recommend_card(program: dict, matched_categories: list, reason_text: str):
    image_path = find_image_path(program["name"])
    tag_class_primary = CATEGORY_CLASS_MAP.get(program["primary_category"], "tag-neutral")
    tag_class_secondary = CATEGORY_CLASS_MAP.get(program["secondary_category"], "tag-neutral")

    matched_html = "".join(
        f"<span class='tag {CATEGORY_CLASS_MAP.get(cat, 'tag-neutral')}'>{escape(cat)}</span>" for cat in matched_categories
    )

    st.markdown("<div class='recommend-card'>", unsafe_allow_html=True)
    if image_path:
        st.image(image_path, use_container_width=True)
    else:
        st.markdown(f"<div class='placeholder-box'>{escape(program['name'])}</div>", unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class='card-body'>
          <p class='program-title'>{escape(program['name'])}</p>
          <p class='broadcaster'>{escape(program['broadcaster'])}</p>
          <p class='desc'>{escape(reason_text)}</p>
          <div class='badge-row'>
            <span class='tag {tag_class_primary}'>{escape(program['primary_category'])}</span>
            <span class='tag {tag_class_secondary}'>{escape(program['secondary_category'])}</span>
          </div>
          <div class='badge-row'>{matched_html}</div>
          <p class='muted-text'><strong>이 프로그램이 잘 맞는 이유</strong><br />선택한 취향과 연결되는 요소가 분명하게 드러나는 구성입니다.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)


inject_css()

st.markdown(
    """
    <div class="hero-box" style="margin-top: 8px;">
      <p class="hero-title">당신에게 알맞는 연애 프로그램을 소개합니다!</p>
      <p class="hero-desc">아래에 나오는 프로그램의 소개를 읽어보시고, 원하는 카테고리를 고르면 당신에게 알맞은 프로그램을 추천드립니다!</p>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown('<div class="section-box"><p class="section-title">프로그램 소개</p><p class="helper-text">다양한 연애 프로그램의 분위기와 매력을 한눈에 살펴보세요.</p></div>', unsafe_allow_html=True)

cols = st.columns(min(len(PROGRAMS), 5), gap="small")
for col, program in zip(cols, PROGRAMS):
    with col:
        render_program_card(program)

st.markdown("<div class='section-box category-box' style='margin-top: 18px;'><p class='section-title'>당신이 보고싶은 연애 프로그램의 카테고리 2개를 골라주세요</p><p class='helper-text'>선택한 취향에 가장 가까운 프로그램을 추천해 드립니다. 카테고리는 최대 2개까지 고를 수 있어요.</p></div>", unsafe_allow_html=True)

selected_categories = st.multiselect(
    "당신이 보고싶은 연애 프로그램의 카테고리 2개를 골라주세요",
    options=ALL_CATEGORIES,
    default=[],
    max_selections=2,
    help="선택한 취향에 가장 가까운 프로그램을 추천해 드립니다.",
)

with st.expander("카테고리 설명 보기", expanded=False):
    for category in ALL_CATEGORIES:
        st.markdown(f"- **{category}**: {CATEGORY_DESCRIPTIONS[category]}")

if len(selected_categories) < 2:
    st.info("카테고리 2개를 선택하면 추천 결과가 나타납니다.")
else:
    canonical_selected_categories = [normalize_category_name(category) for category in selected_categories]

    scored_programs = []
    for idx, program in enumerate(PROGRAMS):
        score = 0
        matched = []
        for category in canonical_selected_categories:
            if category == program["primary_category"]:
                score += 2
                matched.append(category)
            elif category == program["secondary_category"]:
                score += 1
                matched.append(category)
        scored_programs.append((score, idx, program, matched))

    scored_programs.sort(key=lambda item: (-item[0], item[1]))
    top_two = scored_programs[:2]

    st.markdown("<div class='section-box' style='margin-top: 18px;'><p class='section-title'>당신에게 추천하는 프로그램</p><p class='helper-text'>선택한 두 가지 취향과 가장 잘 맞는 프로그램을 정리했습니다.</p></div>", unsafe_allow_html=True)

    cols = st.columns(2, gap="small")
    for col, card in zip(cols, top_two):
        with col:
            score, idx, program, matched = card

            if "설렘·썸 중심" in matched:
                reason_text = "설렘·썸 중심 취향과 잘 맞는 구성이 강점입니다."
            elif "성장·공감 중심" in matched:
                reason_text = "성장·공감 요소가 살아 있어 취향에 잘 맞습니다."
            elif "결혼·현실성 중심" in matched:
                reason_text = "결혼·현실성 중심 취향과 높은 관련이 있습니다."
            elif "재회·감정서사 중심" in matched:
                reason_text = "재회·감정서사 중심의 몰입감이 잘 맞습니다."
            elif score >= 4:
                reason_text = "선택한 카테고리와 가장 많이 일치하는 프로그램입니다."
            elif score == 3:
                reason_text = "선택한 취향과 잘 맞는 구성이 강점입니다."
            elif score == 2:
                reason_text = "선택한 카테고리와 높은 관련이 있습니다."
            else:
                reason_text = "선택한 취향과 연결되는 요소가 분명히 느껴지는 프로그램입니다."

            render_recommend_card(program, matched, reason_text)
