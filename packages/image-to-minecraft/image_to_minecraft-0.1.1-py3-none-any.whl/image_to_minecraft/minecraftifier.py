from PIL import Image
from importlib import resources
from io import BytesIO
from functools import lru_cache

from .image_pixelifier import pixelify_image
from .block_to_color import *


@lru_cache(maxsize=1024)
def _load_block_texture(blocks_dir: str, block_name: str) -> Image.Image:
    # Cache PNGs so we don't reopen them thousands of times.
    with resources.files("image_to_minecraft.blocks").joinpath(block_name).open("rb") as f:
        im = Image.open(f).convert("RGB")
    # Copy into memory so the file handle can close cleanly
    return im.copy()

def converter_path(
        image_path: str,
        width: int = 128, 
        blocks_dir:str = "blocks", 
        blocks_json: str = "blocks.json",
        tile_size: int = 16
    ) -> Image.Image:
    d = load_palette(blocks_json)
    names, palette_arr = build_palette_np(d)

    im = Image.open(image_path)
    im = im.convert("RGB")
    img = pixelify_image(im, width)
    pix = img.load()

    new_im = Image.new('RGB', (img.width * tile_size, img.height * tile_size))
    color_cache = {}
    for y in range(img.height):
        for x in range(img.width):
            cc = pix[x, y]
            print(cc)
            block_name = color_cache.get(cc)
            if block_name == None:
                #opt. idea: instead of dict use 2 lists
                block_name = closest_np(color= cc, names=names, palette_arr=palette_arr)
                color_cache[cc] = block_name

            block_im = _load_block_texture(blocks_dir, block_name)
            new_im.paste(block_im, (x*tile_size, y*tile_size))
    
    #new_im.save("image.png")
    return new_im

                
def converter_bytes(
        image_bytes: bytes,
        width: int = 128, 
        blocks_dir:str = "blocks", 
        blocks_json: str = "blocks.json",
        tile_size: int = 16
    ) -> Image.Image:
    d = load_palette(blocks_json)
    names, palette_arr = build_palette_np(d)

    # Load image from bytes
    with Image.open(BytesIO(image_bytes)) as input_img:
        input_img = input_img.convert("RGB")

        # pixelify_image must accept a PIL Image
        img = pixelify_image(input_img, width)
    pix = img.load()

    new_im = Image.new('RGB', (img.width * tile_size, img.height * tile_size))
    color_cache = {}
    for y in range(img.height):
        for x in range(img.width):
            cc = pix[x, y]
            print(cc)
            block_name = color_cache.get(cc)
            if block_name == None:
                #opt. idea: instead of dict use 2 lists
                block_name = closest_np(color= cc, names=names, palette_arr=palette_arr)
                color_cache[cc] = block_name

            block_im = _load_block_texture(blocks_dir, block_name)
            new_im.paste(block_im, (x*tile_size, y*tile_size))
    
    #new_im.save("image.png")
    return new_im