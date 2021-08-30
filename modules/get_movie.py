import json
import os
import urllib
from urllib import request

import requests
from telegram import Update
from telegram.error import TimedOut
from telegram.ext import CallbackContext

from models.custom_url_object import CustomUrlObject
from modules.movie_menu import movie_menu


def prepare_api():
    requests.get(
        f"https://api.themoviedb.org/3/authentication/guest_session/new?api_key={os.environ.get('API_KEY')}"
    ).json()


def get_movie(url: CustomUrlObject, update: Update, chat_id: str, context: CallbackContext) -> None:
    """Method to get movies information
    :param update: Update - is used tp call for movie menu
    :param url: str - is used to pass movie's url to process
    :param chat_id: str - is used to respond to user in chat
    :param context: CallbackContext - is used to send messages to chat"""
    print("get_movie: Getting movie!")

    prepare_api()

    try:
        response = json.load(urllib.request.urlopen(url.make_url()))
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
    elif number_of_results > 9:
        context.bot.send_message(
            chat_id,
            f"Найденные запросы: {number_of_results}! Но я покажу только пять С:"
        )
        process_data(response, context, chat_id, url.search_type, number_of_results)
    else:
        context.bot.send_message(
            chat_id,
            f"Найденные запросы: {number_of_results}!"
        )
        process_data(response, context, chat_id, url.search_type, number_of_results)
    movie_menu(update=update)


def process_data(
        response: dict,
        context: CallbackContext,
        chat_id: str,
        request_type: str,
        number_of_results: int
) -> None:
    index = 0
    for result in response["results"]:
        if number_of_results > 9 and index == 5 or index == 6:
            break
        else:
            index += 1

        if request_type == "person":

            if result["gender"] == 2:
                gender_emoji = "\U0001F468"
            elif result["gender"] == 1:
                gender_emoji = "\U0001F469"
            else:
                gender_emoji = "\U0001F47D"

            known_for = ""
            person_index = 0
            for movie in result["known_for"]:
                if movie["media_type"] == "movie":
                    person_age = ""
                    if movie["adult"] == "true":
                        person_age = "\U0001F51E"
                    known_for += f"{person_index+1}. {movie['original_title']} {person_age} \n"
                else:
                    known_for += f"{person_index+1}. {movie['original_name']} \n"
                person_index += 1

            result_text = f"""Имя: {result["name"]}
Пол: {gender_emoji}
Основной вид деятельности: {result["known_for_department"]}
Фотография: https://image.tmdb.org/t/p/original{result["profile_path"]}
Основные работы: {known_for}
"""
        elif request_type == "movie":
            stars = count_stars(result["vote_average"])

            if result["adult"] == "true":
                age = "\u2705"
            else:
                age = "\u274C"

            if result["poster_path"]:
                url_body = "https://image.tmdb.org/t/p/original"
            else:
                url_body = ""

            result_text = f"""Название: {result.get("title")} ({result["original_title"]})
Описание: {result["overview"]}
Постер: {url_body}{result["poster_path"]}
Средняя оценка: {result["vote_average"]} ({stars})
Голосов: {result["vote_count"]}
18+? {age}
"""

        else:
            stars = count_stars(result["vote_average"])
            if result["poster_path"]:
                url_body = "https://image.tmdb.org/t/p/original"
            else:
                url_body = ""
            result_text = f"""Название: {result.get("name")} ({result["original_name"]})
Первая серия: {result["first_air_date"]}
Описание: {result["overview"]}
Постер: {url_body}{result["poster_path"]}
Средняя оценка: {result["vote_average"]} ({stars})
Голосов: {result["vote_count"]}
"""

        context.bot.send_message(chat_id, result_text, parse_mode="HTML")


def count_stars(votes: int):
    if 0.0 <= votes < 2:
        stars = '\u2B50 \u2605 \u2605 \u2605 \u2605'
    elif 2 <= votes < 4:
        stars = '\u2B50 \u2B50 \u2605 \u2605 \u2605'
    elif 4 <= votes < 6:
        stars = '\u2B50 \u2B50 \u2B50 \u2605 \u2605'
    elif 6 <= votes < 8:
        stars = '\u2B50 \u2B50 \u2B50 \u2B50 \u2605'
    else:
        stars = '\u2B50 \u2B50 \u2B50 \u2B50 \u2B50'
    return stars
