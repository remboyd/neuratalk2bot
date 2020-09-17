import logging
from typing import Optional

from telegram import Update, Bot, Message, File, ChatAction
from telegram.ext import Updater, MessageHandler, Dispatcher, CallbackContext
from telegram.ext.filters import Filters
import toml
import json

import os
import subprocess

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def describe(path: str) -> Optional[str]:
    subprocess.run([
        config['neuraltalk']['th'],
        'eval.lua',
        '-model', config['neuraltalk']['model'],
        '-image_folder', os.path.abspath(path),
        '-num_images', '-1',
        '-gpuid', '-1'
    ], cwd=config['neuraltalk']['root'])
    try:
        with open(f'{path}/vis.json', 'r') as file:
            res = json.load(file)
        return res[0]['caption']
    except:
        return None


def caption_photo(update: Update, context: CallbackContext):
    bot: Bot = context.bot
    msg: Message = update.message

    photo: File = msg.photo[-1].get_file()
    logger.info(f'Got new image {photo.file_id}')
    path = f'./tmp/{photo.file_id}'
    os.mkdir(path)
    photo.download(f'{path}/{photo.file_id}.jpg')

    bot.send_chat_action(update.effective_chat.id, ChatAction.TYPING)
    res = describe(path)
    if res is not None:
        msg.reply_text(res, reply_to_message_id=msg.message_id)
    else:
        msg.reply_text('Error processing image', reply_to_message_id=msg.message_id)


def main():
    logger.info('Crating tmp directory to store images')
    try:
        os.mkdir('./tmp')
    except FileExistsError:
        pass

    updater: Updater = Updater(token=config['bot']['token'], use_context=True)

    dp: Dispatcher = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.photo, caption_photo))

    logger.info('Starting bot')
    updater.start_polling()


if __name__ == '__main__':
    logger.info('Reading config file')
    with open('config.toml', 'r') as configfile:
        config = toml.load(configfile)
    main()
