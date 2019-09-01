'''
Бот для швидкого та зручного доступу до розкладу занять групи. (КПІ)

Критика та побажання:
@NazarPonochevnyi
'''


import json
import pytz
import datetime
import telegram
from telegram.ext import Updater, InlineQueryHandler, CommandHandler


# Global variables
StartMessage = """
Бот для швидкого та зручного доступу до розкладу занять групи. (КПІ)

Увага! Бот не оновлює розклад автоматично, тому іноді розклад занять може бути не вірним.
Проте ми будемо регулярно слідкувами за оновленями розкладу занять і оновлювати бота.

У бота є спеціальні позначення для розкладу сьогоднішнього дня і поточного тижня:
1) \N{black rightwards arrow} (поточний) - це позначення показує, яка пара йде зараз (команда /today) або який день тижня зараз (команда /week)
2) \N{white heavy check mark} (пройдено) - це позначення показує, які пари вже пройшли (команда /today) або які дні тижня вже пройдені (команда /week)
3) \N{white medium small square} (очікується) - це позначення показує, які пари ще не пройшли (команда /today) або які дні тижня ще залишилися (команда /week)

Критика та побажання:
@NazarPonochevnyi
"""

Times = (
    (datetime.time(8, 30), datetime.time(10, 5)),
    (datetime.time(10, 25), datetime.time(12, 0)),
    (datetime.time(12, 20), datetime.time(13, 55)),
    (datetime.time(14, 15), datetime.time(15, 50)),
    (datetime.time(16, 10), datetime.time(17, 45))
)

with open('schedule.json', 'r', encoding = 'utf-8') as f:
    Schedule = json.load(f)

Weekdays = list(Schedule.keys())


# Methods
def get_lessons_status(time, times):
    status = []
    for i in range(len(times)):
        if times[i][0] <= time <= times[i][1]:
            status.append('\N{black rightwards arrow}') # '->'
        elif time > times[i][1]:
            status.append('\N{white heavy check mark}') # '+'
        elif time < times[i][0]:
            status.append('\N{white medium small square}') # '-'
        else:
            status.append('')
    return status

def get_days_status(day_i, weekdays):
    status = {}
    for i, weekday in enumerate(weekdays):
        if i == day_i:
            status[weekday] = '\N{black rightwards arrow}' # '->'
        elif i > day_i:
            status[weekday] = '\N{white medium small square}' # '-'
        elif i < day_i:
            status[weekday] = '\N{white heavy check mark}' # '+'
        else:
            status[weekday] = ''
    return status

def start(bot, update):
    chat_id = update.message.chat_id
    bot.send_message(chat_id=chat_id, text=StartMessage, parse_mode=telegram.ParseMode.HTML)

def today(bot, update):
    chat_id = update.message.chat_id
    
    tzkiev = pytz.timezone('Europe/Kiev')
    today = datetime.datetime.now(tzkiev)
    year, week_num, day_num = datetime.datetime.isocalendar(today)
    time = datetime.datetime.time(today)
    week_num = '1' if week_num % 2 == 0 else '2'
    
    if day_num <= len(Weekdays):
        day = Weekdays[day_num - 1]
        lessons_status = get_lessons_status(time, Times)
        message = 'Розклад на сьогодні <b>({}</b>, навчання по <b>{})</b>:\nЗараз: {}\n'.format(
            day, 'чисельнику' if week_num == '1' else 'знаменнику', today.strftime("%d.%m.%Y %H:%M")
        )
        for i in range(len(Times)):
            lesson_num = str(i + 1)
            lesson = Schedule[day][lesson_num][week_num]
            if lesson != '':
                message += '\n{} <b>{}.</b> ({} - {})\n'.format(lessons_status[i], lesson_num, Times[i][0].strftime("%H:%M"), Times[i][1].strftime("%H:%M"))
                for key in lesson.keys():
                    message += '<b>{}:</b> {}\n'.format(key, lesson[key])
            else:
                message += '\n{} <b>{}.</b> ({} - {})\nПари немає.\n'.format(lessons_status[i], lesson_num, Times[i][0].strftime("%H:%M"), Times[i][1].strftime("%H:%M"))
        bot.send_message(chat_id=chat_id, text=message, parse_mode=telegram.ParseMode.HTML)
    else:
        bot.send_message(chat_id=chat_id, text='Сьогодні <b>({})</b> занять немає.'.format(today.strftime("%d.%m.%Y")), parse_mode=telegram.ParseMode.HTML)

def tomorrow(bot, update):
    chat_id = update.message.chat_id
    
    tzkiev = pytz.timezone('Europe/Kiev')
    today = datetime.datetime.now(tzkiev)
    year, week_num, day_num = datetime.datetime.isocalendar(today)
    if day_num == 7:
        day_num = 1
        week_num += 1
    else:
        day_num += 1
    week_num = '1' if week_num % 2 == 0 else '2'
    
    if day_num <= len(Weekdays):
        day = Weekdays[day_num - 1]
        message = 'Розклад на завтра <b>({}</b>, навчання по <b>{})</b>:\nЗараз: {}\n'.format(
            day, 'чисельнику' if week_num == '1' else 'знаменнику', today.strftime("%d.%m.%Y %H:%M")
        )
        for i in range(len(Times)):
            lesson_num = str(i + 1)
            lesson = Schedule[day][lesson_num][week_num]
            if lesson != '':
                message += '\n<b>{}.</b> ({} - {})\n'.format(lesson_num, Times[i][0].strftime("%H:%M"), Times[i][1].strftime("%H:%M"))
                for key in lesson.keys():
                    message += '<b>{}:</b> {}\n'.format(key, lesson[key])
            else:
                message += '\n<b>{}.</b> ({} - {})\nПари немає.\n'.format(lesson_num, Times[i][0].strftime("%H:%M"), Times[i][1].strftime("%H:%M"))
        bot.send_message(chat_id=chat_id, text=message, parse_mode=telegram.ParseMode.HTML)
    else:
        bot.send_message(chat_id=chat_id, text='Завтра занять немає.', parse_mode=telegram.ParseMode.HTML)

def week(bot, update):
    chat_id = update.message.chat_id
    
    tzkiev = pytz.timezone('Europe/Kiev')
    today = datetime.datetime.now(tzkiev)
    year, week_num, day_num = datetime.datetime.isocalendar(today)
    week_num = '1' if week_num % 2 == 0 else '2'
    
    days_status = get_days_status(day_num - 1, Weekdays)
    message = 'Розклад на тиждень (навчання по <b>{}</b>):\nЗараз: {}'.format(
        'чисельнику' if week_num == '1' else 'знаменнику', today.strftime("%d.%m.%Y %H:%M")
    )
    for day in Weekdays:
        message += '\n\n{} <b>{}</b>\n'.format(days_status[day], day)
        for i in range(len(Times)):
            lesson_num = str(i + 1)
            lesson = Schedule[day][lesson_num][week_num]
            if lesson != '':
                message += '\n<b>{}.</b> ({} - {})\n'.format(lesson_num, Times[i][0].strftime("%H:%M"), Times[i][1].strftime("%H:%M"))
                for key in lesson.keys():
                    message += '<b>{}:</b> {}\n'.format(key, lesson[key])
            else:
                message += '\n<b>{}.</b> ({} - {})\nПари немає.\n'.format(lesson_num, Times[i][0].strftime("%H:%M"), Times[i][1].strftime("%H:%M"))
    if len(Weekdays) != 0:
        bot.send_message(chat_id=chat_id, text=message, parse_mode=telegram.ParseMode.HTML)
    else:
        bot.send_message(chat_id=chat_id, text='На цьому тижні занять немає.', parse_mode=telegram.ParseMode.HTML)

def next_week(bot, update):
    chat_id = update.message.chat_id
    
    tzkiev = pytz.timezone('Europe/Kiev')
    today = datetime.datetime.now(tzkiev)
    year, week_num, day_num = datetime.datetime.isocalendar(today)
    week_num += 1
    week_num = '1' if week_num % 2 == 0 else '2'
    
    message = 'Розклад на наступний тиждень (навчання по <b>{}</b>):\nЗараз: {}'.format(
        'чисельнику' if week_num == '1' else 'знаменнику', today.strftime("%d.%m.%Y %H:%M")
    )
    for day in Weekdays:
        message += '\n\n<b>{}</b>\n'.format(day)
        for i in range(len(Times)):
            lesson_num = str(i + 1)
            lesson = Schedule[day][lesson_num][week_num]
            if lesson != '':
                message += '\n<b>{}.</b> ({} - {})\n'.format(lesson_num, Times[i][0].strftime("%H:%M"), Times[i][1].strftime("%H:%M"))
                for key in lesson.keys():
                    message += '<b>{}:</b> {}\n'.format(key, lesson[key])
            else:
                message += '\n<b>{}.</b> ({} - {})\nПари немає.\n'.format(lesson_num, Times[i][0].strftime("%H:%M"), Times[i][1].strftime("%H:%M"))
    if len(Weekdays) != 0:
        bot.send_message(chat_id=chat_id, text=message, parse_mode=telegram.ParseMode.HTML)
    else:
        bot.send_message(chat_id=chat_id, text='На наступному тижні занять немає.', parse_mode=telegram.ParseMode.HTML)


# Main
def main():
    updater = Updater('YOUR_TELEGRAM_BOT_TOKEN') # change string to your token!!!
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('today', today))
    dp.add_handler(CommandHandler('tomorrow', tomorrow))
    dp.add_handler(CommandHandler('week', week))
    dp.add_handler(CommandHandler('next_week', next_week))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
