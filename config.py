from os import getenv

from dotenv import load_dotenv

load_dotenv()


class Config:
    BOT_TOKEN = getenv("BOT_TOKEN")
    CHEF_TG_ID = getenv("CHEF_TG_ID")  # todo
    CONTACT_NUMBER = getenv("CONTACT_NUMBER", "+7 123 456-78-99")

    PRODUCT_CATALOG_PATH = "data/product_catalog.json"
    IMAGES_PATH = "data/imgs"
    IMG_MAX_SIZE = (800, 600)
    IMG_CROP_MODE = "hard_resize"
