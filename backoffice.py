import datetime
import html
import io
import os
import sqlite3
import traceback
from io import BytesIO

import pandas as pd
from anticaptchaofficial.imagecaptcha import *
from bs4 import BeautifulSoup
from dateutil.relativedelta import relativedelta
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from config import *


def bypass_captcha(session):
    solver = imagecaptcha()
    solver.set_verbose(0)  # Установите уровень отладки на 0, чтобы отключить сообщения работы
    while True:
        try:
            solver.set_key(captcha_key)
            img = session.get("https://ru.siberianhealth.com/ru/captcha/default/")
            captcha_content = BytesIO(img.content)
            captcha_text = solver.solve_and_return_solution(file_path=None, body=captcha_content.read())
            return captcha_text
        except:
            pass

def auth(user, url="https://ru.siberianhealth.com/ru/backoffice-new/?newStyle=yes"):
    payload = {
        "login": f"{ user['number']}",
        "pass": f"{user['password']}",
        "url": url,
        "_controller": "Backoffice_Auth/submit",
        "_url": "https://ru.siberianhealth.com/ru/backoffice/auth/?url=https://ru.siberianhealth.com/ru/backoffice-new/?newStyle=yes"
    }
    with requests.Session() as session:
        while True :
            response = session.post(url=url_ajax, data=payload, allow_redirects=True)
            response_json = response.json()
            if response_json['result']['status'] == "Denied":
                payload["captcha"] = bypass_captcha(session)
            else:
                break
        if response_json['result']['success'] and "Стать Бизнес-Партнером" not in session.get(url=url).text:
            return session
        elif "Стать Бизнес-Партнером" in session.get(url=url).text:
            return f"{ user['number']} нужно стать Бизнес-Партнером"
        else:
            return f"{ user['number']} {response_json['result']['status']}"



def extract_data(url, session) -> list:
    response = session.get(url=url, allow_redirects=True)
    soup = BeautifulSoup(response.text, 'html.parser')
    data_list = []
    for a in soup.find_all('a', {'class': 'officeReportBuySKUDetailBtn'}):
        key = a.get('data-key')
        group = a.get('data-group')
        data = {"key": key, "group": group}
        data_list.append(data)

    return data_list

def get_current_period(format):
    return datetime.now().strftime(format)

def download_csv_data(id, session):
    data = {
        'filters[page]': '1',
        'filters[perPage]': '20',
        'filters[period]': f'{get_current_period("%m.%Y")}',
        'filters[fromCache]': '0',
        'filters[contract]': '',
        'filters[search]': '',
        'filters[group]': '0',
        'filters[minLO]': '',
        'filters[maxLO]': '',
        'filters[qualificationOpen]': '0',
        'filters[qualificationClosed]': '0',
        'filters[newbies]': '',
        'filters[type]': 'all',
        'filters[sort][field]': 'lo',
        'filters[sort][direction]': 'ASC',
        'filters[club200]': '0',
        'filters[club500]': '0',
        'filters[club1000]': '0',
        'filters[firstLine]': '1',
        'filters[specialDiscount]': '',
        'filters[specialGift]': '',
        '_controller': 'Backoffice_Report_Inf/download_prepare',
        '_contract': f'{id}',
        '_url': 'https://ru.siberianhealth.com/ru/backoffice/report/inf/'
    }

    hash = session.post(url_ajax, data=data, allow_redirects=True)
    hash = hash.json()['result']['hash']
    file = session.get(f'https://ru.siberianhealth.com/ru/backoffice/report/inf/download/{hash}/')
    df = pd.read_excel(io.BytesIO(file.content))
    return df


def get_data(session, url):
    while True:
        try:
            response = session.get(url)
            response.raise_for_status()
            html_content = response.text
            tables = pd.read_html(html_content)
            df = tables[0]  # Получаем первую таблицу
            # print(f"{url} -> {response.url}")
            return df
        except ValueError as e:
            print(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))} Произошла ошибка при чтении таблиц из HTML: {e} {url}")
            time.sleep(60)
        except AttributeError:
            # Обработка ошибки
            return None
        except Exception as e:
            print("Произошла ошибка:", e)
            traceback.print_exc()
            time.sleep(60)



def get_report(session, url):
    data = {
        'action': 'all',
        'period': f'{get_current_period("01.%m.%Y")}',
        'search_contract': '',
        'lv_parent': '0',
        'group_only': '0',
        'show_mobil': '1',
        'show_birthday': '1'
    }
    try:
        response = session.post(url, data=data)
        response.raise_for_status()
        html_content = response.text
        tables = pd.read_html(f'<table>{html_content}</table>')
        df = tables[0]  # Получаем первую таблицу
        df.columns = ['№', 'Номер Соглашения', 'Уровень', 'ФИО', 'E-mail', 'Телефон', 'ЛО ИМ', 'ЛО ИМ ПКН',
                      'Дата рождения', 'ЛО', 'ЛО ПКН', 'ГО', 'ОО', 'Ранг', 'НОО', 'ЦОК', 'Примечание']
        return df

    except Exception as e:
        print("Произошла ошибка:", e)
        traceback.print_exc()


def is_current_month(dataframe, column_index, date_format="%d.%m.%Y"):
    # Извлекаем название столбца и удаляем подстроку " (на текущую дату)"
    column_name = dataframe.columns[column_index].replace(" (на текущую дату)", "")

    # Преобразуем название столбца в объект datetime с помощью функции strptime
    column_date = datetime.strptime(column_name, date_format)

    # Извлекаем текущий месяц из текущей даты с помощью функции strftime
    current_month = datetime.now().strftime("%B")

    # Сравниваем извлеченный месяц со значением текущего месяца
    if column_date.strftime("%B") == current_month:
        return True
    else:
        return False

def process_user_data(user):
    buy_my_team = None

    dataClub200 = None
    dataBonus = None
    dataClose = None
    dataClub50 = None
    dataNew = None
    data_team = None

    try:
        session = auth(user)

        if isinstance(session, requests.sessions.Session):
            dataClub200 = get_data(session, club200Url, )

            dataBonus = get_data(session, bonusUrl)

            dataClose = get_data(session, closeUrl)

            dataClub50 = get_data(session, сlub50Url)

            dataNew = get_report(session, newUrl)

            data_team = download_csv_data( user['number'], session)

            return data_team, dataBonus, dataClose, dataClub50, dataClub200, dataNew, buy_my_team
        else:
            return session

    except Exception as e:
        print("Произошла ошибка:", e)
        traceback.print_exc()
        time.sleep(60)


def calculate_months_difference(last_purchase_date_str):
    last_purchase_date = datetime.strptime(last_purchase_date_str, '%d.%m.%Y').replace(day=1)
    current_date = datetime.now().replace(day=1)

    delta = relativedelta(current_date, last_purchase_date)

    return delta.months

def transfer_data(row):

    note = ''

    if row['Клуб Постоянства'] and pd.notna(row['Клуб Постоянства']):
        note += f"Club 50: {row['Клуб Постоянства']} "

    elif row['Club 200']:
        note += f"Club 200: {row['Club 200']} "

    elif row['Дата последней покупки']:
        if "нет ни одной покупки" in row['Дата последней покупки']:
            note += "Нет покупок </br> будет закрыт"
        elif calculate_months_difference(row['Дата последней покупки']) == 6:
            note += f"Нет покупок 6 месяцев </br> будет закрыт"
        elif calculate_months_difference(row['Дата последней покупки']) == 5:
            note += f"Нет покупок 5 месяцев"

    elif not row['НОО'] and row['Ранг'] == -1:
        note += f"Новичок без покупок"

    if row['Новичок месяца']:
        note = f"Новичок месяца"
        # print(row)

    return note.strip()

def generate_text(user, data_team, dataBonus, dataClose, dataClub50, dataClub200, dataNew, buy_my_team = None):
    # Создание пустых списков для каждого столбца
    new = []
    balance = []
    close = []
    сlub50 = []
    club200 = []
    WhatsApp = []
    birthday = []
    new_dict = []

    # Извлечение имени пользователя, используя условное выражение
    """ Нужно подтягивать имя из базы данных для рассылки"""
    myName = user["myName"] if user["myName"] else data_team.loc[data_team['Уровень'] == 0, 'ФИО'].str.split().str[1].iloc[0]
    # myName = data_team.loc[data_team['Уровень'] == 0, 'ФИО'].str.split().str[1].iloc[0]
    data_team['Email'] = data_team['E-mail']

    # Создание нового датафрейма только с нужными столбцами
    data_team = data_team[['Регистрационный номер', 'Уровень', 'Ранг', 'ОО', 'НОО', 'ФИО', 'Телефон', 'ЛО', 'Email',]]

    # Распечатка названий всех столбцов с помощью атрибута columns
    # print(data_team.columns)

    # Подготовка данных для скалярных запросов
    balance_dict = dataBonus.set_index('Номер Соглашения')['Баланс'].to_dict()

    birthday_dict = {str(row['Номер Соглашения']).replace('.0', ''): row['Дата рождения'] for _, row in
                     dataNew.iterrows()}

    close_dict = dataClose.set_index('Номер соглашения')['Дата последней покупки'].to_dict()

    club50_dict = dataClub50.set_index('Регистрационный номер')['Месяц выполнения по 50 баллов'].to_dict()


    new_dict = dataNew['Номер Соглашения'].tolist()
    new_dict = [elem for elem in new_dict if '*' in elem]
    new_dict = {str(element).replace('*', ''): 'Новичок' for element in new_dict if '*' in str(element)}

    club200_dict = {}
    if is_current_month(dataClub200, 5):
        dataClub200.rename(columns={dataClub200.columns[5]: "на текущую дату"}, inplace=True)
        for key, value in dataClub200.set_index('Регистрационный номер').to_dict(orient='index').items():
            if pd.notna(value['на текущую дату']):
                club200_dict.update({key: f"{int(value['Месяц участия в Club 200'][0]) - 1} из 6 месяцев"})

    # Итерация по столбцу 'Регистрационный номер' для заполнения списков
    for _, reg_num in data_team['Регистрационный номер'].items():
        # balance.append(balance_dict.get(reg_num, ''))
        # birthday.append(birthday_dict.get(str(reg_num), ''))
        # close.append(close_dict.get(reg_num, ''))
        # сlub50.append(club50_dict.get(reg_num, ''))
        # club200.append(club200_dict.get(reg_num, ''))
        # new.append(new_dict.get(str(reg_num), ''))

        balance_value = balance_dict.get(reg_num, '')
        birthday_value = birthday_dict.get(str(reg_num), '')
        close_value = close_dict.get(reg_num, '')
        сlub50_value = club50_dict.get(reg_num, '')
        club200_value = club200_dict.get(reg_num, '')
        new_value = new_dict.get(str(reg_num), '')

        balance.append(balance_value)
        birthday.append(birthday_value)
        close.append(close_value)
        сlub50.append(сlub50_value)
        club200.append(club200_value)
        new.append(new_value)

        # print(f"Reg_num: {reg_num} | Balance: {balance_value} | Birthday: {birthday_value} | Close: {close_value} "
        #       f"| Club50: {club50_value} | Club200: {club200_value} | New: {new_value}")

    # Присвоение списков полученным значениям в датафрейме
    data_team.loc[:, 'Дата рождения'] = birthday
    data_team.loc[:, 'Телефон'] = data_team['Телефон'].str.replace('|', '')
    data_team.loc[:, 'Баланс'] = balance
    data_team.loc[:, 'Клуб Постоянства'] = сlub50
    data_team.loc[:, 'Club 200'] = club200
    data_team.loc[:, 'Дата последней покупки'] = close
    data_team.loc[:, 'Новичок месяца'] = new

    for index, data in data_team.iterrows():
        clientName = f"{data['ФИО'].split()[1] if len(data['ФИО'].split()) > 1 else data['ФИО'].split()[0]}"
        text = ""

        if data['Новичок месяца']:
            club = "Клуб Постоянства" if data['Ранг'] < 0 else "Клуб 200"

            text = f"Здравствуйте {clientName}, Вы зарегистрировались на сайте Siberian Wellness. " \
                   f"Я ваш личный консультант, меня зовут – {myName}. Вы можете принять участие в программе {club} " \
                   f"и получить подарки, рассказать подробнее?"

        elif data['Клуб Постоянства'] and pd.notna(data['Клуб Постоянства']):

            if data['Клуб Постоянства'] == "Начислен подарок - не забрали":
                text = f"Здравствуйте {clientName} Вам начислен сертификат на подарок по программе Клуб Постоянства. " \
                       f"Нужна ли вам помощь при оформлении? Ваш консультант Siberian Wellness - {myName}."

            elif data['ЛО'] < 50:
                text = f"Здравствуйте {clientName}, Вы {str(data['Клуб Постоянства']).split()[0]} из 6 месяцев " \
                       f"идете по программе Клуб постоянства, в этом месяце вы сделали {data['ЛО']} из 50. " \
                       f"У вас на бонусном счету {data['Баланс']} Готовы ли сделать заказ? " \
                       f"Ваш консультант Siberian Wellness - {myName}."

            elif 5 - int(str(data['Клуб Постоянства']).split()[0]):
                ending = '' if 5 - int(str(data['Клуб Постоянства']).split()[0]) == 1 else 'ев' if 5 - int(
                    data['Клуб Постоянства'].split()[0]) == 5 else 'а'
                text = f"Здравствуйте {clientName}, Вы выполнили условия программы Клуб постоянства в текущем месяце. " \
                       f"Для получения подарка необходимо выполнять условия программы Клуб постоянства еще " \
                       f"{5 - int(str(data['Клуб Постоянства'].split()[0]))} месяц {ending}. " \
                       f"У вас на бонусном счету {data['Баланс']} Ваш консультант Siberian Wellness - {myName}."

            else:
                text = f"Здравствуйте {clientName}, Вы выполнили условия программы Клуб постоянства полностью. " \
                       f"В начале следующего месяца вам будет начислен сертификат на подарок. " \
                       f"У вас на бонусном счету {data['Баланс']} Ваш консультант Siberian Wellness - {myName}."

        elif data['Club 200'] and pd.notna(data['Club 200']):
            if data['ЛО'] < 200:
                text = f"Здравствуйте {clientName}, Вы {data['Club 200']} из 6 месяцев " \
                       f"идете по программе Club 200, в этом месяце вы сделали {data['ЛО']} из 200. " \
                       f"У вас на бонусном счету {data['Баланс']}  Готовы ли сделать заказ? " \
                       f"Ваш консультант Siberian Wellness - {myName}."
            else:
                text = f"Здравствуйте {clientName}, Вы выполнили условия программы Club 200, " \
                       f"в начале следующего месяца будет зачислен сертификат на подарок. " \
                       f"У вас на бонусном счету {data['Баланс']} " \
                       f"Ваш консультант Siberian Wellness - {myName}. "

        elif data['Дата последней покупки'] and pd.notna(data['Дата последней покупки']):
            if data['Дата последней покупки'] == "нет ни одной покупки":
                text = f"Здравствуйте {clientName}, у вас есть карта клиента Siberian Wellness, " \
                       f"вы в течение 3 месяцев с момента регистрации не совершали покупок, " \
                       f"сделайте заказ в этом месяце на любую сумму и сохраните карту клиента, или она будет аннулирована. " \
                       f"Ваш консультант Siberian Wellness - {myName}."
            else:
                text = f"Здравствуйте {clientName}, вы не покупали продукцию в течение 5 месяцев подряд, " \
                       f"ваш номер Соглашения будет закрыт, если покупок не будет 6 месяцев подряд. " \
                       f"У вас на бонусном счету {data['Баланс']}, используйте их для покупки в текущем месяце, " \
                       f"иначе они сгорят. " \
                       f"Ваш консультант Siberian Wellness - {myName}."

        elif not data['ЛО']:
            if data['Баланс']:
                text = f"Здравствуйте {clientName}, у вас на бонусном счету {data['Баланс']}  " \
                       f"используйте их для покупки в текущем месяце. " \
                       f"Вам нужна консультация по продукции или информация по текущим акциям? " \
                       f"Ваш консультант Siberian Wellness - {myName}. "
            else:
                text = f"Здравствуйте {clientName}, Вы давно не делали заказы. " \
                       f"Вам нужна консультация по продукции или информация по текущим акциям? " \
                       f"Ваш консультант Siberian Wellness - {myName}. "

        elif data['ЛО'] < 50 and data['Ранг'] < 0:
            if data['Баланс']:
                text = f"Здравствуйте {clientName}, у вас на бонусном счету {data['Баланс']}, " \
                       f"используйте их для покупки в текущем месяце. " \
                       f"Вам нужна консультация по продукции или информация по текущим акциям? " \
                       f"Ваш консультант Siberian Wellness - {myName}."

            else:
                text = f"Здравствуйте {clientName}, Вы можете принять участие в программе  " \
                       f"Клуб Постоянства и получить подарки, рассказать подробнее? " \
                       f"Ваш консультант Siberian Wellness - {myName}."

        elif data['ЛО'] >= 200 and data['Ранг'] < 0:
            if data['Баланс']:
                text = f"Здравствуйте {clientName}, Вы сделали в этом месяце {data['ЛО']} баллов и можете " \
                       f"перейти в Бизнес партнеры совершенно бесплатно. Ваш кэшбэк увеличится до 25%, " \
                       f"а так же сможете участвовать в программе Клуб 200 и получить подарки, рассказать подробнее? " \
                       f"У вас на бонусном счету {data['Баланс']}, можете использовать их для покупки продукции. " \
                       f"Ваш консультант Siberian Wellness - {myName}."
            else:
                text = f"Здравствуйте {clientName}, Вы сделали в этом месяце {data['ЛО']} баллов и можете " \
                       f"перейти в Бизнес партнеры совершенно бесплатно. Ваш кэшбэк увеличится до 25%, " \
                       f"а так же сможете участвовать в программе Клуб 200 и получить подарки, рассказать подробнее?" \
                       f"Ваш консультант Siberian Wellness - {myName}."
        else:
            text = ""

        if text:
            link = f'https://web.whatsapp.com/send/?phone={data["Телефон"]}&text={text}'
            # link = f'https://api.whatsapp.com/send/?phone={data["Телефон"]}&text={text}'

        else:
            link = f'https://web.whatsapp.com/send/?phone={data["Телефон"]}&text=Здравствуйте {clientName}'
            # link = f'https://api.whatsapp.com/send/?phone={data["Телефон"]}&text=Здравствуйте {clientName}'

        WhatsApp.append(f'{link}')

    data_team.loc[:, 'ОО'] = data_team['ОО'].replace(0, "")
    data_team.loc[:, 'НОО'] = data_team['НОО'].replace(0, "")
    data_team.loc[:, 'ЛО'] = data_team['ЛО'].replace(0, "")
    data_team.loc[:, 'Рассылка'] = WhatsApp

    # Применяем функцию к столбцу 'Примечание'
    data_team['Примечание'] = data_team.apply(transfer_data, axis=1)

    return {'data_team': data_team,'buy_my_team': buy_my_team}



def save_tables(id, tables):
    database_file = str(id)

    with sqlite3.connect(database_file) as conn:
        conn.execute(f"PRAGMA key='{PASSWORD}'")
        conn.commit()

        for table_name, table_data in tables.items():
            if isinstance(table_data, pd.DataFrame):
                try:
                    table_data.to_sql(table_name, conn, if_exists='replace', index=False)
                except Exception as e:
                    print(f"Произошла ошибка при сохранении таблицы {table_name}: {e}")
                    traceback.print_exc()


def format_time(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    # Добавляем обозначение переменным
    hours_str = f"{int(hours)} ч" if hours != 0 else ""
    minutes_str = f"{int(minutes)} мин" if minutes != 0 else ""
    seconds_str = f"{int(seconds)} сек" if seconds != 0 else ""

    # Форматируем время и возвращаем результат
    formatted_time = f"{hours_str} {minutes_str} {seconds_str}".strip()
    return formatted_time


def backoffice(number, password, pk, name, request = None):
    status = request.user
    status.status = False
    status.save()
    try:
        user = {'number': number, 'password': password, 'myName' : name}
        user_data = process_user_data(user)

        if isinstance(user_data, tuple):
            tables = generate_text(user, *user_data)
            save_tables(pk, tables)
        else:
            return f"Ошибка - {user_data}"
    except :
        return traceback.print_exc()
    status.status = True
    status.save()



@login_required
def table_main(request):
    def create_link(x):
        return f'<a href="{x}" class="btn btn-primary" target="_blank">Отправить&nbspсообщение</a>'

    pk = request.user.pk
    database_file = str(pk)

    if not os.path.isfile(database_file):
        context = {'name': 'Необходимо обновить данные', 'table_data': ""}
        return render(request, 'main.html', context)

    last_modified = datetime.fromtimestamp(os.path.getmtime(database_file)).strftime('%Y-%m-%d %H:%M:%S')

    with sqlite3.connect(database_file) as conn:
        conn.execute(f"PRAGMA key='{PASSWORD}'")
        conn.commit()

        cursor = conn.cursor()

        # Оптимизированный запрос 1
        query = "SELECT ФИО, Телефон, Email, ОО FROM data_team WHERE Уровень = 0 LIMIT 1"
        cursor.execute(query)
        result = cursor.fetchone()
        # Получить текущего пользователя
        user = request.user
        # Сохранить данные в поля пользователя
        user.sw_name = result[0]
        user.sw_phone = result[1]
        user.sw_email = result[2]
        # Сохранить изменения
        user.save()

        name = f"{user.sw_name} {result[3]} бал, "

        # Оптимизированный запрос 2
        query = """
                SELECT * FROM data_team 
                WHERE 
                    Уровень = 1 OR 
                    Примечание LIKE '%Нет покупок%' OR
                    Примечание LIKE '%Club%' OR
                    Баланс != ''
                """
        cursor.execute(query)
        data_team = cursor.fetchall()

        column_names = [description[0] for description in cursor.description]
        data_team = pd.DataFrame(data_team, columns=column_names)

    if data_team.empty:
        context = {'name': 'Необходимо обновить данные', 'table_data': ""}
        return render(request, 'main.html', context)

    # Копируем столбец "Баланс" в новый столбец "Новый баланс"
    data_team['Новый баланс'] = data_team['Баланс']

    # Удаляем знаки валюты и преобразуем столбец "Новый баланс" в числовой формат
    data_team['Новый баланс'] = data_team['Новый баланс'].str.extract(r'(\d{1,3}[ ]?\d{0,3}[,]\d{2})')\
        .replace(' ', '', regex=True).replace(',', '.', regex=True)

    data_team['Новый баланс'] = pd.to_numeric(data_team['Новый баланс'], errors='coerce')

    data_team.sort_values(by=['Примечание', 'Ранг', 'ОО', 'ЛО', 'Новый баланс'], ascending=False, inplace=True)

    data_team['Рассылка'] = data_team['Рассылка'].apply(create_link)

    data_team.loc[:, 'Ранг'] = data_team['Ранг'].replace(rankDict)

    data_team = data_team[['Регистрационный номер', 'Уровень', 'Ранг', 'ОО','НОО', 'ФИО', 'Телефон',
                           'ЛО', 'Баланс', 'Примечание', 'Рассылка']]

    table_data = html.unescape(data_team.to_html(index=False, classes='table table-striped table-hover'))
    context = {'table_data': table_data, 'name': name, 'last_modified': last_modified}
    return render(request, 'main.html', context)