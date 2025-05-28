import math

def get_tier_and_color(rarity):
    tiers = [
        (1.0, 'Trash', '#a39589'),
        (2.0, 'Common', '#9c7e5a'),
        (3.0, 'Uncommon', '#aed1d1'),
        (4.0, 'Rare', '#11d939'),
        (5.0, 'Elite', '#1172d9'),
        (6.0, 'Epic', '#6811d9'),
        (7.0, 'Legendary', '#f7d40a'),
        (8.0, 'Mythical', '#fc61ff'),
        (9.0, 'Divine', '#ff8c00'),
        (10.0, 'Transcendent', '#ff0000'),
    ]
    for limit, name, color in tiers:
        if rarity < limit:
            return name, color
    return "Transcendent", "#ff0000"

def classify_luck(luck_value):
    if luck_value > 95:
        return "Below Average"
    elif luck_value > 75:
        return "Average"
    elif luck_value > 55:
        return "Above Average"
    elif luck_value > 35:
        return "Notable"
    elif luck_value > 15:
        return "Rare"
    elif luck_value > 5:
        return "Exceptional Pull"
    else:
        return "Mythic Pull"