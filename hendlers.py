def get_direction(deg):
    if 60 <= deg <= 120:
        return 'север'
    if 120 < deg < 150:
        return 'ceверо-запад'
    if 150 <= deg <= 210:
        return 'запад'
    if 210 < deg < 240:
        return 'юго-запад'
    if 240 <= deg <= 300:
        return 'юг'
    if 300 < deg < 330:
        return 'юго-восток'
    if 330 <= deg <= 360 or 0 <= deg <= 30:
        return 'восток'
    if 30 < deg < 60:
        return 'ceверо-восток'


def get_emoji(emoji_id):
    emoji = ''
    if 200 <= emoji_id <= 232:
        emoji = '🌩'
    if 300 <= emoji_id <= 531:
        emoji = '🌧'
    if 600 <= emoji_id <= 622:
        emoji = '🌨'
    if 701 <= emoji_id <= 781:
        emoji = '😶‍🌫'
    if emoji_id == 800:
        emoji = '☀️'
    if 801 <= emoji_id <= 804:
        emoji = '☁️'
    return emoji