from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update


def movie_menu(update: Update) -> None:

    keyboard = [
        [
            InlineKeyboardButton("Фильмы", callback_data='Фильмы'),
            InlineKeyboardButton("Актёры", callback_data='Актёры'),
        ],
        [
            InlineKeyboardButton("Сериалы", callback_data='Сериалы'),
            InlineKeyboardButton("Без разницы", callback_data='Без разницы'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Что вы хотели бы найти?", reply_markup=reply_markup)
