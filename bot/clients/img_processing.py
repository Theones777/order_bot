import os

from PIL import Image

from config import Config


class IMGConverter:
    def __init__(self, crop_mode: str = "resize_with_padding"):
        self.crop_mode = self.resize_with_padding if crop_mode == "resize_with_padding" else self.hard_resize

    def make_images(self, data: dict):
        for step, step_info in data.items():
            new_image_path = os.path.join(Config.IMAGES_PATH, f"{step}.jpg")
            images = [
                self.crop_mode(Image.open(os.path.join(Config.IMAGES_PATH, f"{text}.jpg")))
                for text in step_info
            ]
            new_width = sum(img.width for img in images)
            new_height = max(img.height for img in images)

            new_image = Image.new('RGB', (new_width, new_height))

            x_offset = 0
            for img in images:
                new_image.paste(img, (x_offset, 0))
                x_offset += img.width

            new_image.save(new_image_path)

    @staticmethod
    def resize_with_padding(img: Image) -> Image:
        target_size = Config.IMG_MAX_SIZE
        target_width, target_height = target_size
        img.thumbnail(target_size, Image.Resampling.LANCZOS)

        new_img = Image.new('RGB', target_size, (255, 255, 255))

        x = (target_width - img.width) // 2
        y = (target_height - img.height) // 2

        new_img.paste(img, (x, y))

        return new_img

    @staticmethod
    def hard_resize(img: Image) -> Image:
        return img.resize(Config.IMG_MAX_SIZE, Image.Resampling.LANCZOS)
