"""
현대자동차 지점 네이버 리뷰 샘플 데이터 모듈
==============================================
실제 크롤링 없이 대시보드를 즉시 테스트할 수 있도록
현실적인 가상 리뷰 데이터를 제공합니다.
"""

import random
from datetime import datetime, timedelta

# 지점 정보
BRANCHES = {
    "현대자동차 강남대로점": {
        "address": "서울특별시 강남구 강남대로 396",
        "phone": "02-1234-5678",
        "rating": 4.2,
    },
    "현대자동차 서초서비스센터": {
        "address": "서울특별시 서초구 반포대로 201",
        "phone": "02-2345-6789",
        "rating": 3.8,
    },
    "현대자동차 수원인계점": {
        "address": "경기도 수원시 팔달구 인계로 180",
        "phone": "031-234-5678",
        "rating": 4.5,
    },
}

# 긍정 리뷰 템플릿
POSITIVE_REVIEWS = [
    {
        "author": "김**",
        "rating": 5,
        "text": "직원분들이 정말 친절하시고 상담도 꼼꼼하게 해주셨어요. 투싼 하이브리드 계약했는데 옵션 하나하나 자세히 설명해주셔서 만족스러운 선택을 할 수 있었습니다.",
        "categories": ["친절도", "전문성"],
    },
    {
        "author": "이**",
        "rating": 5,
        "text": "시승 경험이 정말 좋았습니다. 아이오닉 6 시승을 했는데, 영업사원분이 차량의 장단점을 솔직하게 알려주셔서 신뢰가 갔어요. 시설도 깔끔하고 커피도 맛있었습니다.",
        "categories": ["서비스", "전문성", "시설"],
    },
    {
        "author": "박**",
        "rating": 4,
        "text": "그랜저 출고했습니다. 출고 과정도 깔끔하고 차량 상태도 완벽했어요. 다만 출고 대기 시간이 한 달 반 정도 걸린 건 좀 아쉬웠습니다.",
        "categories": ["서비스", "대기시간"],
    },
    {
        "author": "정**",
        "rating": 5,
        "text": "아버지 차량 교체하러 방문했는데 어르신 눈높이에 맞춰서 천천히 설명해주시더라구요. 할인 혜택도 최대한 챙겨주시고 정말 감사했습니다.",
        "categories": ["친절도", "서비스"],
    },
    {
        "author": "최**",
        "rating": 5,
        "text": "매장이 넓고 깨끗해요. 키즈 공간도 있어서 아이 데리고 가기 좋았습니다. 팰리세이드 상담 받았는데 비교 견적도 꼼꼼하게 뽑아주셨어요.",
        "categories": ["시설", "전문성"],
    },
    {
        "author": "한**",
        "rating": 4,
        "text": "전기차 충전 관련해서 궁금한 게 많았는데, 담당자분이 보조금 신청 방법부터 충전 인프라까지 상세하게 안내해주셔서 많은 도움이 됐습니다.",
        "categories": ["전문성", "서비스"],
    },
    {
        "author": "윤**",
        "rating": 5,
        "text": "코나 Electric 계약하고 왔습니다. 다른 브랜드 전기차랑 비교 상담도 해주시고, 시승도 바로 가능했어요. 예약 없이 갔는데도 대기 없이 바로 상담 받았습니다.",
        "categories": ["전문성", "대기시간", "서비스"],
    },
    {
        "author": "강**",
        "rating": 4,
        "text": "차량 인도 후 간단한 하자가 있었는데 바로 A/S 접수해주시고 빠르게 처리해주셨어요. 사후 관리도 신경 쓰시는 모습이 인상적이었습니다.",
        "categories": ["서비스", "친절도"],
    },
    {
        "author": "조**",
        "rating": 5,
        "text": "신형 싼타페 보러 갔다가 디자인에 반해서 바로 계약했어요ㅎㅎ 영업사원분이 부담 없이 편하게 상담해주셔서 좋았습니다. 카페 같은 분위기도 좋아요.",
        "categories": ["친절도", "시설"],
    },
    {
        "author": "송**",
        "rating": 4,
        "text": "주말에 방문했는데 사람이 많아서 좀 기다렸지만, 상담 퀄리티는 확실히 좋았습니다. 견적서도 투명하게 보여주시고 할인 구조도 명확하게 설명해주셨어요.",
        "categories": ["전문성", "대기시간"],
    },
    {
        "author": "임**",
        "rating": 5,
        "text": "블루멤버스 혜택 안내도 잘 해주시고 보험, 등록 대행까지 원스톱으로 처리 가능해서 편했습니다. 다음에도 여기서 구매할 예정이에요.",
        "categories": ["서비스", "전문성"],
    },
    {
        "author": "오**",
        "rating": 5,
        "text": "쇼룸 자체가 전시가 잘 되어있어서 구경하는 재미가 있었어요. 직원분들이 먼저 다가와서 부담주지 않고 필요할 때 도와주는 스타일이라 좋았습니다.",
        "categories": ["시설", "친절도"],
    },
]

# 부정 리뷰 템플릿
NEGATIVE_REVIEWS = [
    {
        "author": "문**",
        "rating": 1,
        "text": "예약하고 갔는데 40분 넘게 기다렸습니다. 직원은 바쁘다는 말만 반복하고 제대로 된 사과도 없었어요. 시간 낭비한 기분입니다.",
        "categories": ["대기시간", "친절도"],
    },
    {
        "author": "서**",
        "rating": 2,
        "text": "견적 상담을 받았는데 다른 지점에서 들은 가격이랑 차이가 많이 나더라구요. 정확한 할인 정보를 주는 건지 의문이 들었습니다.",
        "categories": ["전문성", "서비스"],
    },
    {
        "author": "배**",
        "rating": 1,
        "text": "출고 일정이 세 번이나 변경됐는데, 매번 당일에 연락이 왔습니다. 고객 입장에서는 휴가까지 잡아놓은 건데... 소통이 너무 부족합니다.",
        "categories": ["서비스", "대기시간"],
    },
    {
        "author": "나**",
        "rating": 2,
        "text": "화장실이 좀 지저분하고 주차장도 좁아서 불편했어요. 전시 차량도 먼지가 쌓여있는 게 보이더라구요. 관리가 좀 아쉽습니다.",
        "categories": ["시설"],
    },
    {
        "author": "유**",
        "rating": 1,
        "text": "영업사원이 제가 관심 있는 차보다 더 비싼 차만 계속 추천하더라구요. 예산을 말씀드렸는데도 무시하는 느낌이었습니다. 불쾌했어요.",
        "categories": ["친절도", "전문성"],
    },
    {
        "author": "황**",
        "rating": 2,
        "text": "신차 출고했는데 내부에 작은 스크래치가 있었습니다. 문제를 제기하니까 '이 정도는 괜찮다'는 반응이어서 실망했어요.",
        "categories": ["서비스", "친절도"],
    },
    {
        "author": "권**",
        "rating": 2,
        "text": "주말 오후에 갔더니 대기 인원이 너무 많아서 상담도 못 받고 돌아왔습니다. 예약 시스템이 제대로 안 되는 것 같아요.",
        "categories": ["대기시간", "서비스"],
    },
    {
        "author": "곽**",
        "rating": 1,
        "text": "전화 문의했는데 여러 번 돌려가며 연결해주고, 결국 담당자 부재로 콜백 요청했는데 연락이 안 왔습니다. 기본적인 CS가 안 되는 느낌.",
        "categories": ["서비스", "친절도"],
    },
]

# 중립 리뷰 템플릿
NEUTRAL_REVIEWS = [
    {
        "author": "양**",
        "rating": 3,
        "text": "전반적으로 무난했습니다. 특별히 좋지도 나쁘지도 않은 일반적인 딜러십 경험이에요. 차량 자체는 마음에 듭니다.",
        "categories": ["서비스"],
    },
    {
        "author": "홍**",
        "rating": 3,
        "text": "상담은 괜찮았는데 시승 차량이 원하는 트림이 아니어서 좀 아쉬웠어요. 그래도 다른 부분 설명은 잘 해주셨습니다.",
        "categories": ["서비스", "전문성"],
    },
    {
        "author": "장**",
        "rating": 3,
        "text": "시설은 평범한 편이고 직원 응대도 보통이에요. 좋게 말하면 군더더기 없고, 나쁘게 말하면 특별한 게 없는 곳입니다.",
        "categories": ["시설", "친절도"],
    },
    {
        "author": "구**",
        "rating": 3,
        "text": "온라인으로 먼저 견적 뽑아가서 비교했는데 거의 비슷했어요. 추가 할인은 크지 않았지만 그래도 성실하게 상담해주셨습니다.",
        "categories": ["전문성", "서비스"],
    },
]


def generate_reviews(branch_name: str, count: int = 50) -> list[dict]:
    """
    특정 지점에 대한 가상 리뷰 데이터를 생성합니다.

    Args:
        branch_name: 지점명
        count: 생성할 리뷰 수

    Returns:
        리뷰 딕셔너리 리스트
    """
    random.seed(hash(branch_name) % (2**31))

    reviews = []
    base_date = datetime(2025, 12, 1)

    # 긍정 60%, 부정 25%, 중립 15% 비율
    positive_count = int(count * 0.60)
    negative_count = int(count * 0.25)
    neutral_count = count - positive_count - negative_count

    pool = []
    for _ in range(positive_count):
        pool.append(random.choice(POSITIVE_REVIEWS))
    for _ in range(negative_count):
        pool.append(random.choice(NEGATIVE_REVIEWS))
    for _ in range(neutral_count):
        pool.append(random.choice(NEUTRAL_REVIEWS))

    random.shuffle(pool)

    for i, template in enumerate(pool):
        review_date = base_date - timedelta(days=random.randint(0, 180))
        reviews.append(
            {
                "id": i + 1,
                "branch": branch_name,
                "author": template["author"],
                "rating": template["rating"],
                "text": template["text"],
                "categories": template["categories"],
                "date": review_date.strftime("%Y-%m-%d"),
            }
        )

    # 날짜순 정렬 (최신 먼저)
    reviews.sort(key=lambda x: x["date"], reverse=True)
    return reviews
