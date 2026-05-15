import random

ADJECTIVES = [
    "조용한", "용감한", "따뜻한", "신비한", "엉뚱한", "차분한", "반짝이는",
    "솔직한", "다정한", "느긋한", "씩씩한", "포근한", "사려깊은", "당당한",
]
NOUNS = [
    "고양이", "여우", "수달", "판다", "두루미", "고래", "사슴",
    "다람쥐", "올빼미", "바다거북", "코알라", "햄스터", "토끼", "펭귄",
]


def generate_nickname() -> str:
    return f"{random.choice(ADJECTIVES)}{random.choice(NOUNS)}{random.randint(100, 9999)}"