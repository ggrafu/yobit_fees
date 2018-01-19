# -*- coding: utf-8 -*-
import requests
from random import randint
from lxml import html
import os
import time
from telegram.ext import Updater, CommandHandler, RegexHandler
import csv
import json

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
UPDATE_INTERVAL = int(os.getenv('UPDATE_INTERVAL', 60))

subscribers = set()


def request_fees():
    try:
        page = requests.get('https://yobit.net/ru/fees/')
    except Exception as ex:
        print 'Failed to fetch the website:', ex.message
        return {}

    tree = html.fromstring(page.content.decode('utf-8'))

    in_fee = 0
    out_fee = 0

    try:
        for payment in tree.xpath('//*[@id="fees_table"]/tbody')[0]:
            name = payment[0].xpath('a//text()')

            if name and name[0] == 'QIWI':
                if u'Без комиссии' not in payment[2].text:
                    in_fee = payment[2].text.split('% RUR')[0]
                    out_fee = payment[3].text.split('% RUR')[0]

    except IndexError as ex:
        print 'Was not able to find the datatable on page. Dropping received content to response.html', ex.message
        with open('export/response.html', 'w') as response_html:
            response_html.write(page.content)
        return {}

    return {
        'in_fee': in_fee,
        'out_fee': out_fee
    }


def subscribe(bot, update):
    subscribers.add(update.message.chat_id)
    update.message.reply_text(u'Вы подписаны на обновления')


def unsubscribe(bot, update):
    if update.message.chat_id in subscribers:
        subscribers.remove(update.message.chat_id)
        update.message.reply_text(u'Вы отписаны от обновлений')
    else:
        update.message.reply_text(u'Не обнаружил Вас в подписках')


def now(bot, update):
    fees = request_fees()
    if fees:
        update.message.reply_text(u'Текущая комиссия: ввод: {fees[in_fee]}%, вывод: {fees[out_fee]}%'.format(fees=fees))
    else:
        update.message.reply_text(u'Возникли проблемы с доступ к вебсайту. Обратитесь в поддержку')


def error(bot, update, error):
    print error


def main():
    updater = Updater(TELEGRAM_TOKEN)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler('subscribe', subscribe))
    dp.add_handler(CommandHandler('unsubscribe', unsubscribe))
    dp.add_handler(RegexHandler('now', now))

    dp.add_error_handler(error)

    updater.start_polling()

    try:
        with open('export/subscribers.json', 'r') as subscribers_json:
            global subscribers
            subscribers = set(json.load(subscribers_json))
    except (IOError, ValueError):
        print 'No subscribers found. Starting from empty list.'
        pass

    prev_fees = {}
    try:
        with open('export/output.csv', 'a') as f:
            writer = csv.writer(f)
            try:
                while True:
                    fees = request_fees()
                    if fees and fees != prev_fees:
                        writer.writerow((time.strftime('%c'), fees['in_fee'], fees['out_fee']))
                        f.flush()
                        for chat_id in subscribers:
                            if prev_fees:
                                msg = u'Комиссия QIWI изменилась. Ввод: {prev_fees[in_fee]}% -> {fees[in_fee]}%,'.format(
                                    prev_fees=prev_fees, fees=fees) + \
                                      u' вывод: {prev_fees[out_fee]}% -> {fees[out_fee]}%'.format(prev_fees=prev_fees,
                                                                                                  fees=fees)
                            else:
                                msg = u'Парсер начал работу. Начальные значения: ' + \
                                      u'ввод: {fees[in_fee]}%, вывод: {fees[out_fee]}%'.format(fees=fees)
                            updater.bot.send_message(chat_id=chat_id, text=msg)
                        prev_fees = fees
                    time.sleep(UPDATE_INTERVAL + randint(-int(UPDATE_INTERVAL*0.1), int(UPDATE_INTERVAL*0.1)))
            except KeyboardInterrupt:
                f.close()
    except IOError as ex:
        print 'Failed write to the output file:', ex.message
    finally:
        for chat_id in subscribers:
            updater.bot.send_message(chat_id=chat_id, text=u'Завершаю работу... До встречи!')
        with open('export/subscribers.json', 'w') as subscribers_json :
            json.dump(list(subscribers), subscribers_json)
        updater.stop()


if __name__ == '__main__':
    main()
