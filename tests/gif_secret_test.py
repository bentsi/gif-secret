import pytest

from pathlib import Path
from gif_secret.core import GifSecret


@pytest.fixture
def gif_file():
    return Path("gifs/linux.gif")


@pytest.mark.e2e
def test_encode_save_decode(gif_file):
    gif_secret = GifSecret(file_path=gif_file, key="_FRL_!")
    expected_secret_message = "Bentsi loves to code Python :)"
    gif_secret.encode(secret_text=expected_secret_message)
    gif_secret.save()
    secret_message = gif_secret.decode()
    assert secret_message == expected_secret_message

