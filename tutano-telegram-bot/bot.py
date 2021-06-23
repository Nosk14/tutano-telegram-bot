import logging
import os
from uuid import uuid4
from telegram import InlineQueryResultPhoto, InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardButton, \
    InlineKeyboardMarkup
from telegram.ext import Updater, InlineQueryHandler
import requests
from time import time, sleep

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

last_time_rq = time()


def send_request(query):
    global last_time_rq
    diff = time() - last_time_rq
    if diff < 0.1:
        sleep(diff)
    last_time_rq = time()

    return requests.get("https://api.scryfall.com/cards/search", params={'q': query})


def get_cards(query):
    rs = send_request(query)
    if rs.status_code != 200:
        raise Exception(f"[${rs.status_code}]$ {rs.text}")

    return rs.json()['data']


def build_query_result(card):
    if card['image_status'] == 'missing':
        return None

    if 'image_uris' in card:
        thumb = card['image_uris']['small']
        photo = card['image_uris']['png']
    elif 'card_faces' in card:
        thumb = card['card_faces'][0]['image_uris']['small']
        photo = card['card_faces'][0]['image_uris']['png']
    else:
        return None

    gatherer_button = InlineKeyboardButton("Gatherer", url=card['related_uris']['gatherer'])
    cardmarket_button = InlineKeyboardButton("CardMarket", url=card['purchase_uris']['cardmarket'])
    markup = InlineKeyboardMarkup([[gatherer_button, cardmarket_button]])
    return InlineQueryResultPhoto(id=uuid4(),
                                  title=card['name'],
                                  thumb_url=thumb,
                                  photo_url=photo,
                                  reply_markup=markup
                                  )


def handle_query(update, context):
    query = update.inline_query.query

    if not query or len(query) < 3:
        return

    cards = get_cards(query)

    results = [build_query_result(c) for c in cards[:14]]
    results = [r for r in results if r is not None]

    return update.inline_query.answer(results, cache_time=1)


def handle_error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


if __name__ == '__main__':
    bot_token = os.getenv("TELEGRAM_TOKEN", None)
    if not bot_token:
        raise Exception("Invalid Telegram bo token.")

    updater = Updater(bot_token, use_context=True)

    dispatcher = updater.dispatcher
    dispatcher.add_handler(InlineQueryHandler(handle_query))
    dispatcher.add_error_handler(handle_error)

    updater.start_polling()
    updater.idle()
