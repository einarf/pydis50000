"""
Bake avatars into a singly chunk of bytes in 256 x 256 resolution RGBA.
We can dump this directly into an array texture
"""
from pathlib import Path
from PIL import Image

AVATAR_DIR = (Path(__file__).parent / '..' / 'pydis50000' / 'resources' / 'avatars').resolve()
OUTPUT_FILE = (Path(__file__).parent / '..' / 'pydis50000' / 'resources' / 'avatars.bin').resolve()
AVATAR_SIZE = 256, 256

data = bytearray()

for img_file in AVATAR_DIR.iterdir():
    print(img_file)
    img = Image.open(img_file)
    img = img.resize(AVATAR_SIZE)
    img = img.convert('RGBA')
    img = img.transpose(Image.FLIP_TOP_BOTTOM)
    data.extend(img.tobytes())

with open(OUTPUT_FILE, 'wb') as fd:
    fd.write(data)
