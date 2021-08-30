import mimetypes

import requests
from telegram.ext import CallbackContext


def get_dogs(chat_id: str, context: CallbackContext) -> None:
    """Gets a file form random dog API.
    Can get GIF, MP4, JPEG.
    :param chat_id: is used to respond to user
    :param context: is used to respond to user
    :return str, HTTPResponse
    str is type of file, HTTPResponse is the data to show"""

    print("get_dogs: Getting dogs!")
    response = requests.get('https://random.dog/woof.json').json()
    link = response['url']
    mimetype = mimetypes.guess_type(link)[0]
    if mimetype is not None:
        mimetype = mimetype.split('/')[1]
        print(mimetype)
        if mimetype.lower().endswith(('png', 'jpg', 'jpeg', 'gif')):
            context.bot.send_photo(chat_id=chat_id, photo=link)
        elif link.lower().endswith(('mp4', 'webm', 'wav')):
            context.bot.send_video(chat_id=chat_id, video=link, supports_streaming=True)
        else:  # link.lower().endswith(('.png', '.jpg', '.jpeg'))
            context.bot.send_message(chat_id, link)
    else:
        raise TypeError("Mimetype is None")
