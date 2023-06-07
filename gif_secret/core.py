import random
from math import floor
from pathlib import Path
from random import seed
from typing import List, Optional

from PIL import Image, ImageSequence


class GifSecret:
    SECRET_LENGTH_PIXEL_COORDINATES = (0, 0)  # where to store length of the secret message
    SECRET_CHANNEL_IDX = 0  # which channel to use as a storage for secret character

    def __init__(self, file_path: Path, key: str):
        self.file_path = file_path
        self.original_image = Image.open(fp=self.file_path)
        self.encoded_frames: Optional[List[Image]] = []
        self.key = key
        seed(self.key)
        self._frame_num_with_secret = random.randint(0, self.original_image.n_frames - 1)

    @property
    def max_secret_length(self) -> int:
        """
            We assume that we can hide our message using 1 % of image pixels.
            Max length can be 255 since we use only one color channel to store length of secret,
            however this can be improved.
        """
        one_percent_of_pixels = floor(self.original_image.width * self.original_image.height * 0.01)
        return min(255, one_percent_of_pixels)

    def _encode_secret_length(self, frame, secret_length):
        assert secret_length <= self.max_secret_length, f"Max secret length should be <= {self.max_secret_length}"
        pixel = frame.getpixel(xy=self.SECRET_LENGTH_PIXEL_COORDINATES)
        frame.putpixel(xy=self.SECRET_LENGTH_PIXEL_COORDINATES, value=(pixel[0], secret_length, pixel[2]))

    def _get_secret_coordinates(self, width: int, height: int):
        x = random.randint(self.SECRET_LENGTH_PIXEL_COORDINATES[0] + 1, width - 1)
        y = random.randint(self.SECRET_LENGTH_PIXEL_COORDINATES[1] + 1, height - 1)
        return x, y

    def _encode_secret_on_frame(self, frame: Image.Image, secret):
        seed(self.key)
        for char in secret:
            x, y = self._get_secret_coordinates(width=frame.width, height=frame.height)
            pixel: List[int] = list(frame.getpixel((x, y)))
            pixel[self.SECRET_CHANNEL_IDX] = char
            frame.putpixel((x, y), value=tuple(pixel))

    def encode(self, secret_text: str):
        """
            limitation: encode ASCII string only, max 255 characters
            # TODO: support unicode
            # TODO: support longer messages using all frames to encode
        """
        assert len(secret_text) <= self.max_secret_length, f"Message length should be <= {self.max_secret_length} chars"
        secret_text = secret_text.encode()
        cur_frame_num = 0
        for frame in ImageSequence.Iterator(self.original_image):
            image_frame = frame.copy()  # get current frame as image (not the whole sequence)
            image_frame = image_frame.convert("RGB")
            if cur_frame_num == self._frame_num_with_secret:
                self._encode_secret_length(frame=image_frame, secret_length=len(secret_text))
                self._encode_secret_on_frame(frame=image_frame, secret=secret_text)
            self.encoded_frames.append(image_frame)
            cur_frame_num += 1

    def _decode_secret_length(self, frame: Image.Image) -> int:
        pixel = frame.getpixel(xy=self.SECRET_LENGTH_PIXEL_COORDINATES)
        return pixel[1]

    def _decode_secret_from_frame(self, frame: Image.Image, secret_length: int) -> str:
        decoded_secret = []
        seed(self.key)
        frame_rgba = frame.convert(mode="RGB")
        for _ in range(secret_length):
            x, y = self._get_secret_coordinates(width=frame_rgba.width, height=frame_rgba.height)
            pixel_with_secret = list(frame_rgba.getpixel((x, y)))
            secret_char = pixel_with_secret[self.SECRET_CHANNEL_IDX]
            decoded_secret.append(chr(secret_char))
        return "".join(decoded_secret)

    def decode(self) -> str:
        for frame in ImageSequence.Iterator(self.original_image):
            if frame.tell() == self._frame_num_with_secret:
                secret_length = self._decode_secret_length(frame=frame)
                secret_text = self._decode_secret_from_frame(frame=frame, secret_length=secret_length)
                return secret_text

    def save(self):
        """overwrite current GIF"""
        self.save_to_file(file_path=self.file_path)
        self.original_image.close()
        self.original_image = Image.open(fp=self.file_path)

    def save_to_file(self, file_path: Path = Path("linux_all_frames.gif")):
        if not self.encoded_frames:
            raise Exception("No encoded frames found! Run encode method first.")
        self.encoded_frames[0].save(fp=file_path, format="GIF", save_all=True,
                                    append_images=self.encoded_frames[1:])
