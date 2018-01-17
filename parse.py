# -*- coding: utf-8 -*-
import requests
from random import randint
from lxml import html
import os
import time
from telegram.ext import Updater, CommandHandler
import csv

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
UPDATE_INTERVAL = os.getenv('UPDATE_INTERVAL', 60)

subscribers = set()


def request_fees():
    page = requests.get('https://yobit.net/ru/fees/')
    tree = html.fromstring(page.content.decode('utf-8'))

    in_fee = 0
    out_fee = 0

    for payment in tree.xpath('//*[@id="fees_table"]/tbody')[0]:
        name = payment[0].xpath('a//text()')

        if name and name[0] == 'QIWI':
            if u'Без комиссии' not in payment[2].text:
                in_fee = payment[2].text.split('% RUR')[0]
                out_fee = payment[3].text.split('% RUR')[0]

    return {
        'in_fee': in_fee,
        'out_fee': out_fee
    }


def subscribe(bot, update):
    subscribers.add(update.message.chat_id)
    update.message.reply_text('You have been subscribed')


def unsubscribe(bot, update):
    if update.message.chat_id in subscribers:
        subscribers.remove(update.message.chat_id)
        update.message.reply_text('You have been unsubscribed')
    else:
        update.message.reply_text('You are not in the list')


def error(bot, update, error):
    print error


def main():
    updater = Updater(TELEGRAM_TOKEN)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler('subscribe', subscribe))
    dp.add_handler(CommandHandler('unsubscribe', unsubscribe))

    dp.add_error_handler(error)

    updater.start_polling()
    prev_fees = {}
    with open('export/output.csv', 'wb') as f:
        writer = csv.writer(f)
        writer.writerow(('Time', 'In_Fee', 'Out_Fee'))
        try:
            while True:
                fees = request_fees()
                if fees != prev_fees:
                    writer.writerow((time.strftime('%c'), fees['in_fee'], fees['out_fee']))
                    f.flush()
                    for chat_id in subscribers:
                        msg = u'Комиссия QIWI изменилась. Ввод: {prev_fees[in_fee]}% -> {fees[in_fee]}%,'.format(
                            prev_fees=prev_fees, fees=fees) + \
                              u' вывод: {prev_fees[out_fee]}% -> {fees[out_fee]}%'.format(prev_fees=prev_fees, fees=fees)
                        updater.bot.send_message(chat_id=chat_id, text=msg)
                prev_fees = fees
                time.sleep(UPDATE_INTERVAL + randint(-5, 5))
        except KeyboardInterrupt:
            updater.stop()
            f.close()


if __name__ == '__main__':
    main()
