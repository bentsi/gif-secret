# gif-secret
## Embed and encrypt a message in GIF file
### Install dependencies
Supported Python version: 3.11

Prod
```commandline
    poetry install --only main
```
Development
```commandline
    poetry install --with dev
```

### Usage example
Encode and save the file
```python
    gif_secret = GifSecret(file_path=Path("tests/gifs/linux.gif"), key="key!")
    gif_secret.encode(secret_text="Bentsi loves to code Python :)")
    gif_secret.save()
```
Decode
```python
    gif_secret = GifSecret(file_path=Path("tests/gifs/linux.gif"), key="key!")
    decoded_message = gif_secret.decode()
```