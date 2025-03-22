import json

from transliterate import translit

from bot.clients.img_processing import IMGConverter
from bot.texts import ADD_TO_CART_MESSAGE
from config import Config


class Storage:

    def __init__(self):
        self.photo_ids = {}
        self.revers_callbacks_dict = {}

        with open(Config.PRODUCT_CATALOG_PATH, mode="r", encoding="utf-8") as f:
            self.data = json.load(f)

        for product in self.data.keys():
            callback_data = translit(product, 'ru', reversed=True).replace(" ", "_")
            self.data[product]["callback_data"] = callback_data
            self.revers_callbacks_dict[callback_data] = product

        self.IMGConverter = IMGConverter(crop_mode=Config.IMG_CROP_MODE)
        self.IMGConverter.make_images(self.data)

        self.data[ADD_TO_CART_MESSAGE] = {
            "callback_data": translit(ADD_TO_CART_MESSAGE, 'ru', reversed=True).replace(" ", "_")
        }