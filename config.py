# config.py

# -------------------------
# Параметры безопасности
# -------------------------
# Пароль для шифрования базы данных
PASSWORD = "your_password_here"

# Ключ для решения CAPTCHA
captcha_key = "your_captcha_key_here"

# -------------------------
# URL-адреса
# -------------------------
# Основные URL-адреса для взаимодействия с внешним сервисом Siberian Wellness
backofficeUrl = "https://ru.siberianhealth.com/ru/backoffice/auth/"
myTeamUrl = "https://ru.siberianhealth.com/ru/backoffice/report/inf/"
bonusUrl = "https://ru.siberianhealth.com/ru/office/report/bz/"
closeUrl = "https://ru.siberianhealth.com/ru/office/report/pk/close/"
сlub50Url = "https://ru.siberianhealth.com/ru/office/report/constancy-club/clone/"
club200Url = "https://ru.siberianhealth.com/ru/detail/visual/club-200-struct/"
newUrl = "https://ru.siberianhealth.com/ru/office/report/inf/"
logoutUrl = "https://ru.siberianhealth.com/ru/backoffice/logout/"
captchaUrl = "https://ru.siberianhealth.com/ru/captcha/default/"
buy_sku2_url = "https://ru.siberianhealth.com/ru/office/report/buy_sku2/"

# URL для AJAX запросов
url_ajax = "https://ru.siberianhealth.com/ru/controller/ajax/"

# -------------------------
# Словари и данные
# -------------------------
# Словарь рангов
rankDict = {
    -1: 'КЛИЕНТ',
    1: 'БИЗНЕС-ПАРТНЕР',
    4: 'BUSINESS TEAM 1000',
    5: 'BUSINESS TEAM 2500',
    6: 'BUSINESS TEAM 5000',
    7: 'BUSINESS TEAM 10000',
    8: 'BUSINESS PROFI',
    9: 'BUSINESS LEADER',
    10: 'SAPPHIRE BUSINESS LEADER',
    11: 'RUBY BUSINESS LEADER',
    12: 'PLATINUM BUSINESS LEADER',
    13: 'DIAMOND BUSINESS LEADER',
    14: 'GLOBAL BUSINESS LEADER',
    15: '1 STAR INFINITY LEADER',
    16: '2 STAR INFINITY LEADER',
    17: '3 STAR INFINITY LEADER',
    18: '4 STAR INFINITY LEADER',
    19: '5 STAR INFINITY LEADER'
}

# Данные пользователей
users = {
    'somova': {
        'number': 'your_number_here',
        'password': 'your_password_here',
        'id': 0,
        "myName": "Марина"
    }
}
