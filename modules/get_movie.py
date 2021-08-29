import json
import urllib
from time import sleep
from urllib import request

from telegram.error import TimedOut
from telegram.ext import CallbackContext


def get_movie(url: str, chat_id: str, context: CallbackContext) -> None:
    """Method to get movies information
    :param url: str - is used to pass movie's url to process
    :param chat_id: str - is used to respond to user in chat
    :param context: CallbackContext - is used to send messages to chat"""
    print("get_movie: Getting movie!")
    try:
        response = json.load(urllib.request.urlopen(url))
    except TimedOut as ex:
        context.bot.send_message(
            chat_id,
            f"Ресурс не отвечает: {ex}. Попробуйте повторить попытку позже"
        )
        return

    number_of_results = len(response["results"])
    if number_of_results == 0:
        context.bot.send_message(
            chat_id,
            "Я не нашел результатов. Возможно стоит изменить запрос."
        )
    else:
        context.bot.send_message(
            chat_id,
            f"Найденные запросы: {number_of_results}!"
        )
        process_data(response, context, chat_id)


def process_data(response: dict, context: CallbackContext, chat_id: str) -> None:
    for result in response["results"]:
        result_text = f"""Название: {result["title"]}
Описание: {result["description"]}
Постер: {result["image"]}
"""
        context.bot.send_message(chat_id, result_text)

