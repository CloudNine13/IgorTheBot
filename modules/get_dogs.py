import json
import mimetypes
import urllib

from urllib import request
from telegram.ext import CallbackContext


def get_dogs(chat_id: str, context: CallbackContext) -> None:
    """Gets a file form random dog API.
    Can get GIF, MP4, JPEG.
    :param chat_id: is used to respond to user
    :param context: is used to respond to user
    :return str, HTTPResponse
    str is type of file, HTTPResponse is the data to show"""

    print("get_dogs: Getting dogs!")
    response = json.load(urllib.request.urlopen('https://random.dog/woof.json'))
    link = response['url']
    mimetype = mimetypes.guess_type(link)[0]
    if mimetype is not None:
        mimetype = mimetype.split('/')[0]
        if mimetype.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            context.bot.send_photo(chat_id=chat_id, photo=link)
        elif link.lower().endswith(('.mp4', '.webm', '.wav')):
            context.bot.send_video(chat_id=chat_id, video=link, supports_streaming=True)
        else:  # link.lower().endswith(('.png', '.jpg', '.jpeg'))
            context.bot.send_message(chat_id, link)
    else:
        raise TypeError("Mimetype is None")