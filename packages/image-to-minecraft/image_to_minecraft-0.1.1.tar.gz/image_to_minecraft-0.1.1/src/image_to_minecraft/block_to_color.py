from PIL import Image
from importlib import resources
import numpy as np
import os
import json
from functools import lru_cache

@lru_cache(maxsize=8)
def load_palette(filepath: str = "blocks.json"):
    with resources.files("image_to_minecraft").joinpath(filepath).open("r", encoding="utf-8") as f:
        d = json.load(f)

    # Keep only valid RGB entries
    items = [(k, tuple(v)) for k, v in d.items() if v and len(v) == 3]
    return items  # list[(block_name, (r,g,b))]

def build_palette_np(palette_items):
    names = [n for n, _ in palette_items]
    arr = np.array([rgb for _, rgb in palette_items], dtype=np.int16)
    return names, arr

def closest_np(color, names, palette_arr):
    c = np.array(color, dtype=np.int16)
    d = palette_arr - c
    dist2 = (d.astype(np.int32) ** 2).sum(axis=1)
    return names[int(dist2.argmin())]

def block_to_color(image_path): #for now doesn't work with goofy dimensions
    try:
        im = Image.open(image_path)
        pix = im.load()
        rgb = (0, 0, 0)
        for row in range(im.height):
            for col in range(im.width):
                nc = pix[col, row]
                rgb = tuple(rgb[i] + nc[i] for i in range(3))

        rgb = tuple(x // (im.width*im.height) for x in rgb)
        return rgb
    except TypeError as e:
        print(e)
        print("total color, new color:", rgb, nc)
    except IndexError as e:
        print(e)
        print(image_path)
        print("row+col:",row, col)
        print("image dimensions:", im.height, im.width)

def folder_to_colors(folder_path: str):
    colors = {}
    with os.scandir(folder_path) as d:
        for e in d:
            if os.path.splitext(e)[1] in [".png", ".jpg", ".jpeg"]:
                color = block_to_color(e.path)
                colors[e.name] = color

    return colors

def jsonify(dict):
    with open("blocks.json", "w") as file:
        json.dump(dict, file, indent=4)

#jsonify(folder_to_colors("blocks_filtered"))
        
def find_closest_color_in_json(color: tuple[int, int, int], palette_items):
    best_name = ""
    best_delta2 = float("inf")
    r, g, b = color

    for name, (pr, pg, pb)in palette_items:
        dr = pr - r
        dg = pg - g
        db = pb - b
        delta2 = dr*dr + dg*dg + db*db
        if delta2 < best_delta2:
            best_delta2 = delta2
            best_name = name

    return best_name