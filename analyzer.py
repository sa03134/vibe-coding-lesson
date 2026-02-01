"""
감성 분석 엔진 모듈
====================
리뷰 텍스트에 대한 감성 분석을 수행합니다.
키워드 기반 로컬 분석과 선택적 AI API 분석을 지원합니다.
"""

import re
from collections import Counter

# ──────────────────────────────────────────────
# 감성 사전 (한국어 자동차 딜러십 도메인 특화)
# ──────────────────────────────────────────────

POSITIVE_KEYWORDS = {
    # 친절도
    "친절": 8, "친절하": 8, "따뜻": 6, "편하게": 5, "부담없": 5,
    "부담 없": 5, "웃으며": 4, "반겨": 4, "감사": 6, "고마": 6,
    "배려": 7, "눈높이": 6,
    # 전문성
    "꼼꼼": 7, "자세히": 6, "상세": 6, "정확": 7, "솔직": 6,
    "투명": 7, "비교": 4, "전문": 7, "설명": 4, "안내": 4,
    "명확": 6,
    # 서비스
    "만족": 8, "좋았": 6, "좋아요": 6, "추천": 7, "재방문": 8,
    "원스톱": 6, "빠르게": 5, "신속": 6, "편했": 5, "편리": 5,
    "깔끔": 5, "완벽": 8, "인상적": 7, "감동": 8,
    # 시설
    "넓고": 4, "깨끗": 6, "쾌적": 6, "카페": 4, "키즈": 5,
    "전시": 3, "인테리어": 4, "분위기": 4, "맛있": 3,
}

NEGATIVE_KEYWORDS = {
    # 불만
    "불쾌": -8, "불편": -6, "실망": -8, "짜증": -7, "화가": -7,
    "최악": -9, "후회": -8, "지저분": -6, "먼지": -4, "좁아": -4,
    # 대기
    "기다": -5, "대기": -4, "오래": -4, "느리": -5, "지연": -5,
    "변경": -4, "돌아왔": -6,
    # 서비스 불만
    "무시": -7, "무성의": -7, "사과": -3, "연락이 안": -6,
    "소통이": -4, "부재": -5, "돌려": -4, "낭비": -6,
    "아쉬": -3, "부족": -5,
    # 신뢰 문제
    "의문": -5, "차이가": -3, "스크래치": -5, "하자": -5,
}

CATEGORY_KEYWORDS = {
    "서비스": ["상담", "출고", "계약", "견적", "인도", "A/S", "접수", "처리",
               "대행", "혜택", "보험", "등록", "서비스", "관리", "CS", "콜백"],
    "친절도": ["친절", "따뜻", "반겨", "웃으며", "편하게", "부담",
               "배려", "불쾌", "무시", "사과", "감사", "눈높이"],
    "전문성": ["설명", "안내", "비교", "견적", "옵션", "할인", "정확",
               "꼼꼼", "전문", "솔직", "투명", "트림", "보조금"],
    "시설": ["매장", "전시", "주차", "화장실", "카페", "쇼룸", "키즈",
             "깨끗", "지저분", "넓", "좁", "인테리어", "분위기"],
    "대기시간": ["대기", "기다", "예약", "시간", "오래", "바로", "즉시",
                "빠르", "느리", "지연", "변경", "일정"],
}


def analyze_sentiment(text: str) -> dict:
    """
    단일 리뷰 텍스트의 감성을 분석합니다.

    Returns:
        {
            "score": 0~100 감성 점수,
            "label": "긍정" | "부정" | "중립",
            "positive_words": [...],
            "negative_words": [...],
        }
    """
    positive_score = 0
    negative_score = 0
    found_positive = []
    found_negative = []

    for keyword, weight in POSITIVE_KEYWORDS.items():
        if keyword in text:
            positive_score += weight
            found_positive.append(keyword)

    for keyword, weight in NEGATIVE_KEYWORDS.items():
        if keyword in text:
            negative_score += abs(weight)
            found_negative.append(keyword)

    # 0~100 스케일로 변환
    total = positive_score + negative_score
    if total == 0:
        score = 50  # 키워드가 없으면 중립
    else:
        score = int((positive_score / total) * 100)

    # 라벨 부여
    if score >= 60:
        label = "긍정"
    elif score <= 40:
        label = "부정"
    else:
        label = "중립"

    return {
        "score": score,
        "label": label,
        "positive_words": found_positive,
        "negative_words": found_negative,
    }


def classify_categories(text: str) -> list[str]:
    """
    리뷰 텍스트가 해당하는 카테고리를 분류합니다.
    """
    matched = []
    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                matched.append(category)
                break
    return matched if matched else ["서비스"]  # 기본 카테고리


def extract_keywords(reviews: list[dict], top_n: int = 20) -> list[tuple[str, int]]:
    """
    전체 리뷰에서 자주 등장하는 주요 키워드를 추출합니다.

    Returns:
        [(키워드, 빈도수), ...] top_n개
    """
    # 불용어
    stopwords = {
        "있", "없", "하", "되", "이", "그", "저", "것", "수", "등",
        "좀", "더", "잘", "안", "못", "제", "를", "에", "의", "가",
        "은", "는", "이", "도", "로", "다", "을", "게", "서", "고",
        "지", "나", "한", "데", "들", "때", "와", "랑", "요", "거",
        "건", "에서", "까지", "부터", "마다", "처럼", "같이",
    }

    word_counter = Counter()

    for review in reviews:
        text = review["text"]
        # 간단한 형태소 분리 (2글자 이상 한국어 단어)
        words = re.findall(r"[가-힣]{2,}", text)
        for word in words:
            if word not in stopwords and len(word) >= 2:
                word_counter[word] += 1

    return word_counter.most_common(top_n)


def generate_summary(reviews: list[dict], analyses: list[dict]) -> dict:
    """
    전체 리뷰 분석 결과를 요약합니다.

    Returns:
        {
            "praise_points": [칭찬 포인트 3개],
            "improvement_points": [개선 포인트 3개],
            "overall_score": 평균 감성 점수,
        }
    """
    scores = [a.get("sentiment_score", a.get("score", 50)) for a in analyses]
    overall_score = sum(scores) / len(scores) if scores else 50

    # 긍정/부정 키워드 빈도 집계
    pos_counter = Counter()
    neg_counter = Counter()
    for analysis in analyses:
        for w in analysis["positive_words"]:
            pos_counter[w] += 1
        for w in analysis["negative_words"]:
            neg_counter[w] += 1

    # 칭찬 포인트 생성
    top_positive = pos_counter.most_common(5)
    praise_map = {
        "친절": "직원들의 친절하고 따뜻한 응대가 고객 만족도를 높이고 있습니다.",
        "꼼꼼": "꼼꼼하고 자세한 상담으로 고객 신뢰를 얻고 있습니다.",
        "만족": "전반적인 구매 경험에 대한 고객 만족도가 높습니다.",
        "깨끗": "깨끗하고 쾌적한 매장 시설이 좋은 인상을 주고 있습니다.",
        "추천": "재방문 및 추천 의사를 밝히는 고객이 많습니다.",
        "설명": "차량 옵션과 혜택에 대한 상세한 설명이 호평을 받고 있습니다.",
        "빠르게": "신속한 업무 처리가 고객에게 긍정적 경험을 제공합니다.",
        "전문": "전문적인 지식과 상담 능력이 돋보입니다.",
        "솔직": "장단점을 솔직하게 안내하는 점이 신뢰를 형성합니다.",
        "편했": "원스톱 처리 등 편리한 서비스 프로세스가 호평받고 있습니다.",
    }

    praise_points = []
    for word, _ in top_positive:
        for key, msg in praise_map.items():
            if key in word or word in key:
                if msg not in praise_points:
                    praise_points.append(msg)
                break
    # 부족하면 기본 메시지 추가
    default_praise = [
        "고객 맞춤형 상담으로 좋은 구매 경험을 제공하고 있습니다.",
        "차량 인도 과정이 체계적으로 진행되고 있습니다.",
        "다양한 할인 혜택 안내가 잘 이루어지고 있습니다.",
    ]
    for msg in default_praise:
        if len(praise_points) >= 3:
            break
        if msg not in praise_points:
            praise_points.append(msg)

    # 개선 포인트 생성
    top_negative = neg_counter.most_common(5)
    improve_map = {
        "기다": "예약 시스템 개선으로 고객 대기 시간을 줄일 필요가 있습니다.",
        "대기": "피크타임 인력 배치 최적화로 대기 시간 불만을 해소해야 합니다.",
        "불쾌": "고객 응대 매뉴얼 재교육을 통해 서비스 품질을 개선해야 합니다.",
        "지저분": "매장 시설 정기 청소 및 관리 점검이 필요합니다.",
        "무시": "고객 의견을 경청하는 상담 문화 조성이 필요합니다.",
        "소통": "출고 일정 등 핵심 정보의 사전 소통 체계를 강화해야 합니다.",
        "실망": "고객 기대 관리와 사후 관리 프로세스를 점검해야 합니다.",
        "연락": "콜백 및 문의 응답 시스템을 개선하여 소통 공백을 줄여야 합니다.",
        "아쉬": "고객 피드백을 적극 반영하여 서비스를 보완해야 합니다.",
        "부족": "서비스 일관성을 위한 내부 품질 기준을 수립해야 합니다.",
    }

    improvement_points = []
    for word, _ in top_negative:
        for key, msg in improve_map.items():
            if key in word or word in key:
                if msg not in improvement_points:
                    improvement_points.append(msg)
                break
    default_improve = [
        "주말/공휴일 방문 고객을 위한 추가 인력 배치를 검토해야 합니다.",
        "출고 일정 변동 시 사전 안내 프로세스를 강화해야 합니다.",
        "고객 불만 접수 후 후속 조치의 신속성을 높여야 합니다.",
    ]
    for msg in default_improve:
        if len(improvement_points) >= 3:
            break
        if msg not in improvement_points:
            improvement_points.append(msg)

    return {
        "praise_points": praise_points[:3],
        "improvement_points": improvement_points[:3],
        "overall_score": round(overall_score, 1),
    }


def analyze_reviews(reviews: list[dict]) -> list[dict]:
    """
    리뷰 리스트 전체를 분석합니다.

    Returns:
        각 리뷰에 감성 분석 결과가 추가된 리스트
    """
    results = []
    for review in reviews:
        sentiment = analyze_sentiment(review["text"])
        categories = classify_categories(review["text"])
        results.append(
            {
                **review,
                "sentiment_score": sentiment["score"],
                "sentiment_label": sentiment["label"],
                "positive_words": sentiment["positive_words"],
                "negative_words": sentiment["negative_words"],
                "analyzed_categories": categories,
            }
        )
    return results
