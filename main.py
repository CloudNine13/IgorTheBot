import os
import logging
import threading
import regex

from abc import ABC, abstractmethod
from datetime import datetime
from telegram import ReplyKeyboardMarkup, KeyboardButton, Update, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler

from models.custom_url_object import CustomUrlObject
from modules.get_dogs import get_dogs
from modules.get_movie import get_movie
from modules.movie_menu import movie_menu


def configure_logging() -> logging:
    """This is the method to configure logger.
    :return logging: return configured logger object"""

    logging.basicConfig(
        filename=f"logs/{__name__}log{datetime.now().strftime('%d-%m-%Y-%H-%M-%S')}.log",
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    return logging.getLogger(__name__)


logger = configure_logging()
TOKEN = os.environ.get("API_TOKEN")


class CustomApplication(ABC):
    """This is the abstract class of Telegram Bot
    :param ABC: implementation of Abstract Class library
    :var Updater: is used to set up configs for telegram bot library."""

    updater: Updater
    movieSearchSwitch: bool

    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def config_start_menu(self, update: Update, context: CallbackContext) -> None:
        pass

    @abstractmethod
    def setup_dispatcher(self) -> None:
        pass

    @abstractmethod
    def start(self) -> None:
        pass

    @abstractmethod
    def data_controller(self, update: Update, context: CallbackContext) -> None:
        pass

    @abstractmethod
    def button_controller(self, update: Update, context: CallbackContext) -> None:
        pass

    @abstractmethod
    def error_controller(self, update: Update, context: CallbackContext) -> None:
        pass


class TelegramBot(CustomApplication):
    """This is the class that implements Application abstract.
    :param CustomApplication: is the implementation of abstract class."""

    updater: Updater
    movieSearchSwitch = False
    cuo = CustomUrlObject()

    def __init__(self) -> None:
        self.updater = Updater(TOKEN, use_context=True)
        print("__init__: Successfully initiated!")

    def setup_dispatcher(self) -> None:
        dp = self.updater.dispatcher
        start_handler = CommandHandler("start", self.config_start_menu)
        controller_handler = MessageHandler(Filters.text, self.data_controller)
        dp.add_handler(start_handler)
        dp.add_handler(controller_handler)
        dp.add_handler(CallbackQueryHandler(self.button_controller))
        dp.add_error_handler(self.error_controller)
        print("setup_dispatcher: Dispatcher is successfully configured!")
        self.start()

    def config_start_menu(self, update: Update, context: CallbackContext) -> None:
        main_menu_keyboard = [[KeyboardButton(text="Пёсели\u2764")], [KeyboardButton(text="Фильмы\U0001F3AC")]]
        main_menu = ReplyKeyboardMarkup(main_menu_keyboard)
        um = update.message
        um.reply_text(text="Категорически приветствую!")
        um.reply_text(text="Выберите категорию из списка ниже", reply_markup=main_menu)

    def start(self) -> None:
        print("start: Starting to poll...")
        self.updater.start_polling()
        self.updater.idle()

    def data_controller(self, update: Update, context: CallbackContext) -> None:
        print("data_controller: User made a callback!")
        text = update.message.text
        chat_id = update.effective_chat.id
        ReplyKeyboardRemove(remove_keyboard=True)

        if text == "Пёсели\u2764":
            send_thread = threading.Thread(
                target=get_dogs,
                name="Get dogs",
                args=(chat_id, context)
            )
            send_thread.start()
        elif text == "Фильмы\U0001F3AC":
            self.cuo.locale = update.effective_user.language_code  # Configure custom url object's locale string
            context.bot.send_message(
                chat_id,
                "Вы выбрали категорию Фильмы. Поиск в категории осуществляется _*на английском языке*_",
                parse_mode='Markdown',
                reply_markup=ReplyKeyboardRemove()
            )
            send_thread = threading.Thread(
                target=movie_menu,
                name="Make movie menu",
                args=(update,)
            )
            send_thread.start()
        elif self.movieSearchSwitch:
            if regex.search(r'\p{IsCyrillic}', text) is not None:
                context.bot.send_message(chat_id, "Текст поиска должен быть на английском!")
                context.bot.send_message(chat_id, "Попробуйте еще раз!")
                send_thread = threading.Thread(
                    target=movie_menu,
                    name="Make movie menu",
                    args=(update,)
                )
                send_thread.start()
            else:
                self.cuo.search_term = text
                self.movieSearchSwitch = False
                send_thread = threading.Thread(
                    target=get_movie,
                    name="Get movies",
                    args=(self.cuo.make_url(), chat_id, context)
                )
                send_thread.start()
        else:
            context.bot.send_message(chat_id, "Я пока еще не знаю такой команды :С")

    def button_controller(self, update: Update, context: CallbackContext) -> None:
        print("button_controller: User triggered the button's callback!")
        query = update.callback_query
        query.answer()
        choice = query.data
        query.message.edit_text(f"{choice}")
        chat_id = update.effective_chat.id

        if choice == 'Фильмы':
            self.cuo.search_type = "SearchMovie"
            context.bot.send_message(chat_id, "Вы выбрали категорию фильмы. \nУкажите, пожалуйста, название фильма:")
        if choice == 'Актёры':
            self.cuo.search_type = "SearchName"
            context.bot.send_message(chat_id, "Вы выбрали категорию актеры. \nУкажите, пожалуйста, имя актера:")
        if choice == 'Сериалы':
            self.cuo.search_type = "SearchSeries"
            context.bot.send_message(chat_id, "Вы выбрали категорию сериалы. \nУкажите, пожалуйста, название сериала:")
        if choice == 'Без разницы':
            self.cuo.search_type = "SearchAll"
            context.bot.send_message(chat_id, "Вы выбрали категорию без разницы. \nВведите интересующий вас запрос:")

        self.movieSearchSwitch = True

    def error_controller(self, update: Update, context: CallbackContext) -> None:
        print("error_controller: Error happened!")
        logger.warning(f'Update {update} caused error {context.error}')
        print("error_controller: Shutting down the app..")
        self.updater.stop()
        self.updater.is_idle = False


if __name__ == '__main__':
    TelegramBot().setup_dispatcher()
