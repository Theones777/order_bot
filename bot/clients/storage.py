import json

from transliterate import translit

from bot.clients.img_processing import IMGConverter
from bot.texts import CONFIRM_MESSAGE
from config import Config


class Storage:

    def __init__(self):
        self.callbacks_dict = {}
        self.revers_callbacks_dict = {}
        self.photo_ids = {}

        with open(Config.PRODUCT_CATALOG_PATH, mode="r", encoding="utf-8") as f:
            self.data = json.load(f)

        for step, step_info in self.data.items():
            for text in step_info:
                callback_data = translit(text, 'ru', reversed=True).replace(" ", "_")
                self.callbacks_dict[text] = callback_data
                self.revers_callbacks_dict[callback_data] = text
            self.photo_ids[step] = 0

        self.callbacks_dict[CONFIRM_MESSAGE] = translit(CONFIRM_MESSAGE, 'ru', reversed=True).replace(" ", "_")

        self.steps_name = Config.STEPS_NAMES
        self.IMGConverter = IMGConverter(crop_mode=Config.IMG_CROP_MODE)
        self.IMGConverter.make_images(self.data)

    async def find_step(self, callback_data: str):
        text = ""

        for k, v in self.callbacks_dict.items():
            if v == callback_data:
                text = k
                break

        for k, v in self.data.items():
            if text in v:
                return k
