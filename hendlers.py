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