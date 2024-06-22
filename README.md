# Siberian Wellness Consolidated Report Backoffice

## Описание
Этот проект представляет собой веб-приложение на Django для управления данными пользователей и взаимодействия с внешним сервисом Siberian Wellness. Приложение выполняет аутентификацию пользователей, получает отчеты и данные, обрабатывает их и отображает сводную информацию на веб-странице.

## Функциональность
- Получение данных и отчетов с внешнего сервиса Siberian Wellness.
- Обработка данных пользователей и генерация текстовых сообщений.
- Отображение сводной таблицы данных пользователей на веб-странице.

## Использование
1. Перейдите на [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin) и войдите под учетной записью суперпользователя.
2. Зарегистрируйте новых пользователей или импортируйте данные пользователей.
3. Для запуска обработки данных пользователей и получения отчетов, выполните соответствующие действия через интерфейс приложения.

## Структура Проекта
- **backoffice.py**: Основные функции для взаимодействия с внешним сервисом, аутентификации и обработки данных.
- **config.py**: Конфигурационные параметры и URL-адреса.
- **django_app/**: Основная директория приложения Django.

## Пример Итоговой Таблицы
Итоговая таблица отображает сводную информацию о пользователях, включая их регистрационный номер, уровень, ранг, баллы, контактную информацию и примечания.

| Регистрационный номер | Уровень | Ранг                     | OO | НОО | ФИО           | Телефон     | ЛО | Баланс   | Примечание                    | Рассылка                                             |
|-----------------------|---------|--------------------------|----|-----|---------------|-------------|----|----------|-------------------------------|------------------------------------------------------|
| 1234567890            | 1       | КЛИЕНТ                   | 10 | 100 | Иванов И.И.    | +71234567890 | 50 | 1000 руб | Клуб Постоянства              | [Отправить сообщение](https://web.whatsapp.com/...)  |
| 2345678901            | 2       | БИЗНЕС-ПАРТНЕР           | 20 | 200 | Петров П.П.    | +72345678901 | 100 | 2000 руб | Club 200                      | [Отправить сообщение](https://web.whatsapp.com/...)  |
| 3456789012            | 3       | BUSINESS TEAM 1000       | 30 | 300 | Сидоров С.С.   | +73456789012 | 150 | 3000 руб | Новичок без покупок           | [Отправить сообщение](https://web.whatsapp.com/...)  |
| 4567890123            | 4       | SAPPHIRE BUSINESS LEADER | 40 | 400 | Кузнецов К.К.  | +74567890123 | 200 | 4000 руб | Нет покупок 6 месяцев         | [Отправить сообщение](https://web.whatsapp.com/...)  |
| 5678901234            | 5       | DIAMOND BUSINESS LEADER  | 50 | 500 | Александров А.А.| +75678901234 | 250 | 5000 руб | Выполнил условия программы   | [Отправить сообщение](https://web.whatsapp.com/...)  |
