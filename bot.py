import os
import telebot
from currency_converter import CurrencyConverter
from telebot import types

# Загрузка токена из переменной окружения
TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

currency = CurrencyConverter()
amount = 0


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        'Добро пожаловать в конвертер валют! \n\nВведите сумму для конвертации:'
    )
    bot.register_next_step_handler(message, summa)


def summa(message):
    global amount
    try:
        amount = int(message.text.strip())
    except ValueError:
        bot.send_message(
            message.chat.id,
            'Неверный формат. Введите число (например: 100)'
        )
        bot.register_next_step_handler(message, summa)
        return

    if amount > 0:
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn1 = types.InlineKeyboardButton('USD/EUR', callback_data='usd/eur')
        btn2 = types.InlineKeyboardButton('EUR/USD', callback_data='eur/usd')
        btn3 = types.InlineKeyboardButton('USD/GBP', callback_data='usd/gbp')
        btn4 = types.InlineKeyboardButton('GBP/USD', callback_data='gbp/usd')
        btn5 = types.InlineKeyboardButton('Другие значения ➕', callback_data='else')
        markup.add(btn1, btn2, btn3, btn4, btn5)

        bot.send_message(
            message.chat.id,
            f'Сумма: {amount}\n\nВыберите валютную пару:',
            reply_markup=markup
        )
    else:
        bot.send_message(
            message.chat.id,
            'Число должно быть больше нуля. Повторите ввод суммы:'
        )
        bot.register_next_step_handler(message, summa)


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    global amount
    if call.data != 'else':
        values = call.data.upper().split('/')
        try:
            res = currency.convert(amount, values[0], values[1])
            bot.send_message(
                call.message.chat.id,
                f'💱 {amount} {values[0]} = {round(res, 2)} {values[1]}\n\nМожете ввести новую сумму:'
            )
            bot.register_next_step_handler(call.message, summa)
        except Exception as e:
            bot.send_message(
                call.message.chat.id,
                f'Ошибка конвертации. Попробуйте другую пару.\n\nВведите новую сумму:'
            )
            bot.register_next_step_handler(call.message, summa)
    else:
        bot.send_message(
            call.message.chat.id,
            '💱 Введите пару валют через слэш.\n\nПримеры: `USD/RUB`, `EUR/JPY`, `GBP/USD`',
            parse_mode='Markdown'
        )
        bot.register_next_step_handler(call.message, my_currency)


def my_currency(message):
    global amount
    try:
        values = message.text.upper().split('/')
        if len(values) != 2:
            raise ValueError
        res = currency.convert(amount, values[0], values[1])
        bot.send_message(
            message.chat.id,
            f'💱 {amount} {values[0]} = {round(res, 2)} {values[1]}\n\nМожете ввести новую сумму:'
        )
        bot.register_next_step_handler(message, summa)
    except Exception:
        bot.send_message(
            message.chat.id,
            'Неверный формат или валютная пара.\n\nВведите пару через слэш, например: `USD/RUB`',
            parse_mode='Markdown'
        )
        bot.register_next_step_handler(message, my_currency)


if __name__ == '__main__':
    print('Конвертер валют запущен...')
    print('Команды: /start')
    bot.polling(none_stop=True)
